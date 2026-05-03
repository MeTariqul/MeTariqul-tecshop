from django.db import models
from django.contrib.auth.models import User
from store.models import Product


class WishlistItem(models.Model):
    """Items saved to a user's wishlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
