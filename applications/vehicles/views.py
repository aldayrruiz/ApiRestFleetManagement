from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from applications.allowed_vehicles.services import get_allowed_vehicles_queryset
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from applications.vehicles.serializers.special import DetailedVehicleSerializer
from shared.permissions import IsAdmin, IsNotDisabled
from applications.traccar.utils import post, put
from applications.traccar.models import Device


class VehicleViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If requester is user, returns the user allowed vehicles.
        Otherwise, if user is admin, returns all vehicles.
        :param request:
        :return: vehicles
        """
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester)
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
        queryset = get_allowed_vehicles_queryset(requester)
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
        serializer = CreateOrUpdateVehicleSerializer(data=self.request.data)
        if serializer.is_valid():
            imei = serializer.initial_data['gps_device']
            name = '{} {}'.format(serializer.validated_data['brand'], serializer.validated_data['model'])
            response = post('devices', data={'uniqueId': imei, 'name': name})
            if not response.ok:
                return Response({'errors': 'Error trying to create gps device'}, status=response.status_code)
            json_device = response.json()
            device = Device(id=json_device['id'], imei=json_device['uniqueId'], name=json_device['name'])
            device.save()
            serializer.save(gps_device=device)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = CreateOrUpdateVehicleSerializer(vehicle, self.request.data)
        if serializer.is_valid():
            device = vehicle.gps_device
            imei = serializer.initial_data['gps_device']
            name = '{} {}'.format(serializer.validated_data['brand'], serializer.validated_data['model'])
            response = put('devices', data={'id': device.id, 'uniqueId': imei, 'name': name})
            if not response.ok:
                return Response({'errors': 'Error trying to edit gps device'}, status=response.status_code)
            serializer.save(gps_device=device)
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        It deletes the vehicle.
        Users have not access to this endpoint (permissions).
        :param request:
        :param pk: uuid of the vehicle
        :return:
        """
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester)
        vehicle = get_object_or_404(queryset, pk=pk)
        vehicle.is_disabled = True
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        # This include 'list' and 'retrieve'.
        # HTTP methods like update and partial update are not supported yet.
        else:
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled]
        return [permission() for permission in permission_classes]
