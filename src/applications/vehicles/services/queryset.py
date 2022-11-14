from applications.users.models import User, Role
from applications.vehicles.models import Vehicle


def get_vehicles_queryset(requester: User, even_disabled=False, even_deleted=False):
    """
    Return the queryset of vehicles given user (tenant)
    """
    tenant = requester.tenant

    if requester.role == Role.USER:
        # If requester is USER, return all vehicles except disabled and deleted
        queryset = requester.allowed_vehicles.filter(tenant=tenant, is_disabled=False, is_deleted=False)
        return queryset

    # If requester is ADMIN
    if even_deleted and even_disabled:
        # Wants to see all vehicles (even disabled and deleted)
        queryset = Vehicle.objects.filter(tenant=tenant)
        return queryset
    elif even_disabled:
        # Wants to see all vehicles (even disabled)
        queryset = Vehicle.objects.filter(tenant=tenant, is_deleted=False)
        return queryset
    else:
        # Wants to see only available vehicles
        queryset = Vehicle.objects.filter(tenant=tenant, is_disabled=False, is_deleted=False)
        return queryset
