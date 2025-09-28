import json

import pytest
from playwright.sync_api import APIRequestContext, expect

pytestmark = pytest.mark.order


def test_order_total_amount_calculation(api_request_context: APIRequestContext, fresh_sample_product):
    payload = {"products": [{"product_id": fresh_sample_product.id, "quantity": 3}]}
    response = api_request_context.post(
        "/api/orders/",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    expect(response).to_be_ok()
    data = response.json()
    assert response.status == 201
    assert float(data["total_amount"]) == float(fresh_sample_product.price) * 3


def test_orders_sorted_by_created_date(api_request_context: APIRequestContext, sample_customer, fresh_sample_product):
    # Create two orders to test sorting
    api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": fresh_sample_product.id, "quantity": 1}]}),
        headers={"Content-Type": "application/json"},
    )
    api_request_context.post(
        "/api/orders/",
        data=json.dumps({"products": [{"product_id": fresh_sample_product.id, "quantity": 2}]}),
        headers={"Content-Type": "application/json"},
    )

    response = api_request_context.get("/api/orders/")
    expect(response).to_be_ok()
    data = response.json()
    created_dates = [o["created_at"] for o in data]
    assert created_dates == sorted(created_dates, reverse=True)
