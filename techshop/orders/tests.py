"""
Tests for the orders app — models, checkout flow, and authentication views.
Run with: pytest orders/tests.py -v
"""

import pytest
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User

from orders.models import WebCustomer, WebOrder, OrderItem, PaymentTransaction
from store.models import Product, Inventory


# ===========================================================================
# Model Tests
# ===========================================================================

@pytest.mark.django_db
class TestWebCustomerModel:
    def test_str_full_name(self, customer):
        expected = f"{customer.user.first_name} {customer.user.last_name}"
        assert str(customer) == expected

    def test_customer_linked_to_user(self, customer, user):
        assert customer.user == user

    def test_customer_default_values(self, db):
        u = User.objects.create_user(username='newuser2', password='pass')
        c = WebCustomer.objects.create(user=u)
        assert c.phone == ''
        assert c.address == ''


@pytest.mark.django_db
class TestWebOrderModel:
    def test_order_str(self, web_order):
        assert web_order.order_number in str(web_order)

    def test_order_number_auto_generated(self, web_order):
        """Order number should start with ORD- and be unique."""
        assert web_order.order_number.startswith('ORD-')
        assert len(web_order.order_number) > 4

    def test_order_belongs_to_customer(self, web_order, customer):
        assert web_order.customer == customer

    def test_order_has_items(self, web_order):
        assert web_order.items.count() == 1

    def test_order_status_default(self, web_order):
        assert web_order.status == 'confirmed'


@pytest.mark.django_db
class TestOrderItemModel:
    def test_order_item_subtotal(self, web_order):
        item = web_order.items.first()
        expected = item.unit_price * item.quantity
        assert item.subtotal == expected

    def test_order_item_str(self, web_order):
        item = web_order.items.first()
        assert 'Test Laptop' in str(item)


@pytest.mark.django_db
class TestPaymentTransactionModel:
    def test_payment_creation(self, web_order):
        txn = PaymentTransaction.objects.create(
            order=web_order,
            transaction_id='TXN-TEST-0001',
            payment_method='Credit Card',
            amount=web_order.total_amount,
            status='completed',
        )
        assert txn.status == 'completed'
        assert txn.order == web_order
        assert 'TXN-TEST-0001' in str(txn)


# ===========================================================================
# Authentication View Tests
# ===========================================================================

@pytest.mark.django_db
class TestRegistrationView:
    def test_register_page_200(self, client):
        url = reverse('orders:register')
        response = client.get(url)
        assert response.status_code == 200

    def test_register_creates_user(self, client):
        url = reverse('orders:register')
        response = client.post(url, {
            'username': 'newshopuser',
            'password1': 'StrongP@ss123',
            'password2': 'StrongP@ss123',
        })
        assert User.objects.filter(username='newshopuser').exists()
        # Should redirect after successful registration
        assert response.status_code == 302

    def test_register_invalid_password_mismatch(self, client):
        url = reverse('orders:register')
        response = client.post(url, {
            'username': 'failuser',
            'password1': 'StrongP@ss123',
            'password2': 'WrongPass456',
        })
        # Should stay on page and show form errors
        assert response.status_code == 200
        assert not User.objects.filter(username='failuser').exists()


@pytest.mark.django_db
class TestLoginView:
    def test_login_page_200(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_login_with_valid_credentials(self, client, user, password):
        response = client.post(reverse('login'), {
            'username': user.username,
            'password': password,
        })
        # Redirect on success
        assert response.status_code == 302

    def test_login_with_wrong_password(self, client, user):
        response = client.post(reverse('login'), {
            'username': user.username,
            'password': 'wrongpassword',
        })
        # Should stay on login page
        assert response.status_code == 200

    def test_staff_login_redirects_to_dashboard(self, client, staff_user, password):
        response = client.post(reverse('login'), {
            'username': staff_user.username,
            'password': password,
        })
        assert response.status_code == 302
        assert '/dashboard/' in response['Location']


# ===========================================================================
# Order History & Profile Views (require login)
# ===========================================================================

@pytest.mark.django_db
class TestOrderHistoryView:
    def test_order_history_requires_login(self, client):
        url = reverse('orders:order_history')
        response = client.get(url)
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_order_history_shows_orders(self, auth_client, web_order):
        url = reverse('orders:order_history')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert web_order.order_number.encode() in response.content

    def test_order_history_empty_for_new_customer(self, auth_client, customer):
        """User with no orders should see an empty list."""
        url = reverse('orders:order_history')
        response = auth_client.get(url)
        assert response.status_code == 200
        # No orders — page renders without crashing
        assert response.context['orders'] is not None


@pytest.mark.django_db
class TestUserProfileView:
    def test_profile_requires_login(self, client):
        url = reverse('orders:user_profile')
        response = client.get(url)
        assert response.status_code == 302

    def test_profile_page_200(self, auth_client, customer):
        url = reverse('orders:user_profile')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_profile_update(self, auth_client, customer):
        url = reverse('orders:user_profile')
        response = auth_client.post(url, {
            'phone':    '01800000000',
            'address':  '456 New Street',
            'city':     'Chittagong',
            'state':    'Chittagong',
            'zip_code': '4000',
        })
        assert response.status_code == 302
        customer.refresh_from_db()
        assert customer.phone == '01800000000'
        assert customer.city == 'Chittagong'


# ===========================================================================
# Checkout View Tests
# ===========================================================================

@pytest.mark.django_db
class TestCheckoutView:
    def test_checkout_requires_login(self, client):
        url = reverse('orders:checkout')
        response = client.get(url)
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_checkout_empty_cart_redirects(self, auth_client):
        """Empty cart should redirect back to cart view."""
        url = reverse('orders:checkout')
        response = auth_client.get(url)
        # Empty cart → redirect to cart page
        assert response.status_code == 302

    def test_checkout_with_cart_shows_form(self, auth_client, product):
        """Set up session cart and verify checkout page renders."""
        session = auth_client.session
        session['cart'] = {product.SKU: {'quantity': 1}}
        session.save()
        url = reverse('orders:checkout')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_checkout_post_creates_order(self, auth_client, customer, product):
        """POST to checkout with valid data should create a WebOrder."""
        session = auth_client.session
        session['cart'] = {product.SKU: {'quantity': 2}}
        session.save()

        initial_count = WebOrder.objects.count()
        url = reverse('orders:checkout')
        response = auth_client.post(url, {
            'shipping_address': '123 Test Road',
            'shipping_city':    'Dhaka',
            'shipping_state':   'Dhaka',
            'shipping_zip':     '1200',
        })
        # Should redirect to confirmation on success
        assert response.status_code == 302
        assert WebOrder.objects.count() == initial_count + 1

    def test_checkout_deducts_inventory(self, auth_client, customer, product):
        """Placing an order should reduce inventory quantity_on_hand."""
        initial_stock = product.inventory.quantity_on_hand
        session = auth_client.session
        session['cart'] = {product.SKU: {'quantity': 3}}
        session.save()

        auth_client.post(reverse('orders:checkout'), {
            'shipping_address': '123 Test Road',
            'shipping_city':    'Dhaka',
            'shipping_state':   'Dhaka',
            'shipping_zip':     '1200',
        })

        product.inventory.refresh_from_db()
        assert product.inventory.quantity_on_hand == initial_stock - 3

    def test_checkout_missing_fields_stays_on_page(self, auth_client, customer, product):
        """Incomplete shipping info should keep the user on the checkout page."""
        session = auth_client.session
        session['cart'] = {product.SKU: {'quantity': 1}}
        session.save()

        response = auth_client.post(reverse('orders:checkout'), {
            'shipping_address': '123 Test Road',
            # missing city, state, zip
        })
        # Renders checkout page again with error
        assert response.status_code == 200


# ===========================================================================
# Order Confirmation View
# ===========================================================================

@pytest.mark.django_db
class TestOrderConfirmationView:
    def test_confirmation_shows_order(self, auth_client, web_order):
        url = reverse('orders:order_confirmation', kwargs={'order_id': web_order.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert web_order.order_number.encode() in response.content

    def test_confirmation_404_for_other_user(self, client, web_order, password):
        """Another user should get a 404 when trying to view someone else's order."""
        other = User.objects.create_user(username='other', password=password)
        client.login(username='other', password=password)
        url = reverse('orders:order_confirmation', kwargs={'order_id': web_order.pk})
        response = client.get(url)
        assert response.status_code == 404
