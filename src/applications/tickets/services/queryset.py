from applications.tickets.models import Ticket
from applications.users.models import Role


def get_ticket_queryset(requester, take_all):
    tenant = requester.tenant
    if requester.role == Role.ADMIN and take_all:
        queryset = Ticket.objects.filter(tenant=tenant)
    else:
        queryset = requester.tickets.all()
    return queryset
