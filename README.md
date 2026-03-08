# TechShop - Full-Featured E-Commerce Platform

A complete Django-based e-commerce solution with multi-level admin dashboards, inventory management, and modern shopping experience.

![Django](https://img.shields.io/badge/Django-6.0.2-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/MeTariqul/MeTariqul-tecshop.git

# Navigate to project
cd MeTariqul-tecshop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
cd techshop
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to view the site.

## 📋 Table of Contents

- [Features](#features)
- [Admin Dashboards](#admin-dashboards)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Security](#security)
- [Technology Stack](#technology-stack)

## ✨ Features

### Customer Features
- User registration and authentication
- Product browsing with categories
- Product variants (size, color, storage)
- Shopping cart with persistence
- **Coupon codes** (SAVE10, SAVE20, WELCOME, FLAT50, FLAT100)
- **Save for Later** functionality
- Wishlist
- Checkout process
- Order history and tracking
- **Order tracking page**
- PDF invoice download with QR code
- **Product reviews and ratings**
- **Contact/Support form** for customer inquiries
- **Customer Support dashboard** for admin responses

### New Pages
- About Us
- FAQ
- Terms & Conditions
- Privacy Policy
- Return & Refund Policy
- Shipping Information

### Admin Features
- Multi-level dashboard system
- Product management
- Inventory tracking
- Order management
- Staff management with roles
- **Customer Support management** - respond to customer inquiries
- Reports and analytics

## 🖥️ Admin Dashboards

| Dashboard | URL | Description |
|-----------|-----|-------------|
| Main Admin | `/admin/dashboard/` | Overview, quick stats |
| Director | `/admin/dashboard/director/` | Revenue, analytics, performance |
| Warehouse | `/admin/dashboard/warehouse/` | Stock, transfers, cycle counting |
| Fulfillment | `/admin/dashboard/fulfillment/` | Picking, packing, shipping |

### Staff Roles
- **Director**: Full access
- **Manager**: Orders, reports, customers
- **Warehouse**: Inventory, stock transfers
- **Delivery**: Order delivery updates

## 📁 Project Structure

```
MeTariqul-tecshop/
├── techshop/                 # Django project
│   ├── admin_dashboard/     # Admin panel app
│   ├── cart/               # Shopping cart
│   ├── orders/             # Order management
│   ├── store/              # Store front
│   ├── invoices/           # Invoice generation
│   ├── wishlist/           # Wishlist
│   ├── templates/          # HTML templates
│   └── techshop_proj/      # Settings
├── run_server.bat          # Windows startup script
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- Django 6.0.2
- pip

### Steps

1. **Clone & Setup**
   ```bash
   git clone https://github.com/MeTariqul/MeTariqul-tecshop.git
   cd MeTariqul-tecshop
   ```

2. **Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database**
   ```bash
   cd techshop
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run**
   ```bash
   python manage.py runserver
   ```

## ⚙️ Configuration

Create `techshop/.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - SQLite default)
DB_NAME=techshop
DB_USER=postgres
DB_PASSWORD=your_password
```

## 📖 Usage

### Access Points
- **Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Store**: http://127.0.0.1:8000/store/

### Customer Flow
1. Register at `/accounts/register/`
2. Browse products at `/store/`
3. Add to cart at `/cart/`
4. Checkout at `/orders/checkout/`
5. Download invoice at `/orders/invoice/{id}/`

## 🔗 API Endpoints

### Store
- `/store/` - Products list
- `/store/product/<id>/` - Product details
- `/store/search/` - Search products
- `/store/about/` - About page
- `/store/contact/` - Contact form
- `/store/faq/` - FAQ page
- `/store/track-order/` - Track order
- `/store/privacy/` - Privacy policy
- `/store/terms/` - Terms & conditions
- `/store/return-refund/` - Return & refund
- `/store/shipping/` - Shipping info

### Cart
- `/cart/` - View cart
- `/cart/add/<id>/` - Add product
- `/cart/remove/<id>/` - Remove item
- `/cart/update/<id>/` - Update quantity
- `/cart/apply-coupon/` - Apply coupon code
- `/cart/save-later/<id>/` - Save for later

### Orders
- `/orders/checkout/` - Checkout
- `/orders/confirmation/<id>/` - Confirmation
- `/orders/invoice/<id>/` - PDF Invoice
- `/orders/history/` - Order history
- `/orders/track/<id>/` - Track order

### Invoices
- `/invoices/` - Invoice list
- `/invoices/create/` - Create invoice
- `/invoices/<id>/` - Invoice detail
- `/invoices/<id>/pdf/` - Download PDF

### Admin Dashboard
- `/admin-dashboard/` - Main dashboard
- `/admin-dashboard/customer-support/` - Customer support
- `/admin-dashboard/director/` - Director dashboard
- `/admin-dashboard/warehouse/` - Warehouse dashboard
- `/admin-dashboard/fulfillment/` - Fulfillment dashboard

### Accounts
- `/accounts/login/` - Login
- `/accounts/register/` - Register
- `/accounts/profile/` - Profile

## 🗃️ Database Models

### Core Models
- **Product**: Name, price, SKU, stock, category
- **ProductVariant**: Size, color, storage variants
- **ProductImage**: Product images
- **Category**: Product categories
- **Brand**: Product brands
- **WebCustomer**: User profile, addresses
- **WebOrder**: Order details, status, totals
- **OrderItem**: Products in order
- **StaffProfile**: Staff role, permissions
- **ContactMessage**: Customer inquiries
- **Invoice**: Invoice records
- **Review**: Product reviews and ratings

## 🔒 Security Features

- HTTPS enforcement
- Content Security Policy (CSP)
- CSRF protection
- SQL injection prevention
- XSS protection
- Fraud detection system
- GDPR/CCPA compliance
- Cookie consent banner

## 🛠️ Technology Stack

- **Backend**: Django 6.0.2, Python 3.11+
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode

## 📄 License

MIT License - See LICENSE file for details.

## 👤 Author

MeTariqul - https://github.com/MeTariqul

---

⭐ Star this repo if you found it helpful!
