from django.core.paginator import Paginator
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from .forms import ProductForm, SearchForm
from .models import Product
from orders.models import Order
from django.views import View
from django.utils.text import slugify

def home(request):
    form = SearchForm()
    featured_products = Product.objects.filter(featured=True).order_by('-created_at')[:5]
    hot_selling_products = Product.objects.filter(hot_selling=True).order_by('-created_at')[:5]

    # Handle search query
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            featured_products = Product.objects.filter(name__icontains=query)
            hot_selling_products = Product.objects.filter(name__icontains=query)

    context = {
        'form': form,
        'featured_products': featured_products,
        'hot_selling_products': hot_selling_products,
    }
    return render(request, 'home.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})

def product_gallery(request):
    category_slug = request.GET.get('category')
    products = Product.objects.all()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    form = SearchForm()

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            products = products.filter(name__icontains=query)

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'products/gallery.html', {'form': form, 'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            form.save_m2m()  # For tags/categories if using ManyToMany
            return redirect('products:seller_products')
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})

@login_required
def seller_products(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'products/seller_products.html', {
        'products': products
    })

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.seller != request.user:
        return HttpResponseForbidden("You don't have permission to edit this product.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products:seller_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product
    })

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    return redirect('products:seller_products')

@login_required
def print_label(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    inventory_item = getattr(product, 'inventory_item', None)
    return render(request, 'products/print_label.html', {
        'product': product,
        'inventory_item': inventory_item
    })

def search_plants(request):
    form = SearchForm()
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Product.objects.filter(name__icontains=query)

    return render(request, 'products/search_results.html', {'form': form, 'results': results})
