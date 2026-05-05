from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from io import BytesIO
from PIL import Image
import os

def compress_image(image_field, max_size_kb=200):
    """Compress image to ensure it is under max_size_kb"""
    if not image_field:
        return
    if getattr(image_field.file, 'size', 0) <= max_size_kb * 1024:
        return

    try:
        img = Image.open(image_field)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        output = BytesIO()
        quality = 85
        img.save(output, format='JPEG', quality=quality)
        
        while output.tell() > max_size_kb * 1024 and quality > 20:
            output.seek(0)
            output.truncate(0)
            quality -= 5
            img.save(output, format='JPEG', quality=quality)
            
        output.seek(0)
        file_name = image_field.name.rsplit('.', 1)[0] + '.jpg'
        image_field.save(file_name, ContentFile(output.read()), save=False)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Image compression failed: {e}")

# ====================
# LEGACY TABLES (Physical Shop Data)
# These tables mirror your existing physical shop database structure
# ====================

class Category(models.Model):
    """Product categories for organizing inventory"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    """Supplier information for inventory tracking"""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        verbose_name_plural = 'Suppliers'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Main product catalog - shared between physical and web shop"""
    SKU = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pricing
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Offers / Discounts
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                               help_text="Discount percentage (0-100)")
    discount_label = models.CharField(max_length=100, blank=True,
                                       help_text="e.g. Summer Sale, Flash Deal")
    
    # Tax Settings (product-wise)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   help_text="Product-specific tax rate. Leave empty to use global rate.")
    tax_exempt = models.BooleanField(default=False, help_text="Mark this product as tax-exempt")
    
    # Web-specific fields
    is_available_online = models.BooleanField(default=True)
    featured_image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Inventory tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'is_available_online']),
        ]
    
    def save(self, *args, **kwargs):
        if self.featured_image:
            compress_image(self.featured_image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.SKU})"
    
    @property
    def has_offer(self):
        """Check if product has an active discount"""
        return self.discount_percentage > 0
    
    @property
    def discounted_price(self):
        """Calculate price after discount"""
        if self.has_offer:
            discount = self.selling_price * (self.discount_percentage / 100)
            return round(self.selling_price - discount, 2)
        return self.selling_price
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price and self.selling_price:
            return round(((self.selling_price - self.cost_price) / self.selling_price) * 100, 2)
        return 0
    
    @property
    def stock_quantity(self):
        """Get stock quantity safely"""
        try:
            return self.inventory.quantity_on_hand if self.inventory else 0
        except Inventory.DoesNotExist:
            return 0
    
    @property
    def stock_status(self):
        """Get stock status text"""
        qty = self.stock_quantity
        if qty == 0:
            return 'Out of Stock'
        elif qty <= 10:
            return f'Low Stock ({qty})'
        else:
            return f'In Stock ({qty})'


class ProductVariant(models.Model):
    """Product variants - size, color, etc."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=20, blank=True, help_text="e.g. S, M, L, XL, 40, 42")
    color = models.CharField(max_length=50, blank=True, help_text="e.g. Red, Blue, Black")
    sku_suffix = models.CharField(max_length=20, blank=True, help_text="Additional SKU identifier")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                           help_text="Additional price for this variant")
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_variants'
        unique_together = ['product', 'size', 'color']
    
    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(f"Size: {self.size}")
        if self.color:
            parts.append(f"Color: {self.color}")
        return " - ".join(parts)
    
    @property
    def variant_sku(self):
        """Get complete SKU with variant suffix"""
        if self.sku_suffix:
            return f"{self.product.SKU}-{self.sku_suffix}"
        return self.product.SKU
    
    @property
    def variant_price(self):
        """Get price with variant adjustment"""
        return self.product.discounted_price + self.price_adjustment


class Inventory(models.Model):
    """Inventory levels - shared between physical and web shop"""
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='inventory')
    quantity_on_hand = models.IntegerField(default=0, help_text="Stock available in physical shop")
    reorder_level = models.IntegerField(default=10)
    location = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'Inventory'
    
    def __str__(self):
        return f"{self.product.name}: {self.quantity_on_hand} units"
    
    @property
    def is_low_stock(self):
        """Check if stock is below reorder level"""
        return self.quantity_on_hand <= self.reorder_level
    
    @property
    def has_stock(self):
        """Check if product has any stock available"""
        return self.quantity_on_hand > 0


class ProductImage(models.Model):
    """Multiple images per product for gallery view"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name_plural = 'Product Images'

    def clean(self):
        # Enforce max 5 images per product
        if not self.pk and self.product.images.count() >= 5:
            raise ValidationError("A product can have a maximum of 5 gallery images.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.image:
            compress_image(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name} ({self.sort_order})"


class Review(models.Model):
    """Product reviews - only for verified purchasers"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('orders.WebCustomer', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating from 1-5 stars")
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=True)
    
    # Admin response fields
    admin_response = models.TextField(blank=True, help_text="Admin response to the review")
    admin_response_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='review_responses')
    admin_response_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_reviews'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Review by {self.user} for {self.product.name} - {self.rating} stars"


class ContactMessage(models.Model):
    """Customer support/contact messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Customer info (if logged in)
    customer = models.ForeignKey('orders.WebCustomer', on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    
    # Status and response
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Admin response
    admin_response = models.TextField(blank=True)
    admin_response_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_responses')
    admin_response_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

# ====================
# IMAGE CLEANUP SIGNALS
# Delete actual files from storage when models are deleted or changed
# ====================

@receiver(post_delete, sender=Product)
def delete_product_featured_image(sender, instance, **kwargs):
    if instance.featured_image and os.path.isfile(instance.featured_image.path):
        os.remove(instance.featured_image.path)

@receiver(post_delete, sender=ProductImage)
def delete_product_gallery_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

@receiver(pre_save, sender=Product)
def delete_old_featured_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = Product.objects.get(pk=instance.pk).featured_image
    except Product.DoesNotExist:
        return
    if old_file and old_file != instance.featured_image and os.path.isfile(old_file.path):
        os.remove(old_file.path)

@receiver(pre_save, sender=ProductImage)
def delete_old_gallery_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = ProductImage.objects.get(pk=instance.pk).image
    except ProductImage.DoesNotExist:
        return
    if old_file and old_file != instance.image and os.path.isfile(old_file.path):
        os.remove(old_file.path)
