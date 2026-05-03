from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout and Order URLs
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('history/', views.order_history, name='order_history'),
    
    # User Registration and Profile URLs
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='user_profile'),
]
