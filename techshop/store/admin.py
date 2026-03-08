from django.contrib import admin
from django.utils import timezone
from .models import Product, Category, Supplier, Inventory, ProductImage, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('SKU', 'name', 'selling_price', 'cost_price', 'stock_status', 'is_available_online')
    search_fields = ('SKU', 'name', 'description')
    list_filter = ('is_available_online', 'category', 'supplier')
    list_per_page = 50
    readonly_fields = ('SKU', 'name', 'description', 'category', 'supplier', 
                       'cost_price', 'selling_price', 'is_available_online', 
                       'featured_image', 'created_at', 'updated_at')
    
    # Disable add and delete to protect legacy database
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def stock_status(self, obj):
        try:
            inventory = obj.inventory
            if inventory.quantity_on_hand > 10:
                return "✓ OK"
            elif inventory.quantity_on_hand > 0:
                return "⚠ LOW"
            return "✗ OUT"
        except Inventory.DoesNotExist:
            return "✗ OUT"
    stock_status.short_description = 'STATUS'
    stock_status.admin_order_field = 'inventory__quantity_on_hand'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_on_hand', 'reorder_level', 'location', 'last_updated')
    search_fields = ('product__name', 'product__SKU')
    list_filter = ('location',)
    readonly_fields = ('last_updated',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'sort_order')
    list_filter = ('product',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'is_verified_purchase', 'created_at', 'has_admin_response')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__user__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at', 'is_verified_purchase', 'product', 'user', 'rating', 'title', 'comment', 'admin_response_by')
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title', 'comment', 'is_verified_purchase')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'admin_response_by', 'admin_response_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_admin_response(self, obj):
        return bool(obj.admin_response)
    has_admin_response.short_description = 'Replied'
    has_admin_response.boolean = True
    
    def save_model(self, request, obj, form, change):
        if obj.admin_response:
            obj.admin_response_by = request.user
            obj.admin_response_at = timezone.now()
        super().save_model(request, obj, form, change)

