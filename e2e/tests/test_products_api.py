import json

import pytest

# from playwright.sync_api import APIRequestContext


@pytest.mark.api
class TestProductsAPI:
    """Products API tests."""

    def test_list_all_products(self, api_request_context, test_data, live_server):
        response = api_request_context.get(f"{live_server.url}/api/products/")
        assert response.status == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        expected_fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "stock",
        ]
        for field in expected_fields:
            assert field in data[0]

    def test_filter_products_by_category(self, api_request_context, test_data, live_server):
        sub_category = test_data["sub_category"]
        response = api_request_context.get(f"{live_server.url}/api/products/?category={sub_category.id}")
        assert response.status == 200
        data = response.json()
        for product in data:
            assert product["category"] == sub_category.id
            assert product["category_name"] == sub_category.name

    def test_create_product(self, api_request_context, test_data, live_server):
        root_category = test_data["root_category"]
        new_product = {
            "name": "MacBook Pro",
            "description": "Apple laptop",
            "price": 199999.00,
            "category": root_category.id,
            "stock": 3,
        }
        response = api_request_context.post(
            f"{live_server.url}/api/products/",
            data=json.dumps(new_product),
            headers={"Content-Type": "application/json"},
        )
        assert response.status == 201
        data = response.json()
        assert data["name"] == "MacBook Pro"
        assert float(data["price"]) == 199999.00
        assert data["stock"] == 3

    def test_create_product_invalid_price(self, api_request_context, test_data, live_server):
        sub_category = test_data["sub_category"]
        invalid_product = {
            "name": "Free Phone",
            "description": "This should fail",
            "price": 0,
            "category": sub_category.id,
            "stock": 1,
        }
        response = api_request_context.post(
            f"{live_server.url}/api/products/",
            data=json.dumps(invalid_product),
            headers={"Content-Type": "application/json"},
        )
        assert response.status == 400
        data = response.json()
        assert "price" in data

    def test_get_product_detail(self, api_request_context, test_data, live_server):
        product1 = test_data["products"][0]
        response = api_request_context.get(f"{live_server.url}/api/products/{product1.id}/")
        assert response.status == 200
        data = response.json()
        assert data["id"] == product1.id

    def test_update_product_stock(self, api_request_context, test_data, live_server):
        product1 = test_data["products"][0]
        update_data = {"stock": 15}
        response = api_request_context.patch(
            f"{live_server.url}/api/products/{product1.id}/",
            data=json.dumps(update_data),
            headers={"Content-Type": "application/json"},
        )
        assert response.status == 200
        assert response.json()["stock"] == 15

    def test_product_not_found(self, api_request_context, live_server):
        response = api_request_context.get(f"{live_server.url}/api/products/999/")
        assert response.status == 404
