from django.db import models
from store.models import Product
from orders.models import WebCustomer

# ====================
# CART-SPECIFIC TABLES (Web-Specific Features)
# These tables are managed by Django for cart functionality
# ====================

class ShoppingCart(models.Model):
    """Shopping cart sessions for web customers"""
    customer = models.ForeignKey(WebCustomer, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Cart {self.id} - {self.customer}"
    
    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_amount(self):
        """Total amount for all items in cart"""
        return sum(item.subtotal for item in self.items.all())
    
    class Meta:
        verbose_name_plural = 'Shopping Carts'

class CartItem(models.Model):
    """Individual items in shopping carts"""
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.product.discounted_price * self.quantity
    
    class Meta:
        unique_together = ('cart', 'product')
        verbose_name_plural = 'Cart Items'
