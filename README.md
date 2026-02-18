# TechShop - E-Commerce Platform

A full-featured Django-based e-commerce platform with multi-level admin dashboards, inventory management, and modern shopping experience.

![Django](https://img.shields.io/badge/Django-6.0.2-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Creating Admin Users](#creating-admin-users)
8. [Admin Dashboards](#admin-dashboards)
9. [Customer Features](#customer-features)
10. [API Endpoints](#api-endpoints)
11. [Database Models](#database-models)
12. [Security Features](#security-features)
13. [Customization](#customization)
14. [Troubleshooting](#troubleshooting)
15. [Technologies Used](#technologies-used)

---

## Features

### Multi-Level Admin Dashboard
- **Director/Owner Dashboard**: Executive summary, revenue analytics, staff performance
- **Warehouse Dashboard**: Stock management, inventory movements, cycle counting
- **Fulfillment Dashboard**: Order picking, packing, shipping management
- **Staff Management**: Role-based access control (Managers, Warehouse Staff, Delivery)

### Inventory Management
- Product Information Management (PIM) with variants
- Multi-attribute support (size, color, storage, etc.)
- Real-time stock tracking
- Stock transfers between warehouses
- Cycle counting for inventory accuracy
- Low stock alerts
- Barcode/QR code scanning interface

### Customer Features
- User registration and authentication
- Product browsing with categories and filters
- Product variants selection (size, color, etc.)
- Shopping cart with persistent storage
- Wishlist functionality
- Checkout process with multiple payment methods
- Order history and tracking
- PDF invoice generation with QR codes

### Order Management
- Order creation and processing
- Order status tracking (Pending, Processing, Shipped, Delivered, Cancelled)
- Automatic inventory deduction
- Order confirmation emails (template-based)
- PDF invoice generation

### Security Features
- HTTPS enforcement
- Content Security Policy (CSP) headers
- CSRF protection
- SQL injection prevention
- XSS protection
- Fraud detection system
- GDPR/CCPA compliance (Cookie consent, Privacy policy)

---

## Project Structure

```
Ecommerse/
├── techshop/                    # Main Django project
│   ├── admin_dashboard/         # Admin dashboard app
│   ├── cart/                    # Shopping cart app
│   ├── orders/                  # Orders management app
│   ├── store/                   # Store front app
│   ├── wishlist/                # Wishlist app
│   ├── templates/               # HTML templates
│   ├── templatetags/            # Custom template tags
│   ├── techshop_proj/           # Django project settings
│   └── media/                   # User uploaded files
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

### App Details

| App | Purpose |
|-----|---------|
| `admin_dashboard` | Multi-level admin interfaces, staff management, inventory |
| `cart` | Shopping cart, persistent sessions |
| `orders` | Order processing, checkout, PDF invoices |
| `store` | Product catalog, categories, search |
| `wishlist` | User wishlists |

---

## Prerequisites

- Python 3.11 or higher
- Django 6.0.2
- PostgreSQL (recommended) or SQLite (development)
- pip package manager

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Ecommerse
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create a `.env` file in the `techshop/` directory:

```env
# Database (PostgreSQL recommended for production)
DB_NAME=techshop
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Or use SQLite (default for development)
# Just leave DB settings empty

# Security
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (for order confirmations)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Configuration

### Database Setup

For SQLite (default, recommended for development):
- No additional setup required
- Database file will be created automatically

For PostgreSQL (recommended for production):

```bash
# Create database
psql -U postgres -c "CREATE DATABASE techshop;"

# Update .env with PostgreSQL credentials
```

### Run Migrations

```bash
cd techshop
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## Running the Application

### Development Server

```bash
cd techshop
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

### Admin Panel

Access the admin panel at: `http://127.0.0.1:8000/admin/`

Use the superuser credentials created earlier to login.

---

## Creating Admin Users

### Method 1: Via Admin Panel

1. Login to `/admin/`
2. Go to **Staff Profiles** > **Add**
3. Fill in the user details and assign roles

### Method 2: Via Command Line

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from admin_dashboard.models import StaffProfile

User = get_user_model()

# Create user
user = User.objects.create_user(
    username='manager1',
    email='manager@example.com',
    password='securepassword123',
    is_staff=True
)

# Create staff profile
profile = StaffProfile.objects.create(
    user=user,
    role='manager',
    department='Sales'
)
```

### Staff Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `director` | Owner/Executive | Full access to all features |
| `manager` | Store Manager | Order management, reports, customers |
| `warehouse` | Warehouse Staff | Inventory, stock transfers, cycle counting |
| `delivery` | Delivery Staff | Order delivery updates |

---

## Admin Dashboards

### Director Dashboard (`/admin/dashboard/director/`)
- Revenue analytics and charts
- Order statistics
- Top products
- Staff performance metrics

### Warehouse Dashboard (`/admin/dashboard/warehouse/`)
- Current stock levels
- Inventory movements history
- Low stock alerts
- Stock transfer management

### Fulfillment Dashboard (`/admin/dashboard/fulfillment/`)
- Pending orders queue
- Order picking interface
- Packing slip generation
- Shipping label preparation

### Main Admin Dashboard (`/admin/dashboard/`)
- Quick stats overview
- Recent orders
- Quick actions

---

## Customer Features

### User Registration

1. Visit `/accounts/register/`
2. Fill in the registration form
3. Verify email (if configured)
4. Login at `/accounts/login/`

### Shopping Flow

1. **Browse Products**: `/store/`
2. **View Product Details**: `/store/product/<id>/`
3. **Select Variants**: Choose size, color, etc.
4. **Add to Cart**: `/cart/add/<product_id>/`
5. **View Cart**: `/cart/`
6. **Checkout**: `/orders/checkout/`
7. **Order Confirmation**: `/orders/confirmation/<order_id>/`
8. **Download Invoice**: `/orders/invoice/<order_id>/`

### Order History

View all past orders at: `/orders/history/`

---

## API Endpoints

### Store

| URL | Description |
|-----|-------------|
| `/store/` | Product listing |
| `/store/product/<id>/` | Product details |
| `/store/category/<slug>/` | Products by category |
| `/store/search/` | Product search |

### Cart

| URL | Description |
|-----|-------------|
| `/cart/` | View cart |
| `/cart/add/<product_id>/` | Add to cart |
| `/cart/update/<item_id>/` | Update quantity |
| `/cart/remove/<item_id>/` | Remove item |

### Orders

| URL | Description |
|-----|-------------|
| `/orders/checkout/` | Checkout process |
| `/orders/confirmation/<id>/` | Order confirmation |
| `/orders/invoice/<id>/` | Download PDF invoice |
| `/orders/history/` | Order history |

### Accounts

| URL | Description |
|-----|-------------|
| `/accounts/login/` | User login |
| `/accounts/logout/` | User logout |
| `/accounts/register/` | User registration |
| `/accounts/profile/` | User profile |

### Admin

| URL | Description |
|-----|-------------|
| `/admin/` | Main admin panel |
| `/admin/dashboard/` | Admin dashboard |
| `/admin/dashboard/director/` | Director dashboard |
| `/admin/dashboard/warehouse/` | Warehouse dashboard |
| `/admin/dashboard/fulfillment/` | Fulfillment dashboard |

---

## Database Models

### Core Models

#### Product
- `id`, `name`, `slug`, `description`
- `price`, `discount_price`, `discount_percentage`
- `category`, `brand`
- `SKU`, `stock_quantity`
- `is_active`, `created_at`, `updated_at`

#### ProductVariant
- `product` (FK)
- `sku`, `price`, `stock_quantity`
- `attributes` (JSON)
- `is_active`

#### WebCustomer
- `user` (OneToOne to User)
- `phone`, `shipping_address`
- `shipping_city`, `shipping_state`, `shipping_zip`

#### WebOrder
- `customer` (FK)
- `order_number`, `status`
- `subtotal`, `shipping_cost`, `tax_amount`, `total_amount`
- `shipping_address`, `payment_method`
- `created_at`

#### OrderItem
- `order` (FK)
- `product` (FK)
- `quantity`, `unit_price`, `subtotal`

#### StaffProfile
- `user` (OneToOne)
- `role`, `department`
- `can_manage_orders`, `can_manage_inventory`

---

## Security Features

### HTTPS Enforcement
Automatically redirects HTTP to HTTPS in production.

### Content Security Policy
Configured in `techshop_proj/security.py`:
- Restricts resource loading
- Prevents XSS attacks
- Controls iframe embedding

### Fraud Detection
Analyzes orders for suspicious patterns:
- Multiple orders from same IP
- Unusual order quantities
- Rapid order placement

### GDPR/CCPA Compliance
- Cookie consent banner
- Privacy policy page
- Data export/delete capabilities

---

## Customization

### Changing Site Name and Logo

1. Go to Admin Panel > Site Configuration
2. Update site name, logo, and favicon
3. Save changes

### Currency Settings

1. Go to Admin Panel > Site Configuration
2. Select currency from dropdown (BDT, USD, EUR, etc.)
3. Currency will update throughout the site

### Theme Colors

Edit `techshop/static/css/main.css` to customize:
- Primary color: `#11998e` (teal)
- Secondary colors
- Font styles

---

## Troubleshooting

### Common Issues

#### Migration Errors

```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial
python manage.py showmigrations
```

#### Static Files Not Loading

```bash
python manage.py collectstatic
```

#### Database Locked (SQLite)

```bash
# Remove lock file
rm techshop/db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

#### Port Already in Use

```bash
# Use different port
python manage.py runserver 8001
```

### Getting Help

1. Check Django logs in terminal
2. Enable DEBUG=True in settings for detailed errors
3. Check browser console for JavaScript errors

---

## Technologies Used

### Backend
- **Django 6.0.2** - Web framework
- **Python 3.11+** - Programming language
- **SQLite/PostgreSQL** - Database

### Frontend
- **HTML5/CSS3** - Markup and styling
- **JavaScript** - Interactivity
- **Bootstrap 5** - UI framework

### Libraries
- **ReportLab** - PDF generation
- **qrcode** - QR code generation
- **Pillow** - Image processing
- **django-crispy-forms** - Form rendering

---

## License

MIT License

Copyright © 2026 TechShop. All rights reserved.

---

## Support

For issues and questions:
- Email: support@techshop.com
- Website: https://techshop.com

---

## Changelog

### Version 1.0.0 (2026-02-17)
- Initial release
- Multi-level admin dashboards
- Inventory management system
- Order processing with PDF invoices
- User authentication and profiles
- Shopping cart and checkout
- Security features (HTTPS, CSP, Fraud detection)
- GDPR compliance
