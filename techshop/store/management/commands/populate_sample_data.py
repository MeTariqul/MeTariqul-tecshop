from django.core.management.base import BaseCommand
from store.models import Category, Supplier, Product, Inventory, ProductVariant
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populates the database with premium sample products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database population...')
        
        # 1. Create Supplier
        supplier, _ = Supplier.objects.get_or_create(
            name="Premium Tech Distributors",
            defaults={
                'contact_person': "John Doe",
                'email': "supply@premiumtech.com",
                'phone': "+1 800 555 0199",
                'address': "100 Tech Blvd, Silicon Valley, CA"
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Created/Found Supplier: {supplier.name}'))

        # 2. Create Categories
        categories_data = [
            {"name": "Smartphones", "description": "The latest flagship mobile devices."},
            {"name": "Laptops", "description": "High-performance computing for professionals."},
            {"name": "Audio", "description": "Premium sound devices, headphones, and speakers."},
            {"name": "Wearables", "description": "Smartwatches and fitness trackers."},
            {"name": "Accessories", "description": "Essential add-ons for your devices."}
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]}
            )
            categories[cat.name] = cat
            
        self.stdout.write(self.style.SUCCESS('Created/Found Categories'))

        # 3. Create Products
        products_data = [
            # Smartphones
            {
                "category": "Smartphones", "name": "X-Pro Ultra Max", "SKU": "PHN-XPRO-001",
                "cost": 800.00, "price": 1199.99, "desc": "The ultimate flagship smartphone featuring a revolutionary camera system, aerospace-grade titanium build, and an all-day battery life. Experience the future in the palm of your hand.",
                "discount": 0, "variants": True
            },
            {
                "category": "Smartphones", "name": "Z-Fold Zenith", "SKU": "PHN-ZFOLD-002",
                "cost": 1200.00, "price": 1799.00, "desc": "Unfold your world with the Z-Fold Zenith. A massive 8-inch dynamic AMOLED display folds perfectly into your pocket. Multitask like never before.",
                "discount": 5, "discount_label": "Pre-order Special", "variants": True
            },
            {
                "category": "Smartphones", "name": "A-Series Lite", "SKU": "PHN-ALITE-003",
                "cost": 300.00, "price": 499.00, "desc": "Premium features at an accessible price point. The A-Series Lite brings high-refresh-rate displays and great cameras to everyone.",
                "discount": 0, "variants": False
            },
            # Laptops
            {
                "category": "Laptops", "name": "CreatorBook Pro 16", "SKU": "LAP-CBPRO-001",
                "cost": 1500.00, "price": 2499.00, "desc": "Designed for professionals. The CreatorBook Pro 16 features an M2-equivalent custom silicon, a stunning mini-LED display, and all the ports you need.",
                "discount": 10, "discount_label": "Creator Week", "variants": False
            },
            {
                "category": "Laptops", "name": "Zenith Stealth 14", "SKU": "LAP-ZSTL-002",
                "cost": 900.00, "price": 1399.99, "desc": "Ultrathin, ultralight, and incredibly powerful. The Zenith Stealth is the perfect companion for students and business travelers.",
                "discount": 0, "variants": False
            },
            # Audio
            {
                "category": "Audio", "name": "AuraStudio Over-Ear ANC", "SKU": "AUD-AURA-001",
                "cost": 150.00, "price": 349.00, "desc": "Immerse yourself in high-fidelity audio with class-leading active noise cancellation. 40 hours of battery life and plush memory foam earcups.",
                "discount": 15, "discount_label": "Summer Sale", "variants": True
            },
            {
                "category": "Audio", "name": "SonicBuds Pro", "SKU": "AUD-SONIC-002",
                "cost": 80.00, "price": 199.00, "desc": "True wireless perfection. Spatial audio, sweat resistance, and a compact charging case make these the only earbuds you'll ever need.",
                "discount": 0, "variants": False
            },
            {
                "category": "Audio", "name": "BassBlock Home Speaker", "SKU": "AUD-BASS-003",
                "cost": 200.00, "price": 449.00, "desc": "Room-filling sound with deep, punchy bass. Connects via Wi-Fi and Bluetooth, featuring built-in smart assistant capabilities.",
                "discount": 0, "variants": False
            },
            # Wearables
            {
                "category": "Wearables", "name": "Chrono SmartWatch Series 8", "SKU": "WEA-CHRO-001",
                "cost": 200.00, "price": 399.00, "desc": "Track your fitness, monitor your health, and stay connected without touching your phone. Featuring an always-on Retina display and ECG capabilities.",
                "discount": 0, "variants": True
            },
            {
                "category": "Wearables", "name": "FitBand Active", "SKU": "WEA-FITB-002",
                "cost": 40.00, "price": 99.00, "desc": "A lightweight fitness tracker with 14-day battery life, continuous heart rate monitoring, and built-in GPS for your outdoor runs.",
                "discount": 20, "discount_label": "Clearance", "variants": False
            },
            # Accessories
            {
                "category": "Accessories", "name": "MagPower 10000mAh Bank", "SKU": "ACC-MAGP-001",
                "cost": 25.00, "price": 59.99, "desc": "Snap-on magnetic power bank that perfectly aligns with your phone for wireless charging on the go.",
                "discount": 0, "variants": False
            },
            {
                "category": "Accessories", "name": "ProType Mechanical Keyboard", "SKU": "ACC-PROT-002",
                "cost": 60.00, "price": 149.00, "desc": "Tactile, responsive, and fully customizable. This wireless mechanical keyboard features hot-swappable switches and RGB backlighting.",
                "discount": 0, "variants": False
            },
            {
                "category": "Accessories", "name": "ErgoMouse Master", "SKU": "ACC-ERGM-003",
                "cost": 45.00, "price": 99.99, "desc": "Designed for comfort during long hours of work. Features hyper-fast scrolling, cross-computer control, and customizable buttons.",
                "discount": 0, "variants": False
            },
            {
                "category": "Accessories", "name": "GaN 100W Fast Charger", "SKU": "ACC-GAN-004",
                "cost": 20.00, "price": 49.99, "desc": "Charge your laptop, phone, and tablet simultaneously with this incredibly compact gallium nitride (GaN) power adapter.",
                "discount": 0, "variants": False
            },
            {
                "category": "Accessories", "name": "Armored USB-C Cable (2m)", "SKU": "ACC-CBL-005",
                "cost": 8.00, "price": 24.99, "desc": "Braided nylon, Kevlar-reinforced core, and aluminum housing make this the last charging cable you'll ever need to buy.",
                "discount": 0, "variants": False
            }
        ]

        for p_data in products_data:
            # Create or update product
            product, created = Product.objects.update_or_create(
                SKU=p_data["SKU"],
                defaults={
                    "name": p_data["name"],
                    "description": p_data["desc"],
                    "category": categories[p_data["category"]],
                    "supplier": supplier,
                    "cost_price": Decimal(str(p_data["cost"])),
                    "selling_price": Decimal(str(p_data["price"])),
                    "discount_percentage": Decimal(str(p_data["discount"])),
                    "discount_label": p_data.get("discount_label", ""),
                    "is_available_online": True
                }
            )
            
            # Create inventory
            qty = random.randint(15, 100)
            Inventory.objects.update_or_create(
                product=product,
                defaults={
                    "quantity_on_hand": qty,
                    "reorder_level": 10,
                    "location": f"Aisle {random.randint(1,5)}-{random.choice(['A','B','C'])}"
                }
            )
            
            # Create variants if applicable
            if p_data["variants"]:
                if p_data["category"] == "Smartphones":
                    ProductVariant.objects.update_or_create(product=product, size="256GB", color="Midnight Black", defaults={"stock_quantity": 20, "price_adjustment": 0})
                    ProductVariant.objects.update_or_create(product=product, size="512GB", color="Midnight Black", defaults={"stock_quantity": 10, "price_adjustment": 100})
                    ProductVariant.objects.update_or_create(product=product, size="256GB", color="Starlight White", defaults={"stock_quantity": 15, "price_adjustment": 0})
                elif p_data["category"] == "Audio":
                    ProductVariant.objects.update_or_create(product=product, size="", color="Matte Black", defaults={"stock_quantity": 30, "price_adjustment": 0})
                    ProductVariant.objects.update_or_create(product=product, size="", color="Silver", defaults={"stock_quantity": 15, "price_adjustment": 0})
                elif p_data["category"] == "Wearables":
                    ProductVariant.objects.update_or_create(product=product, size="41mm", color="Graphite", defaults={"stock_quantity": 25, "price_adjustment": 0})
                    ProductVariant.objects.update_or_create(product=product, size="45mm", color="Graphite", defaults={"stock_quantity": 20, "price_adjustment": 30})
            
            status = "Created" if created else "Updated"
            self.stdout.write(f'  - {status} Product: {product.name} (Qty: {qty})')

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample products!'))
