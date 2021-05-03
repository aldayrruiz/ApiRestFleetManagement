from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.views import ObtainAuthToken

from api.roles.admin.permissions import IsAdmin
from api.roles.user.serializers import *


class AdminVehicleViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns all vehicles.
        """
        user = self.request.user
        queryset = Vehicle.objects.all()
        serializer = SimpleVehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        serializer = CreateVehicleSerializer(data=self.request.data)

        # Verify if data request is valid
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        # If serializer is not valid send errors
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=pk)
        vehicle.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]


class VehicleTypeViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns all vehicles types.
        """
        user = self.request.user
        queryset = VehicleType.objects.all()
        serializer = SimpleVehicleTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns the vehicle type.
        """
        user = self.request.user
        queryset = VehicleType.objects.all()
        vehicle_type = get_object_or_404(queryset, pk=pk)
        serializer = SimpleVehicleTypeSerializer(vehicle_type)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Destroy the vehicle type.
        """
        user = self.request.user
        queryset = VehicleType.objects.all()
        vehicle_type = get_object_or_404(queryset, pk=pk)
        vehicle_type.delete()
        # TODO: Show error if vehicles are linked to vehicleType.
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]


class AdminReservationViewSet(viewsets.ViewSet):

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

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]


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
