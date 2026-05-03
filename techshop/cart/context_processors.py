from store.models import Category
from admin_dashboard.models import SiteConfiguration


def cart_context(request):
    """Context processor to make cart item count available in all templates"""
    cart = request.session.get('cart', {})
    cart_item_count = sum(item.get('quantity', 0) for item in cart.values())
    
    return {
        'cart_item_count': cart_item_count
    }


def categories_context(request):
    """Context processor to make categories available in all templates"""
    categories = Category.objects.all()
    return {
        'categories': categories
    }


def currency_context(request):
    """Context processor to make currency and site settings available in all templates"""
    try:
        config = SiteConfiguration.objects.first()
        if config:
            return {
                'currency_short_form': config.currency_short_form,
                'currency_name': config.currency_name,
                'site_name': config.site_name,
            }
    except:
        pass
    
    return {
        'currency_short_form': 'USD',
        'currency_name': 'US Dollar',
        'site_name': 'TechShop',
    }
