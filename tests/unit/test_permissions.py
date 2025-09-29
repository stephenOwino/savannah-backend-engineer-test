import pytest
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User, AnonymousUser
from api.permissions import IsCustomerOrReadOnly, IsOwnerOrReadOnly
from api.models import Customer, Order


@pytest.mark.django_db
class TestIsCustomerOrReadOnly:
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsCustomerOrReadOnly()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.customer = Customer.objects.create(user=self.user, phone_number='+254712345678', address='Test')

    def test_anonymous_user_can_read(self):
        request = self.factory.get('/api/products/')
        request.user = AnonymousUser()
        assert self.permission.has_permission(request, None) is True

    def test_authenticated_customer_can_write(self):
        request = self.factory.post('/api/products/')
        request.user = self.user
        assert self.permission.has_permission(request, None) is True

    def test_authenticated_non_customer_cannot_write(self):
        user_no_customer = User.objects.create_user(username='nocustomer', password='pass')
        Customer.objects.filter(user=user_no_customer).delete()
        request = self.factory.post('/api/products/')
        request.user = user_no_customer
        assert self.permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsOwnerOrReadOnly:
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsOwnerOrReadOnly()
        self.user = User.objects.create_user(username='owner', password='pass')
        self.customer = Customer.objects.create(user=self.user, phone_number='+254712345678', address='Test')
        self.order = Order.objects.create(customer=self.customer)

    def test_owner_can_read_own_order(self):
        request = self.factory.get(f'/api/orders/{self.order.id}/')
        request.user = self.user
        assert self.permission.has_object_permission(request, None, self.order) is True

    def test_other_user_cannot_write_order(self):
        other_user = User.objects.create_user(username='other', password='pass')
        request = self.factory.put(f'/api/orders/{self.order.id}/')
        request.user = other_user
        assert self.permission.has_object_permission(request, None, self.order) is False