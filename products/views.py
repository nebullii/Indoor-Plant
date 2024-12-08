from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

def product_gallery(request):
    # Fetch all products from the database
    product_list = Product.objects.all()
    
    # Set up pagination
    paginator = Paginator(product_list, 6)  # Show 6 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'products/gallery.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Set the seller to the currently logged-in user
            product.save()
            return redirect('product_gallery')  # Redirect to the product gallery after saving
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})