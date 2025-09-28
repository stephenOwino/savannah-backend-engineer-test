import json

import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_update_order_add_item(api_request_context: APIRequestContext, product_factory, sample_customer):
    """Test adding items to an existing order."""
    # Create products for this test
    original_product = product_factory(price=2000.00, stock=30)
    another_product = product_factory(price=2500.00, stock=25)

    # Create initial order
    order_response = api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": original_product.id, "quantity": 1}]}),
        headers={"Content-Type": "application/json"},
    )
    assert order_response.status == 201
    created_order = order_response.json()

    # Update order with additional item
    payload = {
        "products": [
            {"product_id": original_product.id, "quantity": 2},  # Increase quantity
            {"product_id": another_product.id, "quantity": 1},  # Add new item
        ]
    }

    response = api_request_context.put(
        f"/api/orders/{created_order['id']}/",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    expect(response).to_be_ok()
    assert response.status == 200

    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2

    # Validate response structure
    required_fields = ["id", "customer", "total_amount", "items"]
    for field in required_fields:
        assert field in data

    # Verify items structure
    for item in data["items"]:
        item_fields = ["id", "product", "product_name", "quantity", "subtotal"]
        for field in item_fields:
            assert field in item


def test_update_order_restore_stock(api_request_context: APIRequestContext, product_factory, sample_customer):
    """Test that API rejects removing all items from order (empty products array)."""
    # Create product for this test
    product = product_factory(price=2000.00, stock=30)
    initial_stock = product.stock

    # Create order with 1 item
    order_response = api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": product.id, "quantity": 1}]}),
        headers={"Content-Type": "application/json"},
    )
    assert order_response.status == 201
    created_order = order_response.json()

    # Verify stock was reduced
    product_after_order = api_request_context.get(f"/api/products/{product.id}/").json()
    assert product_after_order["stock"] == initial_stock - 1

    # Try to remove all items from order (empty products array)
    payload = {"products": []}
    response = api_request_context.put(
        f"/api/orders/{created_order['id']}/",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    # Expect API to reject empty order
    assert response.status == 400
    error = response.json()
    assert "products" in error
    assert "at least one product" in error["products"][0]

    # Verify stock has NOT changed (still reduced by 1)
    updated_product = api_request_context.get(f"/api/products/{product.id}/").json()
    assert updated_product["stock"] == initial_stock - 1
