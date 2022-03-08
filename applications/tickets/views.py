import logging

from rest_framework import permissions, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK

from applications.reservations.exceptions.already_started import ReservationAlreadyStarted
from applications.reservations.services.timer import reservation_already_started
from applications.tickets.serializers.create import CreateTicketSerializer
from applications.tickets.serializers.simple import SimpleTicketSerializer
from applications.tickets.services.queryset import get_ticket_queryset
from applications.tickets.services.solver import solve_ticket
from applications.tickets.services.validators import check_if_not_mine
from applications.users.services.search import get_admin
from shared.permissions import IsNotDisabled, IsAdmin, ONLY_AUTHENTICATED, ONLY_ADMIN
from utils.api.query import query_bool
from utils.email.tickets.created import send_created_ticket_email

logger = logging.getLogger(__name__)


class TicketViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        When take_all is True and requester is admin, it will return all tickets.
        Otherwise, it will return only the requester tickets.
        :param request:
        :return:
        """
        take_all = query_bool(self.request, 'takeAll')
        logger.info('List tickets request received. [takeAll: {}]'.format(take_all))
        requester = self.request.user
        queryset = get_ticket_queryset(requester, take_all)
        serializer = SimpleTicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('Create ticket request received.')
        requester = self.request.user
        tenant = requester.tenant
        serializer = CreateTicketSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        reservation = serializer.validated_data['reservation']
        check_if_not_mine(requester, reservation)

        if reservation_already_started(reservation):
            raise ReservationAlreadyStarted()

        # Create Ticket and send email to admin
        ticket = serializer.save(owner=requester, tenant=tenant)
        admin = get_admin(tenant)
        send_created_ticket_email(admin, ticket)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        logger.info('Retrieve ticket request received.')
        requester = self.request.user
        queryset = get_ticket_queryset(requester, take_all=True)
        ticket = get_object_or_404(queryset, pk=pk)
        serializer = SimpleTicketSerializer(ticket)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        logger.info('Destroy ticket request received.')
        requester = self.request.user
        queryset = get_ticket_queryset(requester, take_all=True)
        ticket = get_object_or_404(queryset, pk=pk)
        ticket.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    # Solve a ticket
    def update(self, request, pk=None):
        logger.info('Update ticket request received.')
        requester = self.request.user
        queryset = get_ticket_queryset(requester, take_all=True)
        ticket = get_object_or_404(queryset, pk=pk)
        data = self.request.data
        new_status = data['new_status']
        solve_ticket(ticket, new_status)
        return Response(status=HTTP_200_OK)

    def get_permissions(self):
        if self.action in ['list', 'create', 'retrieve', 'destroy']:
            permission_classes = ONLY_AUTHENTICATED
        elif self.action in ['update']:
            permission_classes = ONLY_ADMIN
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]
