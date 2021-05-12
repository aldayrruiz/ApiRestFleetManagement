from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
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
        If requester is user, returns the user allowed vehicles.
        Otherwise, if user is admin, returns all vehicles.
        :param request:
        :return: vehicles
        """
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Vehicle.objects.all()
        else:
            queryset = get_allowed_vehicles(requester)
        serializer = SimpleVehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        If requester is user, he will have access to his allowed vehicles.
        If requester is admin, he will have access to all vehicles.
        :param request:
        :param pk: uuid of the vehicle
        :return: vehicle desired.
        """
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Vehicle.objects.all()
        else:
            queryset = get_allowed_vehicles(requester)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = DetailedVehicleSerializer(vehicle)
        return Response(serializer.data)

    def create(self, request):
        """
        It creates a vehicle given a data.
        Users have not access to this endpoint (permissions).
        :param request:
        :return:
        """
        serializer = CreateVehicleSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        It deletes the vehicle.
        Users have not access to this endpoint (permissions).
        :param request:
        :param pk: uuid of the vehicle
        :return:
        """
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=pk)
        vehicle.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy':
            permission_classes = [IsAdmin]
        # This include 'list' and 'retrieve'.
        # HTTP methods like update and partial update are not supported yet.
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class VehicleTypeViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns a list of vehicle types that user requester has access.
        It could be useful to filter later.
        """
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = VehicleType.objects.all()
        else:
            queryset = requester.allowed_types.all()
        serializer = SimpleVehicleTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns a vehicle type if user requester has access.
        It should return vehicles list too or filter them by url in VehicleViewSet.
        """
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = VehicleType.objects.all()
        else:
            queryset = requester.allowed_types.all()
        vehicle_type = get_object_or_404(queryset, pk=pk)
        serializer = SimpleVehicleTypeSerializer(vehicle_type)
        return Response(serializer.data)

    def create(self, request):
        """
        It creates a vehicle type.
        This endpoint is only reserved for ADMINS
        :param request:
        :return:
        """
        serializer = CreateVehicleTypeSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        It deletes the vehicle type.
        This endpoint is only reserved for ADMINS.
        :param request:
        :param pk:
        :return:
        """
        queryset = VehicleType.objects.all()
        vehicle_type = get_object_or_404(queryset, pk=pk)
        vehicle_type.delete()
        # TODO: Show error if vehicles are linked to vehicleType.
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'destroy' or self.action == 'create':
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


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
            permission_classes = [permissions.IsAuthenticated, IsVehicleAccessibleOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class IncidentViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is True and requester is admin, it will return all incidents.
        Otherwise, it will return only the requester incidents.
        :param request:
        :return:
        """
        take_all = bool(self.request.query_params.get('take_all'))
        requester = self.request.user
        if requester.role == Role.ADMIN and take_all is True:
            queryset = Incident.objects.all()
        else:
            queryset = Incident.objects.filter(owner=requester)
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
    # IF REQUESTER IS ADMIN, HE CAN CREATE AN INCIDENT EVEN IF HE IS NOT OWNER.
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsOwnerReservationOrAdmin]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


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


class UserViewSet(viewsets.ViewSet):
    """
    This entire endpoint class and its methods (endpoints) are only available if requester is admin.
    """

    def list(self, request):
        """
        It returns all users.
        :param request:
        :return: users
        """
        queryset = get_user_model().objects.all()
        serializer = SimpleUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        It returns the user given an id.
        :param request:
        :param pk: user id
        :return:
        """
        queryset = get_user_model().objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = SimpleUserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        It deletes an user and all his relations (reservations, incidents, tickets).
        If requester tries to delete himself, server respond with 403 ERROR.
        :param request:
        :param pk: user id
        :return:
        """
        requester = self.request.user
        queryset = get_user_model().objects.all()
        user = get_object_or_404(queryset, pk=pk)
        if requester == user:
            return Response(status=HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    # Create method is located in /register endpoint

    def get_permissions(self):
        return [permission() for permission in [IsAdmin]]


class RegistrationViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = RegistrationSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        # Only admin can register users.
        return [permission() for permission in [IsAdmin]]


class AdminAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.role == Role.USER:
            return Response(status=HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })
