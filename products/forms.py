# products/forms.py
from django import forms
from .models import Product
from ckeditor.fields import RichTextField

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['seller']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Add CSS classes and ensure id and name attributes are set
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'product-name',
            'name': 'product_name'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'id': 'product-description',
            'name': 'product_description'
        })
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'id': 'product-price',
            'name': 'product_price'
        })
        self.fields['cost_price'].widget.attrs.update({
            'class': 'form-control',
            'id': 'product-cost-price',
            'name': 'product_cost_price'
        })
        self.fields['image'].widget.attrs.update({
            'class': 'form-control-file',
            'id': 'product-image',
            'name': 'product_image'
        })
        self.fields['featured'].widget.attrs.update({
            'class': 'form-check-input',
            'id': 'product-featured',
            'name': 'product_featured'
        })
        self.fields['hot_selling'].widget.attrs.update({
            'class': 'form-check-input',
            'id': 'product-hot-selling',
            'name': 'product_hot_selling'
        })
        # Add for new fields
        if 'slug' in self.fields:
            self.fields['slug'].widget.attrs.update({
                'class': 'form-control',
                'id': 'product-slug',
                'name': 'product_slug',
                'placeholder': 'Auto-generated if left blank'
            })
        if 'meta_title' in self.fields:
            self.fields['meta_title'].widget.attrs.update({
                'class': 'form-control',
                'id': 'product-meta-title',
                'name': 'product_meta_title',
                'placeholder': 'SEO meta title (optional)'
            })
        if 'meta_description' in self.fields:
            self.fields['meta_description'].widget.attrs.update({
                'class': 'form-control',
                'id': 'product-meta-description',
                'name': 'product_meta_description',
                'placeholder': 'SEO meta description (optional)'
            })

class SearchForm(forms.Form):
    query = forms.CharField(label='Search for plants', max_length=100)