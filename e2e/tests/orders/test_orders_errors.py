import pytest
from playwright.sync_api import APIRequestContext

pytestmark = pytest.mark.order


def test_get_nonexistent_order(api_request_context: APIRequestContext):
    response = api_request_context.get("/api/orders/999999/")
    assert response.status == 404


def test_create_order_with_invalid_payload(api_request_context: APIRequestContext):
    response = api_request_context.post("/api/orders/", data={"invalid": "data"})
    assert response.status == 400
