#!/usr/bin/env python
"""
Script to fix missing migrations on Render deployment
Run this after deployment to ensure all tables are created properly
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indoor_plant.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.tables 
            WHERE table_name = %s
        """, [table_name])
        return cursor.fetchone()[0] > 0

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT count(*) 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, [table_name, column_name])
        return cursor.fetchone()[0] > 0

def main():
    print("🔍 Checking database schema...")
    
    # Check critical tables
    critical_tables = [
        'products_category',
        'products_tag', 
        'products_product',
        'products_product_tags'
    ]
    
    missing_tables = []
    for table in critical_tables:
        if check_table_exists(table):
            print(f"✅ Table {table} exists")
        else:
            print(f"❌ Table {table} is missing")
            missing_tables.append(table)
    
    # Check critical columns
    if check_table_exists('products_product'):
        if check_column_exists('products_product', 'category_id'):
            print("✅ products_product.category_id exists")
        else:
            print("❌ products_product.category_id is missing")
            
    # If tables are missing, try to fix
    if missing_tables:
        print("\n🔧 Attempting to fix missing tables...")
        
        print("1️⃣ Running migrate with --fake-initial...")
        call_command('migrate', '--fake-initial', verbosity=2)
        
        print("2️⃣ Running products migrations specifically...")
        call_command('migrate', 'products', verbosity=2)
        
        print("3️⃣ Re-checking tables...")
        for table in missing_tables:
            if check_table_exists(table):
                print(f"✅ Fixed: Table {table} now exists")
            else:
                print(f"❌ Still missing: Table {table}")
                
    else:
        print("\n✅ All critical tables exist!")
        
    print("\n📊 Creating sample data if needed...")
    
    # Create sample categories if none exist
    from products.models import Category, Tag
    
    if not Category.objects.exists():
        Category.objects.create(
            name="Indoor Plants",
            slug="indoor-plants", 
            description="Beautiful plants for indoor spaces",
            type="indoor"
        )
        Category.objects.create(
            name="Outdoor Plants", 
            slug="outdoor-plants",
            description="Hardy plants for outdoor gardens",
            type="outdoor"
        )
        print("✅ Created sample categories")
    
    if not Tag.objects.exists():
        tags = [
            ("Low Light", "low-light", "Perfect for low light conditions"),
            ("Air Purifier", "air-purifier", "Helps purify indoor air"),
            ("Beginner Friendly", "beginner-friendly", "Easy to care for"),
            ("Pet Safe", "pet-safe", "Safe for pets"),
        ]
        
        for name, slug, desc in tags:
            Tag.objects.create(name=name, slug=slug, description=desc)
        print("✅ Created sample tags")
    
    print("\n🎉 Database schema check completed!")

if __name__ == "__main__":
    main()