from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ('total', 'tax_amount')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_date',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_name', 'invoice_date', 'payment_status', 'grand_total')
    list_filter = ('payment_status', 'payment_method', 'invoice_date')
    search_fields = ('invoice_number', 'customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline, PaymentInline]
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'invoice_date', 'order', 'is_finalized')
        }),
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_phone', 'customer_email', 'billing_address', 'shipping_address', 'customer_id_number')
        }),
        ('Shop Information', {
            'fields': ('shop_name', 'shop_address', 'shop_phone', 'shop_email', 'tax_number')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'amount_paid', 'amount_due', 'payment_date', 'transaction_id')
        }),
        ('Price Calculations', {
            'fields': ('subtotal', 'total_discount', 'tax_amount', 'shipping_cost', 'grand_total')
        }),
        ('Additional Info', {
            'fields': ('salesperson', 'notes', 'return_policy', 'warranty_info', 'created_by')
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product_name', 'quantity', 'unit_price', 'total')
    search_fields = ('product_name', 'product_sku', 'invoice__invoice_number')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('invoice__invoice_number', 'transaction_id')
