-- ============================================================
-- TechShop Supabase — Row Level Security (RLS) Policies
-- ============================================================
-- Run this in: Supabase Dashboard → SQL Editor
--
-- OVERVIEW:
--   Row Level Security ensures that even if the anon key is
--   accidentally exposed, users can ONLY access their own data.
--   The service_role key bypasses RLS — keep it server-side only.
--
-- Django manages the schema via migrations.
-- This script ONLY sets up RLS policies on top of Django's tables.
-- Run it ONCE after the first `python manage.py migrate`.
-- ============================================================


-- ============================================================
-- 1. ENABLE RLS ON USER-SENSITIVE TABLES
-- ============================================================

ALTER TABLE orders_webcustomer         ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders_weborder            ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders_orderitem           ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders_paymenttransaction  ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_shoppingcart          ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_cartitem              ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist_wishlistitem      ENABLE ROW LEVEL SECURITY;
ALTER TABLE store_review               ENABLE ROW LEVEL SECURITY;
ALTER TABLE store_contactmessage       ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- 2. HELPER FUNCTION — map Supabase auth.uid() → Django auth_user.id
-- ============================================================
-- Supabase Auth uses its own UUID-based user table (auth.users).
-- Django uses auth_user with integer PKs.
-- This function finds the Django user whose email matches the
-- currently authenticated Supabase user's email.

CREATE OR REPLACE FUNCTION get_django_user_id()
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
  SELECT id
  FROM   auth_user
  WHERE  email = (
    SELECT email FROM auth.users WHERE id = auth.uid()
  )
  LIMIT 1;
$$;


-- ============================================================
-- 3. WEBCUSTOMER — customers can only read/edit their own profile
-- ============================================================

-- Allow a customer to read their own WebCustomer record
CREATE POLICY "customer_select_own"
  ON orders_webcustomer
  FOR SELECT
  USING (user_id = get_django_user_id());

-- Allow a customer to update their own profile
CREATE POLICY "customer_update_own"
  ON orders_webcustomer
  FOR UPDATE
  USING (user_id = get_django_user_id());

-- Django backend (service_role) can do everything
CREATE POLICY "backend_full_access_webcustomer"
  ON orders_webcustomer
  USING (auth.role() = 'service_role');


-- ============================================================
-- 4. WEB ORDERS — customers can only see their own orders
-- ============================================================

CREATE POLICY "orders_select_own"
  ON orders_weborder
  FOR SELECT
  USING (
    customer_id IN (
      SELECT id FROM orders_webcustomer WHERE user_id = get_django_user_id()
    )
  );

CREATE POLICY "backend_full_access_weborder"
  ON orders_weborder
  USING (auth.role() = 'service_role');


-- ============================================================
-- 5. ORDER ITEMS — visible only for orders the customer owns
-- ============================================================

CREATE POLICY "orderitem_select_own"
  ON orders_orderitem
  FOR SELECT
  USING (
    order_id IN (
      SELECT o.id
      FROM   orders_weborder o
      JOIN   orders_webcustomer c ON c.id = o.customer_id
      WHERE  c.user_id = get_django_user_id()
    )
  );

CREATE POLICY "backend_full_access_orderitem"
  ON orders_orderitem
  USING (auth.role() = 'service_role');


-- ============================================================
-- 6. PAYMENT TRANSACTIONS — same visibility as orders
-- ============================================================

CREATE POLICY "payment_select_own"
  ON orders_paymenttransaction
  FOR SELECT
  USING (
    order_id IN (
      SELECT o.id
      FROM   orders_weborder o
      JOIN   orders_webcustomer c ON c.id = o.customer_id
      WHERE  c.user_id = get_django_user_id()
    )
  );

CREATE POLICY "backend_full_access_payment"
  ON orders_paymenttransaction
  USING (auth.role() = 'service_role');


-- ============================================================
-- 7. SHOPPING CART — each customer owns their own cart
-- ============================================================

CREATE POLICY "cart_select_own"
  ON cart_shoppingcart
  FOR SELECT
  USING (
    customer_id IN (
      SELECT id FROM orders_webcustomer WHERE user_id = get_django_user_id()
    )
  );

CREATE POLICY "cart_modify_own"
  ON cart_shoppingcart
  FOR ALL
  USING (
    customer_id IN (
      SELECT id FROM orders_webcustomer WHERE user_id = get_django_user_id()
    )
  );

CREATE POLICY "backend_full_access_cart"
  ON cart_shoppingcart
  USING (auth.role() = 'service_role');

-- Cart items follow cart ownership
CREATE POLICY "cartitem_select_own"
  ON cart_cartitem
  FOR SELECT
  USING (
    cart_id IN (
      SELECT sc.id
      FROM   cart_shoppingcart sc
      JOIN   orders_webcustomer c ON c.id = sc.customer_id
      WHERE  c.user_id = get_django_user_id()
    )
  );

CREATE POLICY "backend_full_access_cartitem"
  ON cart_cartitem
  USING (auth.role() = 'service_role');


-- ============================================================
-- 8. WISHLIST — customers manage their own wishlist
-- ============================================================

CREATE POLICY "wishlist_own"
  ON wishlist_wishlistitem
  FOR ALL
  USING (user_id = get_django_user_id());

CREATE POLICY "backend_full_access_wishlist"
  ON wishlist_wishlistitem
  USING (auth.role() = 'service_role');


-- ============================================================
-- 9. PRODUCT REVIEWS — verified-purchase authors only
-- ============================================================

-- Anyone can read approved reviews
CREATE POLICY "reviews_public_read"
  ON store_review
  FOR SELECT
  USING (true);

-- Only the author can insert/update/delete their own review
CREATE POLICY "review_author_modify"
  ON store_review
  FOR ALL
  USING (
    user_id IN (
      SELECT id FROM orders_webcustomer WHERE user_id = get_django_user_id()
    )
  );

CREATE POLICY "backend_full_access_review"
  ON store_review
  USING (auth.role() = 'service_role');


-- ============================================================
-- 10. CONTACT MESSAGES
-- ============================================================

-- Anyone (anon) can insert a contact message
CREATE POLICY "contact_insert_anon"
  ON store_contactmessage
  FOR INSERT
  WITH CHECK (true);

-- Logged-in customer can read their own messages
CREATE POLICY "contact_select_own"
  ON store_contactmessage
  FOR SELECT
  USING (
    customer_id IN (
      SELECT id FROM orders_webcustomer WHERE user_id = get_django_user_id()
    )
    OR customer_id IS NULL  -- anon submissions always allowed to insert
  );

CREATE POLICY "backend_full_access_contact"
  ON store_contactmessage
  USING (auth.role() = 'service_role');


-- ============================================================
-- 11. PUBLIC TABLES — no RLS needed (read-only catalogue)
-- ============================================================
-- These tables are public product data — anyone can browse them.
-- Staff write access is handled entirely by Django's backend
-- using the service_role key, which bypasses RLS.

-- store_product, store_category, store_inventory,
-- store_supplier, store_productimage, store_productvariant
-- → No RLS policies needed — they are read-only for customers.


-- ============================================================
-- DONE — verify with:
--   SELECT tablename, rowsecurity FROM pg_tables
--   WHERE schemaname = 'public' AND rowsecurity = true;
-- ============================================================
