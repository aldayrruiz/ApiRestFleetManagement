import logging

from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_200_OK

from applications.reservations.utils import is_reservation_already_started
from applications.tickets.models import Ticket
from applications.tickets.serializers.create import CreateTicketSerializer
from applications.tickets.serializers.simple import SimpleTicketSerializer
from applications.tickets.services.solver import solve_ticket
from applications.users.models import Role
from applications.users.services import get_admin
from shared.permissions import IsNotDisabled, IsAdmin
from utils.email.tickets import send_created_ticket_email

logger = logging.getLogger(__name__)


class TicketViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is True and requester is admin, it will return all tickets.
        Otherwise, it will return only the requester tickets.
        :param request:
        :return:
        """
        take_all = bool(self.request.query_params.get('takeAll'))
        logger.info('List tickets request received. [takeAll: {}]'.format(take_all))
        requester = self.request.user
        if requester.role == Role.ADMIN and take_all is True:
            queryset = Ticket.objects.all()
        else:
            queryset = requester.tickets.all()
        serializer = SimpleTicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('Create ticket request received.')
        user = self.request.user
        serializer = CreateTicketSerializer(data=self.request.data)

        # Verify if the data request is valid
        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        reservation = serializer.validated_data['reservation']
        # Pass checks
        self.check_if_not_mine(request, reservation)

        if is_reservation_already_started(reservation):
            logger.error('Error creating a ticket. Reservation already started at {}.'.format(reservation.start))
            return Response({'errors': 'Reservation already started'}, status=HTTP_400_BAD_REQUEST)

        # Create Ticket and send email to admin
        ticket = serializer.save(owner=user)
        admin = get_admin()
        send_created_ticket_email(admin, ticket)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        logger.info('Retrieve ticket request received.')
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Ticket.objects.all()
        else:
            queryset = requester.tickets.all()
        ticket = get_object_or_404(queryset, pk=pk)
        serializer = SimpleTicketSerializer(ticket)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        logger.info('Destroy ticket request received.')
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Ticket.objects.all()
        else:
            queryset = requester.tickets.all()
        ticket = get_object_or_404(queryset, pk=pk)
        ticket.delete()
        ticket.save()
        return Response(status=HTTP_204_NO_CONTENT)

    # Solve a ticket
    def update(self, request, pk=None):
        logger.info('Update ticket request received.')
        ticket = Ticket.objects.get(pk=pk)
        data = self.request.data
        new_status = data['new_status']
        error = solve_ticket(ticket, new_status)
        errors = {'errors': error}
        if error:
            logger.error('Solving tickets {}'.format(errors))
            return Response(errors, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_200_OK)

    def check_if_not_mine(self, request, obj):
        if self.request.user is obj.owner:
            raise PermissionDenied('You cannot create a ticket of your reservation')

    def check_if_not_admin_reservation(self, request, obj):
        # TODO: Check if reservation is not by an admin, because normal user cannot create a ticket of a
        #       reservation from an admin.
        raise Exception('Unsupported check: check_if_not_admin_reservation.')

    def get_permissions(self):
        if self.action in ['list', 'create', 'retrieve', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled]
        elif self.action in ['update']:
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled, IsAdmin]
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]


def log_error_serializing(serializer):
    logger.error("Ticket couldn't be serialized with {} because of {}."
                 .format(serializer.__class__.__name__, serializer.errors))
