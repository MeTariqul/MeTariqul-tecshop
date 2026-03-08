from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.create_invoice, name='create_invoice'),
    path('<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('<int:invoice_id>/view/', views.view_invoice, name='view_invoice'),
    path('<int:invoice_id>/pdf/', views.download_invoice_pdf, name='download_pdf'),
    path('<int:invoice_id>/print/', views.print_invoice, name='print_invoice'),
    path('<int:invoice_id>/payment/', views.add_payment, name='add_payment'),
]
