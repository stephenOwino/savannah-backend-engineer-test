import os
import sys
from pathlib import Path

import django
import pytest
from django.contrib.auth.models import User

from api.models import Category, Customer, Order, OrderItem, Product

# Django environment setup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "savannah_assess.settings")
django.setup()


# Configure pytest for E2E vs regular tests
def pytest_addoption(parser):
    parser.addoption(
        "--e2e",
        action="store_true",
        default=False,
        help="Enable when running e2e tests",
    )


def determine_django_db_setup_scope(fixture_name, config):
    """
    E2E tests use the live_server fixture, which will wipe
    the db after each test run, which conflicts with a
    session scoped db setup.
    Therefore, we use a function scoped db setup for e2e tests.
    """
    if config.getoption("--e2e"):
        return "function"
    return "session"


@pytest.fixture(scope=determine_django_db_setup_scope)
def django_db_setup(django_db_setup, django_db_blocker):
    """Custom database setup that handles E2E vs regular tests."""
    pass


# Custom live server fixture with proper static assets
@pytest.fixture
def my_live_server(live_server, settings):
    """
    Customized live_server fixture that configures STATIC_URL to point to the live server URL.
    """
    settings.STATIC_URL = live_server.url + "/static/"
    yield live_server


@pytest.fixture
def test_data(db) -> dict:
    """Create initial test data - works with live_server."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

    customer = Customer.objects.create(
        user=user,
        phone_number="+254700123456",
        address="123 Test Street, Nairobi",
    )

    root_category = Category.objects.create(name="Electronics")
    sub_category = Category.objects.create(
        name="Smartphones",
        parent=root_category
    )

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
def shared_category(db) -> Category:
    """Create a shared category to reduce DB writes."""
    return Category.objects.create(name="Shared Category")


@pytest.fixture
def sample_product(db, shared_category) -> dict:
    """Create a sample product for testing."""
    user = User.objects.create_user(
        username="sampleuser",
        email="sample@example.com",
        password="testpass123"
    )
    customer = Customer.objects.create(
        user=user,
        phone_number="+254700123457",
        address="456 Test Avenue, Nairobi",
    )

    product = Product.objects.create(
        name="Sample Product",
        description="A sample product",
        price=1000.00,
        category=shared_category,
        stock=50,
    )

    return {
        "id": product.id,
        "product": product,
        "category": shared_category,
        "customer": customer,
        "user": user
    }


@pytest.fixture
def another_product(db, shared_category) -> dict:
    """Create another product for testing."""
    product = Product.objects.create(
        name="Another Test Product",
        description="Another test product",
        price=2000.00,
        category=shared_category,
        stock=25,
    )

    return {
        "id": product.id,
        "product": product,
        "category": shared_category,
    }


@pytest.fixture
def sample_order(db, sample_product) -> dict:
    """Create a sample order for testing."""
    order = Order.objects.create(
        customer=sample_product["customer"]
    )

    order_item = OrderItem.objects.create(
        order=order,
        product=sample_product["product"],
        quantity=2
    )

    order.update_total_amount()

    return {
        "order": order,
        "order_item": order_item,
        "product": sample_product["product"],
        "customer": sample_product["customer"]
    }


# Playwright fixtures for API testing - Using built-in fixtures properly
@pytest.fixture
def api_request_context(my_live_server, playwright):
    """Provide a Playwright APIRequestContext for API testing."""
    request_context = playwright.request.new_context(
        base_url=my_live_server.url,
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def browser_context_args(browser_context_args):
    """Override browser context options."""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }
