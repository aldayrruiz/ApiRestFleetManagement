from .serializers import *
from rest_framework import generics


# GET/POST: List all vehicles or create a vehicle
class VehicleList(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


# GET: vehicles type detailed
class VehicleDetail(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


# GET: List all vehicles types or create a vehicle type
class VehicleTypeList(generics.ListCreateAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


# GET: vehicles type detailed
class VehicleTypeDetail(generics.RetrieveAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


# GET/POST: List all vehicles types or create a new reservation
class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


# GET: Reservation detailed
class ReservationDetail(generics.RetrieveDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
