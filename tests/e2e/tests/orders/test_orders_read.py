import json

import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_list_orders(api_request_context: APIRequestContext, product_factory, sample_customer):
    """Test listing orders for authenticated user."""
    # Create a product and order for this test
    product = product_factory(price=2000.00, stock=30)

    # Create an order
    order_response = api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": product.id, "quantity": 1}]}),
        headers={"Content-Type": "application/json"},
    )
    assert order_response.status == 201
    created_order = order_response.json()

    # List orders
    response = api_request_context.get("/api/orders/")
    expect(response).to_be_ok()

    data = response.json()
    assert isinstance(data, list)
    assert any(order["id"] == created_order["id"] for order in data)

    # Validate order structure in list
    for order in data:
        required_fields = ["id", "customer", "customer_name", "created_at", "total_amount"]
        for field in required_fields:
            assert field in order


def test_get_order_detail(api_request_context: APIRequestContext, product_factory, sample_customer):
    """Test retrieving specific order details."""
    # Create a product and order for this test
    product = product_factory(price=2000.00, stock=30)

    # Create an order
    order_response = api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": product.id, "quantity": 1}]}),
        headers={"Content-Type": "application/json"},
    )
    assert order_response.status == 201
    created_order = order_response.json()

    # Get order detail
    response = api_request_context.get(f"/api/orders/{created_order['id']}/")
    expect(response).to_be_ok()

    data = response.json()
    assert data["id"] == created_order["id"]

    # Validate complete order structure
    required_fields = ["id", "customer", "customer_name", "created_at", "total_amount", "items"]
    for field in required_fields:
        assert field in data

    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

    # Validate order item structure
    for item in data["items"]:
        item_fields = ["id", "product", "product_name", "quantity", "subtotal"]
        for field in item_fields:
            assert field in item
