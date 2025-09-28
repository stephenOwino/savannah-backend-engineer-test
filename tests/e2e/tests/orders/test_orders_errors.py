import pytest
from playwright.sync_api import APIRequestContext

pytestmark = pytest.mark.order


def test_get_nonexistent_order(api_request_context: APIRequestContext):
    """Test retrieving a non-existent order returns 404."""
    response = api_request_context.get("/api/orders/999999/")
    assert response.status == 404

    error_data = response.json()
    assert "detail" in error_data


def test_create_order_with_invalid_payload(api_request_context: APIRequestContext):
    """Test order creation with invalid payload structure."""
    response = api_request_context.post("/api/orders/", data='{"invalid": "data"}', headers={"Content-Type": "application/json"})
    assert response.status == 400

    error_data = response.json()
    assert isinstance(error_data, dict)
