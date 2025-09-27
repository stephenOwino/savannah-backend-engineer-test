from rest_framework import serializers

from .models import Category, Order, OrderItem, Product


class RecursiveCategorySerializer(serializers.Serializer):
    """Serializer for nested children categories."""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "children"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "stock",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Serializer for reading order items."""

    product_name = serializers.CharField(source="product.name")
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "subtotal"]


class OrderItemWriteSerializer(serializers.Serializer):
    """Serializer for writing (creating) order items."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    # For reading order details
    items = OrderItemReadSerializer(source="orderitem_set", many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)

    # For creating an order
    products = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "created_at",
            "total_amount",
            "items",
            "products",
        ]

        read_only_fields = [
            "id",
            "customer",
            "customer_name",
            "created_at",
            "total_amount",
            "items",
        ]
