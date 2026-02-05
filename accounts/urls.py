from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'
urlpatterns = [
    path('dashboard/', views.profile_view, name='profile'),  # Changed to match template
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('buyer-dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('cart/', views.cart_view, name='cart'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('seller/<slug:seller_slug>/', views.seller_storefront, name='seller_storefront'),
]