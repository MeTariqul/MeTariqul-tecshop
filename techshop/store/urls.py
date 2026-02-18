from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # About, Contact, FAQ pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy_policy, name='privacy'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/<str:sku>/', views.product_detail, name='product_detail'),
    path('products/category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
]