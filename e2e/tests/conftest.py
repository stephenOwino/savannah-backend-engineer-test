import os
import sys
from pathlib import Path

import django
import pytest
from playwright.sync_api import APIRequestContext, sync_playwright

# Django setup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "savannah_assess.settings")
django.setup()

from django.contrib.auth.models import User

from api.models import Category, Customer, Product


@pytest.fixture
def test_data(db):
    """Create initial test data."""
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
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
def api_request_context(live_server) -> APIRequestContext:
    """Provide a Playwright APIRequestContext for each test."""
    with sync_playwright() as p:
        request_context = p.request.new_context(
            base_url=live_server.url,  # Use live_server.url instead of hardcoded URL
            extra_http_headers={"Content-Type": "application/json"},
        )
        yield request_context
        request_context.dispose()
