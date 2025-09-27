import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_list_orders(api_request_context: APIRequestContext):
    response = api_request_context.get("/api/orders/")
    expect(response).to_be_ok()
    data = response.json()
    assert isinstance(data, list)


def test_get_order_detail(api_request_context: APIRequestContext, sample_order):
    response = api_request_context.get(f"/api/orders/{sample_order['id']}/")
    expect(response).to_be_ok()
    data = response.json()
    assert data["id"] == sample_order["id"]
    assert "items" in data
