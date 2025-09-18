from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, OrderViewSet, ProductViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"products", ProductViewSet)
router.register(r"orders", OrderViewSet)

# MY above API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
