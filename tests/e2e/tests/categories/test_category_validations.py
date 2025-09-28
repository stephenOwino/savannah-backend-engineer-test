import json

import pytest


@pytest.mark.api
class TestCategoryValidations:
    """Validation rules for categories."""

    @pytest.mark.parametrize(
        "payload,expected_status",
        [
            ({"name": ""}, 400),  # Empty name
            ({"parent": 9999, "name": "Invalid Parent"}, 400),  # Bad parent
        ],
        ids=["empty_name", "invalid_parent"],
    )
    def test_invalid_payloads(self, api_request_context, payload, expected_status):
        """Test various invalid category payloads."""
        resp = api_request_context.post(
            "/api/categories/",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == expected_status

        # Validate error response structure
        error_data = resp.json()
        assert isinstance(error_data, dict)
        # Should have field-specific errors or general error message
        assert len(error_data) > 0

    def test_duplicate_name(self, api_request_context, test_data):
        """Test creating category with duplicate name."""
        dup_payload = {"name": test_data["root_category"].name}
        resp = api_request_context.post(
            "/api/categories/",
            data=json.dumps(dup_payload),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400

        # Validate error response
        error_data = resp.json()
        assert "name" in error_data
        assert isinstance(error_data["name"], list)
        assert len(error_data["name"]) > 0
