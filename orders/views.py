from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShippingAddress, Order, OrderItem
from .forms import ShippingAddressForm
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from products.models import Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.services.fedex import get_fedex_access_token, create_fedex_shipment
import json

@login_required
def shipping_address_list(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    return render(request, 'orders/shipping_address_list.html', {'addresses': addresses})

@login_required
def add_shipping_address(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Shipping address added successfully!')
            return redirect('orders:shipping_address_list')
    else:
        form = ShippingAddressForm()
    return render(request, 'orders/shipping_address_form.html', {'form': form})

@login_required
def edit_shipping_address(request, pk):
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipping address updated successfully!')
            return redirect('orders:shipping_address_list')
    else:
        form = ShippingAddressForm(instance=address)
    return render(request, 'orders/shipping_address_form.html', 
                 {'form': form, 'editing': True})

@login_required
def set_default_address(request, pk):
    if request.method == 'POST':
        address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
        # Remove default from other addresses
        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
        # Set new default
        address.is_default = True
        address.save()
        messages.success(request, 'Default shipping address updated.')
    return redirect('orders:shipping_address_list')

@login_required
def order_review(request):
    if request.method != 'POST':
        return redirect('orders:shipping_address_select')
    
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:view_cart')
    
    address_id = request.POST.get('address_id')
    shipping_address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    subtotal = sum(item.get_total for item in cart_items)
    shipping_cost = Decimal('5.00')
    total = subtotal + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'shipping_address': shipping_address,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    
    return render(request, 'orders/order_review.html', context)

@login_required
def create_order(request):
    if request.method == 'POST':
        cart = request.user.cart
        shipping_address = ShippingAddress.objects.filter(
            user=request.user, 
            is_default=True
        ).first()
        
        if not shipping_address:
            messages.error(request, 'Please add a shipping address.')
            return redirect('orders:shipping_address_list')
        
        try:
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address
            )
            
            for cart_item in cart.cartitem_set.all():
                order.orderitem_set.create(
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            cart.cartitem_set.all().delete()
            messages.success(request, 'Order placed successfully!')

            return redirect('orders:order_success', order_id=order.id)
            
        except Exception as e:
            messages.error(request, 'There was an error placing your order.')
            return redirect('cart:view_cart')
    
    return redirect('orders:order_review')

@staff_member_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def shipping_address_select(request):
    # Check if cart is empty
    if not request.user.cart.cartitem_set.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:view_cart')
    
    # Get user's addresses
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    # If no addresses exist, redirect to add address page
    if not addresses.exists():
        messages.info(request, 'Please add a shipping address to continue.')
        return redirect('orders:add_shipping_address')
    
    context = {
        'addresses': addresses,
        'default_address': addresses.filter(is_default=True).first()
    }
    return render(request, 'orders/select_address.html', context)

@login_required
def proceed_to_payment(request, address_id):
    if request.method != 'POST':
        return redirect('orders:shipping_address_select')
    
    try:
        # Get and set the selected address as default
        shipping_address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
        
        # Set all addresses to non-default first
        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
        
        # Set selected address as default
        shipping_address.is_default = True
        shipping_address.save()
        
        # Redirect to payment checkout
        return redirect('payments:checkout')
    
    except ShippingAddress.DoesNotExist:
        messages.error(request, 'Invalid shipping address selected.')
        return redirect('orders:shipping_address_select')
    
@login_required
def order_detail(request, order_id):
    # For regular users, show only their own orders
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def customer_order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def seller_order_list(request):
    # Get all order IDs where the seller's products are present
    order_ids = OrderItem.objects.filter(product__seller=request.user).values_list('order_id', flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@csrf_exempt
@login_required
def fedex_manifest(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        shipment_type = data.get('shipment_type')
        service = data.get('service')
        declared_value = data.get('declared_value')
        pickup_time = data.get('pickup_time')
        total_weight = data.get('total_weight')
        length = data.get('length')
        width = data.get('width')
        height = data.get('height')

        try:
            # Get order and shipping address
            order_id = request.GET.get('order_id') or request.POST.get('order_id') or data.get('order_id')
            order = Order.objects.get(id=order_id) if order_id else None
            shipping_address = order.shipping_address if order else None
            
            if not shipping_address:
                return JsonResponse({'success': False, 'error': 'No shipping address found for this order.'})
            
            # Call FedEx API to create shipment/manifest and get label
            shipment_data = create_fedex_shipment(
                shipment_type, service, declared_value, pickup_time, total_weight, length, width, height, shipping_address
            )
            # Extract label (FedEx may return base64 or a URL)
            label_url = None
            tracking_number = None
            # Try to extract label and tracking number from response (adjust as per actual FedEx response)
            label_b64 = None
            if 'output' in shipment_data and 'transactionShipments' in shipment_data['output']:
                ts = shipment_data['output']['transactionShipments'][0]
                if 'pieceResponses' in ts and ts['pieceResponses']:
                    label_b64 = ts['pieceResponses'][0].get('packageDocuments', [{}])[0].get('content')
                    tracking_number = ts['pieceResponses'][0].get('trackingNumber')
            if label_b64:
                label_url = f"data:application/pdf;base64,{label_b64}"
            if not label_url and 'label_url' in shipment_data:
                label_url = shipment_data['label_url']
            # Save tracking number to order if available
            if tracking_number and order:
                order.tracking_number = tracking_number
                order.save()
            if label_url and tracking_number:
                return JsonResponse({'success': True, 'label_url': label_url, 'tracking_number': tracking_number})
            elif label_url:
                return JsonResponse({'success': True, 'label_url': label_url})
            else:
                return JsonResponse({'success': False, 'error': 'Label not found in FedEx response.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})