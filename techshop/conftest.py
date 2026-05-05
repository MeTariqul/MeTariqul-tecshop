"""
conftest.py — shared pytest fixtures for the TechShop test suite.

These fixtures create the minimum objects needed to test views and models
without hitting Supabase's remote database (Django's test runner spins up
a temporary database automatically, using the same engine — PostgreSQL —
configured in settings.py, so tests remain backend-accurate).
"""

import pytest
from django.contrib.auth.models import User
from decimal import Decimal

from store.models import Category, Product, Inventory
from orders.models import WebCustomer, WebOrder, OrderItem


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def password():
    return 'StrongP@ss123'


@pytest.fixture
def user(db, password):
    """A regular authenticated customer."""
    return User.objects.create_user(
        username='testcustomer',
        email='customer@test.com',
        password=password,
        first_name='Test',
        last_name='Customer',
    )


@pytest.fixture
def staff_user(db, password):
    """A staff user who can access the admin dashboard."""
    return User.objects.create_user(
        username='teststaff',
        email='staff@test.com',
        password=password,
        is_staff=True,
    )


@pytest.fixture
def superuser(db, password):
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password=password,
    )


# ---------------------------------------------------------------------------
# Store fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def category(db):
    return Category.objects.create(name='Electronics', description='Electronic gadgets')


@pytest.fixture
def product(db, category):
    """A simple product with inventory."""
    p = Product.objects.create(
        SKU='TEST-001',
        name='Test Laptop',
        description='A test laptop product',
        category=category,
        cost_price=Decimal('500.00'),
        selling_price=Decimal('799.99'),
        discount_percentage=Decimal('0'),
        is_available_online=True,
    )
    Inventory.objects.create(product=p, quantity_on_hand=50, reorder_level=5)
    return p


@pytest.fixture
def discounted_product(db, category):
    """A product with a 10% discount."""
    p = Product.objects.create(
        SKU='TEST-002',
        name='Discounted Phone',
        description='A phone on sale',
        category=category,
        cost_price=Decimal('200.00'),
        selling_price=Decimal('399.99'),
        discount_percentage=Decimal('10'),
        is_available_online=True,
    )
    Inventory.objects.create(product=p, quantity_on_hand=20, reorder_level=3)
    return p


@pytest.fixture
def out_of_stock_product(db, category):
    """A product with zero inventory."""
    p = Product.objects.create(
        SKU='TEST-003',
        name='Sold Out Headphones',
        description='Currently unavailable',
        category=category,
        cost_price=Decimal('50.00'),
        selling_price=Decimal('89.99'),
        is_available_online=True,
    )
    Inventory.objects.create(product=p, quantity_on_hand=0, reorder_level=5)
    return p


# ---------------------------------------------------------------------------
# Customer & Order fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def customer(db, user):
    return WebCustomer.objects.create(
        user=user,
        phone='01700000000',
        address='123 Test Street',
        city='Dhaka',
        state='Dhaka',
        zip_code='1200',
    )


@pytest.fixture
def web_order(db, customer, product):
    order = WebOrder.objects.create(
        customer=customer,
        subtotal=Decimal('799.99'),
        tax_amount=Decimal('64.00'),
        shipping_cost=Decimal('0.00'),
        total_amount=Decimal('863.99'),
        shipping_address='123 Test Street',
        shipping_city='Dhaka',
        shipping_state='Dhaka',
        shipping_zip='1200',
        status='confirmed',
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=Decimal('799.99'),
    )
    return order


# ---------------------------------------------------------------------------
# Authenticated client helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_client(client, user, password):
    """Django test client pre-logged-in as a regular customer."""
    client.login(username=user.username, password=password)
    return client


@pytest.fixture
def staff_client(client, staff_user, password):
    """Django test client pre-logged-in as staff."""
    client.login(username=staff_user.username, password=password)
    return client
