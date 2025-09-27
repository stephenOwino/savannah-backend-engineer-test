# import os
# import time

# import pytest
# from playwright.sync_api import APIRequestContext, expect

# # --- Configuration ---
# BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8888/api")
# TEST_USER_AUTH_TOKEN = os.getenv("E2E_AUTH_TOKEN", "PASTE_YOUR_OIDC_BEARER_TOKEN_HERE")

# UNIQUE_SUFFIX = str(int(time.time()))


# @pytest.fixture(scope="session")
# def api_auth_headers() -> dict:
#     """Provide authentication headers for all tests."""
#     if not TEST_USER_AUTH_TOKEN or "PASTE" in TEST_USER_AUTH_TOKEN:
#         pytest.fail(
#             "ERROR: E2E_AUTH_TOKEN environment variable is not set. "
#             "Please provide a valid OIDC Bearer token to run the E2E tests."
#         )
#     return {"Authorization": f"Bearer {TEST_USER_AUTH_TOKEN}"}


# def create_resource(
#     api_request_context: APIRequestContext,
#     endpoint: str,
#     payload: dict,
#     headers: dict,
# ) -> int:
#     """Helper to POST a new resource and return its ID."""
#     response = api_request_context.post(
#         f"{BASE_URL}/{endpoint}/", headers=headers, data=payload
#     )
#     expect(response).to_be_ok()
#     response_json = response.json()
#     assert "id" in response_json
#     return response_json["id"]


# def test_full_user_journey(
#     api_request_context: APIRequestContext, api_auth_headers: dict
# ):
#     """Simulate a user journey: create categories/products, place order, verify outcomes."""

#     # --- Arrange ---
#     parent_cat_id = create_resource(
#         api_request_context,
#         "categories",
#         {"name": f"E2E Produce_{UNIQUE_SUFFIX}", "parent": None},
#         api_auth_headers,
#     )

#     child_cat_id = create_resource(
#         api_request_context,
#         "categories",
#         {"name": f"E2E Fruits_{UNIQUE_SUFFIX}", "parent": parent_cat_id},
#         api_auth_headers,
#     )

#     product_id = create_resource(
#         api_request_context,
#         "products",
#         {
#             "name": f"E2E Banana_{UNIQUE_SUFFIX}",
#             "price": "50.00",
#             "category": child_cat_id,
#             "stock": 100,
#         },
#         api_auth_headers,
#     )

#     # --- Act ---
#     order_quantity = 5
#     order_payload = {
#         "products": [{"product_id": product_id, "quantity": order_quantity}]
#     }

#     order_res = api_request_context.post(
#         f"{BASE_URL}/orders/", headers=api_auth_headers, data=order_payload
#     )
#     expect(order_res).to_be_ok()
#     order = order_res.json()
#     order_id = order["id"]

#     # --- Assert ---
#     # 1. Order appears in history
#     orders_list_res = api_request_context.get(
#         f"{BASE_URL}/orders/", headers=api_auth_headers
#     )
#     expect(orders_list_res).to_be_ok()
#     assert any(o["id"] == order_id for o in orders_list_res.json())

#     # 2. Total amount matches
#     expected_total = 50.00 * order_quantity
#     actual_total = float(order["total_amount"])
#     assert actual_total == expected_total

#     # 3. Stock deduction is correct
#     product_res = api_request_context.get(
#         f"{BASE_URL}/products/{product_id}/", headers=api_auth_headers
#     )
#     expect(product_res).to_be_ok()
#     expected_stock = 100 - order_quantity
#     actual_stock = product_res.json()["stock"]
#     assert actual_stock == expected_stock, (
#         f"Stock deduction incorrect! " f"Expected {expected_stock}, got {actual_stock}"
#     )
