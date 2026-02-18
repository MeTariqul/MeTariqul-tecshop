from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from store.models import Product, Inventory


def cart_view(request):
    """Display the shopping cart with real-time stock availability"""
    cart = request.session.get('cart', {})
    
    cart_items = []
    subtotal = Decimal('0')
    out_of_stock_items = []
    
    for sku, item_data in cart.items():
        try:
            product = Product.objects.select_related('inventory').get(SKU=sku)
            quantity = item_data.get('quantity', 1)
            
            # Get real-time inventory
            available_stock = 0
            if hasattr(product, 'inventory') and product.inventory:
                available_stock = product.inventory.quantity_on_hand
            
            # Check if item is available
            if available_stock < quantity:
                out_of_stock_items.append({
                    'sku': sku,
                    'name': product.name,
                    'requested': quantity,
                    'available': available_stock
                })
                # Adjust quantity to available stock
                if available_stock > 0:
                    quantity = available_stock
                    cart[sku]['quantity'] = quantity
                else:
                    continue
            
            item_total = product.discounted_price * Decimal(str(quantity))
            subtotal += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
                'sku': sku,
                'available_stock': available_stock
            })
        except Product.DoesNotExist:
            continue
    
    # Save updated cart if quantities were adjusted
    if out_of_stock_items:
        request.session['cart'] = cart
        request.session.modified = True
    
    # Read tax & shipping config
    from admin_dashboard.models import SiteConfiguration
    config = SiteConfiguration.objects.first()
    
    if config and config.tax_enabled:
        tax_amount = subtotal * (config.tax_rate / Decimal('100'))
    else:
        tax_amount = Decimal('0.00')
    
    if config:
        shipping_threshold = config.free_shipping_threshold
        default_shipping = config.default_shipping_cost
    else:
        shipping_threshold = Decimal('50')
        default_shipping = Decimal('5.99')
        
    shipping_cost = default_shipping if subtotal > 0 and subtotal < shipping_threshold else Decimal('0')
    total_amount = subtotal + tax_amount + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, sku):
    """Add a product to the shopping cart with stock validation and variant support"""
    product = get_object_or_404(Product, SKU=sku, is_available_online=True)
    
    # Get variant details if provided
    variant_id = request.POST.get('variant_id')
    selected_size = request.POST.get('size', '')
    selected_color = request.POST.get('color', '')
    
    # Determine which inventory to check
    available_stock = 0
    price = product.discounted_price
    variant = None
    
    if variant_id:
        # Check specific variant stock
        from store.models import ProductVariant
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)
        available_stock = variant.stock_quantity
        price = variant.variant_price
    elif selected_size or selected_color:
        # Find matching variant
        from store.models import ProductVariant
        variant_qs = ProductVariant.objects.filter(
            product=product,
            size__iexact=selected_size,
            color__iexact=selected_color,
            is_active=True
        )
        if variant_qs.exists():
            variant = variant_qs.first()
            available_stock = variant.stock_quantity
            price = variant.variant_price
        else:
            # Check product inventory
            available_stock = product.stock_quantity
    else:
        # Check product inventory
        available_stock = product.stock_quantity
    
    if available_stock <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock!')
        return redirect('store:product_detail', sku=sku)
    
    # Get current cart from session
    cart = request.session.get('cart', {})
    
    # Get quantity from POST or default to 1
    quantity = int(request.POST.get('quantity', 1))
    
    # Build cart key including variant info
    cart_key = sku
    if variant:
        cart_key = f"{sku}-V{variant.id}"
    
    # Check if requested quantity is available
    current_qty = cart.get(cart_key, {}).get('quantity', 0)
    if current_qty + quantity > available_stock:
        quantity = max(0, available_stock - current_qty)
        if quantity == 0:
            messages.error(request, f'Sorry, only {available_stock} {product.name}(s) available!')
            return redirect('cart:cart_view')
        messages.warning(request, f'Only {quantity} {product.name}(s) available. Added to cart.')
    
    # Check if product already in cart
    if cart_key in cart:
        cart[cart_key]['quantity'] = cart[cart_key].get('quantity', 0) + quantity
    else:
        cart[cart_key] = {
            'quantity': quantity,
            'name': product.name,
            'price': str(price),
            'variant_id': variant.id if variant else None,
            'size': selected_size,
            'color': selected_color
        }
    
    # Save cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart:cart_view')


def remove_from_cart(request, sku):
    """Remove a product from the shopping cart"""
    cart = request.session.get('cart', {})
    
    if sku in cart:
        del cart[sku]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart')
    else:
        messages.error(request, 'Item not found in cart')
    
    return redirect('cart:cart_view')


def update_cart_item(request, sku):
    """Update the quantity of a cart item"""
    cart = request.session.get('cart', {})
    
    if sku in cart:
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            # Remove item if quantity is 0 or less
            del cart[sku]
            messages.success(request, 'Item removed from cart')
        else:
            cart[sku]['quantity'] = quantity
            messages.success(request, 'Cart updated')
        
        request.session['cart'] = cart
        request.session.modified = True
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Recalculate totals
            subtotal = Decimal('0')
            item_subtotal = Decimal('0')
            
            for s, item in cart.items():
                try:
                    p = Product.objects.get(SKU=s)
                    q = item.get('quantity', 1)
                    total = p.discounted_price * Decimal(str(q))
                    subtotal += total
                    if s == sku:
                        item_subtotal = total
                except Product.DoesNotExist:
                    continue
            
            from admin_dashboard.models import SiteConfiguration
            config = SiteConfiguration.objects.first()
            
            if config and config.tax_enabled:
                tax_amount = subtotal * (config.tax_rate / Decimal('100'))
            else:
                tax_amount = Decimal('0.00')
            
            if config:
                shipping_threshold = config.free_shipping_threshold
                default_shipping = config.default_shipping_cost
            else:
                shipping_threshold = Decimal('50')
                default_shipping = Decimal('5.99')
            
            shipping_cost = default_shipping if subtotal > 0 and subtotal < shipping_threshold else Decimal('0')
            total_amount = subtotal + tax_amount + shipping_cost
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'item_subtotal': str(item_subtotal),
                'cart_total': str(subtotal),
                'tax_amount': str(round(tax_amount, 2)),
                'shipping_cost': str(shipping_cost),
                'total_amount': str(round(total_amount, 2))
            })
    else:
        messages.error(request, 'Item not found in cart')
    
    return redirect('cart:cart_view')
