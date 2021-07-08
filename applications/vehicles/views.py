import logging

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from applications.allowed_vehicles.services import get_allowed_vehicles_queryset
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from applications.vehicles.serializers.special import DetailedVehicleSerializer
from shared.permissions import IsAdmin, IsNotDisabled
from applications.traccar.utils import post, put, delete
from applications.traccar.models import Device


logger = logging.getLogger(__name__)


class VehicleViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If requester is user, returns the user allowed vehicles.
        Otherwise, if user is admin, returns all vehicles.
        :param request:
        :return: vehicles
        """
        even_disabled = bool(self.request.query_params.get('evenDisabled'))
        logger.info('List vehicles request received. [evenDisabled: {}]'.format(even_disabled))
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=even_disabled)
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
        even_disabled = bool(self.request.query_params.get('evenDisabled'))
        logger.info('Retrieve vehicle request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=even_disabled)
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
        logger.info('Create user request received.')
        serializer = CreateOrUpdateVehicleSerializer(data=self.request.data)

        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        imei = serializer.initial_data['gps_device']
        name = '{} {}'.format(serializer.validated_data['brand'], serializer.validated_data['model'])
        response = post('devices', data={'uniqueId': imei, 'name': name})

        if not response.ok:
            logger.error('Traccar sent a device creation response (status {}).'.format(response.status_code))
            return Response({'errors': 'Error trying to create gps device'}, status=response.status_code)

        json_device = response.json()
        device = Device(id=json_device['id'], imei=json_device['uniqueId'], name=json_device['name'])
        device.save()
        serializer.save(gps_device=device)
        return Response(serializer.data)

    def update(self, request, pk=None):
        logger.info('Update vehicle request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=True)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = CreateOrUpdateVehicleSerializer(vehicle, self.request.data)

        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        device = vehicle.gps_device
        imei = serializer.initial_data['gps_device']
        name = '{} {}'.format(serializer.validated_data['brand'], serializer.validated_data['model'])
        response = put('devices', data={'id': device.id, 'uniqueId': imei, 'name': name})

        if not response.ok:
            return Response({'errors': 'Error trying to edit gps device'}, status=response.status_code)

        serializer.save(gps_device=device)
        return Response(serializer.data)

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
        response = delete('devices', vehicle.gps_device.id)
        if not response.ok:
            return Response({'errors': 'Error trying to delete gps device'}, status=response.status_code)
        vehicle.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        # This include 'list' and 'retrieve'.
        # HTTP methods like update and partial update are not supported yet.
        else:
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled]
        return [permission() for permission in permission_classes]


def log_error_serializing(serializer):
    logger.error("Vehicle couldn't be serialized with {} because of {}"
                 .format(serializer.__class__.__name__, serializer.errors))
