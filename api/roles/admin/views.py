from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.response import Response

from rest_framework.authtoken.views import ObtainAuthToken

from api.roles.user.serializers import *


class AdminVehicleViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns a list a vehicles from admin fleet.
        """
        user = self.request.user
        queryset = Vehicle.objects.filter(fleet=user.fleet)
        serializer = SimpleVehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        serializer = CreateVehicleSerializer(data=self.request.data)

        # Verify if data request is valid
        if serializer.is_valid():
            serializer.save(fleet=user.fleet)
            return Response(serializer.data)
        # If serializer is not valid send errors
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        queryset = Vehicle.objects.filter(fleet=user.fleet)
        vehicle = get_object_or_404(queryset, pk=pk)
        vehicle.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class VehicleTypeViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        Returns vehicles types of the fleet of the admin (requester).
        """
        user = self.request.user
        queryset = VehicleType.objects.filter(fleet=user.fleet)
        serializer = SimpleVehicleTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns the vehicle type if it is in admin fleet.
        """
        user = self.request.user
        queryset = VehicleType.objects.filter(fleet=user.fleet)
        vehicle_type = get_object_or_404(queryset, pk=pk)
        serializer = SimpleVehicleTypeSerializer(vehicle_type)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Destroy the vehicle type if is in admin fleet.
        """
        user = self.request.user
        queryset = VehicleType.objects.filter(fleet=user.fleet)
        vehicle_type = get_object_or_404(queryset, pk=pk)
        vehicle_type.delete()
        # TODO: Show error if vehicles are linked to vehicleType.
        return Response(status=HTTP_204_NO_CONTENT)


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



class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })