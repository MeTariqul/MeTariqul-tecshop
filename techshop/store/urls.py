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
    path('terms/', views.terms, name='terms'),
    path('return-refund/', views.return_refund, name='return_refund'),
    path('shipping/', views.shipping_policy, name='shipping'),
    path('track-order/', views.track_order, name='track_order'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/<str:sku>/', views.product_detail, name='product_detail'),
    path('products/category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
    
    # Review URL
    path('products/<str:sku>/review/', views.add_review, name='add_review'),
    path('products/<str:sku>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
]