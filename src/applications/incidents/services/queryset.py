from applications.incidents.models import Incident
from applications.users.models import Role


def get_incident_queryset(requester, take_all=False):
    tenant = requester.tenant
    if requester.role == Role.ADMIN and take_all:
        queryset = Incident.objects.filter(tenant=tenant)
    else:
        queryset = Incident.objects.filter(owner=requester)
    return queryset
