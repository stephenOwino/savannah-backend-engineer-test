import pytest


@pytest.mark.api
class TestListCategories:
    """Tests for listing and retrieving categories."""

    def test_list_categories(self, api_request_context, test_data):
        """Test listing all categories."""
        response = api_request_context.get("/api/categories/")
        assert response.status == 200
        data = response.json()

        assert isinstance(data, list)
        category_ids = [c["id"] for c in data]
        assert test_data["root_category"].id in category_ids
        assert test_data["sub_category"].id in category_ids

        # Validate category structure
        for category in data:
            required_fields = ["id", "name", "parent", "children"]
            for field in required_fields:
                assert field in category

    def test_get_category_detail(self, api_request_context, test_data):
        """Test retrieving a specific category."""
        root_id = test_data["root_category"].id
        response = api_request_context.get(f"/api/categories/{root_id}/")
        assert response.status == 200
        data = response.json()

        assert data["id"] == root_id
        assert data["name"] == test_data["root_category"].name
        assert "children" in data
        assert isinstance(data["children"], list)

        # Validate complete category structure
        required_fields = ["id", "name", "parent", "children"]
        for field in required_fields:
            assert field in data
