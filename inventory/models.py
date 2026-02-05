import os
import uuid
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from products.models import Product
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image


def generate_unique_barcode():
    # Generate a short unique code (8 chars from UUID)
    return uuid.uuid4().hex[:8].upper()


def generate_barcode_image(barcode_value):
    # Generate a barcode image and return as ContentFile
    buffer = BytesIO()
    barcode = Code128(barcode_value, writer=ImageWriter())
    barcode.write(buffer, options={"write_text": False})
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"barcode_{barcode_value}.png")


def make_label_text(product):
    short_name = product.name[:15] + ("..." if len(product.name) > 15 else "")
    return f"ID:{product.id} | {short_name} | SKU:{product.sku or ''}"


class InventoryItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory_item')
    stock = models.IntegerField(default=0)
    barcode_value = models.CharField(max_length=32, unique=True, blank=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    label_text = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        # Generate barcode if missing
        if not self.barcode_value:
            self.barcode_value = generate_unique_barcode()
        # Generate label
        self.label_text = make_label_text(self.product)
        # Generate barcode image
        if not self.barcode_image:
            image_file = generate_barcode_image(self.barcode_value)
            self.barcode_image.save(image_file.name, image_file, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inventory for {self.product.name} (Stock: {self.stock})"
