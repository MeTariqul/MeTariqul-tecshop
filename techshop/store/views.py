from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg
from .models import Product, Category

# ====================
# Home and Product Views
# ====================

def home(request):
    """Home page with featured products"""
    featured_products = Product.objects.filter(
        is_available_online=True,
        inventory__quantity_on_hand__gt=0
    ).select_related('inventory')[:8]
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def about(request):
    """About us page"""
    context = {
        'page_title': 'About Us',
    }
    return render(request, 'store/about.html', context)

def contact(request):
    """Contact us page"""
    from django.contrib import messages
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # In production, you would send an email here
        messages.success(request, f'Thank you, {name}! Your message has been received. We will contact you soon.')
        return redirect('store:contact')
    
    context = {
        'page_title': 'Contact Us',
    }
    return render(request, 'store/contact.html', context)

def faq(request):
    """FAQ page"""
    faqs = [
        {
            'question': 'How do I track my order?',
            'answer': 'You can track your order by logging into your account and visiting the Order History section. You will find tracking information for each order there.'
        },
        {
            'question': 'What is your return policy?',
            'answer': 'We offer a 30-day return policy for most products. Items must be unused and in their original packaging. Please contact our support team to initiate a return.'
        },
        {
            'question': 'How long does delivery take?',
            'answer': 'Standard delivery takes 3-5 business days. Express delivery is available for an additional fee and takes 1-2 business days.'
        },
        {
            'question': 'Do you offer warranty on products?',
            'answer': 'Yes, most of our products come with a manufacturer warranty. The warranty period varies by product and is specified on each product page.'
        },
        {
            'question': 'How can I become a reseller?',
            'answer': 'Please contact our business development team at business@techshop.com for information about our reseller program.'
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': 'We accept all major credit cards, debit cards, bKash, and cash on delivery for eligible orders.'
        },
    ]
    
    context = {
        'page_title': 'Frequently Asked Questions',
        'faqs': faqs,
    }
    return render(request, 'store/faq.html', context)


def privacy_policy(request):
    """Privacy policy page with GDPR/CCPA compliance"""
    context = {
        'page_title': 'Privacy Policy',
    }
    return render(request, 'store/privacy.html', context)

def product_list(request):
    """Display all available products with stock"""
    # Filter: Show only items with stock > 0
    products = Product.objects.filter(
        is_available_online=True, 
        inventory__quantity_on_hand__gt=0
    ).select_related('inventory')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(selling_price__gte=min_price)
    if max_price:
        products = products.filter(selling_price__lte=max_price)
    
    # Filter: In stock only
    if request.GET.get('in_stock') == 'true':
        products = products.filter(inventory__quantity_on_hand__gt=0)
    
    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        products = products.order_by('selling_price')
    elif sort == 'price_high':
        products = products.order_by('-selling_price')
    elif sort == 'name':
        products = products.order_by('name')
    # Featured (default) - by newest/available
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(SKU__icontains=search_query)
        )
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_id,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)

def product_list_by_category(request, category_id):
    """Display products by category with stock"""
    category = get_object_or_404(Category, id=category_id)
    # Filter: Show only items with stock > 0
    products = Product.objects.filter(
        category=category, 
        is_available_online=True, 
        inventory__quantity_on_hand__gt=0
    ).select_related('inventory')
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_id,
        'category': category,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, sku):
    """Display individual product details with gallery, variants, and wishlist"""
    # Optimized query with select_related and prefetch_related
    product = get_object_or_404(
        Product.objects.select_related('inventory', 'category').prefetch_related('variants', 'images'), 
        SKU=sku, 
        is_available_online=True
    )
    inventory = getattr(product, 'inventory', None)
    gallery_images = product.images.all()
    variants = product.variants.filter(is_active=True)
    
    # Group variants by size and color for easy display
    available_sizes = variants.values_list('size', flat=True).distinct()
    available_colors = variants.values_list('color', flat=True).distinct()
    
    # Check if user has wishlisted this product
    in_wishlist = False
    if request.user.is_authenticated:
        from wishlist.models import WishlistItem
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'inventory': inventory,
        'gallery_images': gallery_images,
        'variants': variants,
        'available_sizes': [s for s in available_sizes if s],
        'available_colors': [c for c in available_colors if c],
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)