from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Shopping cart URLs
    path('', views.cart_view, name='cart_view'),
    path('add/<str:sku>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:sku>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<str:sku>/', views.update_cart_item, name='update_cart_item'),
]