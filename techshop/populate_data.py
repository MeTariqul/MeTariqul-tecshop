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
    print("Populating database with 20 sample products...")

    # Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created.")

    # Create Test User
    if not User.objects.filter(username='testuser').exists():
        User.objects.create_user('testuser', 'test@example.com', 'test1234')
        print("Test user 'testuser' created.")

    # Create Categories
    categories = ['Laptops', 'Smartphones', 'Accessories', 'Audio', 'Gaming', 'Tablets', 'Cameras', 'Wearables']
    cat_objs = {}
    for cat_name in categories:
        cat, created = Category.objects.get_or_create(name=cat_name)
        cat_objs[cat_name] = cat
        if created:
            print(f"Category '{cat_name}' created.")

    # Create Suppliers
    suppliers_data = [
        {'name': 'TechDistributor Inc.', 'email': 'contact@techdist.com', 'phone': '555-0101'},
        {'name': 'Global Gadgets Co.', 'email': 'sales@globalgadgets.com', 'phone': '555-0102'},
        {'name': 'Premium Electronics', 'email': 'info@premiumelec.com', 'phone': '555-0103'},
    ]
    supplier_objs = {}
    for sup_data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(
            name=sup_data['name'],
            defaults={'email': sup_data['email'], 'phone': sup_data['phone']}
        )
        supplier_objs[sup_data['name']] = supplier
        if created:
            print(f"Supplier '{sup_data['name']}' created.")

    # Create 20 Sample Products
    products_data = [
        # Laptops (4 products)
        {'Category': 'Laptops', 'Name': 'Pro Laptop X1', 'Description': 'High performance laptop for professionals with 16GB RAM and 512GB SSD.', 'SKU': 'LAP-X1-001', 'Cost': 800.00, 'Price': 1200.00, 'Supplier': 'TechDistributor Inc.'},
        {'Category': 'Laptops', 'Name': 'UltraBook Air 13', 'Description': 'Lightweight ultrabook perfect for traveling professionals.', 'SKU': 'LAP-UA13-001', 'Cost': 600.00, 'Price': 899.00, 'Supplier': 'Global Gadgets Co.'},
        {'Category': 'Laptops', 'Name': 'Gaming Laptop Pro', 'Description': 'Powerful gaming laptop with RTX graphics and 144Hz display.', 'SKU': 'LAP-GAME-001', 'Cost': 1200.00, 'Price': 1799.00, 'Supplier': 'Premium Electronics'},
        {'Category': 'Laptops', 'Name': 'Business Laptop B5', 'Description': 'Reliable business laptop with security features.', 'SKU': 'LAP-BUS-001', 'Cost': 550.00, 'Price': 749.00, 'Supplier': 'TechDistributor Inc.'},
        
        # Smartphones (3 products)
        {'Category': 'Smartphones', 'Name': 'Galaxy Phone S24', 'Description': 'Latest flagship smartphone with AI features and camera.', 'SKU': 'PHN-S24-001', 'Cost': 600.00, 'Price': 999.00, 'Supplier': 'TechDistributor Inc.'},
        {'Category': 'Smartphones', 'Name': 'iPhone 15 Pro', 'Description': 'Premium smartphone with titanium design.', 'SKU': 'PHN-IP15-001', 'Cost': 700.00, 'Price': 1199.00, 'Supplier': 'Global Gadgets Co.'},
        {'Category': 'Smartphones', 'Name': 'Pixel Phone 8', 'Description': 'Pure Android experience with great camera.', 'SKU': 'PHN-PX8-001', 'Cost': 500.00, 'Price': 799.00, 'Supplier': 'Premium Electronics'},
        
        # Audio (3 products)
        {'Category': 'Audio', 'Name': 'Noise Cancelling Headphones', 'Description': 'Premium wireless headphones with ANC and 30hr battery.', 'SKU': 'AUD-NC-001', 'Cost': 150.00, 'Price': 299.00, 'Supplier': 'TechDistributor Inc.'},
        {'Category': 'Audio', 'Name': 'Wireless Earbuds Pro', 'Description': 'True wireless earbuds with noise cancellation.', 'SKU': 'AUD-EBPRO-001', 'Cost': 80.00, 'Price': 159.00, 'Supplier': 'Global Gadgets Co.'},
        {'Category': 'Audio', 'Name': 'Bluetooth Speaker Max', 'Description': 'Portable waterproof speaker with rich bass.', 'SKU': 'AUD-SPK-001', 'Cost': 40.00, 'Price': 79.00, 'Supplier': 'Premium Electronics'},
        
        # Gaming (3 products)
        {'Category': 'Gaming', 'Name': 'Gaming Console 5', 'Description': 'Next-gen gaming console with 1TB storage.', 'SKU': 'GMG-C5-001', 'Cost': 350.00, 'Price': 499.00, 'Supplier': 'TechDistributor Inc.'},
        {'Category': 'Gaming', 'Name': 'Pro Gaming Controller', 'Description': 'Ergonomic controller with customizable buttons.', 'SKU': 'GMG-CTR-001', 'Cost': 40.00, 'Price': 69.00, 'Supplier': 'Global Gadgets Co.'},
        {'Category': 'Gaming', 'Name': 'Gaming Monitor 27"', 'Description': '27" 144Hz gaming monitor with 1ms response.', 'SKU': 'GMG-MON-001', 'Cost': 200.00, 'Price': 349.00, 'Supplier': 'Premium Electronics'},
        
        # Accessories (3 products)
        {'Category': 'Accessories', 'Name': 'Laptop Backpack', 'Description': 'Waterproof backpack with laptop compartment.', 'SKU': 'ACC-BP-001', 'Cost': 25.00, 'Price': 49.00, 'Supplier': 'TechDistributor Inc.'},
        {'Category': 'Accessories', 'Name': 'USB-C Hub', 'Description': '7-in-1 USB-C hub with HDMI and card reader.', 'SKU': 'ACC-HUB-001', 'Cost': 20.00, 'Price': 39.00, 'Supplier': 'Global Gadgets Co.'},
        {'Category': 'Accessories', 'Name': 'Wireless Mouse', 'Description': 'Ergonomic wireless mouse with silent clicks.', 'SKU': 'ACC-MOU-001', 'Cost': 15.00, 'Price': 29.00, 'Supplier': 'Premium Electronics'},
        
        # Tablets (2 products)
        {'Category': 'Tablets', 'Name': 'ProTab 11', 'Description': '11" tablet with stylus support.', 'SKU': 'TAB-PRO-001', 'Cost': 350.00, 'Price': 549.00, 'Supplier': 'TechDistributor Inc.'},
        {'Category': 'Tablets', 'Name': 'Fire Tablet 10', 'Description': 'Budget-friendly 10" tablet for entertainment.', 'SKU': 'TAB-FIRE-001', 'Cost': 80.00, 'Price': 149.00, 'Supplier': 'Global Gadgets Co.'},
        
        # Cameras (1 product)
        {'Category': 'Cameras', 'Name': 'DSLR Camera Pro', 'Description': 'Professional DSLR with 24MP sensor.', 'SKU': 'CAM-DSLR-001', 'Cost': 600.00, 'Price': 999.00, 'Supplier': 'Premium Electronics'},
        
        # Wearables (1 product)
        {'Category': 'Wearables', 'Name': 'Smart Watch Series 9', 'Description': 'Health and fitness tracking smartwatch.', 'SKU': 'WEA-SW-001', 'Cost': 150.00, 'Price': 299.00, 'Supplier': 'TechDistributor Inc.'},
    ]

    for p_data in products_data:
        cat = cat_objs[p_data['Category']]
        supplier = supplier_objs[p_data['Supplier']]
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
        else:
            print(f"Product '{product.name}' already exists.")

    print(f"Database population complete. Added {len(products_data)} sample products.")

if __name__ == '__main__':
    run()
