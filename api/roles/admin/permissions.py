from rest_framework import permissions
from api.utils import Role


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN
