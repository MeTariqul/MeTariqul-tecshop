from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
import io
import uuid
import logging

logger = logging.getLogger(__name__)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from store.models import Product, Inventory
from .models import WebCustomer, WebOrder, OrderItem, PaymentTransaction
from .services import OrderService, InsufficientStockError
from admin_dashboard.models import SiteConfiguration

# ====================
# Order Views
# ====================

@login_required
def checkout(request):
    """
    Thin controller — all business logic lives in OrderService.
    Handles HTTP concerns only: session, messages, redirects.
    """
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_view')

    config = SiteConfiguration.objects.first()

    if request.method == 'POST':
        shipping_data = {
            'shipping_address': request.POST.get('shipping_address', '').strip(),
            'shipping_city':    request.POST.get('shipping_city',    '').strip(),
            'shipping_state':   request.POST.get('shipping_state',   '').strip(),
            'shipping_zip':     request.POST.get('shipping_zip',     '').strip(),
        }
        try:
            service = OrderService(request.user, cart, config)
            order   = service.create_order(shipping_data)
            del request.session['cart']
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('orders:order_confirmation', order_id=order.id)

        except ValueError as exc:          # missing shipping fields
            messages.error(request, str(exc))
            return render(request, 'orders/checkout.html', _checkout_context(cart, config))

        except InsufficientStockError as exc:   # stock ran out
            messages.error(request, str(exc))
            return redirect('cart:cart_view')

        except Exception as exc:
            messages.error(request, f'Unexpected error processing order: {exc}')
            return redirect('cart:cart_view')

    # --- GET: preview totals ---
    return render(request, 'orders/checkout.html', _checkout_context(cart, config))


def _checkout_context(cart: dict, config) -> dict:
    """Build the template context for the checkout GET preview."""
    cart_items = []
    subtotal   = Decimal('0')

    for sku, item_data in cart.items():
        try:
            product    = Product.objects.select_related('inventory').get(SKU=sku)
            quantity   = int(item_data.get('quantity', 1))
            item_total = product.discounted_price * Decimal(str(quantity))
            subtotal  += item_total
            cart_items.append({'product': product, 'quantity': quantity, 'item_total': item_total})
        except Product.DoesNotExist:
            continue

    # Reuse service logic for tax + shipping preview
    from .services import OrderService as _S
    dummy = _S.__new__(_S)
    dummy.cart   = cart
    dummy.config = config

    tax_amount = Decimal('0')
    for sku, item_data in cart.items():
        try:
            product    = Product.objects.get(SKU=sku)
            quantity   = int(item_data.get('quantity', 1))
            line_total = product.discounted_price * Decimal(str(quantity))
            tax_amount += dummy._get_item_tax(product, line_total)
        except Product.DoesNotExist:
            continue

    if config:
        threshold      = Decimal(str(config.free_shipping_threshold))
        default_ship   = Decimal(str(config.default_shipping_cost))
    else:
        threshold, default_ship = Decimal('50'), Decimal('5.99')
    shipping_cost = Decimal('0') if subtotal >= threshold else default_ship
    total_amount  = subtotal + tax_amount + shipping_cost

    return {
        'cart_items':    cart_items,
        'subtotal':      subtotal,
        'tax_amount':    tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount':  total_amount,
        'tax_rate':      config.tax_rate if config else 0,
    }

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
    """Custom login view that syncs with Supabase Auth and redirects staff users"""
    from techshop_proj.supabase_client import get_supabase_client
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # 1. Log the user into Django session
                login(request, user)
                
                # 2. Attempt to sign into Supabase Auth (to get JWT for frontend usage if needed)
                try:
                    supabase = get_supabase_client()
                    response = supabase.auth.sign_in_with_password({
                        "email": user.email,
                        "password": password
                    })
                    # You could store response.session.access_token in cookies/session if the frontend needs it
                    request.session['supabase_token'] = response.session.access_token
                except Exception as e:
                    # Supabase Auth failure (e.g. user not in Supabase) must not break Django login.
                    logger.warning("Supabase auth login failed for user %s: %s", user.username, e)
                
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
    """User registration view integrating Supabase Auth"""
    from techshop_proj.supabase_client import get_supabase_admin_client
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 1. Also create the user in Supabase Auth
            try:
                supabase = get_supabase_admin_client()
                # Supabase requires an email for signup
                email = request.POST.get('email', f"{user.username}@example.com") 
                user.email = email
                user.save()
                
                # Create user in Supabase Auth using the admin client
                supabase.auth.admin.create_user({
                    "email": email,
                    "password": request.POST.get('password1'),
                    "email_confirm": True
                })
            except Exception as e:
                # Log error but don't break Django registration
                logger.error("Failed to create user '%s' in Supabase Auth: %s", user.username, e)

            # 2. Log them into Django
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