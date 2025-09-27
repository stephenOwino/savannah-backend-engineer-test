import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_create_order(api_request_context: APIRequestContext, sample_product):
    payload = {"items": [{"product": sample_product["id"], "quantity": 2}]}
    response = api_request_context.post("/api/orders/", data=payload)
    expect(response).to_be_ok()
    data = response.json()
    assert "id" in data
    assert data["total_amount"] > 0


def test_create_order_invalid_quantity(api_request_context: APIRequestContext, sample_product):
    payload = {"items": [{"product": sample_product["id"], "quantity": 9999}]}
    response = api_request_context.post("/api/orders/", data=payload)
    assert response.status == 400
