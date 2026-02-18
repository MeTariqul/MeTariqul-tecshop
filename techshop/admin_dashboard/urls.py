from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('role-dashboard/', views.role_based_dashboard, name='role_dashboard'),
    
    # Role Switching
    path('switch-role/<int:staff_id>/', views.switch_role, name='switch_role'),
    path('switch-back/', views.switch_back, name='switch_back'),
    
    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/edit/<int:staff_id>/', views.staff_edit, name='staff_edit'),
    path('staff/delete/<int:staff_id>/', views.staff_delete, name='staff_delete'),
    path('staff/permissions/<int:staff_id>/', views.manage_permissions, name='manage_permissions'),
    
    # Product Management
    path('products/', views.products, name='products'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    
    # Order Management
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Customer Management
    path('customers/', views.customers, name='customers'),
    path('customers/delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
    
    # Activity Logs
    path('activity/', views.activity_logs, name='activity_logs'),
    path('activity/delete/<int:log_id>/', views.delete_activity_log, name='delete_activity_log'),
    path('activity/clear/', views.clear_activity_logs, name='clear_activity_logs'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('website-settings/', views.website_settings, name='website_settings'),
    path('database-backup/', views.database_backup, name='database_backup'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Director Dashboard
    path('director/', views.director_dashboard, name='director_dashboard'),
    
    # Warehouse/Inventory Dashboard
    path('warehouse/', views.warehouse_dashboard, name='warehouse_dashboard'),
    path('warehouse/receive/<int:po_id>/', views.receive_purchase_order, name='receive_po'),
    
    # Fulfillment Dashboard
    path('fulfillment/', views.fulfillment_dashboard, name='fulfillment_dashboard'),
    path('fulfillment/start-picking/<int:order_id>/', views.start_picking, name='start_picking'),
    path('fulfillment/ready-to-ship/<int:order_id>/', views.mark_ready_to_ship, name='ready_to_ship'),
    path('fulfillment/ship/<int:order_id>/', views.ship_order, name='ship_order'),
    
    # Suppliers & Purchase Orders
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/create/', views.create_supplier, name='create_supplier'),
    path('purchase-orders/', views.purchase_orders, name='purchase_orders'),
    path('purchase-orders/create/', views.create_purchase_order, name='create_purchase_order'),
    
    # Stock Transfer
    path('stock-transfer/', views.stock_transfer, name='stock_transfer'),
    
    # Cycle Counting
    path('cycle-count/', views.cycle_count, name='cycle_count'),
    
    # Scanning & Packing
    path('scan/', views.scan_item, name='scan_item'),
    path('packing-slip/<int:order_id>/', views.packing_slip, name='packing_slip'),
]
