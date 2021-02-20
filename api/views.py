from .serializers import *
from rest_framework import generics
from rest_framework import permissions
from api.permissions import *


""" VEHICLES """

# TODO: Change all for Viewsets
# GET/POST: List all vehicles or create a vehicle


class VehicleList(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        """
         Get a list of vehicles corresponding to the user's fleet, allowed vehicle types and available=True.
        """
        user = self.request.user
        allowed_types = AllowedTypes.objects.filter(user_id=user.id).values('type_id')
        return Vehicle.objects.filter(fleet__id=user.fleet.id, type__in=allowed_types, available=True)


# POST
class VehicleCreate(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = CreateVehicleSerializer


# GET: vehicle detailed
class VehicleDetail(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


""" VEHICLES TYPES """


# GET: List all vehicles types or create a vehicle type
class VehicleTypeList(generics.ListAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


# POST
class VehicleTypeCreate(generics.CreateAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = CreateVehicleTypeSerializer


# GET: vehicles type detailed
class VehicleTypeDetail(generics.RetrieveAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


""" RESERVATION """


class ReservationList(generics.ListAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# POST: List all vehicles types or create a new reservation
class ReservationCreate(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = CreateReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# GET: Reservation detailed
class ReservationDetail(generics.RetrieveDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


""" USER """


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrSuperuser]
