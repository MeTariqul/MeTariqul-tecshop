from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Shopping cart URLs
    path('', views.cart_view, name='cart_view'),
    path('add/<str:sku>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:sku>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<str:sku>/', views.update_cart_item, name='update_cart_item'),
    path('save-later/<str:sku>/', views.save_for_later, name='save_for_later'),
    path('move-to-cart/<str:sku>/', views.move_to_cart, name='move_to_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Compare URLs
    path('compare/', views.compare_view, name='compare_view'),
    path('compare/add/<str:sku>/', views.add_to_compare, name='add_to_compare'),
    path('compare/remove/<str:sku>/', views.remove_from_compare, name='remove_from_compare'),
    path('compare/clear/', views.clear_compare, name='clear_compare'),
]