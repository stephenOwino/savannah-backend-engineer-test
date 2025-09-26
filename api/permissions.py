from rest_framework import permissions


class IsCustomerOrReadOnly(permissions.BasePermission):
    """
    Allow read access to everyone, write access only to authenticated customers.

    Use case: Categories and Products should be readable by all,
    but only customers can create/modify them.
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication and Customer profile for writes
        return request.user.is_authenticated and hasattr(request.user, "customer")

    def has_object_permission(self, request, view, obj):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication and Customer profile for writes
        return request.user.is_authenticated and hasattr(request.user, "customer")


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read access to authenticated users, write access only to object owner.

    Use case: Orders should only be readable/writable by the customer who owns them.
    """

    def has_permission(self, request, view):
        # Require authentication for all order operations
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions only for owner
        if hasattr(obj, "customer"):
            return obj.customer.user == request.user

        return False
