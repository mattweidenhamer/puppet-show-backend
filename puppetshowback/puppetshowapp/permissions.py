from rest_framework import permissions
from rest_framework.authtoken.models import Token


class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Get the token from the request, and then get the user from the token
        token = request.auth
        user = Token.objects.get(key=token).user
        if user == obj.get_owner:
            return True


class UserIsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Get the token from the request, and then get the user from the token
        token = request.auth
        user = Token.objects.get(key=token).user
        if user == obj:
            return True


class HasValidToken(permissions.BasePermission):
    def has_permission(self, request, view):
        # Get the token from the request, and then get the user from the token
        token = request.auth
        if token is None:
            return False
        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return False
        return True
