"""
orders/services.py — Order processing service layer.

Keeps business logic (stock checks, tax calc, order creation) out of views
so it can be tested independently and reused (e.g. from an API endpoint).
"""

import uuid
import logging
from decimal import Decimal

from django.db import transaction

from store.models import Product, Inventory, ProductVariant
from .models import WebCustomer, WebOrder, OrderItem, PaymentTransaction

logger = logging.getLogger(__name__)


class InsufficientStockError(Exception):
    """Raised when a product does not have enough stock to fulfil the order."""
    pass


class OrderService:
    """
    Encapsulates all order-creation business rules.

    Usage:
        service = OrderService(request.user, cart_session, site_config)
        order   = service.create_order(shipping_data)
    """

    def __init__(self, user, cart: dict, config):
        """
        :param user:   Django auth User object
        :param cart:   Session cart dict  {SKU: {'quantity': int, 'variant_id': int|None}}
        :param config: SiteConfiguration instance (or None for defaults)
        """
        self.user   = user
        self.cart   = cart
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @transaction.atomic
    def create_order(self, shipping_data: dict) -> WebOrder:
        """
        Validate stock → calculate totals → create WebOrder → deduct stock
        → record PaymentTransaction.  All inside a single DB transaction so
        nothing is persisted if any step fails.

        :param shipping_data: dict with keys:
            shipping_address, shipping_city, shipping_state, shipping_zip
        :returns: the newly created WebOrder instance
        :raises InsufficientStockError: if any product lacks stock
        :raises ValueError: if shipping_data is incomplete
        """
        self._validate_shipping(shipping_data)

        customer = self._get_or_create_customer()
        subtotal, tax_amount, shipping_cost = self._calculate_totals()
        total_amount = subtotal + tax_amount + shipping_cost

        order = WebOrder.objects.create(
            customer=customer,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            **shipping_data,
        )

        self._create_order_items(order)
        self._record_payment(order, total_amount)

        logger.info("Order %s created for user %s", order.order_number, self.user.username)
        return order

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_shipping(self, data: dict):
        required = ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip')
        missing  = [k for k in required if not data.get(k)]
        if missing:
            raise ValueError(f"Missing shipping fields: {', '.join(missing)}")

    def _get_or_create_customer(self) -> WebCustomer:
        customer, _ = WebCustomer.objects.get_or_create(user=self.user)
        return customer

    def _get_global_tax_rate(self) -> Decimal:
        if self.config and self.config.tax_enabled:
            return Decimal(str(self.config.tax_rate))
        return Decimal('0')

    def _get_item_tax(self, product: Product, item_total: Decimal) -> Decimal:
        """Return the tax amount for a single line item respecting product overrides."""
        if product.tax_exempt:
            return Decimal('0.00')
        rate = product.tax_rate if product.tax_rate is not None else self._get_global_tax_rate()
        return item_total * (Decimal(str(rate)) / Decimal('100'))

    def _calculate_totals(self):
        """Return (subtotal, tax_amount, shipping_cost) as Decimal."""
        subtotal   = Decimal('0')
        tax_amount = Decimal('0')

        for sku, item_data in self.cart.items():
            quantity   = int(item_data.get('quantity', 1))
            variant_id = item_data.get('variant_id')

            try:
                if variant_id:
                    variant    = ProductVariant.objects.get(id=variant_id)
                    product    = variant.product
                    line_price = variant.variant_price
                else:
                    product    = Product.objects.get(SKU=sku)
                    line_price = product.discounted_price

                line_total  = line_price * Decimal(str(quantity))
                subtotal   += line_total
                tax_amount += self._get_item_tax(product, line_total)

            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                logger.warning("Cart item %s not found — skipping", sku)
                continue

        # Shipping
        if self.config:
            threshold = Decimal(str(self.config.free_shipping_threshold))
            default   = Decimal(str(self.config.default_shipping_cost))
        else:
            threshold = Decimal('50')
            default   = Decimal('5.99')

        shipping_cost = Decimal('0.00') if subtotal >= threshold else default
        return subtotal, tax_amount, shipping_cost

    def _create_order_items(self, order: WebOrder):
        """Deduct stock and create OrderItem records for every cart entry."""
        for sku, item_data in self.cart.items():
            quantity   = int(item_data.get('quantity', 1))
            variant_id = item_data.get('variant_id')

            try:
                if variant_id:
                    variant  = ProductVariant.objects.select_for_update().get(id=variant_id)
                    product  = variant.product
                    inventory = Inventory.objects.select_for_update().get(product=product)

                    if variant.stock_quantity < quantity:
                        raise InsufficientStockError(
                            f"'{product.name} ({variant})' only has "
                            f"{variant.stock_quantity} unit(s) in stock."
                        )
                    variant.stock_quantity  -= quantity
                    inventory.quantity_on_hand -= quantity
                    variant.save()
                    inventory.save()

                    variant_info = ", ".join(
                        filter(None, [
                            f"Size: {variant.size}"  if variant.size  else "",
                            f"Color: {variant.color}" if variant.color else "",
                        ])
                    )
                    unit_price = variant.variant_price
                else:
                    product   = Product.objects.get(SKU=sku)
                    inventory = Inventory.objects.select_for_update().get(product=product)

                    if inventory.quantity_on_hand < quantity:
                        raise InsufficientStockError(
                            f"'{product.name}' only has "
                            f"{inventory.quantity_on_hand} unit(s) in stock."
                        )
                    inventory.quantity_on_hand -= quantity
                    inventory.save()
                    variant_info = ""
                    unit_price   = product.discounted_price

                tax_rate = product.tax_rate if product.tax_rate is not None else (
                    self.config.tax_rate if self.config else None
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    tax_rate=tax_rate,
                    variant_info=variant_info,
                )

            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                logger.error("Product %s disappeared during checkout", sku)
                raise

    @staticmethod
    def _record_payment(order: WebOrder, amount: Decimal):
        PaymentTransaction.objects.create(
            order=order,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            payment_method='Cash on Delivery',
            amount=amount,
            status='completed',
        )
