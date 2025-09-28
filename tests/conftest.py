# conftest.py

import os
import uuid
from typing import Any, Callable, Dict

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import APIRequestContext, Playwright
from pytest_django.live_server_helper import LiveServer
from rest_framework.authtoken.models import Token

from api.models import Category, Customer, Product

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

# ----------------- Pytest Configuration Hooks -----------------


def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption("--e2e", action="store_true", default=False, help="Enable when running end-to-end tests.")
    parser.addoption("--runplaywright", action="store_true", default=False, help="Run playwright tests")


def pytest_configure(config):
    """Configure pytest markers and settings."""
    config.addinivalue_line("markers", "playwright: mark test as playwright test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "order: mark test as order-related test")


def pytest_collection_modifyitems(config, items):
    """Skip Playwright tests if --runplaywright option is not given."""
    if config.getoption("--runplaywright"):
        return
    skip_playwright = pytest.mark.skip(reason="need --runplaywright option to run")
    for item in items:
        if "playwright" in item.keywords:
            item.add_marker(skip_playwright)


# ----------------- Core Test Infrastructure Fixtures -----------------


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Configure browser context arguments for testing."""
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture(scope="function")
def api_live_server(live_server: LiveServer, settings) -> LiveServer:
    """
    Configure the live server with DRF settings required for API tests.
    Renamed from 'my_live_server' for clarity.
    """
    settings.REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    }
    return live_server


# ----------------- API and Playwright Fixtures -----------------


@pytest.fixture(scope="function")
def api_request_context(api_live_server: LiveServer, playwright: Playwright, auth_token: str) -> APIRequestContext:
    """Create an authenticated API request context for testing."""
    request_context = playwright.request.new_context(
        base_url=api_live_server.url,
        extra_http_headers={"Authorization": f"Token {auth_token}"},
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="function")
def unauth_api_request_context(api_live_server: LiveServer, playwright: Playwright) -> APIRequestContext:
    """Create an unauthenticated API request context."""
    request_context = playwright.request.new_context(base_url=api_live_server.url)
    yield request_context
    request_context.dispose()


# ----------------- Data Factory Fixtures -----------------


@pytest.fixture(scope="function")
def sample_user(db) -> User:
    """Create a sample user with unique credentials."""
    unique_id = uuid.uuid4().hex[:8]
    return User.objects.create_user(
        username=f"testuser_{unique_id}",
        password="testpassword123",
    )


@pytest.fixture
def auth_token(db, sample_user: User) -> str:
    """Create an authentication token for the sample user."""
    token, _ = Token.objects.get_or_create(user=sample_user)
    return token.key


@pytest.fixture(scope="function")
def sample_customer(db, sample_user: User) -> Customer:
    """Create a sample customer linked to the sample user."""
    customer, _ = Customer.objects.get_or_create(user=sample_user)
    customer.phone_number = f"+2547{uuid.uuid4().int % (10**8):08d}"
    customer.address = "456 Test Avenue, Nairobi"
    customer.save()
    return customer


@pytest.fixture(scope="function")
def category_factory(db) -> Callable[..., Category]:
    """A factory fixture to create categories."""

    def _create_category(**kwargs: Dict[str, Any]) -> Category:
        name = kwargs.pop("name", f"Category-{uuid.uuid4().hex[:6]}")
        return Category.objects.create(name=name, **kwargs)

    return _create_category


@pytest.fixture(scope="function")
def product_factory(db, category_factory: Callable[..., Category]) -> Callable[..., Product]:
    """
    A factory fixture to create products.
    This replaces `sample_product`, `another_product`, and `fresh_sample_product`.
    """

    def _create_product(**kwargs: Dict[str, Any]) -> Product:
        # If no category is provided, create a default one.
        if "category" not in kwargs:
            kwargs["category"] = category_factory()

        # Set default values that can be overridden by kwargs.
        defaults = {
            "name": f"Product-{uuid.uuid4().hex[:6]}",
            "description": "A test product.",
            "price": 1000.00,
            "stock": 50,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)

    return _create_product


# ----------------- Combined Test Data Fixture -----------------


@pytest.fixture(scope="function")
def test_data(db, category_factory, product_factory, sample_customer) -> Dict[str, Any]:
    """
    Combine common test data into a single, convenient fixture.
    Uses the new factories for setup.
    """
    root_category = category_factory(name="Electronics")
    sub_category = category_factory(name="Smartphones", parent=root_category)

    product1 = product_factory(category=sub_category, price=1500.00)
    product2 = product_factory(category=sub_category, price=2500.00)

    return {
        "root_category": root_category,
        "sub_category": sub_category,
        "products": [product1, product2],
        "customer": sample_customer,
    }
