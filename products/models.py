from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from django_quill.fields import QuillField
from ckeditor.fields import RichTextField

class Category(models.Model):
    CATEGORY_TYPES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor')
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='indoor')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ]
    
    name = models.CharField(max_length=255)  # Name of the plant
    description = models.TextField()          # Description of the plant (will use Quill.js in frontend)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the plant
    image = models.ImageField(upload_to='products/')  # Image of the plant
    seller = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Seller of the plant
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the product was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the product was last updated
    featured = models.BooleanField(default=False)  # Whether the product is featured
    hot_selling = models.BooleanField(default=False)  # Whether the product is hot selling
    in_stock = models.BooleanField(default=True)  # Whether the product is in stock
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        default='draft'
    )
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True, default=None)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, default=None)
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO meta title")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO meta description")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    about = models.TextField(blank=True, null=True)
    care_tip = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        if self.stock == 0:
            self.status = 'inactive'
        else:
            self.status = 'active'
        super().save(*args, **kwargs)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # One review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"