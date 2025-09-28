import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_order_total_amount_calculation(api_request_context: APIRequestContext, sample_product):
    payload = {"products": [{"product_id": sample_product.id, "quantity": 3}]}
    # Ensure JSON body is sent correctly
    response = api_request_context.post("/api/orders/", json=payload)
    expect(response).to_be_ok()
    data = response.json()
    assert response.status == 201
    # Cast total_amount to float to match test expectation
    assert float(data["total_amount"]) == float(sample_product.price) * 3


def test_orders_sorted_by_created_date(api_request_context: APIRequestContext):
    response = api_request_context.get("/api/orders/")
    expect(response).to_be_ok()
    data = response.json()
    created_dates = [o["created_at"] for o in data]
    assert created_dates == sorted(created_dates, reverse=True)
