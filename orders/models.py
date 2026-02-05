from django.db import models
from django.conf import settings
from decimal import Decimal
from django_countries.fields import CountryField

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = CountryField(blank=True, null=True)  # Modified field
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Shipping Addresses'

    def __str__(self):
        return f"{self.full_name}'s address - {self.city}"

    def save(self, *args, **kwargs):
        # If this is the first address, make it default
        if not self.pk and not ShippingAddress.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='orders'  # Add this line
    )
    shipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    tracking_number = models.CharField(max_length=64, blank=True, null=True)

    @property
    def subtotal(self):
        return sum(item.get_total for item in self.orderitem_set.all())

    @property
    def total(self):
        return self.subtotal + self.shipping_cost

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.id}"


