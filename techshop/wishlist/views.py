from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from store.models import Product
from .models import WishlistItem


@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    items = WishlistItem.objects.filter(user=request.user).select_related('product', 'product__inventory')
    context = {'wishlist_items': items}
    return render(request, 'wishlist/wishlist.html', context)


@login_required
def toggle_wishlist(request, sku):
    """Add or remove a product from wishlist (toggle)"""
    product = get_object_or_404(Product, SKU=sku)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        messages.info(request, f'"{product.name}" removed from wishlist.')
    else:
        messages.success(request, f'"{product.name}" added to wishlist!')

    # AJAX support
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'added' if created else 'removed',
            'count': WishlistItem.objects.filter(user=request.user).count()
        })

    return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_view'))


@login_required
def remove_from_wishlist(request, sku):
    """Remove a product from wishlist"""
    product = get_object_or_404(Product, SKU=sku)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.info(request, f'"{product.name}" removed from wishlist.')
    return redirect('wishlist:wishlist_view')
