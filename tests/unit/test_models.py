# tests/unit/test_models.py
from decimal import Decimal

import pytest

from api.models import Customer
from tests.factories.factories import UserFactory
from tests.factories.factories import ProductFactory, OrderItemFactory



@pytest.mark.django_db
def test_customer_signal_creates_customer():
    user = UserFactory()
    assert Customer.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_product_has_sufficient_stock():
    product = ProductFactory(stock=5)
    assert product.has_sufficient_stock(3) is True
    assert product.has_sufficient_stock(10) is False


@pytest.mark.django_db
def test_order_item_subtotal_and_order_total():
    order_item = OrderItemFactory(quantity=2, product__price=Decimal("15.00"))
    assert order_item.subtotal == Decimal("30.00")
    total = order_item.order.update_total_amount()
    assert total == Decimal("30.00")
    assert order_item.order.total_amount == Decimal("30.00")
