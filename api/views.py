from .serializers import *
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


# Use this function for development purposes while authentication is not available.
# When authentication is ready delete this func, the errors where this func were used will show up.
# Fix the errors getting the user by self.request.user.
def get_aldayr():
    return User.objects.get(username='aldayr')


def get_vehicles(user):
    """
    Returns a queryset of vehicles the user has access.
    :param user: user model instance.
    :return: a queryset of vehicles you have access.
    """
    allowed_types = user.allowed_types.all().values('id')
    return Vehicle.objects.filter(fleet__id=user.fleet.id, type__in=allowed_types)


def is_vehicle_accessible(user, vehicle_id):
    return get_vehicles(user).filter(id=vehicle_id).exists()


class VehicleViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns a list of vehicles user requester has access.
        """
        user = get_aldayr()
        queryset = get_vehicles(user)
        serializer = VehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns the vehicle if user requester has access.
        """
        user = get_aldayr()
        queryset = get_vehicles(user)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)


class VehicleTypeViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns a list of vehicle types that user requester has access.
        It could be useful to filter later.
        """
        user = get_aldayr()
        queryset = user.allowed_types.all()
        serializer = VehicleTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns a vehicle type if user requester has access.
        It should return vehicles list too or filter them by url in VehicleViewSet.
        """
        user = get_aldayr()
        queryset = user.allowed_types.all()
        vehicle_type = get_object_or_404(queryset, pk=pk)
        serializer = VehicleTypeSerializer(vehicle_type)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ViewSet):

    def list(self, request):
        user = get_aldayr()
        queryset = user.reservations.all()
        serializer = ReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = get_aldayr()
        serializer = CreateReservationSerializer(data=self.request.data)

        # Verify if you have access to the vehicle. Try to permission_classes later, I couldn't do it.
        if not is_vehicle_accessible(user, self.request.data['vehicle']):
            return Response({'non_field_errors': ['Vehicle inaccessible']}, status=status.HTTP_401_UNAUTHORIZED)
        # Verify if the data request is valid
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        # If serializer is not valid send errors.
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsOwnerOrSuperuser]
