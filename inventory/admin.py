from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock', 'barcode_value', 'label_text')
    search_fields = ('product__name', 'barcode_value', 'label_text')
