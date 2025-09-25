import pytest
import json
from playwright.sync_api import APIRequestContext

@pytest.mark.api
class TestCategoriesAPI:
    """Categories API tests."""

    def test_list_categories(self, api_request_context, live_server, test_data):
        response = api_request_context.get(f"{live_server.url}/api/categories/")
        assert response.status == 200
        data = response.json()
        assert isinstance(data, list)

        # Ensure root and sub-category exist
        category_ids = [c["id"] for c in data]
        assert test_data["root_category"].id in category_ids
        assert test_data["sub_category"].id in category_ids

    def test_create_category(self, api_request_context, live_server, test_data):
        new_category = {
            "name": "Laptops",
            "parent": test_data["root_category"].id
        }
        response = api_request_context.post(
            f"{live_server.url}/api/categories/",
            data=json.dumps(new_category),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 201
        data = response.json()
        assert data["name"] == "Laptops"
        assert data["parent"] == test_data["root_category"].id

    def test_category_not_found(self, api_request_context, live_server):
        response = api_request_context.get(f"{live_server.url}/api/categories/999/")
        assert response.status == 404
