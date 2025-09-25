import pytest


@pytest.mark.api
class TestListCategories:
    """Tests for listing and retrieving categories."""

    def test_list_categories(self, api_request_context, live_server, test_data):
        response = api_request_context.get(f"{live_server.url}/api/categories/")
        assert response.status == 200
        data = response.json()

        assert isinstance(data, list)
        category_ids = [c["id"] for c in data]
        assert test_data["root_category"].id in category_ids
        assert test_data["sub_category"].id in category_ids

    def test_get_category_detail(self, api_request_context, live_server, test_data):
        root_id = test_data["root_category"].id
        response = api_request_context.get(
            f"{live_server.url}/api/categories/{root_id}/"
        )
        assert response.status == 200
        data = response.json()

        assert data["id"] == root_id
        assert data["name"] == test_data["root_category"].name
        assert "children" in data
