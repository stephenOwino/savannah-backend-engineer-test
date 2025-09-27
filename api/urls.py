# Django imports
from django.urls import include, path
# Third-party imports
from rest_framework.routers import DefaultRouter

# Local application imports
from .views import (CategoryViewSet, OrderViewSet, ProductViewSet,
                    order_form_view)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path("order_form/", order_form_view, name="order_form"),
]
