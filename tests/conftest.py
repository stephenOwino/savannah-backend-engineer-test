# tests/conftest.py
import os
import uuid

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from django.conf import LazySettings
from django.contrib.auth.models import User
from django.utils import timezone
from playwright.sync_api import APIRequestContext, Playwright
from pytest_django.live_server_helper import LiveServer
from rest_framework.authtoken.models import Token

from api.models import Category, Customer, Order, OrderItem, Product

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


# ---------------- Pytest hooks/options ----------------
def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--e2e", action="store_true", default=False, help="Enable when running end-to-end tests.")
    parser.addoption("--runplaywright", action="store_true", default=False, help="Run playwright tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "playwright: mark test as playwright test")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runplaywright"):
        return
    skip_playwright = pytest.mark.skip(reason="need --runplaywright option to run")
    for item in items:
        if "playwright" in item.keywords:
            item.add_marker(skip_playwright)


def determine_django_db_setup_scope(fixture_name: str, config: Config) -> str:
    return "function" if config.getoption("--e2e") else "session"


@pytest.fixture(scope=determine_django_db_setup_scope)
def django_db_setup(django_db_setup: FixtureRequest, django_db_blocker) -> None:
    pass


# ---------------- Core fixtures ----------------
@pytest.fixture(scope="function")
def my_live_server(live_server: LiveServer, settings: LazySettings) -> LiveServer:
    settings.STATIC_URL = f"{live_server.url}/static/"
    settings.REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ],
    }
    return live_server


# ---------------- Data fixtures ----------------
@pytest.fixture(scope="function")
def sample_user(db: None) -> User:
    unique_id = uuid.uuid4().hex[:8]
    return User.objects.create_user(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password="testpassword123",
    )


@pytest.fixture(scope="function")
def sample_customer(db: None, sample_user: User) -> Customer:
    customer = Customer.objects.get(user=sample_user)
    digits = uuid.uuid4().int % (10**8)
    customer.phone_number = f"+2547{digits:08d}"
    customer.address = "456 Test Avenue, Nairobi"
    customer.save()
    return customer


@pytest.fixture(scope="function")
def root_and_sub_categories(db: None):
    root = Category.objects.create(name=f"RootCat-{uuid.uuid4().hex[:6]}")
    sub = Category.objects.create(name=f"SubCat-{uuid.uuid4().hex[:6]}", parent=root)
    return root, sub


@pytest.fixture(scope="function")
def sample_product(db: None, root_and_sub_categories) -> Product:
    _, sub = root_and_sub_categories
    return Product.objects.create(
        name=f"Sample Product {uuid.uuid4().hex[:6]}",
        description="A product for testing purposes.",
        price=1500.00,
        category=sub,
        stock=50,
    )


@pytest.fixture(scope="function")
def another_product(db: None, root_and_sub_categories) -> Product:
    _, sub = root_and_sub_categories
    return Product.objects.create(
        name=f"Another Product {uuid.uuid4().hex[:6]}",
        description="Another product for complex scenarios.",
        price=2500.00,
        category=sub,
        stock=25,
    )


@pytest.fixture(scope="function")
def sample_order(db: None, sample_customer: Customer, sample_product: Product) -> Order:
    order = Order.objects.create(customer=sample_customer, created_at=timezone.now())
    OrderItem.objects.create(order=order, product=sample_product, quantity=2)
    order.update_total_amount()
    return order


@pytest.fixture(scope="function")
def auth_token(sample_user: User, db: None) -> str:
    token, _ = Token.objects.get_or_create(user=sample_user)
    return token.key


# ---------------- Playwright / API fixtures ----------------
@pytest.fixture(scope="function")
def test_server(page, live_server):
    page.goto(live_server.url)
    return page


@pytest.fixture(scope="function")
def api_request_context(my_live_server: LiveServer, playwright: Playwright, auth_token: str) -> APIRequestContext:
    request_context = playwright.request.new_context(
        base_url=my_live_server.url,
        extra_http_headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {auth_token}",
        },
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="function")
def unauth_api_request_context(my_live_server: LiveServer, playwright: Playwright) -> APIRequestContext:
    request_context = playwright.request.new_context(
        base_url=my_live_server.url,
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "ignore_https_errors": True}


# ---------------- Combined fixture ----------------
@pytest.fixture(scope="function")
def test_data(sample_product: Product, another_product: Product, root_and_sub_categories, sample_customer: Customer):
    root, sub = root_and_sub_categories
    return {
        "root_category": root,
        "sub_category": sub,
        "products": [sample_product, another_product],
        "customer": sample_customer,
    }
