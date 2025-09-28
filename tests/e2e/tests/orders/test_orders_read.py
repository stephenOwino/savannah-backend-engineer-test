import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_list_orders(api_request_context: APIRequestContext, isolated_order):
    response = api_request_context.get("/api/orders/")
    expect(response).to_be_ok()
    data = response.json()
    assert isinstance(data, list)
    assert any(o["id"] == isolated_order.id for o in data)


def test_get_order_detail(api_request_context: APIRequestContext, isolated_order):
    response = api_request_context.get(f"/api/orders/{isolated_order.id}/")
    expect(response).to_be_ok()
    data = response.json()
    assert data["id"] == isolated_order.id
    # Use the correct key from serializer
    assert "items" in data
    assert isinstance(data["items"], list)
