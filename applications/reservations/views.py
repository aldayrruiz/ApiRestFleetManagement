from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from applications.incidents.models import Incident
from applications.reservations.models import Reservation
from applications.reservations.serializers.create import CreateReservationSerializer
from applications.reservations.serializers.simple import SimpleReservationSerializer
from shared.permissions import IsVehicleAllowedOrAdmin
from applications.users.models import Role


class ReservationViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is present as True, it will return all reservations.
        Otherwise, if take_all is False or is not present, it will return only requester reservations.
        :param request:
        :return: Returns a list of reservations.
        """
        take_all = bool(self.request.query_params.get('take_all'))
        requester = self.request.user
        if requester.role == Role.ADMIN and take_all is True:
            queryset = Reservation.objects.all()
        # If requester is not ADMIN and take_all is not True. Just get the requester reservations.
        else:
            queryset = requester.reservations.all()
        serializer = SimpleReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Creates a reservation.
        :param request:
        :return:
        """
        requester = self.request.user
        serializer = CreateReservationSerializer(data=self.request.data)

        # Verify if the data request is valid
        if serializer.is_valid():
            serializer.save(owner=requester)
            return Response(serializer.data)
        # If serializer is not valid send errors.
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Reservation.objects.all()
        else:
            queryset = requester.reservations.all()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = SimpleReservationSerializer(reservation)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        requester = self.request.user
        if requester == Role.ADMIN:
            queryset = Reservation.objects.all()
        else:
            queryset = requester.reservations.all()
        reservation = get_object_or_404(queryset, pk=pk)
        # Delete tickets of reservation
        reservation.tickets.all().delete()
        # Delete incidents of reservation
        Incident.objects.filter(reservation=reservation).delete()
        reservation.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    # THIS RESTRICT TO REQUESTER MAKE A RESERVATION OF VEHICLE TYPES THAT HE DOESN'T HAVE ACCESS.
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsVehicleAllowedOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
