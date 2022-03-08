from rest_framework import permissions

from applications.users.models import Role


class IsOwnerReservationOrAdmin(permissions.BasePermission):
    """
    This class gives permission to the owner of a reservation.

    If requester is admin. It returns True, so he will have access.
    """

    def has_permission(self, request, view):
        requester = request.user
        if requester.role == Role.ADMIN:
            return True
        reservations = requester.reservations.all()
        return reservations.filter(id=request.data['reservation']).exists()


class IsOwnerOrSuperuser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or bool(request.user and request.user.is_superuser)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN


class IsVehicleAllowedOrAdmin(permissions.BasePermission):
    """
    Use this class when you have to restrict people create a reservation of a vehicle.
    This permission takes in count allowed vehicles types.
    So a user can't reserve a vehicle not allowed to him.

    If requester is admin. It returns True, so he will have access.
    """

    def has_permission(self, request, view):
        requester = request.user
        if requester.role == Role.ADMIN:
            return True

        vehicles = requester.allowed_vehicles.all()
        # request.data['vehicle'] contains the vehicle id.
        return vehicles.filter(id=request.data['vehicle']).exists()


class IsNotDisabled(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_disabled


ONLY_ADMIN = [permissions.IsAuthenticated, IsAdmin]
ONLY_AUTHENTICATED = [permissions.IsAuthenticated, IsNotDisabled]
ALLOW_UNAUTHENTICATED = [permissions.AllowAny]
