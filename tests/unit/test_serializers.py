# tests/unit/test_serializers.py
import pytest

from api.serializers import CategorySerializer, OrderItemWriteSerializer, ProductSerializer
from tests.factories import CategoryFactory


@pytest.mark.django_db
def test_category_serializer_children():
    parent = CategoryFactory()
    CategoryFactory(parent=parent)
    serializer = CategorySerializer(parent)
    data = serializer.data
    assert data["name"] == parent.name
    assert len(data["children"]) == 1


@pytest.mark.django_db
def test_product_serializer_validation():
    category = CategoryFactory()
    serializer = ProductSerializer(data={"name": "Book", "description": "desc", "price": 10, "category": category.id, "stock": 5})
    assert serializer.is_valid()

    serializer2 = ProductSerializer(data={"name": "Book", "description": "desc", "price": 0, "category": category.id, "stock": 5})
    assert not serializer2.is_valid()
    assert "Price must be greater than zero." in str(serializer2.errors)


@pytest.mark.django_db
def test_order_item_write_serializer_validation():
    serializer = OrderItemWriteSerializer(data={"product_id": 1, "quantity": 0})
    assert not serializer.is_valid()
    assert "Quantity must be greater than zero." in str(serializer.errors)
