from django.contrib import admin
from .models import StaffProfile, ActivityLog, SystemSettings, SiteConfiguration


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'employee_id', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'department']
    search_fields = ['user__username', 'user__email', 'employee_id']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'object_repr', 'description']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'description', 'timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'category', 'is_public', 'updated_at']
    list_filter = ['category', 'is_public']
    search_fields = ['key', 'description']
    ordering = ['category', 'key']


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'maintenance_mode', 'updated_at']
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        ('Social Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Currency & Tax', {
            'fields': ('currency_symbol', 'currency_code', 'tax_rate')
        }),
        ('Order Settings', {
            'fields': ('free_shipping_threshold', 'default_shipping_cost')
        }),
        ('Inventory', {
            'fields': ('low_stock_threshold', 'enable_backorders')
        }),
    )
    readonly_fields = ['updated_at']
