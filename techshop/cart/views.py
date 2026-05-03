from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
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
                'price': product.discounted_price,
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
    
    # Get currency
    currency_short_form = config.currency_short_form if config else 'BDT'
    
    # Calculate cart item count
    cart_item_count = sum(item['quantity'] for item in cart_items)
    
    # Calculate product-wise tax
    tax_amount = Decimal('0.00')
    if config and config.tax_enabled:
        global_tax_rate = config.tax_rate
        for item in cart_items:
            product = item['product']
            price = item['price']
            quantity = item['quantity']
            item_subtotal = price * quantity
            
            # Use product-specific tax rate if set, otherwise use global rate
            if product.tax_exempt:
                item_tax = Decimal('0.00')
            elif product.tax_rate is not None:
                item_tax = item_subtotal * (product.tax_rate / Decimal('100'))
            else:
                item_tax = item_subtotal * (global_tax_rate / Decimal('100'))
            
            tax_amount += item_tax
    
    if config:
        shipping_threshold = config.free_shipping_threshold
        default_shipping = config.default_shipping_cost
    else:
        shipping_threshold = Decimal('50')
        default_shipping = Decimal('5.99')
        
    shipping_cost = default_shipping if subtotal > 0 and subtotal < shipping_threshold else Decimal('0')
    
    # Calculate discount
    discount_amount = Decimal('0')
    coupon_discount = request.session.get('coupon_discount')
    coupon_code = request.session.get('coupon_code')
    if coupon_discount and subtotal > 0:
        discount_amount = subtotal * (Decimal(str(coupon_discount)) / Decimal('100'))
    
    total_amount = subtotal - discount_amount + tax_amount + shipping_cost
    
    # Get saved items
    saved_items_dict = request.session.get('saved_items', {})
    saved_count = len(saved_items_dict)
    
    context = {
        'cart_items': cart_items,
        'cart_item_count': cart_item_count,
        'currency_short_form': currency_short_form,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'coupon_code': coupon_code,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
        'saved_count': saved_count,
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
            
            # Calculate product-wise tax
            tax_amount = Decimal('0.00')
            if config and config.tax_enabled:
                global_tax_rate = config.tax_rate
                for s, item in cart.items():
                    try:
                        p = Product.objects.get(SKU=s)
                        q = item.get('quantity', 1)
                        item_total = p.discounted_price * Decimal(str(q))
                        
                        # Use product-specific tax rate if set, otherwise use global rate
                        if p.tax_exempt:
                            item_tax = Decimal('0.00')
                        elif p.tax_rate is not None:
                            item_tax = item_total * (p.tax_rate / Decimal('100'))
                        else:
                            item_tax = item_total * (global_tax_rate / Decimal('100'))
                        
                        tax_amount += item_tax
                    except Product.DoesNotExist:
                        continue
            
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
  
  
"def save_for_later(request, sku):"  
'    """Save item for later - move from cart to saved items"""'  
"    cart = request.session.get('cart', {})"  
"    saved_items = request.session.get('saved_items', {})"  
"    "  
"    if sku in cart:"  
"        saved_items[sku] = cart[sku]"  
"        del cart[sku]"  
"        "  
"        request.session['cart'] = cart"  
"        request.session['saved_items'] = saved_items"  
"        request.session.modified = True"  
"        "  
"    return redirect('cart:cart_view')" 
  
def save_for_later(request, sku):  
    """Save item for later"""  
    cart = request.session.get('cart', {})  
    saved = request.session.get('saved_items', {})  
    if sku in cart:  
        saved[sku] = cart[sku]  
        del cart[sku]  
        request.session['cart'] = cart  
        request.session['saved_items'] = saved  
        request.session.modified = True  
    return redirect('cart:cart_view') 
  
def apply_coupon(request):  
    """Apply coupon code to cart"""  
    if request.method == 'POST':  
        code = request.POST.get('code', '').strip().upper()  
        coupons = {'SAVE10': 10, 'SAVE20': 20, 'WELCOME': 15, 'FLAT50': 50, 'FLAT100': 100}  
        if code in coupons:  
            request.session['coupon_code'] = code  
            request.session['coupon_discount'] = coupons[code]  
            return JsonResponse({'success': True, 'message': f'Coupon {code} applied!'})  
        return JsonResponse({'success': False, 'message': 'Invalid coupon'})  
    return JsonResponse({'success': False}) 
  
def move_to_cart(request, sku):  
    """Move item from saved for later back to cart"""  
    saved = request.session.get('saved_items', {})  
    cart = request.session.get('cart', {})  
    if sku in saved:  
        cart[sku] = saved[sku]  
        del saved[sku]  
        request.session['cart'] = cart  
        request.session['saved_items'] = saved  
        request.session.modified = True  
    return redirect('cart:cart_view') 


def compare_view(request):
    """View compare page"""
    compare_list = request.session.get('compare_list', [])
    products = []
    from store.models import Product
    for sku in compare_list:
        try:
            product = Product.objects.get(SKU=sku)
            products.append(product)
        except Product.DoesNotExist:
            pass
    
    context = {
        'compare_products': products,
        'compare_count': len(products),
    }
    return render(request, 'cart/compare.html', context)


def add_to_compare(request, sku):
    """Add product to compare list"""
    compare_list = request.session.get('compare_list', [])
    
    if sku not in compare_list:
        if len(compare_list) < 4:
            compare_list.append(sku)
            request.session['compare_list'] = compare_list
            messages.success(request, f'Product added to compare list!')
        else:
            messages.warning(request, 'You can compare maximum 4 products at a time.')
    else:
        messages.info(request, 'Product is already in compare list.')
    
    return redirect(request.META.get('HTTP_REFERER', 'store:product_list'))


def remove_from_compare(request, sku):
    """Remove product from compare list"""
    compare_list = request.session.get('compare_list', [])
    if sku in compare_list:
        compare_list.remove(sku)
        request.session['compare_list'] = compare_list
        messages.success(request, 'Product removed from compare list.')
    return redirect('cart:compare_view')


def clear_compare(request):
    """Clear all products from compare list"""
    request.session['compare_list'] = []
    messages.success(request, 'Compare list cleared.')
    return redirect('cart:compare_view')
