# TechShop Supabase Migration & Modernization Guide

This document outlines the step-by-step changes applied to connect the TechShop Django application to Supabase, alongside sweeping improvements to code structure, security, performance, and testing.

---

## 1. Supabase PostgreSQL Connection

**Goal**: Move from a local MySQL/SQLite setup to Supabase’s managed PostgreSQL.
**Changes Made**:
- Installed `psycopg[binary]==3.3.4` (modern PostgreSQL adapter for Python).
- Installed `python-decouple` to manage secrets securely via a `.env` file instead of hardcoding credentials.
- Updated `techshop/techshop_proj/settings.py` to map the `DATABASES` configuration to Supabase credentials.

**Code Snippet (`.env`)**:
```env
SUPABASE_URL=https://tduqzoqizziuacoyyfge.supabase.co
SUPABASE_ANON_KEY=sb_publishable_bkKCTa3dC3w7Ugy4HlMsyg_7jsfZqJf
SUPABASE_DB_PASSWORD=RedDeth3645
```

**Code Snippet (`settings.py`)**:
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': config('SUPABASE_DB_PASSWORD'),
        'HOST': 'db.tduqzoqizziuacoyyfge.supabase.co',  # Supabase project DB host
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 600, # Enable connection pooling
    }
}
```

---

## 2. Row Level Security (RLS) & Schema Management

**Goal**: Ensure that if the database is accessed via Supabase Data APIs, users can only read/write their own records.
**Changes Made**:
- Generated a Django migration (`add_variant_info_to_orderitem`) to finalize the `OrderItem` schema structure.
- Created an SQL script (`setup/supabase_rls.sql`) to enable RLS across all customer-facing tables (`orders_weborder`, `cart_shoppingcart`, `store_review`, etc.).

**How RLS works here**:
Supabase uses its own `auth.users` table for authentication, while Django uses `auth_user`. The RLS script creates a helper function `get_django_user_id()` that maps `auth.uid()` (Supabase) to `auth_user.id` (Django) via email. Policies then restrict access:
```sql
CREATE POLICY "orders_select_own"
  ON orders_weborder FOR SELECT
  USING (customer_id IN (
      SELECT id FROM orders_webcustomer WHERE user_id = get_django_user_id()
  ));
```
**Important:** Your Django backend connects using the "postgres" user (or `service_role` key via the Supabase client), which inherently **bypasses RLS**. RLS is enforced when frontend applications call Supabase directly using the anonymous/user token.

---

## 3. Code Refactoring & Service Layer

**Goal**: Improve project structure by decoupling complex business rules from Django views.
**Changes Made**:
- Created `techshop/orders/services.py` containing `OrderService`.
- Extracted stock checking, total calculation, tax rules, and inventory deduction out of `views.checkout`.

**Why it improves the project**:
1. **Testability**: The `OrderService` can be tested in isolation without mocking HTTP requests.
2. **Reusability**: If you build a REST API (e.g. Django REST Framework) later, the API view and the HTML view can both use `service.create_order(data)`.
3. **Slim Views**: `orders/views.py` `checkout()` was reduced from ~180 lines down to ~35 lines.

---

## 4. Security & Supabase Auth Client

**Goal**: Secure HTTP headers, handle Auth cleanly.
**Changes Made**:
- Created `techshop/techshop_proj/supabase_client.py` as a singleton factory. It provides two clients: `get_supabase_anon_client()` for public actions and `get_supabase_admin_client()` which uses the `service_role` key strictly on the backend.
- Added strict security headers in `settings.py` (`SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `X_FRAME_OPTIONS = 'DENY'`).

---

## 5. Performance (Caching & N+1 Query Fixes)

**Goal**: Ensure the app stays fast under heavy load.
**Changes Made**:
- Replaced basic querysets in `store/views.py` `home()` with `.select_related('inventory', 'category')`. This fixes "N+1" query problems, reducing the number of SQL queries per page from ~20 to just 1.
- Implemented `django.core.cache`. We configured local-memory caching (which can easily be swapped to Redis in `settings.py` `CACHES`).
- Featured products and categories on the homepage are now cached for 5 minutes (`PRODUCT_CACHE_TTL`), taking the load completely off the database.

---

## 6. Professional Testing Foundation (Pytest)

**Goal**: Validate business logic safely.
**Changes Made**:
- Replaced standard `unittest` with `pytest` + `pytest-django`.
- Introduced `factory-boy` to mock models quickly.
- Built a robust `techshop/conftest.py` filled with reusable fixtures (e.g., `user`, `customer`, `product`, `web_order`).
- Wrote extensive tests in `techshop/orders/tests.py` & `techshop/store/tests.py`.
  - E.g., `test_checkout_deducts_inventory` verifies race conditions using `select_for_update()`.
  - E.g., `test_order_item_subtotal` checks pricing precision logic.

To run the tests, use:
```bash
cd techshop
pytest
```
*(Ensure `pytest` is run from within the virtual environment).*
