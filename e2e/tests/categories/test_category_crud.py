import json

import pytest


@pytest.mark.api
class TestCategoryCRUD:
    """CRUD operations for categories."""

    def test_create_root_and_child(self, api_request_context, live_server):
        # Root category
        root_payload = {"name": "Home & Garden"}
        root_resp = api_request_context.post(
            f"{live_server.url}/api/categories/",
            data=json.dumps(root_payload),
            headers={"Content-Type": "application/json"},
        )
        assert root_resp.status == 201
        root_data = root_resp.json()
        assert root_data["name"] == "Home & Garden"
        assert root_data["parent"] is None

        # Child category
        child_payload = {"name": "Tools", "parent": root_data["id"]}
        child_resp = api_request_context.post(
            f"{live_server.url}/api/categories/",
            data=json.dumps(child_payload),
            headers={"Content-Type": "application/json"},
        )
        assert child_resp.status == 201
        assert child_resp.json()["parent"] == root_data["id"]

    def test_update_category(self, api_request_context, live_server, test_data):
        update_data = {"name": "Updated Electronics"}
        resp = api_request_context.patch(
            f"{live_server.url}/api/categories/{test_data['root_category'].id}/",
            data=json.dumps(update_data),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200
        assert resp.json()["name"] == "Updated Electronics"

    def test_delete_category(self, api_request_context, live_server, test_data):
        sub_id = test_data["sub_category"].id
        resp = api_request_context.delete(f"{live_server.url}/api/categories/{sub_id}/")
        assert resp.status == 204

        get_resp = api_request_context.get(
            f"{live_server.url}/api/categories/{sub_id}/"
        )
        assert get_resp.status == 404
