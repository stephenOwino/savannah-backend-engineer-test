# Standard library imports
import logging

# Django imports
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.contrib.auth.decorators import login_required

# Local application imports
logger = logging.getLogger(__name__)


@login_required
def api_landing(request):
    """Landing page for authenticated users"""
    return JsonResponse(
        {
            "message": "Welcome to Savannah Assess API",
            "authenticated": True,
            "user": {"username": request.user.username, "email": request.user.email},
            "next_steps": [
                "View orders at /api/orders/",
                "Create order at /api/order_form/",
            ],
        }
    )


def api_root(request):
    """API root with basic info"""
    return JsonResponse(
        {
            "message": "Savannah Assess API",
            "version": "1.0.0",
            "authenticated": request.user.is_authenticated,
            "user": (
                {
                    "username": request.user.username,
                    "email": request.user.email,
                }
                if request.user.is_authenticated
                else None
            ),
            "endpoints": {
                "categories": "/api/categories/",
                "products": "/api/products/",
                "orders": "/api/orders/",
                "admin": "/admin/",
                "order_form": "/api/order_form/",
            },
            "auth": {
                "login": "/oidc/authenticate/",
                "callback": "/oidc/callback/",
                "logout": "/oidc/logout/",
            },
            "docs": {
                "description": "Authenticated via OpenID Connect (Auth0). Use Bearer token for APIs.",
            },
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", api_root, name="api-root"),
    path("api/landing/", api_landing, name="api-landing"),
]
