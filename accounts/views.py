from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import get_user_model, login
from orders.models import Order
from django.db.models import Sum, F
from products.models import Product
from .forms import SellerProfileForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import CustomUser

User = get_user_model()

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")  # Fixed typo: removed space
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log in the user
        login(self.request, self.object)
        return response

@login_required
def buyer_dashboard(request):
    # Get user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    total_orders = orders.count()
    recent_orders = orders[:5]  # Get 5 most recent orders
    
    context = {
        'orders': recent_orders,
        'total_orders': total_orders,
    }
    return render(request, 'buyer_dashboard.html', context)

@login_required
def seller_dashboard(request):
    # Orders where any order item is for a product sold by this seller
    orders = Order.objects.filter(orderitem__product__seller=request.user).distinct()
    return render(request, 'seller_dashboard.html', {'orders': orders})

def is_admin(user):
    """Check if user has admin privileges (staff, superuser, or ADMIN role)"""
    return user.is_authenticated and (
        user.is_staff or 
        user.is_superuser or 
        getattr(user, 'role', None) == 'ADMIN'
    )

def is_admin_user(user):
    """Alias for is_admin for backward compatibility"""
    return is_admin(user)

def is_seller_user(user):
    """Check if user is a seller"""
    return user.is_authenticated and getattr(user, 'role', None) == 'SELLER'

def is_buyer_user(user):
    """Check if user is a buyer"""
    return user.is_authenticated and getattr(user, 'role', None) == 'BUYER' 


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
    else:
        form = SellerProfileForm(instance=request.user)
    return render(request, 'seller_dashboard/profile.html', {
        'user': request.user,
        'form': form
    })

@login_required
def cart_view(request):
    return render(request, 'cart.html')

def seller_storefront(request, seller_slug):
    seller = get_object_or_404(CustomUser, slug=seller_slug, role='SELLER')
    products = Product.objects.filter(seller=seller).order_by('-created_at')
    return render(request, 'seller_dashboard/storefront.html', {
        'seller': seller,
        'products': products,
    })