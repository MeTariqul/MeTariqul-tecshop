from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_view, name='wishlist_view'),
    path('toggle/<str:sku>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('remove/<str:sku>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
