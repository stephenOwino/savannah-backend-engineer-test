import pytest


@pytest.mark.api
class TestCategoryCustomActions:
    """Custom endpoints like average_price and not found errors."""

    def test_average_price_action(self, api_request_context, live_server, test_data):
        resp = api_request_context.get(f"{live_server.url}/api/categories/{test_data['root_category'].id}/average_price/")
        assert resp.status == 200
        data = resp.json()
        assert "average_price" in data
        assert data["average_price"] > 0

    def test_not_found_errors(self, api_request_context, live_server):
        resp = api_request_context.get(f"{live_server.url}/api/categories/999/")
        assert resp.status == 404

        resp = api_request_context.get(f"{live_server.url}/api/categories/999/average_price/")
        assert resp.status == 404
