from django.contrib import admin
from .models import WebCustomer, WebOrder, OrderItem, PaymentTransaction


@admin.register(WebCustomer)
class WebCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    list_filter = ('city', 'created_at')


@admin.register(WebOrder)
class WebOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__user__username', 'shipping_city')
    date_hierarchy = 'created_at'
    readonly_fields = ('order_number', 'customer', 'subtotal', 'tax_amount', 
                       'shipping_cost', 'total_amount', 'shipping_address',
                       'shipping_city', 'shipping_state', 'shipping_zip',
                       'created_at', 'updated_at')
    
    # Disable add and delete for order integrity
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'subtotal')
    search_fields = ('order__order_number', 'product__name')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'transaction_id', 'payment_method', 'amount', 'status', 'processed_at')
    list_filter = ('status', 'payment_method', 'processed_at')
    search_fields = ('transaction_id', 'order__order_number')
    readonly_fields = ('order', 'transaction_id', 'payment_method', 'amount', 'processed_at')
