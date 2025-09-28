import json

import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_update_order_add_item(api_request_context: APIRequestContext, isolated_order, another_product):
    payload = {
        "products": [
            {"product_id": isolated_order.items.first().product.id, "quantity": 2},
            {"product_id": another_product.id, "quantity": 1},
        ]
    }
    response = api_request_context.put(
        f"/api/orders/{isolated_order.id}/",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    expect(response).to_be_ok()
    data = response.json()
    assert response.status == 200
    # Updated key to match serializer
    assert "items" in data
    assert len(data["items"]) == 2


def test_update_order_restore_stock(api_request_context: APIRequestContext, isolated_order):
    product = isolated_order.items.first().product
    old_stock = product.stock
    payload = {"products": []}  # remove all items
    response = api_request_context.put(
        f"/api/orders/{isolated_order.id}/",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    expect(response).to_be_ok()

    refreshed_product = api_request_context.get(f"/api/products/{product.id}/").json()
    assert refreshed_product["stock"] == old_stock
