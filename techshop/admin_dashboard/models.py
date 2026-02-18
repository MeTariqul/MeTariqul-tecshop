from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class StaffProfile(models.Model):
    """Extended profile for staff members with access control"""
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('manager', 'Manager'),
        ('inventory_manager', 'Inventory Manager'),
        ('order_manager', 'Order Manager'),
        ('support', 'Customer Support'),
        ('accountant', 'Accountant'),
        ('delivery_person', 'Delivery Person'),
        ('seller', 'Seller'),
        ('viewer', 'Viewer'),
        ('customer', 'Customer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom Permissions (can be overridden by admin)
    can_manage_products = models.BooleanField(default=False)
    can_manage_orders = models.BooleanField(default=False)
    can_manage_inventory = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_manage_finance = models.BooleanField(default=False)
    can_manage_sellers = models.BooleanField(default=False)
    can_view_all_orders = models.BooleanField(default=False)
    can_view_own_orders = models.BooleanField(default=True)
    can_manage_delivery = models.BooleanField(default=False)
    
    # Role switching - Admin can temporarily switch to another role
    original_role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    is_switched = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            import uuid
            self.employee_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class UserPermission(models.Model):
    """Custom permissions that can be assigned to users"""
    
    PERMISSION_CHOICES = [
        ('manage_products', 'Manage Products'),
        ('manage_orders', 'Manage Orders'),
        ('manage_inventory', 'Manage Inventory'),
        ('manage_customers', 'Manage Customers'),
        ('manage_staff', 'Manage Staff'),
        ('manage_sellers', 'Manage Sellers'),
        ('view_reports', 'View Reports'),
        ('manage_settings', 'Manage Settings'),
        ('manage_finance', 'Manage Finance'),
        ('manage_delivery', 'Manage Delivery'),
        ('view_all_orders', 'View All Orders'),
        ('view_own_orders', 'View Own Orders'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    permission = models.CharField(max_length=50, choices=PERMISSION_CHOICES)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    can_grant = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'permission']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_permission_display()}"


class ActivityLog(models.Model):
    """Track all administrative activities in the system"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} {self.model_name} at {self.timestamp}"


class SystemSettings(models.Model):
    """Store configurable system settings"""
    
    SITE_SETTINGS = 'site'
    ORDER_SETTINGS = 'order'
    INVENTORY_SETTINGS = 'inventory'
    PAYMENT_SETTINGS = 'payment'
    SHIPPING_SETTINGS = 'shipping'
    EMAIL_SETTINGS = 'email'
    
    CATEGORY_CHOICES = [
        (SITE_SETTINGS, 'Site Settings'),
        (ORDER_SETTINGS, 'Order Settings'),
        (INVENTORY_SETTINGS, 'Inventory Settings'),
        (PAYMENT_SETTINGS, 'Payment Settings'),
        (SHIPPING_SETTINGS, 'Shipping Settings'),
        (EMAIL_SETTINGS, 'Email Settings'),
    ]
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category} - {self.key}"


class SiteConfiguration(models.Model):
    """Main site configuration for easy customization"""
    
    site_name = models.CharField(max_length=200, default='TechShop')
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # Contact Info
    contact_email = models.EmailField(default='info@techshop.com')
    contact_phone = models.CharField(max_length=20, default='(555) 123-4567')
    contact_address = models.TextField(default='123 Tech Street, Dhaka, Bangladesh')
    
    # Social Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
# Currency & Tax
    CURRENCY_CHOICES = [
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('BDT', 'BDT - Bangladeshi Taka'),
        ('INR', 'INR - Indian Rupee'),
        ('PKR', 'PKR - Pakistani Rupee'),
        ('CNY', 'CNY - Chinese Yuan'),
        ('JPY', 'JPY - Japanese Yen'),
        ('KRW', 'KRW - South Korean Won'),
        ('AUD', 'AUD - Australian Dollar'),
        ('CAD', 'CAD - Canadian Dollar'),
        ('CHF', 'CHF - Swiss Franc'),
        ('SGD', 'SGD - Singapore Dollar'),
        ('MYR', 'MYR - Malaysian Ringgit'),
        ('THB', 'THB - Thai Baht'),
        ('VND', 'VND - Vietnamese Dong'),
        ('PHP', 'PHP - Philippine Peso'),
        ('IDR', 'IDR - Indonesian Rupiah'),
        ('AED', 'AED - UAE Dirham'),
        ('SAR', 'SAR - Saudi Riyal'),
        ('NZD', 'NZD - New Zealand Dollar'),
        ('SEK', 'SEK - Swedish Krona'),
        ('NOK', 'NOK - Norwegian Krone'),
        ('DKK', 'DKK - Danish Krone'),
        ('MXN', 'MXN - Mexican Peso'),
        ('BRL', 'BRL - Brazilian Real'),
        ('RUB', 'RUB - Russian Ruble'),
        ('ZAR', 'ZAR - South African Rand'),
        ('EGP', 'EGP - Egyptian Pound'),
        ('NGN', 'NGN - Nigerian Naira'),
        ('KES', 'KES - Kenyan Shilling'),
    ]
    
    currency_short_form = models.CharField(max_length=10, default='USD', choices=CURRENCY_CHOICES, help_text='Short form like USD, EUR, BDT')
    currency_name = models.CharField(max_length=50, default='US Dollar', help_text='Full currency name')
    tax_enabled = models.BooleanField(default=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=8.00)
    
    # Order Settings
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    default_shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=5.99)
    
    # Inventory
    low_stock_threshold = models.IntegerField(default=10)
    enable_backorders = models.BooleanField(default=False)
    
    # Product Reviews
    reviews_enabled = models.BooleanField(default=True, help_text='Enable or disable product reviews')
    require_approval_for_reviews = models.BooleanField(default=True, help_text='Require admin approval before reviews are visible')
    
    # Order Status Defaults
    default_order_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
    ])
    auto_cancel_unpaid_orders = models.BooleanField(default=False, help_text='Automatically cancel unpaid orders after X hours')
    auto_cancel_hours = models.IntegerField(default=48, help_text='Hours before cancelling unpaid orders')
    
    # Email Notification Settings
    email_notifications_enabled = models.BooleanField(default=True)
    notify_new_order = models.BooleanField(default=True, help_text='Notify admins when new order is placed')
    notify_order_status_change = models.BooleanField(default=True, help_text='Notify customers when order status changes')
    notify_new_review = models.BooleanField(default=True, help_text='Notify admins when new review is submitted')
    notify_low_stock = models.BooleanField(default=True, help_text='Notify admins when stock is low')
    notification_email = models.EmailField(default='admin@techshop.com', help_text='Email address for notifications')
    
    # Database & System
    enable_database_backup = models.BooleanField(default=True, help_text='Allow database backup downloads')
    show_system_health = models.BooleanField(default=True, help_text='Display system health metrics on dashboard')
    show_database_status = models.BooleanField(default=True, help_text='Display database connection status')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configurations'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteConfiguration.objects.exists():
            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)


class Supplier(models.Model):
    """Supplier/Vendor management for procurement"""
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class PurchaseOrder(models.Model):
    """Purchase Orders for stock replenishment"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Supplier'),
        ('confirmed', 'Confirmed'),
        ('ordered', 'Ordered'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(null=True, blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"PO-{self.po_number}"
    
    class Meta:
        ordering = ['-created_at']


class PurchaseOrderItem(models.Model):
    """Items in a Purchase Order"""
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('store.Product', on_delete=models.PROTECT)
    quantity_ordered = models.IntegerField(default=0)
    quantity_received = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def total_cost(self):
        return self.quantity_ordered * self.unit_cost
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity_ordered}"


class InventoryMovement(models.Model):
    """Track all inventory movements"""
    
    MOVEMENT_TYPES = [
        ('received', 'Stock Received'),
        ('sold', 'Sold'),
        ('returned', 'Customer Return'),
        ('adjusted', 'Stock Adjustment'),
        ('transfer', 'Transfer'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
    ]
    
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='inventory_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Positive for additions, negative for deductions
    reference_number = models.CharField(max_length=100, blank=True)  # PO number, Order number, etc.
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity})"
    
    class Meta:
        ordering = ['-created_at']
