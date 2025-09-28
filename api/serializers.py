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
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price


class OrderItemWriteSerializer(serializers.Serializer):
    """Serializer for writing (creating/updating) order items."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer for read/write operations."""

    items = OrderItemReadSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)
    products = OrderItemWriteSerializer(many=True, write_only=True, required=False)

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

    def create(self, validated_data):
        products_data = validated_data.pop("products", [])
        order = Order.objects.create(**validated_data)
        for item in products_data:
            product = Product.objects.get(id=item["product_id"])
            quantity = item["quantity"]
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            product.stock -= quantity
            product.save()
        order.update_total_amount()
        order.save()
        return order

    def update(self, instance, validated_data):  # FIX: now inside class
        products_data = validated_data.pop("products", [])

        for item_data in products_data:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            # Check if product already exists in the order
            order_item = instance.items.filter(product=product).first()
            if order_item:
                # Restore old stock, then apply new quantity
                product.stock += order_item.quantity
                product.save()

                order_item.quantity = quantity
                order_item.save()

                product.stock -= quantity
                product.save()
            else:
                # Create new order item
                OrderItem.objects.create(order=instance, product=product, quantity=quantity)
                product.stock -= quantity
                product.save()

        instance.update_total_amount()
        instance.save()
        return instance
