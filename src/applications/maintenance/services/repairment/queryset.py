from applications.maintenance.models import Repairment
from applications.users.models import Role, User


def get_repairment_queryset(requester: User, vehicle_id: str = None):
    tenant = requester.tenant

    # If requester is USER, return all repairments except completed
    if requester.role == Role.USER:
        queryset = Repairment.objects.filter(tenant=tenant, owner=requester)
    else:
        # If requester is ADMIN
        queryset = Repairment.objects.filter(tenant=tenant)

    if vehicle_id:
        queryset = queryset.filter(vehicle_id=vehicle_id)
    return queryset
