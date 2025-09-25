import json

import pytest
from playwright.sync_api import APIRequestContext


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.django_db
class TestIntegrationFlows:
    """Full e2e integration tests."""

    def test_complete_ecommerce_flow(self, api_request_context, test_data, live_server):
        # Create category
        new_category = {"name": "Accessories", "parent": test_data["root_category"].id}
        cat_resp = api_request_context.post(
            f"{live_server.url}/api/categories/",
            data=json.dumps(new_category),
        )
        assert cat_resp.status == 201
        category_id = cat_resp.json()["id"]

        # Create product
        new_product = {
            "name": "Wireless Mouse",
            "description": "Ergonomic mouse",
            "price": 2500.0,
            "category": category_id,
            "stock": 10,
        }
        prod_resp = api_request_context.post(
            f"{live_server.url}/api/products/",
            data=json.dumps(new_product),
        )
        assert prod_resp.status == 201
        product_id = prod_resp.json()["id"]

        # Place order - Fixed to match OrderSerializer structure
        order_data = {
            "products": [{"product_id": product_id, "quantity": 2}]  # Correct structure
        }
        order_resp = api_request_context.post(
            f"{live_server.url}/api/orders/",
            data=json.dumps(order_data),
        )
        assert order_resp.status == 201
        order_json = order_resp.json()
        assert "created_at" in order_json
        assert order_json["customer"] == test_data["customer"].id

    def test_inventory_management_flow(
        self, api_request_context, test_data, live_server
    ):
        product = test_data["products"][0]
        # Correct field name is "stock" (from your Product model)
        update_data = {"stock": 20}
        resp = api_request_context.patch(
            f"{live_server.url}/api/products/{product.id}/",
            data=json.dumps(update_data),
        )
        assert resp.status == 200
        assert resp.json()["stock"] == 20

    def test_category_hierarchy_with_pricing(
        self, api_request_context, test_data, live_server
    ):
        resp = api_request_context.get(f"{live_server.url}/api/categories/")
        assert resp.status == 200
        categories = resp.json()
        ids = [c["id"] for c in categories]
        assert test_data["root_category"].id in ids
        assert test_data["sub_category"].id in ids

    def test_error_handling_flow(self, api_request_context, live_server):
        resp = api_request_context.get(f"{live_server.url}/api/nonexistent/")
        assert resp.status == 404

        # Fixed order data structure for error test
        order_data = {"products": [{"product_id": 9999, "quantity": 1}]}
        resp = api_request_context.post(
            f"{live_server.url}/api/orders/",
            data=json.dumps(order_data),
        )
        assert resp.status == 400
