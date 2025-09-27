# conftest.py
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from django.conf import LazySettings
from django.contrib.auth.models import User
from playwright.sync_api import APIRequestContext, Playwright
from pytest_django.live_server_helper import LiveServer
from pytest_django.plugin import Blocker


from api.models import Category, Customer, Order, OrderItem, Product

# --- Pytest Hooks and Configuration ---


def pytest_addoption(parser: Parser) -> None:
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--e2e",
        action="store_true",
        default=False,
        help="Enable when running end-to-end tests.",
    )


def determine_django_db_setup_scope(fixture_name: str, config: Config) -> str:
    """
    Dynamically set the database fixture scope.

    End-to-end tests use the `live_server` fixture, which conflicts with
    a session-scoped database setup. Therefore, we switch to a 'function'
    scope when the --e2e flag is present.
    """
    return "function" if config.getoption("--e2e") else "session"


@pytest.fixture(scope=determine_django_db_setup_scope)
def django_db_setup(django_db_setup: FixtureRequest, django_db_blocker: "Blocker") -> None:
    """Custom database setup that handles E2E vs. regular test scopes."""
    pass


# --- Core Test Fixtures ---


@pytest.fixture(scope="function")
def my_live_server(live_server: LiveServer, settings: LazySettings) -> LiveServer:
    """
    Customizes the `live_server` fixture to configure STATIC_URL,
    ensuring static assets are served correctly during E2E tests.
    """
    settings.STATIC_URL = f"{live_server.url}/static/"
    return live_server


@pytest.fixture(scope="function")
def shared_category(db: None) -> Category:
    """Creates a single, shared category to reduce database writes in tests."""
    return Category.objects.create(name="Shared Testing Category")


# --- Data Creation Fixtures ---


@pytest.fixture(scope="function")
def sample_user(db: None) -> User:
    """Creates a standard user for tests."""
    return User.objects.create_user(username="sampleuser", email="sample@example.com", password="testpassword123")


@pytest.fixture(scope="function")
def sample_customer(db: None, sample_user: User) -> Customer:
    """Creates a customer profile linked to a user."""
    return Customer.objects.create(
        user=sample_user,
        phone_number="+254712345678",
        address="456 Test Avenue, Nairobi",
    )


@pytest.fixture(scope="function")
def sample_product(db: None, shared_category: Category) -> Product:
    """Creates a standard product for tests."""
    return Product.objects.create(
        name="Sample Product",
        description="A product for testing purposes.",
        price=1500.00,
        category=shared_category,
        stock=50,
    )


@pytest.fixture(scope="function")
def another_product(db: None, shared_category: Category) -> Product:
    """Creates a second, distinct product for tests."""
    return Product.objects.create(
        name="Another Test Product",
        description="Another product for complex scenarios.",
        price=2500.00,
        category=shared_category,
        stock=25,
    )


@pytest.fixture(scope="function")
def sample_order(db: None, sample_customer: Customer, sample_product: Product) -> Order:
    """Creates a sample order with one item."""
    order = Order.objects.create(customer=sample_customer)
    OrderItem.objects.create(order=order, product=sample_product, quantity=2)
    order.update_total_amount()
    return order


# --- Playwright and API Testing Fixtures ---


@pytest.fixture(scope="function")
def api_request_context(my_live_server: LiveServer, playwright: Playwright) -> APIRequestContext:
    """
    Provides a Playwright APIRequestContext for efficient and reliable API testing.
    """
    request_context = playwright.request.new_context(
        base_url=my_live_server.url,
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Overrides default Playwright browser context options for all tests."""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }
