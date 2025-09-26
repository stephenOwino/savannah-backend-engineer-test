# Standard library imports
import json
import logging

# Django imports
from django.db import transaction
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt

# Third-party imports
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Local application imports
from . import notifications
from .models import Category, Customer, Order, OrderItem, Product
from .permissions import IsCustomerOrReadOnly, IsOwnerOrReadOnly
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Categories API:
    - Public read access (anyone can view categories)
    - Write access requires customer authentication
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsCustomerOrReadOnly]

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def average_price(self, request, pk=None):
        """Calculate average price for products in this category (including all descendant categories)"""
        category = self.get_object()
        descendant_ids = category.get_all_descendant_ids()
        avg_price = (
            Product.objects.filter(category__id__in=descendant_ids)
            .aggregate(average_price=Avg("price"))
            .get("average_price")
        )
        return Response(
            {"category": category.name, "average_price": float(avg_price or 0)}
        )


class ProductViewSet(viewsets.ModelViewSet):
    """
    Products API:
    - Public read access (anyone can view products)
    - Write access requires customer authentication
    """

    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [IsCustomerOrReadOnly]

    def get_queryset(self):
        """Filter products by category if requested"""
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    """
    Orders API:
    - Requires authentication
    - Users can only access their own orders
    - Automatic stock management and notifications
    """

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_customer(self, user):
        """Get or create customer profile for authenticated user"""
        customer, created = Customer.objects.get_or_create(
            user=user, defaults={"phone_number": "", "address": ""}
        )
        return customer

    def get_queryset(self):
        """Return only orders belonging to the authenticated user"""
        if self.request.user.is_anonymous:
            return Order.objects.none()
        customer = self.get_customer(self.request.user)
        return self.queryset.filter(customer=customer)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create order with stock validation and notifications.
        Process:
        1. Validate request data
        2. Check product availability and stock
        3. Create order and order items
        4. Update product stock
        5. Send notifications
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
        product_ids = [item["product_id"] for item in products_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        for item in products_data:
            product_id = item["product_id"]
            quantity = item["quantity"]
            product = products.get(product_id)
            if not product:
                return Response(
                    {"error": f"Product with ID {product_id} not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not product.has_sufficient_stock(quantity):
                return Response(
                    {
                        "error": f"Insufficient stock for {product.name}. "
                        f"Requested: {quantity}, Available: {product.stock}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        order = Order.objects.create(customer=customer)
        for item in products_data:
            product = products[item["product_id"]]
            quantity = item["quantity"]
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            product.stock -= quantity
            product.save()
        order.update_total_amount()
        try:
            notifications.send_order_confirmation_sms(order)
            notifications.send_new_order_admin_email(order)
        except Exception as e:
            logger.warning(f"Notification failed for order {order.id}: {e}")
        response_serializer = self.get_serializer(order)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@csrf_exempt  # For demo simplicity; remove in production with proper CSRF
def order_form_view(request):
    """Handle order creation via a simple form submission"""
    if request.method == "POST":
        products_data = request.POST.get("products")
        try:
            products = json.loads(products_data)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON data for products"}, status=400)
        serializer = OrderSerializer(
            data={"products": products}, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(customer=request.user.customer)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    return Response({"error": "Method not allowed"}, status=405)
