import os
import sys
from pathlib import Path

import django
import pytest
from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

from api.models import Category, Customer, Order, OrderItem, Product

# Django environment setup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "savannah_assess.settings")
django.setup()


@pytest.fixture
@pytest.mark.django_db(transaction=True)
def test_data(db):
    """Create initial test data."""
    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    customer = Customer.objects.create(
        user=user,
        phone_number="+254700123456",
        address="123 Test Street, Nairobi",
    )

    root_category = Category.objects.create(name="Electronics")
    sub_category = Category.objects.create(name="Smartphones", parent=root_category)

    product1 = Product.objects.create(
        name="iPhone 14",
        description="Latest iPhone model",
        price=99999.00,
        category=sub_category,
        stock=10,
    )

    product2 = Product.objects.create(
        name="Samsung Galaxy S23",
        description="Latest Samsung model",
        price=89999.00,
        category=sub_category,
        stock=5,
    )

    return {
        "user": user,
        "customer": customer,
        "root_category": root_category,
        "sub_category": sub_category,
        "products": [product1, product2],
    }


@pytest.fixture
@pytest.mark.django_db(transaction=True)
def sample_product(db):
    """Create a sample product for testing."""
    user = User.objects.create_user(username="sampleuser", email="sample@example.com", password="testpass123")
    customer = Customer.objects.create(
        user=user,
        phone_number="+254700123457",
        address="456 Test Avenue, Nairobi",
    )

    category = Category.objects.create(name="Sample Category")
    product = Product.objects.create(
        name="Sample Product",
        description="A sample product",
        price=1000.00,
        category=category,
        stock=50,
    )

    return {"id": product.id, "product": product, "category": category, "customer": customer, "user": user}


@pytest.fixture
@pytest.mark.django_db(transaction=True)
def another_product(db):
    """Create another product for testing."""
    category = Category.objects.create(name="Another Category")
    product = Product.objects.create(
        name="Another Test Product",
        description="Another test product",
        price=2000.00,
        category=category,
        stock=25,
    )

    return product


@pytest.fixture
@pytest.mark.django_db(transaction=True)
def sample_order(db, sample_product):
    """Create a sample order for testing."""
    # Create an order using the customer from sample_product
    order = Order.objects.create(customer=sample_product["customer"])

    # Create order item
    order_item = OrderItem.objects.create(order=order, product=sample_product["product"], quantity=2)

    # Update the order total
    order.update_total_amount()

    return {
        "order": order,
        "order_item": order_item,
        "product": sample_product["product"],
        "customer": sample_product["customer"],
    }


@pytest.fixture
def api_request_context(live_server):
    """Provide a Playwright APIRequestContext for each test."""
    with sync_playwright() as p:
        request_context = p.request.new_context(
            base_url=live_server.url,
            extra_http_headers={"Content-Type": "application/json"},
        )
        yield request_context
        request_context.dispose()
