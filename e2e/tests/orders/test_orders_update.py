import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_update_order_add_item(api_request_context: APIRequestContext, sample_order, another_product):
    payload = {"items": [
        {"product": sample_order["items"][0]["product"], "quantity": 2},
        {"product": another_product["id"], "quantity": 1}
    ]}
    response = api_request_context.put(f"/api/orders/{sample_order['id']}/", data=payload)
    expect(response).to_be_ok()
    data = response.json()
    assert len(data["items"]) == 2


def test_update_order_restore_stock(api_request_context: APIRequestContext, sample_order, sample_product):
    old_stock = sample_product["stock"]
    payload = {"items": []}  # remove all items
    api_request_context.put(f"/api/orders/{sample_order['id']}/", data=payload)
    refreshed_product = api_request_context.get(f"/api/products/{sample_product['id']}/").json()
    assert refreshed_product["stock"] == old_stock
