from .serializers import *
from rest_framework import generics


""" VEHICLES """


# GET/POST: List all vehicles or create a vehicle
class VehicleList(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

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


# POST: List all vehicles types or create a new reservation
class ReservationCreate(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = CreateReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# GET: Reservation detailed
class ReservationDetail(generics.RetrieveDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


""" USER """


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
