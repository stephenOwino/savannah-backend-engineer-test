from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import notifications
from .models import Category, Customer, Order, OrderItem, Product
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        # Return ALL categories, not just root categories
        queryset = self.get_queryset()  # Remove the .filter(parent=None)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def average_price(self, request, pk=None):
        # Return the average price for all products in a category (including children).
        category = self.get_object()
        descendant_ids = [category.id] + list(
            category.children.values_list("id", flat=True)
        )

        result = (
            Product.objects.filter(category__id__in=descendant_ids)
            .aggregate(average_price=Avg("price"))
            .get("average_price")
        )

        return Response({"average_price": result or 0})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Filter products by category if ?category=<id> is provided.
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_customer(self, user):
        if not user or user.is_anonymous:
            return Customer.objects.first()
        return get_object_or_404(Customer, user=user)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset
        customer = self.get_customer(self.request.user)
        return self.queryset.filter(customer=customer)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create an order:
        - Validate stock
        - Deduct stock
        - Save items + total
        - Trigger notifications
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        products_data = serializer.validated_data.get("products", [])
        if not products_data:
            return Response(
                {"error": "Order must contain at least one product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = self.get_customer(request.user)

        # Preload all products to reduce queries
        product_ids = [item["product_id"] for item in products_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        # 1. Validate stock
        for item in products_data:
            product = products.get(item["product_id"])
            if not product:
                return Response(
                    {"error": f"Product with id {item['product_id']} not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not product.has_sufficient_stock(item["quantity"]):
                return Response(
                    {
                        "error": f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 2. Create order
        order = Order.objects.create(customer=customer)

        total = 0
        for item in products_data:
            product = products[item["product_id"]]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
            )
            product.stock -= item["quantity"]
            product.save()
            total += product.price * item["quantity"]

        # 3. Save total
        order.total_amount = total
        order.save()

        # 4. Notifications (can be async)
        notifications.send_order_confirmation_sms(order)
        notifications.send_new_order_admin_email(order)

        # 5. Return created order
        response_serializer = self.get_serializer(order)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # Update an order:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        products_data = serializer.validated_data.pop("products", None)

        # Update base fields
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)

        if products_data is not None:
            # Restore stock from old items
            for item in instance.items.all():
                item.product.stock += item.quantity
                item.product.save()
            instance.items.all().delete()

            # Preload new products
            product_ids = [item["product_id"] for item in products_data]
            products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

            total = 0
            for item in products_data:
                product = products[item["product_id"]]
                if not product.has_sufficient_stock(item["quantity"]):
                    return Response(
                        {
                            "error": f"Insufficient stock for {product.name}. "
                            f"Available: {product.stock}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                OrderItem.objects.create(
                    order=instance,
                    product=product,
                    quantity=item["quantity"],
                )
                product.stock -= item["quantity"]
                product.save()
                total += product.price * item["quantity"]

            instance.total_amount = total

        instance.save()
        return Response(self.get_serializer(instance).data)
