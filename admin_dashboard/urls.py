from django.urls import path, include
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('sellers/', views.sellers_list, name='sellers'),
    path('products/', views.all_products, name='all_products'),  # New URL for all products
    # Remove the analytics URL if it exists
    # path('analytics/', views.sales_analytics, name='sales_analytics'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]