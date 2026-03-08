# TechShop Database Schema

This document describes the database models and their relationships for the TechShop e-commerce platform.

## Overview

TechShop uses Django's ORM with support for SQLite (development) and PostgreSQL/MySQL (production).

## Database Models

### 1. Store App Models

#### Product
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| SKU | CharField(50) | Unique product identifier |
| name | CharField(200) | Product name |
| slug | SlugField | URL-friendly name |
| description | TextField | Product description |
| category | ForeignKey | Link to Category |
| brand | ForeignKey | Link to Brand |
| cost_price | DecimalField | Original cost |
| selling_price | DecimalField | Current selling price |
| discount_percentage | DecimalField | Discount percentage (0-100) |
| discount_label | CharField | Discount label text |
| stock_quantity | IntegerField | Available stock |
| low_stock_threshold | IntegerField | Low stock alert level |
| is_available_online | BooleanField | Available for online purchase |
| featured_image | ImageField | Main product image |
| is_featured | BooleanField | Show on homepage |
| is_active | BooleanField | Product visibility |
| tax_rate | DecimalField | Tax percentage |
| tax_exempt | BooleanField | Tax exempt flag |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

**Related Models:** ProductImage, ProductVariant, Review

#### Category
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| name | CharField(100) | Category name |
| slug | SlugField | URL-friendly name |
| description | TextField | Category description |
| image | ImageField | Category image |
| parent | ForeignKey | Parent category (for subcategories) |
| is_active | BooleanField | Visibility flag |
| display_order | IntegerField | Sort order |

#### Brand
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| name | CharField(100) | Brand name |
| slug | SlugField | URL-friendly name |
| logo | ImageField | Brand logo |
| is_active | BooleanField | Visibility flag |

#### ProductImage
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| product | ForeignKey | Link to Product |
| image | ImageField | Product image |
| alt_text | CharField | Alt text for accessibility |
| display_order | IntegerField | Sort order |

#### ProductVariant
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| product | ForeignKey | Link to Product |
| SKU | CharField(50) | Variant SKU |
| size | CharField(20) | Size (if applicable) |
| color | CharField(30) | Color (if applicable) |
| storage | CharField(20) | Storage (if applicable) |
| additional_price | DecimalField | Price modifier |
| stock_quantity | IntegerField | Variant stock |
| is_active | BooleanField | Visibility flag |

#### Review
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| product | ForeignKey | Link to Product |
| user | ForeignKey | Link to User |
| rating | IntegerField | Rating (1-5) |
| title | CharField(200) | Review title |
| comment | TextField | Review content |
| admin_response | TextField | Admin reply |
| admin_response_at | DateTimeField | Admin reply timestamp |
| is_approved | BooleanField | Approved by admin |
| created_at | DateTimeField | Creation timestamp |

#### ContactMessage
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| name | CharField(100) | Customer name |
| email | EmailField | Customer email |
| phone | CharField(20) | Customer phone |
| subject | CharField(200) | Message subject |
| message | TextField | Message content |
| status | CharField | Status: new, read, in_progress, resolved, closed |
| admin_response | TextField | Admin reply |
| admin_response_by | ForeignKey | Admin user |
| admin_response_at | DateTimeField | Reply timestamp |
| created_at | DateTimeField | Message timestamp |

---

### 2. Cart App Models

#### Cart (Session-based - stored in Django session)
```python
# Cart is stored in session as dictionary:
{
    'sku': {
        'quantity': 1,
        'price': 100.00
    }
}

# Additional session data:
- saved_items: dict - Items saved for later
- compare_list: list - Product SKUs for comparison
- coupon_code: str - Applied coupon code
- coupon_discount: int - Discount percentage
```

---

### 3. Orders App Models

#### WebCustomer
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | OneToOneField | Link to User |
| phone | CharField(20) | Phone number |
| address | TextField | Shipping address |
| city | CharField(100) | City |
| postal_code | CharField(20) | Postal code |
| profile_picture | ImageField | Profile image |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update |

#### WebOrder
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| order_id | CharField(20) | Unique order ID |
| user | ForeignKey | Link to User |
| customer | ForeignKey | Link to WebCustomer |
| status | CharField | Order status |
| subtotal | DecimalField | Items total |
| shipping_cost | DecimalField | Shipping fee |
| tax_amount | DecimalField | Tax amount |
| discount_amount | DecimalField | Discount applied |
| total | DecimalField | Final total |
| payment_method | CharField | Payment method |
| payment_status | CharField | Payment status |
| shipping_address | TextField | Shipping address |
| notes | TextField | Order notes |
| fraud_score | IntegerField | Fraud detection score |
| created_at | DateTimeField | Order timestamp |
| updated_at | DateTimeField | Last update |

**Order Statuses:**
- pending
- confirmed
- processing
- shipped
- delivered
- cancelled
- refunded

#### OrderItem
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| order | ForeignKey | Link to WebOrder |
| product | ForeignKey | Link to Product |
| product_name | CharField | Product name at time of order |
| SKU | CharField | SKU at time of order |
| quantity | IntegerField | Quantity ordered |
| unit_price | DecimalField | Price per unit |
| total | DecimalField | Line total |
| tax_rate | DecimalField | Tax rate at time of order |

---

### 4. Admin Dashboard Models

#### StaffProfile
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | OneToOneField | Link to User |
| role | CharField | Staff role |
| can_manage_products | BooleanField | Product management permission |
| can_manage_orders | BooleanField | Order management permission |
| can_manage_customers | BooleanField | Customer management permission |
| can_manage_delivery | BooleanField | Delivery management permission |
| can_view_reports | BooleanField | Reports access |
| can_manage_settings | BooleanField | Settings access |
| can_manage_staff | BooleanField | Staff management permission |
| created_at | DateTimeField | Creation timestamp |

**Staff Roles:**
- director
- manager
- warehouse
- delivery

#### SiteConfiguration
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| site_name | CharField | Site name |
| currency_short_form | CharField | Currency symbol (Tk, $, etc.) |
| contact_email | EmailField | Contact email |
| contact_phone | CharField | Contact phone |
| notification_email | EmailField | Notification email |
| reviews_enabled | BooleanField | Enable reviews |
| require_approval_for_reviews | BooleanField | Review approval required |
| default_order_status | CharField | Default order status |
| auto_cancel_unpaid_orders | BooleanField | Auto-cancel unpaid |
| auto_cancel_hours | IntegerField | Hours before auto-cancel |
| email_notifications_enabled | BooleanField | Email notifications |
| notify_new_order | BooleanField | Notify on new order |
| notify_order_status_change | BooleanField | Notify on status change |
| notify_new_review | BooleanField | Notify on new review |
| notify_low_stock | BooleanField | Notify on low stock |

#### Supplier
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| name | CharField(200) | Supplier name |
| code | CharField(50) | Supplier code |
| contact_person | CharField(100) | Contact name |
| email | EmailField | Email address |
| phone | CharField(20) | Phone number |
| address | TextField | Address |
| is_active | BooleanField | Active flag |

#### PurchaseOrder
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| po_number | CharField(50) | PO number |
| supplier | ForeignKey | Link to Supplier |
| status | CharField | Status |
| total | DecimalField | Total amount |
| expected_date | DateField | Expected delivery |
| received_date | DateField | Actual received date |
| created_by | ForeignKey | Created by staff |
| created_at | DateTimeField | Creation timestamp |

#### InventoryMovement
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| product | ForeignKey | Link to Product |
| movement_type | CharField | Type: in, out, adjustment |
| quantity | IntegerField | Quantity moved |
| reference | CharField | Reference (PO, order, etc.) |
| notes | TextField | Notes |
| staff | ForeignKey | Staff member |
| created_at | DateTimeField | Timestamp |

---

### 5. Invoices App Models

#### Invoice
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| invoice_number | CharField(50) | Unique invoice number |
| order | ForeignKey | Link to WebOrder |
| invoice_date | DateTimeField | Invoice date |
| due_date | DateField | Due date |
| subtotal | DecimalField | Subtotal |
| tax_amount | DecimalField | Tax amount |
| total | DecimalField | Total amount |
| status | CharField | Status: draft, sent, paid, overdue |
| notes | TextField | Notes |
| created_at | DateTimeField | Creation timestamp |

---

### 6. Wishlist App Models

#### Wishlist
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | ForeignKey | Link to User |
| product | ForeignKey | Link to Product |
| created_at | DateTimeField | Creation timestamp |

---

## ER Diagram (Text)

```
┌─────────────────┐     ┌──────────────────┐
│    Category     │     │      Brand       │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ name            │     │ name             │
│ slug            │     │ slug             │
│ parent_id (FK)  │     │ logo             │
└────────┬────────┘     └──────────────────┘
         │
         │
┌────────▼────────┐     ┌──────────────────┐
│    Product      │     │   ProductImage   │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ SKU (unique)    │◄────│ product_id (FK)  │
│ name            │     │ image            │
│ category_id(FK) │     └──────────────────┘
│ brand_id (FK)  │
│ price fields   │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐     ┌──────────────────┐
│   OrderItem     │     │     Review       │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ order_id (FK)  │     │ product_id (FK)  │
│ product_id (FK)│     │ user_id (FK)     │
│ quantity        │     │ rating           │
│ unit_price      │     │ comment          │
└────────┬────────┘     └──────────────────┘
         │
         │ N:1
         ▼
┌─────────────────┐
│   WebOrder      │
├─────────────────┤
│ id (PK)         │
│ order_id (unique)│
│ user_id (FK)    │
│ status          │
│ totals          │
│ created_at      │
└─────────────────┘
```

---

## Database Indexes

### Product Table
- `SKU` (unique)
- `category_id`
- `is_active`, `is_featured`
- `created_at`

### Order Table
- `order_id` (unique)
- `user_id`
- `status`
- `created_at`

### OrderItem Table
- `order_id`
- `product_id`

---

## Migrations

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Check Migration Status
```bash
python manage.py showmigrations
```

### Reset Database (Development Only)
```bash
python manage.py flush
# Or delete db.sqlite3 and run migrate
```

---

## Sample Data

### Create Sample Products
```bash
python manage.py shell
>>> from store.models import Category, Brand, Product
>>> from django.contrib.auth import get_user_model
>>> 
>>> # Create category
>>> cat = Category.objects.create(name='Laptops', slug='laptops')
>>> 
>>> # Create brand
>>> brand = Brand.objects.create(name='Dell', slug='dell')
>>> 
>>> # Create product
>>> product = Product.objects.create(
...     SKU='DELL-XPS-15',
...     name='Dell XPS 15',
...     category=cat,
...     brand=brand,
...     cost_price=100000,
...     selling_price=120000,
...     stock_quantity=10
... )
```

---

## Backup & Restore

### Backup Database (PostgreSQL)
```bash
pg_dump -U postgres -h localhost techshop_db > backup.sql
```

### Restore Database
```bash
psql -U postgres -h localhost techshop_db < backup.sql
```

### Backup with Django
```bash
python manage.py dbbackup
```

---

## Performance Tips

1. **Add Database Indexes** on frequently queried fields
2. **Use select_related()** for ForeignKey lookups
3. **Use prefetch_related()** for ManyToMany/reverse FK
4. **Enable Query Caching** for expensive queries
5. **Use Pagination** for large lists
6. **Optimize Images** - use WebP format

---

## Support

For database-related questions:
- Django ORM: https://docs.djangoproject.com/en/stable/topics/db/
- PostgreSQL: https://www.postgresql.org/docs/
