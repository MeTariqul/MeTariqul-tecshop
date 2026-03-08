from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
from decimal import Decimal
import uuid
import io
import qrcode
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from .fraud_detection import check_order_security
from store.models import Product, Inventory
from .models import WebCustomer, WebOrder, OrderItem, PaymentTransaction
from cart.models import ShoppingCart, CartItem
from admin_dashboard.models import SiteConfiguration

# ====================
# Order Views
# ====================

@login_required
def checkout(request):
    """Process checkout and create order with atomic stock deduction"""
    # Get cart from session
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_view')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get or create customer profile
                customer, created = WebCustomer.objects.get_or_create(user=request.user)
                
                # Process order
                shipping_address = request.POST.get('shipping_address')
                shipping_city = request.POST.get('shipping_city')
                shipping_state = request.POST.get('shipping_state')
                shipping_zip = request.POST.get('shipping_zip')
                
                if not all([shipping_address, shipping_city, shipping_state, shipping_zip]):
                    messages.error(request, 'Please fill in all shipping information')
                    return render(request, 'orders/checkout.html')
                
                # Calculate totals
                subtotal = Decimal('0')
                for sku, item_data in cart.items():
                    try:
                        product = Product.objects.get(SKU=sku)
                        quantity = item_data.get('quantity', 1)
                        subtotal += product.discounted_price * Decimal(str(quantity))
                    except Product.DoesNotExist:
                        continue
                
                # Read tax & shipping config
                config = SiteConfiguration.objects.first()
                
                # Calculate product-wise tax
                tax_amount = Decimal('0.00')
                if config and config.tax_enabled:
                    global_tax_rate = config.tax_rate
                    for sku, item_data in cart.items():
                        try:
                            product = Product.objects.get(SKU=sku)
                            quantity = item_data.get('quantity', 1)
                            item_total = product.discounted_price * Decimal(str(quantity))
                            
                            # Use product-specific tax rate if set, otherwise use global rate
                            if product.tax_exempt:
                                item_tax = Decimal('0.00')
                            elif product.tax_rate is not None:
                                item_tax = item_total * (product.tax_rate / Decimal('100'))
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
                shipping_cost = default_shipping if subtotal < shipping_threshold else Decimal('0.00')
                total_amount = subtotal + tax_amount + shipping_cost
                
                # Create order record (for Web history)
                order = WebOrder.objects.create(
                    customer=customer,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=total_amount,
                    shipping_address=shipping_address,
                    shipping_city=shipping_city,
                    shipping_state=shipping_state,
                    shipping_zip=shipping_zip,
                )
                
                # Process each item in the cart and deduct stock
                for sku, item_data in cart.items():
                    quantity = item_data.get('quantity', 1)
                    variant_id = item_data.get('variant_id')
                    
                    # Check if this is a variant product
                    if variant_id:
                        from store.models import ProductVariant
                        variant = ProductVariant.objects.select_for_update().get(id=variant_id)
                        product = variant.product
                        
                        if variant.stock_quantity < quantity:
                            raise Exception(f"Product {product.name} ({variant}) is out of stock! Only {variant.stock_quantity} available.")
                        
                        # Deduct from variant stock
                        variant.stock_quantity -= quantity
                        variant.save()
                        
                        # Also update product inventory
                        inventory = Inventory.objects.select_for_update().get(product=product)
                        inventory.quantity_on_hand -= quantity
                        inventory.save()
                        
                        # Add to Order Items with variant info
                        tax_rate = product.tax_rate if product.tax_rate else config.tax_rate
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=variant.variant_price,
                            tax_rate=tax_rate,
                            variant_info=f"Size: {variant.size}, Color: {variant.color}" if variant.size or variant.color else ""
                        )
                    else:
                        # Original product-only logic
                        product = Product.objects.select_for_update().get(SKU=sku)
                        inventory = Inventory.objects.select_for_update().get(product=product)
                        
                        if inventory.quantity_on_hand < quantity:
                            raise Exception(f"Product {product.name} is out of stock! Only {inventory.quantity_on_hand} available.")
                        
                        # Deduct Stock from Physical Shop DB
                        inventory.quantity_on_hand -= quantity
                        inventory.save()
                        
                        # Add to Order Items
                        tax_rate = product.tax_rate if product.tax_rate else config.tax_rate
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=product.discounted_price,
                            tax_rate=tax_rate
                        )
                
                # Create payment transaction (simulated)
                PaymentTransaction.objects.create(
                    order=order,
                    transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                    payment_method='Credit Card',
                    amount=total_amount,
                    status='completed'
                )
                
                # 5. Clear Cart
                del request.session['cart']
                
                messages.success(request, f'Order {order.order_number} placed successfully!')
                return redirect('orders:order_confirmation', order_id=order.id)
                
        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('cart:cart_view')
    
    # For GET request, show cart items from session
    cart_items = []
    subtotal = Decimal('0')
    
    for sku, item_data in cart.items():
        try:
            product = Product.objects.get(SKU=sku)
            quantity = item_data.get('quantity', 1)
            item_total = product.discounted_price * Decimal(str(quantity))
            subtotal += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
        except Product.DoesNotExist:
            continue
    
    # Read tax & shipping config for GET preview
    config = SiteConfiguration.objects.first()
    
    # Calculate product-wise tax
    tax_amount = Decimal('0.00')
    if config and config.tax_enabled:
        global_tax_rate = config.tax_rate
        for sku, item_data in cart.items():
            try:
                product = Product.objects.get(SKU=sku)
                quantity = item_data.get('quantity', 1)
                item_total = product.discounted_price * Decimal(str(quantity))
                
                # Use product-specific tax rate if set, otherwise use global rate
                if product.tax_exempt:
                    item_tax = Decimal('0.00')
                elif product.tax_rate is not None:
                    item_tax = item_total * (product.tax_rate / Decimal('100'))
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
    shipping_cost = default_shipping if subtotal < shipping_threshold else Decimal('0.00')
    total_amount = subtotal + tax_amount + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
        'tax_rate': config.tax_rate if config else 0,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    """Display order confirmation"""
    order = get_object_or_404(WebOrder, id=order_id, customer__user=request.user)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/order_confirmation.html', context)

@login_required
def download_invoice(request, order_id):
    """Generate and download PDF invoice - Modern Minimalist Design"""
    order = get_object_or_404(WebOrder, id=order_id, customer__user=request.user)
    items = order.items.all()
    
    # Get currency from settings
    from admin_dashboard.models import SiteConfiguration
    config = SiteConfiguration.objects.first()
    currency = config.currency_short_form if config else 'BDT'
    
    # Create the PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40, bottomMargin=40,
                            leftMargin=40, rightMargin=40)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Clean modern styles
    text_color = colors.HexColor('#333333')
    muted_color = colors.HexColor('#888888')
    accent_color = colors.HexColor('#2563eb')  # Modern blue
    light_gray = colors.HexColor('#f5f5f5')
    
    normal_style = ParagraphStyle('NormalCustom', parent=styles['Normal'],
                                   fontSize=10, leading=14, textColor=text_color)
    right_style = ParagraphStyle('Right', parent=styles['Normal'],
                                  fontSize=10, alignment=TA_RIGHT)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'],
                                 fontSize=10, bold=True)
    
    # ============= HEADER =============
    # Clean minimal header
    elements.append(Table([[
        Paragraph("<b><font size=20 color=#2563eb>TECH</font><font size=20 color=#333333>SHOP</font></b>", 
                   ParagraphStyle('Logo', fontSize=18, bold=True)),
        Paragraph(f"<b>INVOICE</b>", ParagraphStyle('InvLabel', fontSize=12, alignment=TA_RIGHT, 
                                                     textColor=accent_color, bold=True))
    ]], colWidths=[doc.width/2, doc.width/2]))
    
    elements.append(Spacer(1, 5))
    
    # Invoice details - minimal and clean
    details_data = [[
        Paragraph(f"<b>Invoice No:</b> {order.order_number}", normal_style),
        Paragraph(f"<b>Date:</b> {order.created_at.strftime('%d %b %Y')}", right_style),
    ]]
    details_table = Table(details_data, colWidths=[doc.width/2, doc.width/2])
    details_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(details_table)
    
    # Divider line
    divider = Table([['']], colWidths=[doc.width])
    divider.setStyle(TableStyle([('LINEABOVE', (0, 0), (0, 0), 1, light_gray)]))
    elements.append(divider)
    elements.append(Spacer(1, 20))
    
    # ============= BILL TO SECTION =============
    # Clean two-column address section
    addr_data = [[
        Paragraph("<b>BILL TO</b>", ParagraphStyle('Label', fontSize=9, textColor=muted_color)),
        Paragraph("<b>SHIP TO</b>", ParagraphStyle('Label', fontSize=9, textColor=muted_color)),
    ], [
        Paragraph(f"{order.customer.user.get_full_name() or order.customer.user.username}", bold_style),
        Paragraph(f"{order.customer.user.get_full_name() or order.customer.user.username}", bold_style),
    ], [
        Paragraph(f"{order.customer.user.email}", normal_style),
        Paragraph(f"{order.shipping_address}", normal_style),
    ], [
        Paragraph(f"Phone: {order.customer.phone}", normal_style),
        Paragraph(f"{order.shipping_city}, {order.shipping_zip}", normal_style),
    ]]
    
    addr_table = Table(addr_data, colWidths=[doc.width * 0.5, doc.width * 0.5])
    addr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(addr_table)
    elements.append(Spacer(1, 25))
    
    # ============= ITEMS TABLE =============
    # Clean header row
    header_style = ParagraphStyle('Header', fontSize=9, textColor=colors.white, bold=True)
    
    table_data = [
        [Paragraph('<b>#</b>', header_style),
         Paragraph('<b>Item</b>', header_style),
         Paragraph('<b>Qty</b>', ParagraphStyle('c', parent=header_style, alignment=TA_CENTER)),
         Paragraph('<b>Price</b>', right_style),
         Paragraph('<b>Total</b>', right_style)],
    ]
    
    for idx, item in enumerate(items, 1):
        table_data.append([
            Paragraph(str(idx), normal_style),
            Paragraph(item.product.name, normal_style),
            Paragraph(str(item.quantity), ParagraphStyle('c', parent=normal_style, alignment=TA_CENTER)),
            Paragraph(f"{currency} {item.unit_price:,.2f}", right_style),
            Paragraph(f"{currency} {item.subtotal:,.2f}", right_style),
        ])
    
    items_table = Table(table_data, colWidths=[doc.width * 0.08, doc.width * 0.42, 
                                                doc.width * 0.12, doc.width * 0.19, doc.width * 0.19])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), accent_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0, None),
        ('LINEBELOW', (0, 0), (-1, 0), 1, accent_color),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 25))
    
    # ============= TOTALS =============
    # Clean totals section aligned right
    totals_data = [
        [Paragraph('Subtotal', normal_style), 
         Paragraph(f"{currency} {order.subtotal:,.2f}", right_style)],
        [Paragraph('Shipping', normal_style), 
         Paragraph(f"{currency} {order.shipping_cost:,.2f}" if order.shipping_cost > 0 else "FREE", right_style)],
        [Paragraph('Tax', normal_style), 
         Paragraph(f"{currency} {order.tax_amount:,.2f}", right_style)],
        [Paragraph('', normal_style), Paragraph('', right_style)],  # Spacer
        [Paragraph('<b>Total</b>', ParagraphStyle('Total', fontSize=12, bold=True)), 
         Paragraph(f"{currency} {order.total_amount:,.2f}", ParagraphStyle('TotalAmt', fontSize=12, bold=True, textColor=accent_color))],
    ]
    
    totals_table = Table(totals_data, colWidths=[doc.width * 0.7, doc.width * 0.3])
    totals_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (3, 0), (4, 0), 1, light_gray),
        ('LINEABOVE', (4, 0), (4, 0), 2, accent_color),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # ============= PAYMENT INFO =============
    # Clean payment status box
    payment_data = [[
        Paragraph("<b>Payment Status:</b> PAID", ParagraphStyle('Paid', fontSize=11, textColor=colors.HexColor('#16a34a'), bold=True)),
        Paragraph("<b>Payment Method:</b> Cash on Delivery", normal_style),
    ]]
    payment_table = Table(payment_data, colWidths=[doc.width])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 30))
    
    # ============= FOOTER =============
    # Minimal footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=8, textColor=muted_color, alignment=TA_CENTER)
    
    elements.append(Paragraph("Thank you for your purchase!", 
                             ParagraphStyle('Thanks', fontSize=11, alignment=TA_CENTER, bold=True, textColor=text_color)))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("Questions? Contact us at support@techshop.com", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    
    # If print mode, serve inline so the browser opens the PDF for printing
    if request.GET.get('print'):
        response['Content-Disposition'] = f'inline; filename="{order.order_number}.pdf"'
    else:
        response['Content-Disposition'] = f'attachment; filename="{order.order_number}.pdf"'
    return response

@login_required
def order_history(request):
    """Display user's order history"""
    try:
        customer = request.user.webcustomer
        orders = WebOrder.objects.filter(customer=customer).order_by('-created_at')
    except WebCustomer.DoesNotExist:
        orders = []
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)

# ====================
# Authentication Views
# ====================

def custom_login(request):
    """Custom login view that redirects staff users to dashboard"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Check if user is a staff member or has staff profile
                if user.is_staff or hasattr(user, 'staff_profile'):
                    return redirect('admin_dashboard:dashboard')
                else:
                    return redirect('store:home')
    else:
        form = AuthenticationForm(request)
    
    return render(request, 'registration/login.html', {'form': form})


# ====================
# Account Views
# ====================

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('store:home')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'orders/register.html', context)

@login_required
def user_profile(request):
    """User profile management"""
    try:
        customer = request.user.webcustomer
    except WebCustomer.DoesNotExist:
        customer = WebCustomer.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update profile information
        customer.phone = request.POST.get('phone', customer.phone)
        customer.address = request.POST.get('address', customer.address)
        customer.city = request.POST.get('city', customer.city)
        customer.state = request.POST.get('state', customer.state)
        customer.zip_code = request.POST.get('zip_code', customer.zip_code)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            customer.profile_picture = request.FILES['profile_picture']
        
        customer.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('orders:user_profile')
    
    context = {
        'customer': customer,
    }
    return render(request, 'orders/profile.html', context)