# api/serializers.py
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock']

# This serializer is for creating an order
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'created_at', 'products', 'total_amount']
        read_only_fields = ['customer', 'total_amount']

    def create(self, validated_data):
        # Get the product data from the request
        products_data = validated_data.pop('products')

        # Create the main order object
        order = Order.objects.create(**validated_data)

        # Create an OrderItem for each product in the request
        total = 0
        for product_data in products_data:
            order_item = OrderItem.objects.create(order=order, **product_data)
            total += order_item.product.price * order_item.quantity

        # Save the calculated total price
        order.total_amount = total
        order.save()

        return order