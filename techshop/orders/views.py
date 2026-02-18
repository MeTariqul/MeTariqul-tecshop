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
from reportlab.lib.pagesizes import A4
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
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=variant.variant_price,
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
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=product.discounted_price
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
    shipping_cost = default_shipping if subtotal < shipping_threshold else Decimal('0.00')
    total_amount = subtotal + tax_amount + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
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
    """Generate and download PDF invoice with QR code"""
    order = get_object_or_404(WebOrder, id=order_id, customer__user=request.user)
    items = order.items.all()
    
    # Get currency from settings
    from admin_dashboard.models import SiteConfiguration
    config = SiteConfiguration.objects.first()
    currency = config.currency_short_form if config else 'BDT'
    
    # Create the PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Custom styles - Modern teal theme
    title_style = ParagraphStyle('InvoiceTitle', parent=styles['Title'],
                                 fontSize=32, textColor=colors.HexColor('#11998e'),
                                 spaceAfter=4)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=9, textColor=colors.grey, spaceAfter=16)
    heading_style = ParagraphStyle('SectionHead', parent=styles['Heading2'],
                                    fontSize=12, textColor=colors.HexColor('#11998e'),
                                    spaceBefore=20, spaceAfter=10)
    normal_style = ParagraphStyle('NormalCustom', parent=styles['Normal'],
                                   fontSize=10, leading=16)
    right_style = ParagraphStyle('Right', parent=styles['Normal'],
                                  fontSize=10, alignment=TA_RIGHT)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'],
                                 fontSize=10, leading=14, textColor=colors.HexColor('#333'))
    
    # ============= HEADER =============
    # Green gradient header box
    header_data = [[
        Paragraph("<b>TechShop</b>", ParagraphStyle('CoName', fontSize=28, textColor=colors.white, bold=True)),
        Paragraph("<b>INVOICE</b>", ParagraphStyle('InvNum', fontSize=24, textColor=colors.white, alignment=TA_RIGHT))
    ]]
    header_table = Table(header_data, colWidths=[doc.width * 0.5, doc.width * 0.5])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#11998e')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(header_table)
    
    # Company info
    elements.append(Paragraph("123 Tech Street, Dhaka, Bangladesh", subtitle_style))
    elements.append(Paragraph("info@techshop.com | +880 1234 567890", subtitle_style))
    elements.append(Spacer(1, 10))
    
    # Divider line
    divider_data = [['', '']]
    divider_table = Table(divider_data, colWidths=[doc.width])
    divider_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#11998e')),
    ]))
    elements.append(divider_table)
    elements.append(Spacer(1, 15))
    
    # ============= ORDER INFO =============
    info_data = [
        [Paragraph("<b>Order Number:</b>", bold_style), 
         Paragraph(f"<b>{order.order_number}</b>", ParagraphStyle('OrdNum', fontSize=12, textColor=colors.HexColor('#11998e'))),
         Paragraph("<b>Date:</b>", right_style), 
         Paragraph(f"{order.created_at.strftime('%B %d, %Y')}", right_style)],
        [Paragraph("<b>Status:</b>", bold_style), 
         Paragraph("<b>Confirmed</b>", ParagraphStyle('Stat', textColor=colors.HexColor('#11998e'))),
         Paragraph("<b>Payment:</b>", right_style), 
         Paragraph("<b>Paid</b>", ParagraphStyle('Pay', textColor=colors.HexColor('#11998e')))],
    ]
    info_table = Table(info_data, colWidths=[doc.width * 0.15, doc.width * 0.35, doc.width * 0.20, doc.width * 0.30])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # ============= SHIPPING ADDRESS =============
    ship_heading = ParagraphStyle('ShipHead', fontSize=11, textColor=colors.HexColor('#11998e'),
                                  spaceAfter=6)
    elements.append(Paragraph("Shipping Address", ship_heading))
    
    ship_data = [[
        Paragraph(f"{order.customer.user.get_full_name() or order.customer.user.username}", bold_style),
        Paragraph("Billing Address", ship_heading),
    ]]
    ship_table = Table(ship_data, colWidths=[doc.width * 0.5, doc.width * 0.5])
    ship_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(ship_table)
    
    ship_addr_data = [[
        Paragraph(f"{order.shipping_address}<br/>{order.shipping_city}, {order.shipping_state} {order.shipping_zip}", normal_style),
        Paragraph(f"{order.shipping_address}<br/>{order.shipping_city}, {order.shipping_state} {order.shipping_zip}", normal_style),
    ]]
    ship_addr_table = Table(ship_addr_data, colWidths=[doc.width * 0.5, doc.width * 0.5])
    ship_addr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(ship_addr_table)
    elements.append(Spacer(1, 20))
    
    # ============= ITEMS TABLE =============
    elements.append(Paragraph("Order Items", ship_heading))
    
    table_data = [
        [Paragraph('<b>#</b>', normal_style),
         Paragraph('<b>Product</b>', normal_style),
         Paragraph('<b>SKU</b>', normal_style),
         Paragraph('<b>Qty</b>', ParagraphStyle('c', parent=normal_style, alignment=TA_CENTER)),
         Paragraph('<b>Price</b>', ParagraphStyle('r', parent=normal_style, alignment=TA_RIGHT)),
         Paragraph('<b>Subtotal</b>', ParagraphStyle('r', parent=normal_style, alignment=TA_RIGHT))],
    ]
    
    for idx, item in enumerate(items, 1):
        table_data.append([
            Paragraph(str(idx), normal_style),
            Paragraph(item.product.name, normal_style),
            Paragraph(str(item.product.SKU), normal_style),
            Paragraph(str(item.quantity), ParagraphStyle('c', parent=normal_style, alignment=TA_CENTER)),
            Paragraph(f"{currency} {item.unit_price:,.2f}", ParagraphStyle('r', parent=normal_style, alignment=TA_RIGHT)),
            Paragraph(f"{currency} {item.subtotal:,.2f}", ParagraphStyle('r', parent=normal_style, alignment=TA_RIGHT)),
        ])
    
    items_table = Table(table_data, colWidths=[doc.width * 0.05, doc.width * 0.30, doc.width * 0.15,
                                            doc.width * 0.10, doc.width * 0.20, doc.width * 0.20])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#11998e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (4, 0), (5, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # ============= TOTALS =============
    # Right-aligned totals
    totals_x = doc.width * 0.60
    totals_width = doc.width * 0.40
    
    totals_data = [
        [Paragraph('Subtotal:', right_style), 
         Paragraph(f"{currency} {order.subtotal:,.2f}", right_style)],
        [Paragraph('Shipping:', right_style), 
         Paragraph(f"{currency} {order.shipping_cost:,.2f}" if order.shipping_cost > 0 else "FREE", right_style)],
        [Paragraph('Tax:', right_style), 
         Paragraph(f"{currency} {order.tax_amount:,.2f}", right_style)],
        [Paragraph('<b>Total:</b>', ParagraphStyle('Tot', parent=bold_style, fontSize=14)), 
         Paragraph(f"<b>{currency} {order.total_amount:,.2f}</b>", ParagraphStyle('TotAmt', parent=bold_style, fontSize=14, textColor=colors.HexColor('#11998e')))],
    ]
    totals_table = Table(totals_data, colWidths=[totals_x, totals_width])
    totals_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 3), (1, 3), 2, colors.HexColor('#11998e')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # ============= QR CODE =============
    order_url = request.build_absolute_uri(f'/orders/confirmation/{order.id}/')
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(order_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#11998e", back_color="white")
    
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    qr_rl_image = RLImage(qr_buffer, width=2.5*cm, height=2.5*cm)
    
    qr_data = [[
        qr_rl_image, 
        Paragraph("<b>Track Your Order</b><br/><br/>Scan this QR code to view your order details and tracking information online.", 
                  ParagraphStyle('QRText', fontSize=9, textColor=colors.grey))
    ]]
    qr_table = Table(qr_data, colWidths=[3*cm, doc.width - 3*cm])
    qr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 0), (1, 0), 15),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(qr_table)
    elements.append(Spacer(1, 25))
    
    # ============= FOOTER =============
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph("Thank you for shopping with TechShop!", footer_style))
    elements.append(Paragraph("This is a computer-generated invoice. No signature required.", footer_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("© 2026 TechShop. All rights reserved.", ParagraphStyle('Copy', fontSize=8, textColor=colors.lightgrey, alignment=TA_CENTER)))
    
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