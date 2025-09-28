from django.db import transaction
from rest_framework import serializers

from .models import Category, Order, OrderItem, Product


class RecursiveCategorySerializer(serializers.Serializer):
    """Serializer for nested children categories."""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with nested children support."""

    children = RecursiveCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "children"]

    def validate_name(self, value):
        """Ensure category name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        return value.strip()


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer with category information."""

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "category", "category_name", "stock"]

    def validate_price(self, value):
        """Ensure price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        """Ensure stock is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for order items with calculated subtotal."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "product_price", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        """Calculate subtotal for this order item."""
        return obj.quantity * obj.product.price


class OrderItemWriteSerializer(serializers.Serializer):
    """Write-only serializer for creating/updating order items."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        """Ensure product exists."""
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"Product with ID {value} does not exist.")
        return value

    def validate_quantity(self, value):
        """Ensure quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer with separate read/write serializers for items."""

    items = OrderItemReadSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)
    customer_email = serializers.CharField(source="customer.user.email", read_only=True)
    products = OrderItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Order
        fields = ["id", "customer", "customer_name", "customer_email", "created_at", "total_amount", "items", "products"]
        read_only_fields = ["id", "customer", "customer_name", "customer_email", "created_at", "total_amount", "items"]

    def validate_products(self, value):
        """Ensure at least one product is provided."""
        if not value:
            raise serializers.ValidationError("Order must contain at least one product.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create order with order items and stock management."""
        products_data = validated_data.pop("products", [])
        order = Order.objects.create(**validated_data)

        for item_data in products_data:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            product.stock -= quantity
            product.save()

        order.update_total_amount()
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update order with stock restoration and new item management."""
        products_data = validated_data.pop("products", [])

        # Restore stock for all existing items
        for existing_item in instance.items.all():
            existing_item.product.stock += existing_item.quantity
            existing_item.product.save()

        # Clear existing items
        instance.items.all().delete()

        # Create new items
        for item_data in products_data:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            OrderItem.objects.create(order=instance, product=product, quantity=quantity)
            product.stock -= quantity
            product.save()

        instance.update_total_amount()
        return instance
