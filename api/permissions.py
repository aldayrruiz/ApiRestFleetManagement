from rest_framework import permissions
from api.models import *
from api.utils import Role


def get_allowed_vehicles(user):
    """
    Returns a queryset of vehicles the user has access.
    :param user: user model instance.
    :return: a queryset of vehicles the user have access.
    """
    allowed_types = user.allowed_types.all().values('id')
    return Vehicle.objects.filter(type__in=allowed_types)


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
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user


class IsVehicleAccessibleOrAdmin(permissions.BasePermission):
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

        vehicles = get_allowed_vehicles(requester)
        # request.data['vehicle'] contains the vehicle id.
        return vehicles.filter(id=request.data['vehicle']).exists()


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


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN
