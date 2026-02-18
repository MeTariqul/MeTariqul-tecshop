from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.db import connection
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import os
import json

from .models import StaffProfile, ActivityLog, SystemSettings, SiteConfiguration, UserPermission, Supplier, PurchaseOrder, PurchaseOrderItem, InventoryMovement
from store.models import Product, Category, Inventory
from orders.models import WebOrder, OrderItem, WebCustomer
from cart.models import ShoppingCart


def is_admin_user(user):
    """Check if user has admin access"""
    if not user.is_authenticated:
        return False
    try:
        staff = user.staff_profile
        return staff.is_active and staff.role in ['super_admin', 'manager']
    except StaffProfile.DoesNotExist:
        return user.is_superuser


def is_super_admin(user):
    """Check if user is super admin (only super_admin role or superuser)"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        staff = user.staff_profile
        return staff.is_active and staff.role == 'super_admin'
    except StaffProfile.DoesNotExist:
        return False


def admin_required(view_func):
    """Decorator to require admin access"""
    def wrapper(request, *args, **kwargs):
        if not is_admin_user(request.user):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('store:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_role_permissions(role):
    """Get permissions based on role"""
    permissions = {
        'super_admin': {
            'can_manage_products': True,
            'can_manage_orders': True,
            'can_manage_inventory': True,
            'can_manage_customers': True,
            'can_manage_staff': True,
            'can_view_reports': True,
            'can_manage_settings': True,
            'can_manage_finance': True,
            'can_manage_sellers': True,
            'can_view_all_orders': True,
            'can_view_own_orders': True,
            'can_manage_delivery': True,
        },
        'manager': {
            'can_manage_products': True,
            'can_manage_orders': True,
            'can_manage_inventory': True,
            'can_manage_customers': True,
            'can_manage_staff': False,
            'can_view_reports': True,
            'can_manage_settings': True,
            'can_manage_finance': True,
            'can_manage_sellers': False,
            'can_view_all_orders': True,
            'can_view_own_orders': True,
            'can_manage_delivery': True,
        },
        'inventory_manager': {
            'can_manage_products': True,
            'can_manage_orders': False,
            'can_manage_inventory': True,
            'can_manage_customers': False,
            'can_manage_staff': False,
            'can_view_reports': True,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': False,
            'can_view_own_orders': False,
            'can_manage_delivery': False,
        },
        'order_manager': {
            'can_manage_products': False,
            'can_manage_orders': True,
            'can_manage_inventory': False,
            'can_manage_customers': True,
            'can_manage_staff': False,
            'can_view_reports': True,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': True,
            'can_view_own_orders': True,
            'can_manage_delivery': True,
        },
        'support': {
            'can_manage_products': False,
            'can_manage_orders': True,
            'can_manage_inventory': False,
            'can_manage_customers': True,
            'can_manage_staff': False,
            'can_view_reports': False,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': True,
            'can_view_own_orders': True,
            'can_manage_delivery': False,
        },
        'accountant': {
            'can_manage_products': False,
            'can_manage_orders': False,
            'can_manage_inventory': False,
            'can_manage_customers': False,
            'can_manage_staff': False,
            'can_view_reports': True,
            'can_manage_settings': False,
            'can_manage_finance': True,
            'can_manage_sellers': False,
            'can_view_all_orders': True,
            'can_view_own_orders': True,
            'can_manage_delivery': False,
        },
        'delivery_person': {
            'can_manage_products': False,
            'can_manage_orders': False,
            'can_manage_inventory': False,
            'can_manage_customers': False,
            'can_manage_staff': False,
            'can_view_reports': False,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': False,
            'can_view_own_orders': True,
            'can_manage_delivery': True,
        },
        'seller': {
            'can_manage_products': True,
            'can_manage_orders': False,
            'can_manage_inventory': True,
            'can_manage_customers': False,
            'can_manage_staff': False,
            'can_view_reports': False,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': False,
            'can_view_own_orders': True,
            'can_manage_delivery': False,
        },
        'viewer': {
            'can_manage_products': False,
            'can_manage_orders': False,
            'can_manage_inventory': False,
            'can_manage_customers': False,
            'can_manage_staff': False,
            'can_view_reports': True,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': False,
            'can_view_own_orders': True,
            'can_manage_delivery': False,
        },
        'customer': {
            'can_manage_products': False,
            'can_manage_orders': False,
            'can_manage_inventory': False,
            'can_manage_customers': False,
            'can_manage_staff': False,
            'can_view_reports': False,
            'can_manage_settings': False,
            'can_manage_finance': False,
            'can_manage_sellers': False,
            'can_view_all_orders': False,
            'can_view_own_orders': True,
            'can_manage_delivery': False,
        },
    }
    return permissions.get(role, {})


@login_required
@admin_required
def dashboard(request):
    """Main admin dashboard"""
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get user permissions
    try:
        staff = request.user.staff_profile
        permissions = get_role_permissions(staff.role)
    except StaffProfile.DoesNotExist:
        permissions = get_role_permissions('super_admin')
    
    # Orders statistics
    total_orders = WebOrder.objects.count()
    orders_today = WebOrder.objects.filter(created_at__date=today).count()
    orders_this_week = WebOrder.objects.filter(created_at__date__gte=week_ago).count()
    orders_this_month = WebOrder.objects.filter(created_at__date__gte=month_ago).count()
    
    # Revenue
    revenue_today = WebOrder.objects.filter(created_at__date=today, status__in=['delivered', 'confirmed', 'processing', 'shipped']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    revenue_week = WebOrder.objects.filter(created_at__date__gte=week_ago, status__in=['delivered', 'confirmed', 'processing', 'shipped']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    revenue_month = WebOrder.objects.filter(created_at__date__gte=month_ago, status__in=['delivered', 'confirmed', 'processing', 'shipped']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Products
    total_products = Product.objects.count()
    low_stock_products = Inventory.objects.filter(quantity_on_hand__lte=10).count()
    out_of_stock = Inventory.objects.filter(quantity_on_hand=0).count()
    
    # Customers
    total_customers = WebCustomer.objects.count()
    new_customers_this_month = WebCustomer.objects.filter(created_at__date__gte=month_ago).count()
    
    # Recent orders
    recent_orders = WebOrder.objects.select_related('customer__user').order_by('-created_at')[:10]
    
    # Recent activities
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:15]
    
    # Order status distribution
    order_status_counts = WebOrder.objects.values('status').annotate(count=Count('id'))
    
    # Low stock alerts
    low_stock_items = Inventory.objects.select_related('product').filter(quantity_on_hand__lte=10)[:10]
    
    context = {
        'permissions': permissions,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_this_week': orders_this_week,
        'orders_this_month': orders_this_month,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock': out_of_stock,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'recent_orders': recent_orders,
        'recent_activities': recent_activities,
        'order_status_counts': order_status_counts,
        'low_stock_items': low_stock_items,
    }
    
    return render(request, 'admin/dashboard.html', context)


# ====================
# STAFF MANAGEMENT
# ====================

@login_required
@admin_required
def staff_list(request):
    """List all staff members"""
    staff_members = StaffProfile.objects.select_related('user').order_by('-created_at')
    
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'admin/staff_list.html', context)


@login_required
@admin_required
def staff_create(request):
    """Create new staff member"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin_dashboard:staff_create')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Get permissions for role
        permissions = get_role_permissions(role)
        
        # Create staff profile
        staff = StaffProfile.objects.create(
            user=user,
            role=role,
            department=department,
            phone=phone,
            can_manage_products=permissions.get('can_manage_products', False),
            can_manage_orders=permissions.get('can_manage_orders', False),
            can_manage_inventory=permissions.get('can_manage_inventory', False),
            can_manage_customers=permissions.get('can_manage_customers', False),
            can_manage_staff=permissions.get('can_manage_staff', False),
            can_view_reports=permissions.get('can_view_reports', False),
            can_manage_settings=permissions.get('can_manage_settings', False),
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='create',
            model_name='StaffProfile',
            object_id=staff.id,
            object_repr=str(staff),
            description=f'Created new staff member: {username} with role {role}'
        )
        
        messages.success(request, f'Staff member {username} created successfully!')
        return redirect('admin_dashboard:staff_list')
    
    return render(request, 'admin/staff_form.html', {'action': 'Create'})


@login_required
@admin_required
def staff_edit(request, staff_id):
    """Edit staff member"""
    staff = get_object_or_404(StaffProfile, id=staff_id)
    
    if request.method == 'POST':
        staff.role = request.POST.get('role')
        staff.department = request.POST.get('department')
        staff.phone = request.POST.get('phone')
        staff.is_active = request.POST.get('is_active') == 'on'
        
        # Update permissions based on role
        permissions = get_role_permissions(staff.role)
        staff.can_manage_products = permissions.get('can_manage_products', False)
        staff.can_manage_orders = permissions.get('can_manage_orders', False)
        staff.can_manage_inventory = permissions.get('can_manage_inventory', False)
        staff.can_manage_customers = permissions.get('can_manage_customers', False)
        staff.can_manage_staff = permissions.get('can_manage_staff', False)
        staff.can_view_reports = permissions.get('can_view_reports', False)
        staff.can_manage_settings = permissions.get('can_manage_settings', False)
        
        staff.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='update',
            model_name='StaffProfile',
            object_id=staff.id,
            object_repr=str(staff),
            description=f'Updated staff member: {staff.user.username}'
        )
        
        messages.success(request, f'Staff member updated successfully!')
        return redirect('admin_dashboard:staff_list')
    
    context = {
        'staff': staff,
        'action': 'Edit'
    }
    return render(request, 'admin/staff_form.html', context)


@login_required
@admin_required
def staff_delete(request, staff_id):
    """Delete staff member"""
    staff = get_object_or_404(StaffProfile, id=staff_id)
    
    if request.user == staff.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_dashboard:staff_list')
    
    username = staff.user.username
    user = staff.user
    
    # Log activity before deletion
    ActivityLog.objects.create(
        user=request.user,
        action='delete',
        model_name='StaffProfile',
        object_id=staff.id,
        object_repr=str(staff),
        description=f'Deleted staff member: {username}'
    )
    
    staff.delete()
    user.delete()
    
    messages.success(request, f'Staff member {username} deleted successfully!')
    return redirect('admin_dashboard:staff_list')


# ====================
# ACTIVITY LOGS
# ====================

@login_required
@admin_required
def activity_logs(request):
    """View activity logs"""
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    
    # Check if user is super admin
    is_super = is_super_admin(request.user)
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    logs = logs[:100]
    
    users = User.objects.filter(staff_profile__isnull=False)
    
    context = {
        'logs': logs,
        'users': users,
        'is_super_admin': is_super,
    }
    return render(request, 'admin/activity_logs.html', context)


@login_required
def delete_activity_log(request, log_id):
    """Delete a single activity log - super admin only"""
    if not is_super_admin(request.user):
        messages.error(request, 'Only super admins can delete activity logs.')
        return redirect('admin_dashboard:activity_logs')
    
    log = get_object_or_404(ActivityLog, id=log_id)
    log.delete()
    
    messages.success(request, 'Activity log deleted successfully.')
    return redirect('admin_dashboard:activity_logs')


@login_required
def clear_activity_logs(request):
    """Clear all activity logs - super admin only"""
    if not is_super_admin(request.user):
        messages.error(request, 'Only super admins can clear activity logs.')
        return redirect('admin_dashboard:activity_logs')
    
    if request.method == 'POST':
        ActivityLog.objects.all().delete()
        messages.success(request, 'All activity logs have been cleared.')
    
    return redirect('admin_dashboard:activity_logs')


# ====================
# SETTINGS
# ====================

@login_required
@admin_required
def settings_view(request):
    """Site settings management"""
    config = SiteConfiguration.objects.first()
    if not config:
        config = SiteConfiguration.objects.create()
    
    if request.method == 'POST':
        config.site_name = request.POST.get('site_name', config.site_name)
        config.contact_email = request.POST.get('contact_email', config.contact_email)
        config.contact_phone = request.POST.get('contact_phone', config.contact_phone)
        config.contact_address = request.POST.get('contact_address', config.contact_address)
        config.facebook_url = request.POST.get('facebook_url', config.facebook_url)
        config.twitter_url = request.POST.get('twitter_url', config.twitter_url)
        config.instagram_url = request.POST.get('instagram_url', config.instagram_url)
        config.youtube_url = request.POST.get('youtube_url', config.youtube_url)
        config.meta_title = request.POST.get('meta_title', config.meta_title)
        config.meta_description = request.POST.get('meta_description', config.meta_description)
        config.meta_keywords = request.POST.get('meta_keywords', config.meta_keywords)
        config.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        config.maintenance_message = request.POST.get('maintenance_message', config.maintenance_message)
        config.currency_symbol = request.POST.get('currency_symbol', config.currency_symbol)
        config.currency_code = request.POST.get('currency_code', config.currency_code)
        config.tax_enabled = request.POST.get('tax_enabled') == 'on'
        config.tax_rate = Decimal(request.POST.get('tax_rate', config.tax_rate))
        config.free_shipping_threshold = Decimal(request.POST.get('free_shipping_threshold', config.free_shipping_threshold))
        config.default_shipping_cost = Decimal(request.POST.get('default_shipping_cost', config.default_shipping_cost))
        config.low_stock_threshold = int(request.POST.get('low_stock_threshold', config.low_stock_threshold))
        config.enable_backorders = request.POST.get('enable_backorders') == 'on'
        config.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='update',
            model_name='SiteConfiguration',
            object_id=config.id,
            object_repr=str(config),
            description='Updated site configuration'
        )
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('admin_dashboard:settings')
    
    context = {
        'config': config,
    }
    return render(request, 'admin/settings.html', context)


# ====================
# REPORTS
# ====================

@login_required
@admin_required
def reports(request):
    """Reports and analytics"""
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    orders = WebOrder.objects.all()
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Sales by status
    sales_by_status = orders.values('status').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')
    
    # Top selling products
    top_products = OrderItem.objects.filter(
        order__in=orders
    ).values(
        'product__name', 'product__SKU'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('unit_price')
    ).order_by('-total_sold')[:10]
    
    # Orders by day
    from django.db.models.functions import TruncDate
    orders_by_day = orders.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-date')[:30]
    
    context = {
        'sales_by_status': sales_by_status,
        'top_products': top_products,
        'orders_by_day': orders_by_day,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'admin/reports.html', context)


# ====================
# PRODUCT MANAGEMENT (Admin Full Access)
# ====================

@login_required
@admin_required
def products(request):
    """Product management"""
    products = Product.objects.select_related('category', 'supplier').prefetch_related('inventory').order_by('-created_at')
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(SKU__icontains=search))
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by stock status
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        products = products.filter(inventory__quantity_on_hand__lte=10, inventory__quantity_on_hand__gt=0)
    elif stock_filter == 'out':
        products = products.filter(inventory__quantity_on_hand=0)
    elif stock_filter == 'in':
        products = products.filter(inventory__quantity_on_hand__gt=10)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'admin/products.html', context)


@login_required
@admin_required
def product_edit(request, product_id):
    """Edit product"""
    product = get_object_or_404(Product, id=product_id)
    inventory, _ = Inventory.objects.get_or_create(product=product)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.is_available_online = request.POST.get('is_available_online') == 'on'
        
        # Pricing
        new_cost_price = request.POST.get('cost_price')
        new_selling_price = request.POST.get('selling_price')
        if new_cost_price:
            product.cost_price = Decimal(new_cost_price)
        if new_selling_price:
            product.selling_price = Decimal(new_selling_price)
        
        # Offers
        discount_pct = request.POST.get('discount_percentage', '0')
        product.discount_percentage = Decimal(discount_pct) if discount_pct else Decimal('0')
        product.discount_label = request.POST.get('discount_label', '')
        
        product.save()
        
        # Update inventory
        inventory.quantity_on_hand = int(request.POST.get('quantity_on_hand', 0))
        inventory.reorder_level = int(request.POST.get('reorder_level', 10))
        inventory.save()
        
        ActivityLog.objects.create(
            user=request.user,
            action='update',
            model_name='Product',
            object_id=product.id,
            object_repr=str(product),
            description=f'Updated product: {product.name}'
        )
        
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_dashboard:products')
    
    context = {
        'product': product,
        'inventory': inventory,
    }
    return render(request, 'admin/product_form.html', context)


# ====================
# ORDER MANAGEMENT
# ====================

@login_required
@admin_required
def orders(request):
    """Order management"""
    orders_list = WebOrder.objects.select_related('customer__user').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders_list = orders_list.filter(status=status)
    
    # Filter by date
    date_from = request.GET.get('date_from')
    if date_from:
        orders_list = orders_list.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        orders_list = orders_list.filter(created_at__date__lte=date_to)
    
    context = {
        'orders': orders_list,
    }
    return render(request, 'admin/orders.html', context)


@login_required
@admin_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(WebOrder, id=order_id)
    items = order.items.select_related('product')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='WebOrder',
                object_id=order.id,
                object_repr=str(order),
                description=f'Updated order status to: {new_status}'
            )
            
            messages.success(request, f'Order status updated to {new_status}')
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'admin/order_detail.html', context)


# ====================
# CUSTOMER MANAGEMENT
# ====================

@login_required
@admin_required
@login_required
@admin_required
def customers(request):
    """Customer management"""
    customers_list = WebCustomer.objects.select_related('user').annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).order_by('-created_at')
    
    # Search
    search = request.GET.get('search')
    if search:
        customers_list = customers_list.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    context = {
        'customers': customers_list,
    }
    return render(request, 'admin/customers.html', context)


@login_required
@admin_required
def delete_customer(request, customer_id):
    """Delete a customer and their associated user account"""
    customer = get_object_or_404(WebCustomer, id=customer_id)
    user = customer.user
    username = user.username
    
    # Log activity before deletion
    ActivityLog.objects.create(
        user=request.user,
        action='delete',
        model_name='WebCustomer',
        object_id=customer.id,
        object_repr=str(customer),
        description=f'Deleted customer: {username}'
    )
    
    # Delete the User object (cascades to WebCustomer and Orders)
    user.delete()
    
    messages.success(request, f'Customer {username} has been permanently deleted.')
    return redirect('admin_dashboard:customers')


# ====================
# ROLE SWITCHING (Admin Only)
# ====================

@login_required
def switch_role(request, staff_id):
    """Allow admin to temporarily switch to another user's role"""
    # Check if current user is admin
    if not is_admin_user(request.user):
        messages.error(request, 'You do not have permission to switch roles.')
        return redirect('admin_dashboard:dashboard')
    
    staff = get_object_or_404(StaffProfile, id=staff_id)
    
    # Save current role
    request.session['original_role'] = request.user.staff_profile.role
    request.session['switched_to'] = staff.user.username
    
    # Set the switched role
    staff.is_switched = True
    staff.original_role = staff.role
    staff.save()
    
    messages.success(request, f'You are now viewing as {staff.user.username} ({staff.get_role_display()})')
    return redirect('admin_dashboard:dashboard')


@login_required
def switch_back(request):
    """Switch back to original role after viewing as another user"""
    if not hasattr(request.user, 'staff_profile'):
        return redirect('admin_dashboard:dashboard')
    
    staff = request.user.staff_profile
    
    if staff.is_switched and staff.original_role:
        # Restore original role
        staff.role = staff.original_role
        staff.is_switched = False
        staff.original_role = ''
        staff.save()
        
        # Clear session
        request.session.pop('original_role', None)
        request.session.pop('switched_to', None)
        
        messages.success(request, 'You have switched back to your original role.')
    
    return redirect('admin_dashboard:dashboard')


# ====================
# PERMISSION MANAGEMENT
# ====================

@login_required
@admin_required
def manage_permissions(request, staff_id):
    """Manage custom permissions for a staff member"""
    staff = get_object_or_404(StaffProfile, id=staff_id)
    
    if request.method == 'POST':
        # Get all permission checkboxes
        permissions = [
            'can_manage_products', 'can_manage_orders', 'can_manage_inventory',
            'can_manage_customers', 'can_manage_staff', 'can_view_reports',
            'can_manage_settings', 'can_manage_finance', 'can_manage_sellers',
            'can_view_all_orders', 'can_view_own_orders', 'can_manage_delivery'
        ]
        
        for perm in permissions:
            setattr(staff, perm, request.POST.get(perm) == 'on')
        
        staff.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='update',
            model_name='StaffProfile',
            object_id=staff.id,
            object_repr=str(staff),
            description=f'Updated permissions for {staff.user.username}'
        )
        
        messages.success(request, f'Permissions updated for {staff.user.username}')
        return redirect('admin_dashboard:staff_list')
    
    context = {
        'staff': staff,
    }
    return render(request, 'admin/permissions.html', context)


# ====================
# USER PROFILE (Role-based)
# ====================

@login_required
def user_profile(request):
    """User's own profile - shows only their data"""
    user = request.user
    
    # Get or create staff profile
    try:
        staff = user.staff_profile
        permissions = get_role_permissions(staff.role)
        
        # Add custom permissions from UserPermission model
        custom_perms = user.custom_permissions.all()
        for perm in custom_perms:
            perm_key = f'can_{perm.permission}'
            if perm_key in permissions:
                permissions[perm_key] = True
        
        role = staff.role
        is_staff = True
    except StaffProfile.DoesNotExist:
        permissions = {'can_view_own_orders': True}
        role = 'customer'
        is_staff = False
    
    # Get user's own orders
    if permissions.get('can_view_own_orders', False):
        try:
            customer = user.webcustomer
            user_orders = WebOrder.objects.filter(customer=customer).order_by('-created_at')[:10]
        except WebCustomer.DoesNotExist:
            user_orders = []
    else:
        user_orders = []
    
    context = {
        'user_obj': user,
        'staff': staff if is_staff else None,
        'permissions': permissions,
        'role': role,
        'is_staff': is_staff,
        'user_orders': user_orders,
    }
    return render(request, 'admin/user_profile.html', context)


# ====================
# SEPARATE DASHBOARDS BY ROLE
# ====================

@login_required
def role_based_dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    user = request.user
    
    # Check if user has staff profile
    try:
        staff = user.staff_profile
        permissions = get_role_permissions(staff.role)
        
        # Add custom permissions
        custom_perms = user.custom_permissions.all()
        for perm in custom_perms:
            perm_key = f'can_{perm.permission}'
            if perm_key in permissions:
                permissions[perm_key] = True
        
        role = staff.role
    except StaffProfile.DoesNotExist:
        # Regular customer or no profile
        if user.is_superuser:
            return redirect('admin_dashboard:dashboard')
        return redirect('store:home')
    
    # Redirect based on role
    if role in ['super_admin', 'manager']:
        return redirect('admin_dashboard:dashboard')
    elif role == 'inventory_manager':
        return redirect('admin_dashboard:products')
    elif role == 'order_manager':
        return redirect('admin_dashboard:orders')
    elif role == 'support':
        return redirect('admin_dashboard:customers')
    elif role == 'accountant':
        return redirect('admin_dashboard:reports')
    elif role == 'delivery_person':
        return redirect('admin_dashboard:orders')
    elif role == 'seller':
        return redirect('admin_dashboard:products')
    else:
        return redirect('admin_dashboard:user_profile')


# ====================
# HELPER FUNCTION
# ====================

def log_activity(user, action, model_name, object_id=None, object_repr='', changes=None, description=''):
    """Helper function to log activities"""
    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        object_repr=object_repr,
        changes=changes or {},
        description=description
    )


# ====================
# WEBSITE SETTINGS VIEW
# ====================

@login_required
@admin_required
def website_settings(request):
    """Website settings page with system configuration options"""
    
    # Get or create site configuration
    config, created = SiteConfiguration.objects.get_or_create(pk=1)
    
    # Get database status
    db_status = {
        'connected': False,
        'engine': settings.DATABASES['default']['ENGINE'],
        'name': settings.DATABASES['default']['NAME'],
    }
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status['connected'] = True
    except Exception as e:
        db_status['error'] = str(e)
    
    # Get system health metrics
    system_health = {}
    try:
        # CPU and memory info (Windows)
        import psutil
        system_health['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        system_health['memory_percent'] = memory.percent
        system_health['memory_available'] = memory.available / (1024**3)  # GB
    except ImportError:
        system_health['cpu_percent'] = 'N/A'
        system_health['memory_percent'] = 'N/A'
    
    # Get database size
    try:
        with connection.cursor() as cursor:
            # MySQL specific - get database size
            cursor.execute("""
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, [settings.DATABASES['default']['NAME']])
            result = cursor.fetchone()
            system_health['database_size_mb'] = result[0] if result and result[0] else 0
    except Exception as e:
        system_health['database_size_mb'] = 'N/A'
    
    # Get order stats
    total_orders = WebOrder.objects.count()
    pending_orders = WebOrder.objects.filter(status='pending').count()
    system_health['total_orders'] = total_orders
    system_health['pending_orders'] = pending_orders
    
    # Get product stats
    try:
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(inventory__quantity_on_hand__lt=10).count()
        system_health['total_products'] = total_products
        system_health['low_stock_products'] = low_stock_products
    except Exception as e:
        system_health['total_products'] = Product.objects.count()
        system_health['low_stock_products'] = 0
    
    if request.method == 'POST':
        # Update site configuration
        config.site_name = request.POST.get('site_name', config.site_name)
        config.currency_short_form = request.POST.get('currency_short_form', config.currency_short_form)
        config.contact_email = request.POST.get('contact_email', config.contact_email)
        config.contact_phone = request.POST.get('contact_phone', config.contact_phone)
        config.notification_email = request.POST.get('notification_email', config.notification_email)
        
        # Product reviews settings
        config.reviews_enabled = 'reviews_enabled' in request.POST
        config.require_approval_for_reviews = 'require_approval_for_reviews' in request.POST
        
        # Order status settings
        config.default_order_status = request.POST.get('default_order_status', config.default_order_status)
        config.auto_cancel_unpaid_orders = 'auto_cancel_unpaid_orders' in request.POST
        config.auto_cancel_hours = int(request.POST.get('auto_cancel_hours', 48))
        
        # Email notification settings
        config.email_notifications_enabled = 'email_notifications_enabled' in request.POST
        config.notify_new_order = 'notify_new_order' in request.POST
        config.notify_order_status_change = 'notify_order_status_change' in request.POST
        config.notify_new_review = 'notify_new_review' in request.POST
        config.notify_low_stock = 'notify_low_stock' in request.POST
        
        # Database & System settings
        config.enable_database_backup = 'enable_database_backup' in request.POST
        config.show_system_health = 'show_system_health' in request.POST
        config.show_database_status = 'show_database_status' in request.POST
        
        config.save()
        messages.success(request, 'Settings saved successfully!')
        return redirect('admin_dashboard:website_settings')
    
    context = {
        'config': config,
        'db_status': db_status,
        'system_health': system_health,
    }
    return render(request, 'admin/website_settings.html', context)


@login_required
@admin_required
def database_backup(request):
    """Generate and download database backup"""
    config = SiteConfiguration.objects.first()
    if not config or not config.enable_database_backup:
        messages.error(request, 'Database backup is not enabled.')
        return redirect('admin_dashboard:website_settings')
    
    try:
        import subprocess
        from datetime import datetime
        
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        
        # Create backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_{db_name}_{timestamp}.sql'
        backup_path = os.path.join(settings.MEDIA_ROOT, 'backups')
        os.makedirs(backup_path, exist_ok=True)
        full_path = os.path.join(backup_path, backup_file)
        
        # Run mysqldump (for MySQL)
        cmd = [
            'mysqldump',
            f'-u{db_user}',
            f'-p{db_password}',
            f'-h{db_host}',
            f'-P{db_port}',
            db_name,
        ]
        
        with open(full_path, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        # Read and return the backup file
        with open(full_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
            return response
            
    except Exception as e:
        messages.error(request, f'Backup failed: {str(e)}')
        return redirect('admin_dashboard:website_settings')


# =====================
# Director/Owner Dashboard
# =====================

@login_required
@admin_required
def director_dashboard(request):
    """Director Dashboard - Executive Summary with P&L, Inventory Value, Staff Management"""
    
    today = timezone.now().date()
    
    # Today's sales
    today_orders = WebOrder.objects.filter(created_at__date=today, status__in=['confirmed', 'processing', 'shipped', 'delivered'])
    today_sales = sum(order.total_amount for order in today_orders)
    today_order_count = today_orders.count()
    
    # This month's sales
    month_start = today.replace(day=1)
    month_orders = WebOrder.objects.filter(created_at__date__gte=month_start, status__in=['confirmed', 'processing', 'shipped', 'delivered'])
    month_sales = sum(order.total_amount for order in month_orders)
    
    # Inventory Value
    total_inventory_value = 0
    for product in Product.objects.select_related('inventory').all():
        if product.inventory:
            total_inventory_value += product.selling_price * product.inventory.quantity_on_hand
    
    # Total products count
    total_products = Product.objects.count()
    total_stock = sum(p.inventory.quantity_on_hand if p.inventory else 0 for p in Product.objects.select_related('inventory').all())
    
    # Low stock items
    low_stock_items = Product.objects.filter(
        inventory__quantity_on_hand__lt=10
    ).select_related('inventory')[:10]
    
    # Recent orders
    recent_orders = WebOrder.objects.order_by('-created_at')[:10]
    
    # Staff count
    total_staff = StaffProfile.objects.filter(is_active=True).count()
    
    # Pending POs
    pending_pos = PurchaseOrder.objects.filter(status__in=['draft', 'sent', 'confirmed', 'ordered', 'in_transit']).count()
    
    # Quick stats
    context = {
        'today_sales': today_sales,
        'today_order_count': today_order_count,
        'month_sales': month_sales,
        'total_inventory_value': total_inventory_value,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock_items': low_stock_items,
        'recent_orders': recent_orders,
        'total_staff': total_staff,
        'pending_pos': pending_pos,
    }
    return render(request, 'admin/director_dashboard.html', context)


# =====================
# Warehouse/Inventory Dashboard
# =====================

@login_required
@admin_required
def warehouse_dashboard(request):
    """Warehouse Dashboard - Stock Levels, Low Stock Alerts, Receiving, Cycle Counting"""
    
    # Get all products with inventory
    products = Product.objects.select_related('inventory', 'category').all()
    
    # Stock levels
    in_stock = products.filter(inventory__quantity_on_hand__gt=10)
    low_stock = products.filter(inventory__quantity_on_hand__lte=10, inventory__quantity_on_hand__gt=0)
    out_of_stock = products.filter(inventory__quantity_on_hand=0)
    
    # Recent inventory movements
    recent_movements = InventoryMovement.objects.select_related('product').order_by('-created_at')[:20]
    
    # Pending POs to receive
    pending_receiving = PurchaseOrder.objects.filter(status='in_transit')
    
    context = {
        'total_products': products.count(),
        'in_stock_count': in_stock.count(),
        'low_stock_count': low_stock.count(),
        'out_of_stock_count': out_of_stock.count(),
        'low_stock_items': low_stock[:20],
        'out_of_stock_items': out_of_stock[:10],
        'recent_movements': recent_movements,
        'pending_receiving': pending_receiving,
    }
    return render(request, 'admin/warehouse_dashboard.html', context)


@login_required
@admin_required
def receive_purchase_order(request, po_id):
    """Receive a Purchase Order and update inventory"""
    po = get_object_or_404(PurchaseOrder, id=po_id)
    
    if request.method == 'POST':
        for item in po.items.all():
            qty_received = int(request.POST.get(f'qty_{item.id}', 0))
            if qty_received > 0:
                # Update inventory
                inventory, _ = Inventory.objects.get_or_create(product=item.product)
                inventory.quantity_on_hand += qty_received
                inventory.save()
                
                # Record movement
                InventoryMovement.objects.create(
                    product=item.product,
                    movement_type='received',
                    quantity=qty_received,
                    reference_number=po.po_number,
                    notes=f'Received from PO {po.po_number}',
                    performed_by=request.user
                )
                
                item.quantity_received += qty_received
                item.save()
        
        # Update PO status
        all_received = all(item.quantity_received >= item.quantity_ordered for item in po.items.all())
        if all_received:
            po.status = 'received'
            po.received_date = timezone.now().date()
            po.save()
        
        messages.success(request, f'PO {po.po_number} received successfully!')
        return redirect('admin_dashboard:warehouse_dashboard')
    
    context = {'po': po}
    return render(request, 'admin/receive_po.html', context)


# =====================
# Fulfillment Dashboard
# =====================

@login_required
@admin_required
def fulfillment_dashboard(request):
    """Fulfillment Dashboard - Picking Lists, Packing, Shipping"""
    
    # Orders ready for picking
    pending_orders = WebOrder.objects.filter(status='pending').order_by('created_at')
    processing_orders = WebOrder.objects.filter(status='processing').order_by('created_at')
    ready_to_ship = WebOrder.objects.filter(status='confirmed').order_by('created_at')
    
    # Group orders by status
    context = {
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'ready_to_ship': ready_to_ship,
        'pending_count': pending_orders.count(),
        'processing_count': processing_orders.count(),
        'ready_to_ship_count': ready_to_ship.count(),
    }
    return render(request, 'admin/fulfillment_dashboard.html', context)


@login_required
@admin_required
def start_picking(request, order_id):
    """Start picking an order"""
    order = get_object_or_404(WebOrder, id=order_id)
    
    if order.status == 'pending':
        order.status = 'processing'
        order.save()
        messages.success(request, f'Order #{order.id} started picking')
    
    return redirect('admin_dashboard:fulfillment_dashboard')


@login_required
@admin_required
def mark_ready_to_ship(request, order_id):
    """Mark order as ready to ship"""
    order = get_object_or_404(WebOrder, id=order_id)
    
    if order.status == 'processing':
        order.status = 'confirmed'
        order.save()
        messages.success(request, f'Order #{order.id} ready to ship')
    
    return redirect('admin_dashboard:fulfillment_dashboard')


@login_required
@admin_required
def ship_order(request, order_id):
    """Mark order as shipped"""
    order = get_object_or_404(WebOrder, id=order_id)
    
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number', '')
        order.status = 'shipped'
        order.tracking_number = tracking_number
        order.shipped_at = timezone.now()
        order.save()
        
        # Deduct inventory
        for item in order.items.all():
            if item.product.inventory:
                item.product.inventory.quantity_on_hand -= item.quantity
                item.product.inventory.save()
                
                # Record movement
                InventoryMovement.objects.create(
                    product=item.product,
                    movement_type='sold',
                    quantity=-item.quantity,
                    reference_number=f'Order #{order.id}',
                    performed_by=request.user
                )
        
        messages.success(request, f'Order #{order.id} marked as shipped!')
        return redirect('admin_dashboard:fulfillment_dashboard')
    
    context = {'order': order}
    return render(request, 'admin/ship_order.html', context)


# =====================
# Supplier & Purchase Orders
# =====================

@login_required
@admin_required
def suppliers(request):
    """Supplier management"""
    suppliers = Supplier.objects.all()
    return render(request, 'admin/suppliers.html', {'suppliers': suppliers})


@login_required
@admin_required
def create_supplier(request):
    """Create new supplier"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        contact_person = request.POST.get('contact_person', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        Supplier.objects.create(
            name=name, code=code, contact_person=contact_person,
            email=email, phone=phone, address=address
        )
        messages.success(request, f'Supplier {name} created!')
        return redirect('admin_dashboard:suppliers')
    
    return render(request, 'admin/supplier_form.html')


@login_required
@admin_required
def purchase_orders(request):
    """Purchase Order list"""
    pos = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')
    return render(request, 'admin/purchase_orders.html', {'purchase_orders': pos})


@login_required
@admin_required
def create_purchase_order(request):
    """Create new Purchase Order"""
    suppliers = Supplier.objects.filter(is_active=True)
    products = Product.objects.select_related('inventory').all()
    
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        supplier = get_object_or_404(Supplier, id=supplier_id)
        
        # Generate PO number
        from datetime import datetime
        po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{PurchaseOrder.objects.count() + 1:04d}"
        
        po = PurchaseOrder.objects.create(
            po_number=po_number,
            supplier=supplier,
            status='draft',
            order_date=timezone.now().date(),
            created_by=request.user
        )
        
        # Add items
        product_ids = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')
        unit_costs = request.POST.getlist('unit_cost[]')
        
        total = 0
        for pid, qty, cost in zip(product_ids, quantities, unit_costs):
            if pid and qty and cost:
                product = Product.objects.get(id=pid)
                qty = int(qty)
                cost = Decimal(cost)
                PurchaseOrderItem.objects.create(
                    purchase_order=po, product=product,
                    quantity_ordered=qty, unit_cost=cost
                )
                total += qty * cost
        
        po.total_amount = total
        po.save()
        
        messages.success(request, f'PO {po.po_number} created!')
        return redirect('admin_dashboard:purchase_orders')
    
    context = {'suppliers': suppliers, 'products': products}
    return render(request, 'admin/purchase_order_form.html', context)


# =====================
# Stock Transfer
# =====================

@login_required
@admin_required
def stock_transfer(request):
    """Stock Transfer - Move stock between locations"""
    products = Product.objects.select_related('inventory').filter(inventory__quantity_on_hand__gt=0)
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 0))
        from_location = request.POST.get('from_location', 'Back Room')
        to_location = request.POST.get('to_location', 'Shop Floor')
        notes = request.POST.get('notes', '')
        
        product = get_object_or_404(Product, id=product_id)
        inventory = product.inventory
        
        if quantity > 0 and inventory.quantity_on_hand >= quantity:
            # Record transfer movement
            InventoryMovement.objects.create(
                product=product,
                movement_type='transfer',
                quantity=-quantity,
                reference_number=f'TRANSFER-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                notes=f'Transfer: {from_location} → {to_location}. {notes}',
                performed_by=request.user
            )
            
            # Update location (simplified - could be enhanced)
            inventory.location = to_location
            inventory.save()
            
            messages.success(request, f'Transferred {quantity} x {product.name} to {to_location}')
        else:
            messages.error(request, 'Invalid quantity or insufficient stock')
        
        return redirect('admin_dashboard:stock_transfer')
    
    recent_transfers = InventoryMovement.objects.filter(
        movement_type='transfer'
    ).select_related('product').order_by('-created_at')[:20]
    
    context = {
        'products': products,
        'recent_transfers': recent_transfers,
    }
    return render(request, 'admin/stock_transfer.html', context)


@login_required
@admin_required
def cycle_count(request):
    """Cycle Counting - Audit inventory counts"""
    # Get products for counting (could be filtered by category/location)
    products = Product.objects.select_related('inventory', 'category').all()
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        counted_qty = int(request.POST.get('counted_qty', 0))
        notes = request.POST.get('notes', '')
        
        product = get_object_or_404(Product, id=product_id)
        inventory = product.inventory
        
        # Calculate difference
        system_qty = inventory.quantity_on_hand
        difference = counted_qty - system_qty
        
        if difference != 0:
            # Record adjustment
            inventory.quantity_on_hand = counted_qty
            inventory.save()
            
            InventoryMovement.objects.create(
                product=product,
                movement_type='adjusted',
                quantity=difference,
                reference_number=f'CC-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                notes=f'Cycle Count Adjustment. System: {system_qty}, Counted: {counted_qty}. {notes}',
                performed_by=request.user
            )
            
            if difference > 0:
                messages.success(request, f'Adjusted {product.name}: +{difference} units')
            else:
                messages.warning(request, f'Adjusted {product.name}: {difference} units')
        else:
            messages.info(request, f'{product.name} count matches system')
        
        return redirect('admin_dashboard:cycle_count')
    
    # Get recent cycle counts
    recent_counts = InventoryMovement.objects.filter(
        movement_type='adjusted',
        reference_number__startswith='CC-'
    ).select_related('product').order_by('-created_at')[:20]
    
    context = {
        'products': products,
        'recent_counts': recent_counts,
    }
    return render(request, 'admin/cycle_count.html', context)


# =====================
# Scanning & Packing
# =====================

@login_required
@admin_required
def scan_item(request):
    """Scanning Interface - Scan barcode to confirm picking"""
    if request.method == 'POST':
        barcode = request.POST.get('barcode', '').strip()
        order_id = request.POST.get('order_id')
        
        # Try to find product by SKU or barcode
        product = Product.objects.filter(SKU__iexact=barcode).first()
        
        if product and order_id:
            order = get_object_or_404(WebOrder, id=order_id)
            # Check if product is in order
            order_item = order.items.filter(product=product).first()
            
            if order_item:
                return JsonResponse({
                    'success': True,
                    'product_name': product.name,
                    'quantity': order_item.quantity,
                    'order_number': order.order_number
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Product not in this order'
                })
        elif product:
            return JsonResponse({
                'success': True,
                'product_name': product.name,
                'sku': product.SKU,
                'in_stock': product.inventory.quantity_on_hand if hasattr(product, 'inventory') else 0
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            })
    
    return render(request, 'admin/scan_item.html')


@login_required
@admin_required
def packing_slip(request, order_id):
    """Generate Packing Slip for an order"""
    order = get_object_or_404(WebOrder, id=order_id)
    items = order.items.select_related('product')
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'admin/packing_slip.html', context)
