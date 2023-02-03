from applications.maintenance.models import Revision
from applications.users.models import Role, User


def get_revision_queryset(requester: User, vehicle_id: str = None):
    tenant = requester.tenant

    # If requester is USER, return all revisions except completed
    if requester.role == Role.USER:
        queryset = Revision.objects.filter(tenant=tenant, owner=requester)

    # If requester is ADMIN
    else:
        queryset = Revision.objects.filter(tenant=tenant)

    if vehicle_id:
        queryset = queryset.filter(vehicle_id=vehicle_id)

    return queryset
