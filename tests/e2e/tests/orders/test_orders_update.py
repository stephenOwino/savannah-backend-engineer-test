import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_update_order_add_item(api_request_context: APIRequestContext, live_server, sample_order, another_product):
    payload = {
        "products": [
            {"product_id": sample_order.items.first().product.id, "quantity": 2},
            {"product_id": another_product.id, "quantity": 1},
        ]
    }
    response = api_request_context.put(f"{live_server.url}/api/orders/{sample_order.id}/", json=payload)
    expect(response).to_be_ok()
    data = response.json()
    assert response.status == 200
    assert "items" in data
    assert len(data["items"]) == 2


def test_update_order_restore_stock(api_request_context: APIRequestContext, live_server, sample_order, sample_product):
    old_stock = sample_product.stock
    payload = {"products": []}  # remove all items
    response = api_request_context.put(f"{live_server.url}/api/orders/{sample_order.id}/", json=payload)
    expect(response).to_be_ok()
    refreshed_product = api_request_context.get(f"{live_server.url}/api/products/{sample_product.id}/").json()
    assert refreshed_product["stock"] == old_stock
