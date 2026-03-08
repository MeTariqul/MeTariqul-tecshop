from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
import io

from .models import Invoice, InvoiceItem, Payment
from orders.models import WebOrder
from admin_dashboard.models import SiteConfiguration


def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.all()
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        invoices = invoices.filter(
            invoice_number__icontains=search_query,
            customer_name__icontains=search_query
        ) | invoices.filter(customer_phone__icontains=search_query)
    
    if status_filter:
        invoices = invoices.filter(payment_status=status_filter)
    
    context = {
        'invoices': invoices[:50],
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'invoices/invoice_list.html', context)


@user_passes_test(is_staff)
def create_invoice(request):
    """Create a new invoice"""
    if request.method == 'POST':
        # Get form data
        customer_id = request.POST.get('customer')
        order_id = request.POST.get('order')
        
        try:
            if order_id:
                order = WebOrder.objects.get(id=order_id)
                customer = order.customer
            else:
                from orders.models import WebCustomer
                customer = WebCustomer.objects.get(id=customer_id)
            
            # Get currency
            config = SiteConfiguration.objects.first()
            currency = config.currency_short_form if config else 'BDT'
            
            # Calculate totals from order items if order selected
            subtotal = 0
            total_discount = 0
            tax_amount = 0
            
            if order_id:
                for item in order.items.all():
                    subtotal += float(item.subtotal)
                    # Calculate tax (assuming 15% VAT)
                    tax_amount += float(item.subtotal) * 0.15
            
            shipping_cost = float(request.POST.get('shipping_cost', 0))
            grand_total = subtotal - total_discount + tax_amount + shipping_cost
            
            # Create invoice
            invoice = Invoice.objects.create(
                invoice_number=Invoice.generate_invoice_number(),
                order=order if order_id else None,
                customer=customer,
                customer_name=request.POST.get('customer_name', customer.user.get_full_name() or customer.user.username),
                customer_phone=request.POST.get('customer_phone', customer.phone),
                customer_email=request.POST.get('customer_email', customer.user.email),
                billing_address=request.POST.get('billing_address', f"{customer.address}\n{customer.city}"),
                shipping_address=request.POST.get('shipping_address', request.POST.get('billing_address', '')),
                payment_method=request.POST.get('payment_method', 'cash'),
                payment_status=request.POST.get('payment_status', 'pending'),
                subtotal=subtotal,
                total_discount=total_discount,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                grand_total=grand_total,
                amount_paid=request.POST.get('amount_paid', 0),
                salesperson=request.POST.get('salesperson', ''),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            
            # Add invoice items from order
            if order_id:
                for item in order.items.all():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=item.product,
                        product_name=item.product.name,
                        product_sku=item.product.SKU,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        tax_rate=15,  # 15% VAT
                    )
            
            # Recalculate totals
            invoice.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
            return redirect('invoices:invoice_detail', invoice_id=invoice.id)
            
        except Exception as e:
            messages.error(request, f'Error creating invoice: {str(e)}')
    
    # Get orders and customers for the form
    orders = WebOrder.objects.all()[:20]
    from orders.models import WebCustomer
    customers = WebCustomer.objects.all()[:20]
    
    context = {
        'orders': orders,
        'customers': customers,
    }
    return render(request, 'invoices/create_invoice.html', context)


@user_passes_test(is_staff)
def invoice_detail(request, invoice_id):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {'invoice': invoice}
    return render(request, 'invoices/invoice_detail.html', context)


@user_passes_test(is_staff)
def view_invoice(request, invoice_id):
    """View invoice in web format"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    config = SiteConfiguration.objects.first()
    currency = config.currency_short_form if config else 'BDT'
    
    context = {
        'invoice': invoice,
        'currency': currency,
    }
    return render(request, 'invoices/view_invoice.html', context)


@user_passes_test(is_staff)
def download_invoice_pdf(request, invoice_id):
    """Download invoice as PDF (print to PDF via browser)"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    config = SiteConfiguration.objects.first()
    currency = config.currency_short_form if config else 'BDT'
    
    context = {
        'invoice': invoice,
        'currency': currency,
    }
    
    # Return HTML view that can be printed to PDF via browser
    return render(request, 'invoices/pdf_invoice.html', context)


@user_passes_test(is_staff)
def print_invoice(request, invoice_id):
    """Print invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    config = SiteConfiguration.objects.first()
    currency = config.currency_short_form if config else 'BDT'
    
    context = {
        'invoice': invoice,
        'currency': currency,
    }
    return render(request, 'invoices/pdf_invoice.html', context)


@user_passes_test(is_staff)
def add_payment(request, invoice_id):
    """Add payment to invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '')
        
        if amount > 0:
            Payment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
            )
            
            # Update invoice
            invoice.amount_paid += amount
            if invoice.amount_paid >= invoice.grand_total:
                invoice.payment_status = 'paid'
            elif invoice.amount_paid > 0:
                invoice.payment_status = 'partial'
            invoice.save()
            
            messages.success(request, 'Payment added successfully!')
        else:
            messages.error(request, 'Invalid payment amount!')
    
    return redirect('invoices:invoice_detail', invoice_id=invoice.id)
