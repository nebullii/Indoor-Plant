# Generated by Django 5.1.2 on 2024-11-23 02:30

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]