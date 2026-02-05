# Keep only the CustomUser model
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.text import slugify

class CustomUserManager(UserManager):
    """Custom manager for user role-based queries"""
    
    def get_sellers(self):
        """Get all sellers"""
        return self.filter(role='SELLER')
    
    def get_verified_sellers(self):
        """Get verified sellers only"""
        return self.filter(role='SELLER', is_verified=True)
    
    def get_active_sellers(self):
        """Get active sellers only"""
        return self.filter(role='SELLER', is_active=True)
    
    def get_inactive_sellers(self):
        """Get inactive sellers only"""
        return self.filter(role='SELLER', is_active=False)
    
    def get_buyers(self):
        """Get all buyers"""
        return self.filter(role='BUYER')
    
    def get_admins(self):
        """Get all admin users"""
        return self.filter(role='ADMIN')
    
    def sellers_count(self):
        """Get total seller count"""
        return self.get_sellers().count()
    
    def verified_sellers_count(self):
        """Get verified seller count"""
        return self.get_verified_sellers().count()
    
    def active_sellers_count(self):
        """Get active seller count"""
        return self.get_active_sellers().count()

class CustomUser(AbstractUser):
   ROLE_CHOICES = (
       ('BUYER', 'Buyer'),
       ('SELLER', 'Seller'),
       ('ADMIN', 'Admin'),
   )
   role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='BUYER')
   is_verified = models.BooleanField(default=False)
   business_name = models.CharField(max_length=255, blank=True, null=True)
   phone = models.CharField(max_length=20, blank=True, null=True)
   address = models.TextField(blank=True, null=True)
   store_banner = models.ImageField(upload_to='store_banners/', blank=True, null=True)
   slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

   def save(self, *args, **kwargs):
       if not self.slug:
           base = self.business_name or self.username
           self.slug = slugify(base)
       super().save(*args, **kwargs)

   def is_buyer(self):
       return self.role == 'BUYER'

   def is_seller(self):
       return self.role == 'SELLER'

   def is_admin(self):
       return self.role == 'ADMIN'

   # Use custom manager
   objects = CustomUserManager()