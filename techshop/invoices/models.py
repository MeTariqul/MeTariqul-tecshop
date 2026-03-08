from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from orders.models import WebCustomer


class Invoice(models.Model):
    """Invoice model for the tech shop"""
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
        ('mobile_banking', 'Mobile Banking'),
    ]
    
    PAYMENT_STATUS = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partial'),
    ]
    
    # Invoice Details
    invoice_number = models.CharField(max_length=20, unique=True, db_index=True)
    invoice_date = models.DateField(auto_now_add=True)
    order = models.ForeignKey('orders.WebOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    # Customer Information
    customer = models.ForeignKey(WebCustomer, on_delete=models.CASCADE, related_name='invoices')
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    billing_address = models.TextField()
    shipping_address = models.TextField(blank=True)
    customer_id_number = models.CharField(max_length=50, blank=True, help_text='Customer ID number')
    
    # Shop Information
    shop_name = models.CharField(max_length=200, default='TechShop')
    shop_address = models.TextField(default='123 Tech Street, Dhaka, Bangladesh')
    shop_phone = models.CharField(max_length=20, default='+880 1234 567890')
    shop_email = models.EmailField(default='info@techshop.com')
    shop_website = models.URLField(blank=True)
    tax_number = models.CharField(max_length=50, blank=True, help_text='Tax/VAT registration number')
    
    # Salesperson
    salesperson = models.CharField(max_length=100, blank=True)
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Price Calculations
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    return_policy = models.TextField(default='7-day return policy applies. Contact support for details.')
    warranty_info = models.TextField(default='1 year service warranty on all electronics.')
    
    # Status
    is_finalized = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        if not self.customer_name:
            self.customer_name = self.customer.user.get_full_name() or self.customer.user.username
        if not self.customer_phone:
            self.customer_phone = self.customer.phone
        if not self.customer_email:
            self.customer_email = self.customer.user.email
        if not self.billing_address:
            self.billing_address = f"{self.customer.address}\n{self.customer.city}"
        if not self.shipping_address:
            self.shipping_address = self.billing_address
        
        # Calculate amounts
        self.amount_due = self.grand_total - self.amount_paid
        
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_invoice_number(cls):
        from datetime import datetime
        year = datetime.now().year
        last_invoice = cls.objects.filter(invoice_number__startswith=f'INV-{year}-').order_by('-invoice_number').first()
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'INV-{year}-{new_num:04d}'


class InvoiceItem(models.Model):
    """Individual items in an invoice"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate totals
        subtotal = self.unit_price * self.quantity
        self.tax_amount = (subtotal - self.discount) * (self.tax_rate / 100)
        self.total = subtotal - self.discount + self.tax_amount
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records for invoices"""
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
        ('mobile_banking', 'Mobile Banking'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"
