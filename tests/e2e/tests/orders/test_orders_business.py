import json

import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_order_total_amount_calculation(api_request_context: APIRequestContext, product_factory):
    """Test that order total is calculated correctly."""
    # Create a fresh product for this test
    fresh_product = product_factory(price=2000.00, stock=30)
    quantity = 3
    expected_total = float(fresh_product.price) * quantity

    payload = {"products": [{"product_id": fresh_product.id, "quantity": quantity}]}
    response = api_request_context.post(
        "/api/orders/",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    expect(response).to_be_ok()
    assert response.status == 201

    data = response.json()
    assert float(data["total_amount"]) == expected_total

    # Validate response structure
    required_fields = ["id", "customer", "created_at", "total_amount", "items"]
    for field in required_fields:
        assert field in data


def test_orders_sorted_by_created_date(api_request_context: APIRequestContext, sample_customer, product_factory):
    """Test that orders are returned sorted by creation date (newest first)."""
    # Create a fresh product for this test
    fresh_product = product_factory(price=2000.00, stock=30)

    # Create two orders to test sorting
    first_order = api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": fresh_product.id, "quantity": 1}]}),
        headers={"Content-Type": "application/json"},
    )
    assert first_order.status == 201

    second_order = api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": fresh_product.id, "quantity": 2}]}),
        headers={"Content-Type": "application/json"},
    )
    assert second_order.status == 201

    # Get orders list
    response = api_request_context.get("/api/orders/")
    expect(response).to_be_ok()

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Validate sorting (newest first)
    created_dates = [order["created_at"] for order in data]
    assert created_dates == sorted(created_dates, reverse=True)
