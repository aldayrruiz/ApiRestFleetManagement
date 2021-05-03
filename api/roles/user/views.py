from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.response import Response

from api.roles.user.permissions import *
from api.roles.user.serializers import *


def get_responsible_admin(ticket):
    """
    Returns a queryset of admins that could resolve the ticket.
    :param ticket: Ticket requested by a user that need the vehicle
    :return: queryset of user (admins)
    """
    admins = User.objects.filter(is_admin=True)
    return admins


def is_vehicle_accessible(user, vehicle_id):
    return get_allowed_vehicles(user).filter(id=vehicle_id).exists()


class VehicleViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns a list of vehicles user requester has access.
        """
        user = self.request.user
        queryset = get_allowed_vehicles(user)
        serializer = SimpleVehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns the vehicle if user requester has access.
        """
        user = self.request.user
        queryset = get_allowed_vehicles(user)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = DetailedVehicleSerializer(vehicle)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class VehicleTypeViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns a list of vehicle types that user requester has access.
        It could be useful to filter later.
        """
        user = self.request.user
        queryset = user.allowed_types.all()
        serializer = SimpleVehicleTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns a vehicle type if user requester has access.
        It should return vehicles list too or filter them by url in VehicleViewSet.
        """
        user = self.request.user
        queryset = user.allowed_types.all()
        vehicle_type = get_object_or_404(queryset, pk=pk)
        serializer = SimpleVehicleTypeSerializer(vehicle_type)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ReservationViewSet(viewsets.ViewSet):

    def list(self, request):
        user = self.request.user
        vehicle_id = request.GET.get('vehicleId')
        if vehicle_id:
            queryset = user.reservations.filter(vehicle_id=vehicle_id)
        else:
            queryset = user.reservations.all()
        serializer = SimpleReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        serializer = CreateReservationSerializer(data=self.request.data)

        # Verify if the data request is valid
        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data)
        # If serializer is not valid send errors.
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = self.request.user
        queryset = user.reservations.all()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = SimpleReservationSerializer(reservation)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = self.request.user
        queryset = user.reservations.all()
        reservation = get_object_or_404(queryset, pk=pk)
        # Delete tickets of reservation
        reservation.tickets.all().delete()
        # Delete incidents of reservation
        Incident.objects.filter(reservation=reservation).delete()
        reservation.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    # THIS RESTRICT TO REQUESTER MAKE A RESERVATION OF VEHICLE TYPES THAT HE DOESN'T HAVE ACCESS.
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = [permissions.IsAuthenticated, IsVehicleAccessible]
        return [permission() for permission in permission_classes]


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer


class IncidentViewSet(viewsets.ViewSet):

    def list(self, request):
        user = self.request.user
        queryset = Incident.objects.filter(owner=user)
        serializer = SimpleIncidentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        serializer = CreateIncidentSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = self.request.user
        queryset = Incident.objects.filter(owner=user)
        incident = get_object_or_404(queryset, pk=pk)
        serializer = SimpleIncidentSerializer(incident)
        return Response(serializer.data)

    # THIS RESTRICT TO REQUESTER CREATE AN INCIDENT OF RESERVATION WHICH IS NOT OWNER.
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = [permissions.IsAuthenticated, IsOwnerReservation]
        return [permission() for permission in permission_classes]


class TicketViewSet(viewsets.ViewSet):

    def list(self, request):
        user = self.request.user
        queryset = user.tickets.all()
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
        user = self.request.user
        queryset = user.tickets.all()
        ticket = get_object_or_404(queryset, pk=pk)
        serializer = SimpleTicketSerializer(ticket)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = self.request.user
        queryset = user.tickets.all()
        ticket = get_object_or_404(queryset, pk=pk)
        ticket.delete()
        return Response(status=HTTP_204_NO_CONTENT)
