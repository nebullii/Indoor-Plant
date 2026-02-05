# products/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products'

urlpatterns = [
    path('', views.product_gallery, name='product_gallery'),
    path('gallery/', views.product_gallery, name='product_gallery'),
    path('add/', views.add_product, name='add_product'),
    path('seller_products/', views.seller_products, name='seller_products'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('search/', views.search_plants, name='search'),
    path('product/<int:product_id>/print_label/', views.print_label, name='print_label'),
    # Slug pattern MUST be last to avoid conflicts
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
