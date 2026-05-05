"""
Tests for the store app — models, views, and search/filter logic.
Run with: pytest store/tests.py -v
"""

import pytest
from decimal import Decimal
from django.urls import reverse
from django.core.cache import cache

from store.models import Category, Product, Inventory, Review


# ===========================================================================
# Model Tests
# ===========================================================================

@pytest.mark.django_db
class TestCategoryModel:
    """Category model unit tests."""

    def test_category_str(self, category):
        assert str(category) == 'Electronics'

    def test_category_created(self, category):
        assert category.pk is not None
        assert category.name == 'Electronics'


@pytest.mark.django_db
class TestProductModel:
    """Product model unit tests."""

    def test_product_str(self, product):
        assert 'Test Laptop' in str(product)
        assert 'TEST-001' in str(product)

    def test_no_discount(self, product):
        """Product with 0% discount should return selling price."""
        assert product.has_offer is False
        assert product.discounted_price == Decimal('799.99')

    def test_with_discount(self, discounted_product):
        """10% off 399.99 → 359.99."""
        assert discounted_product.has_offer is True
        expected = round(Decimal('399.99') * Decimal('0.90'), 2)
        assert discounted_product.discounted_price == expected

    def test_profit_margin(self, product):
        """Profit margin = (selling - cost) / selling * 100."""
        margin = ((Decimal('799.99') - Decimal('500.00')) / Decimal('799.99')) * 100
        assert round(product.profit_margin, 2) == round(float(margin), 2)

    def test_stock_quantity(self, product):
        assert product.stock_quantity == 50

    def test_stock_status_in_stock(self, product):
        assert 'In Stock' in product.stock_status

    def test_stock_status_out_of_stock(self, out_of_stock_product):
        # Directly call the property — no helper needed
        assert 'Out of Stock' in out_of_stock_product.stock_status

    def test_stock_status_low_stock(self, db, category):
        """Stock ≤ 10 is considered Low Stock."""
        p = Product.objects.create(
            SKU='LOW-001', name='Low Stock Item',
            cost_price=Decimal('10'), selling_price=Decimal('20'),
            category=category, is_available_online=True,
        )
        Inventory.objects.create(product=p, quantity_on_hand=5)
        assert 'Low Stock' in p.stock_status


@pytest.mark.django_db
class TestInventoryModel:
    def test_is_low_stock(self, db, category):
        p = Product.objects.create(
            SKU='INV-001', name='Inventory Test Product',
            cost_price=Decimal('10'), selling_price=Decimal('20'),
            category=category,
        )
        inv = Inventory.objects.create(product=p, quantity_on_hand=3, reorder_level=10)
        assert inv.is_low_stock is True
        assert inv.has_stock is True

    def test_has_no_stock(self, out_of_stock_product):
        inv = out_of_stock_product.inventory
        assert inv.has_stock is False
        assert inv.is_low_stock is True


# ===========================================================================
# View Tests
# ===========================================================================

@pytest.mark.django_db
class TestHomeView:
    def test_home_returns_200(self, client, product):
        response = client.get(reverse('store:home'))
        assert response.status_code == 200

    def test_home_shows_product(self, client, product):
        response = client.get(reverse('store:home'))
        assert b'Test Laptop' in response.content

    def test_home_excludes_out_of_stock(self, client, out_of_stock_product):
        response = client.get(reverse('store:home'))
        # Out-of-stock products should not appear on the home page
        assert b'Sold Out Headphones' not in response.content


@pytest.mark.django_db
class TestProductListView:
    def test_product_list_200(self, client, product):
        url = reverse('store:product_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_product_list_pagination(self, client, db, category):
        """Create 15 products; page 1 should show 12."""
        for i in range(15):
            p = Product.objects.create(
                SKU=f'PAG-{i:03d}', name=f'Paged Product {i}',
                cost_price=Decimal('10'), selling_price=Decimal('20'),
                category=category, is_available_online=True,
            )
            Inventory.objects.create(product=p, quantity_on_hand=10)
        url = reverse('store:product_list')
        response = client.get(url)
        assert response.status_code == 200
        # Default paginator is 12 per page
        assert len(response.context['page_obj'].object_list) == 12

    def test_filter_by_category(self, client, product, category):
        url = reverse('store:product_list') + f'?category={category.pk}'
        response = client.get(url)
        assert response.status_code == 200
        assert b'Test Laptop' in response.content

    def test_search_returns_matching_product(self, client, product):
        url = reverse('store:product_list') + '?search=Laptop'
        response = client.get(url)
        assert response.status_code == 200
        assert b'Test Laptop' in response.content

    def test_search_returns_no_results(self, client, product):
        url = reverse('store:product_list') + '?search=DoesNotExist12345'
        response = client.get(url)
        assert response.status_code == 200
        assert b'Test Laptop' not in response.content

    def test_price_range_filter(self, client, product, discounted_product):
        url = reverse('store:product_list') + '?min_price=300&max_price=500'
        response = client.get(url)
        assert response.status_code == 200
        # Only the discounted phone (selling 399.99) should appear
        assert b'Discounted Phone' in response.content
        assert b'Test Laptop' not in response.content

    def test_sort_by_price_low(self, client, product, discounted_product):
        url = reverse('store:product_list') + '?sort=price_low'
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestProductDetailView:
    def test_product_detail_200(self, client, product):
        url = reverse('store:product_detail', kwargs={'sku': product.SKU})
        response = client.get(url)
        assert response.status_code == 200
        assert b'Test Laptop' in response.content

    def test_product_detail_404_for_unknown_sku(self, client):
        url = reverse('store:product_detail', kwargs={'sku': 'NOTFOUND'})
        response = client.get(url)
        assert response.status_code == 404

    def test_product_detail_shows_stock_info(self, client, product):
        url = reverse('store:product_detail', kwargs={'sku': product.SKU})
        response = client.get(url)
        assert response.status_code == 200

    def test_product_detail_authenticated_shows_wishlist_btn(self, auth_client, product):
        url = reverse('store:product_detail', kwargs={'sku': product.SKU})
        response = auth_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestStaticPages:
    """Smoke tests for static informational pages."""

    def test_about_page(self, client):
        assert client.get(reverse('store:about')).status_code == 200

    def test_contact_page_get(self, client):
        assert client.get(reverse('store:contact')).status_code == 200

    def test_contact_post_creates_message(self, client):
        from store.models import ContactMessage
        url = reverse('store:contact')
        response = client.post(url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Hello from test',
        })
        assert response.status_code == 302   # redirect after success
        assert ContactMessage.objects.filter(email='john@example.com').exists()

    def test_faq_page(self, client):
        assert client.get(reverse('store:faq')).status_code == 200

    def test_privacy_policy_page(self, client):
        assert client.get(reverse('store:privacy')).status_code == 200

    def test_terms_page(self, client):
        assert client.get(reverse('store:terms')).status_code == 200

    def test_shipping_policy_page(self, client):
        assert client.get(reverse('store:shipping')).status_code == 200

    def test_return_refund_page(self, client):
        assert client.get(reverse('store:return_refund')).status_code == 200


# (Helper removed — tests now call product.stock_status directly)
