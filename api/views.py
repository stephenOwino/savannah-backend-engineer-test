from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg

from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'])
    def average_price(self, request, pk=None):
        """
        Returns the average product price for this category,
        including all its sub-categories.
        """
        category = self.get_object()

        # Find all descendant category IDs
        descendant_ids = [category.id]
        queue = [category]
        while queue:
            current_cat = queue.pop(0)
            children = current_cat.children.all()
            for child in children:
                descendant_ids.append(child.id)
                queue.append(child)

        # Calculate the average price for products in these categories
        result = Product.objects.filter(
            category__id__in=descendant_ids
        ).aggregate(average_price=Avg('price'))

        return Response(result)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        
        pass 
