from django.db.models import Avg
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

from .models import Category, Order, Product, Customer
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"])
    def average_price(self, request, pk=None):
        category = self.get_object()
        descendant_ids = [category.id]
        queue = [category]
        while queue:
            current_cat = queue.pop(0)
            children = current_cat.children.all()
            for child in children:
                descendant_ids.append(child.id)
                queue.append(child)
        result = Product.objects.filter(category__id__in=descendant_ids).aggregate(
            average_price=Avg("price")
        )
        return Response(result)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]
   
    def perform_create(self, serializer):
        try:
            # Attempt to get customer with ID 1
            customer = Customer.objects.get(id=1)
        except Customer.DoesNotExist:
            # If not found, raise error
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Test customer with ID 1 does not exist. Please create one.")

        serializer.save(customer=customer)
