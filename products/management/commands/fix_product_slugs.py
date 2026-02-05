from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import models
from products.models import Product


class Command(BaseCommand):
    help = 'Fix product slugs that are None or empty'

    def handle(self, *args, **options):
        # Get all products with None or empty slugs
        products_without_slugs = Product.objects.filter(
            models.Q(slug__isnull=True) | models.Q(slug='')
        )
        
        self.stdout.write(f"Found {products_without_slugs.count()} products without slugs")
        
        for product in products_without_slugs:
            if product.name:
                # Generate slug from name
                base_slug = slugify(product.name)
                slug = base_slug
                counter = 1
                
                # Ensure slug is unique
                while Product.objects.filter(slug=slug).exclude(id=product.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                product.slug = slug
                product.save()
                self.stdout.write(f"Fixed slug for product '{product.name}': {slug}")
            else:
                self.stdout.write(f"Product {product.id} has no name, cannot generate slug")
        
        self.stdout.write(self.style.SUCCESS("Successfully fixed product slugs")) 