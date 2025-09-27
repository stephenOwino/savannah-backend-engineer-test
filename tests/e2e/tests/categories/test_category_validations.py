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
    )
    def test_invalid_payloads(self, api_request_context, live_server, payload, expected_status):
        resp = api_request_context.post(
            f"{live_server.url}/api/categories/",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == expected_status

    def test_duplicate_name(self, api_request_context, live_server, test_data):
        dup_payload = {"name": test_data["root_category"].name}
        resp = api_request_context.post(
            f"{live_server.url}/api/categories/",
            data=json.dumps(dup_payload),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400
