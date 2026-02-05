from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from inventory.models import InventoryItem

@receiver(post_save, sender=Product)
def create_inventory_item(sender, instance, created, **kwargs):
    if created:
        # Only create if not already exists
        InventoryItem.objects.get_or_create(product=instance) 