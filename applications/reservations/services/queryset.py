from applications.reservations.models import Reservation
from applications.users.models import Role


def get_reservation_queryset(requester, take_all=False, vehicle_id=None, _from=None, _to=None):
    tenant = requester.tenant
    if requester.role == Role.ADMIN and take_all:
        # For admin web - All reservations
        queryset = Reservation.objects.filter(tenant=tenant)
    else:
        # For mobile (Users or Admins) - All reservations made by requester
        # Filter by tenant is not needed because of own requester
        queryset = requester.reservations.all()

    if vehicle_id:
        # If reservations of vehicle is specified
        queryset = Reservation.objects.filter(tenant=tenant, vehicle_id=vehicle_id)

    if _from and _to:
        # Not needed, but useful in future
        queryset = queryset.filter(start__gte=_from, start__lte=_to)
    return queryset
