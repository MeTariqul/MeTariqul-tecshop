from django.contrib import admin
from .models import Product, Category, Supplier, Inventory, ProductImage


# Global Admin Site Header
admin.site.site_header = "TECH SHOP // SYSTEM TERMINAL"
admin.site.site_title = "Admin Access"
admin.site.index_title = "Database Management"


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

