# import pytest
# from django.contrib.auth.models import AnonymousUser, User

# from api.models import Order
# from api.permissions import IsCustomerOrReadOnly, IsOwnerOrReadOnly


# @pytest.mark.django_db
# class TestIsCustomerOrReadOnly:

#     def test_anonymous_user_can_read(self, api_factory):
#         permission = IsCustomerOrReadOnly()
#         request = api_factory.get("/api/products/")
#         request.user = AnonymousUser()
#         assert permission.has_permission(request, None) is True

#     def test_authenticated_customer_can_write(self, api_factory, sample_user, sample_customer):
#         permission = IsCustomerOrReadOnly()
#         request = api_factory.post("/api/products/")
#         request.user = sample_user
#         assert permission.has_permission(request, None) is True

#     def test_authenticated_non_customer_cannot_write(self, api_factory):
#         permission = IsCustomerOrReadOnly()
#         # Create a user without a customer
#         user_no_customer = User.objects.create_user(username="nocustomer", password="pass")
#         request = api_factory.post("/api/products/")
#         request.user = user_no_customer
#         assert permission.has_permission(request, None) is False


# @pytest.mark.django_db
# class TestIsOwnerOrReadOnly:

#     def test_owner_can_read_own_order(self, api_factory, sample_customer):
#         permission = IsOwnerOrReadOnly()
#         order = Order.objects.create(customer=sample_customer)
#         request = api_factory.get(f"/api/orders/{order.id}/")
#         request.user = sample_customer.user
#         assert permission.has_object_permission(request, None, order) is True

#     def test_other_user_cannot_write_order(self, api_factory, sample_customer):
#         permission = IsOwnerOrReadOnly()
#         order = Order.objects.create(customer=sample_customer)
#         other_user = User.objects.create_user(username="other", password="pass")
#         request = api_factory.put(f"/api/orders/{order.id}/")
#         request.user = other_user
#         assert permission.has_object_permission(request, None, order) is False
