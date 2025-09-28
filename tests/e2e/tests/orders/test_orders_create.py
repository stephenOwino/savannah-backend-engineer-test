import json

import pytest


@pytest.mark.api
class TestOrdersAPI:
    """Orders API tests for order creation scenarios."""

    def test_create_order_success(self, api_request_context, test_data):
        """Test successful order creation with multiple products."""
        product1, product2 = test_data["products"][:2]
        initial_stock1 = product1.stock
        initial_stock2 = product2.stock

        order_data = {
            "products": [
                {"product_id": product1.id, "quantity": 2},
                {"product_id": product2.id, "quantity": 1},
            ]
        }

        response = api_request_context.post(
            "/api/orders/",
            data=json.dumps(order_data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status == 201
        data = response.json()

        # Validate response structure
        required_fields = ["id", "customer", "customer_name", "created_at", "total_amount", "items"]
        for field in required_fields:
            assert field in data

        assert data["customer"] == test_data["customer"].id
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 2

        # Validate stock was updated
        updated_product1 = api_request_context.get(f"/api/products/{product1.id}/").json()
        updated_product2 = api_request_context.get(f"/api/products/{product2.id}/").json()

        assert updated_product1["stock"] == initial_stock1 - 2
        assert updated_product2["stock"] == initial_stock2 - 1

    def test_create_order_insufficient_stock(self, api_request_context, test_data):
        """Test order creation fails when insufficient stock."""
        product1 = test_data["products"][0]
        excessive_quantity = product1.stock + 100

        order_data = {"products": [{"product_id": product1.id, "quantity": excessive_quantity}]}
        response = api_request_context.post(
            "/api/orders/",
            data=json.dumps(order_data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status == 400
        error_data = response.json()
        assert "error" in error_data
        assert "insufficient stock" in error_data["error"].lower()

    def test_create_order_invalid_quantity(self, api_request_context, test_data):
        """Test order creation fails with invalid quantity."""
        product1 = test_data["products"][0]
        order_data = {"products": [{"product_id": product1.id, "quantity": 0}]}

        response = api_request_context.post(
            "/api/orders/",
            data=json.dumps(order_data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status == 400
        error_data = response.json()
        assert isinstance(error_data, dict)
        # Should contain validation error about quantity
