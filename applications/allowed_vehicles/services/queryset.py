from django.db.models import Case, When

from applications.users.models import Role
from applications.vehicles.services.queryset import get_vehicles_queryset


def get_allowed_vehicles_queryset(user, even_disabled=False):
    if user.role == Role.USER:
        return user.allowed_vehicles.filter(tenant=user.tenant)
    else:
        if even_disabled:
            return get_vehicles_queryset(user)
        else:
            return get_vehicles_queryset(user).filter(is_disabled=False)


def get_vehicles_ordered_by_ids(ids, user):
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    queryset_vehicles = get_allowed_vehicles_queryset(user)
    vehicles = queryset_vehicles.filter(id__in=ids).order_by(preserved).all()
    return vehicles
