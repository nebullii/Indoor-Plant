from django.core.management.base import BaseCommand
from products.models import Product
from inventory.models import InventoryItem

class Command(BaseCommand):
    help = 'Generate InventoryItem and barcode for all existing products without one.'

    def handle(self, *args, **options):
        created_count = 0
        for product in Product.objects.all():
            obj, created = InventoryItem.objects.get_or_create(product=product)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created inventory for: {product.name}'))
        self.stdout.write(self.style.SUCCESS(f'Total new inventory items created: {created_count}')) 