from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from reservations.models import Reservation
from shared.permissions import IsOwnerReservationOrAdmin
from tickets.models import Ticket
from tickets.serializers.create import CreateTicketSerializer
from tickets.serializers.simple import SimpleTicketSerializer
from users.models import Role, User


def get_responsible_admin(ticket):
    """
    Returns a queryset of admins that could resolve the ticket.
    :param ticket: Ticket requested by a user that need the vehicle
    :return: queryset of user (admins)
    """
    admins = User.objects.filter(is_admin=True)
    return admins


class TicketViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is True and requester is admin, it will return all tickets.
        Otherwise, it will return only the requester tickets.
        :param request:
        :return:
        """
        take_all = bool(self.request.query_params.get('take_all'))
        requester = self.request.user
        if requester.role == Role.ADMIN and take_all is True:
            queryset = Ticket.objects.all()
        else:
            queryset = requester.tickets.all()
        serializer = SimpleTicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        serializer = CreateTicketSerializer(data=self.request.data)

        # Verify if the data request is valid
        if serializer.is_valid():
            ticket = serializer.save(owner=user)
            reservation = Reservation.objects.get(pk=serializer.data['reservation'])
            admins = get_responsible_admin(ticket)
            # TODO: Uncomment this to send emails
            # send_emails(admins=admins, reservation=reservation, ticket=ticket)
            return Response(serializer.data)
        # If serializer is not valid send errors.
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Ticket.objects.all()
        else:
            queryset = requester.tickets.all()
        ticket = get_object_or_404(queryset, pk=pk)
        serializer = SimpleTicketSerializer(ticket)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Ticket.objects.all()
        else:
            queryset = requester.tickets.all()
        ticket = get_object_or_404(queryset, pk=pk)
        ticket.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsOwnerReservationOrAdmin]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
