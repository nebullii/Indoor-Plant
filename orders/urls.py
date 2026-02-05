from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Shipping Address URLs
    path('shipping/', views.shipping_address_list, name='shipping_address_list'),
    path('shipping/add/', views.add_shipping_address, name='add_shipping_address'),
    path('shipping/edit/<int:pk>/', views.edit_shipping_address, name='edit_shipping_address'),
    path('shipping/set-default/<int:pk>/', views.set_default_address, name='set_default_address'),
    path('shipping/select/', views.shipping_address_select, name='shipping_address_select'),
    
    # Order URLs
    path('review/', views.order_review, name='order_review'),
    path('create/', views.create_order, name='create_order'),
    path('list/', views.order_list, name='order_list'),
    path('my/', views.customer_order_list, name='customer_order_list'),
    path('seller/', views.seller_order_list, name='seller_order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('proceed-to-payment/<int:address_id>/', views.proceed_to_payment, name='proceed_to_payment'),
    path('fedex/manifest/', views.fedex_manifest, name='fedex_manifest'),
]