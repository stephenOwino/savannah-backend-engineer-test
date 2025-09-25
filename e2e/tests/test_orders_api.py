import pytest
import json
from playwright.sync_api import APIRequestContext

@pytest.mark.api
class TestOrdersAPI:
    """Orders API tests."""

    def test_create_order_success(self, api_request_context, test_data, live_server):
        product1, product2 = test_data["products"][:2]
        order_data = {
            "products": [
                {"product_id": product1.id, "quantity": 2},
                {"product_id": product2.id, "quantity": 1},
            ]
        }
        response = api_request_context.post(
            f"{live_server.url}/api/orders/",
            data=json.dumps(order_data),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 201
        data = response.json()
        # Fix: check actual API fields
        assert data["customer"] == test_data["customer"].id
        assert "created_at" in data

    def test_create_order_insufficient_stock(self, api_request_context, test_data, live_server):
        product1 = test_data["products"][0]
        order_data = {"products": [{"product_id": product1.id, "quantity": 1000}]}
        response = api_request_context.post(
            f"{live_server.url}/api/orders/",
            data=json.dumps(order_data),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 400

    def test_create_order_invalid_quantity(self, api_request_context, test_data, live_server):
        product1 = test_data["products"][0]
        order_data = {"products": [{"product_id": product1.id, "quantity": 0}]}
        response = api_request_context.post(
            f"{live_server.url}/api/orders/",
            data=json.dumps(order_data),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 400

