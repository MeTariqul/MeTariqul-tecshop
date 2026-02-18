import os
import django
import random
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techshop_proj.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Supplier, Product, Inventory

def run():
    print("Populating database...")

    # Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created.")

    # Create Test User
    if not User.objects.filter(username='testuser').exists():
        User.objects.create_user('testuser', 'test@example.com', 'test1234')
        print("Test user 'testuser' created.")

    # Create Categories
    categories = ['Laptops', 'Smartphones', 'Accessories', 'Audio', 'Gaming']
    cat_objs = {}
    for cat_name in categories:
        cat, created = Category.objects.get_or_create(name=cat_name)
        cat_objs[cat_name] = cat
        if created:
            print(f"Category '{cat_name}' created.")

    # Create Suppliers
    supplier, created = Supplier.objects.get_or_create(
        name='TechDistributor Inc.',
        defaults={'email': 'contact@techdist.com', 'phone': '555-0101'}
    )
    if created:
        print("Supplier created.")

    # Create Products
    products_data = [
        {
            'Category': 'Laptops',
            'Name': 'Pro Laptop X1',
            'Description': 'High performance laptop for professionals.',
            'SKU': 'LAP-X1-001',
            'Cost': 800.00,
            'Price': 1200.00,
        },
        {
            'Category': 'Smartphones',
            'Name': 'Galaxy Phone S24',
            'Description': 'Latest flagship smartphone with AI features.',
            'SKU': 'PHN-S24-001',
            'Cost': 600.00,
            'Price': 999.00,
        },
        {
            'Category': 'Audio',
            'Name': 'Noise Cancelling Headphones',
            'Description': 'Premium wireless headphones with ANC.',
            'SKU': 'AUD-NC-001',
            'Cost': 150.00,
            'Price': 299.00,
        },
        {
            'Category': 'Gaming',
            'Name': 'Gaming Console 5',
            'Description': 'Next-gen gaming console.',
            'SKU': 'GMG-C5-001',
            'Cost': 350.00,
            'Price': 499.00,
        }
    ]

    for p_data in products_data:
        cat = cat_objs[p_data['Category']]
        product, created = Product.objects.get_or_create(
            SKU=p_data['SKU'],
            defaults={
                'name': p_data['Name'],
                'description': p_data['Description'],
                'category': cat,
                'supplier': supplier,
                'cost_price': Decimal(str(p_data['Cost'])),
                'selling_price': Decimal(str(p_data['Price'])),
                'is_available_online': True
            }
        )
        if created:
            print(f"Product '{product.name}' created.")
            # Create Inventory
            Inventory.objects.create(
                product=product,
                quantity_on_hand=random.randint(10, 50),
                reorder_level=5,
                location='Warehouse A'
            )
            print(f"Inventory for '{product.name}' created.")

    print("Database population complete.")

if __name__ == '__main__':
    run()
