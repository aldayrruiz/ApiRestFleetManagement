import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from applications.allowed_vehicles.services.queryset import get_allowed_vehicles_queryset
from applications.traccar.models import Device
from applications.traccar.utils import post, put, delete
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from applications.vehicles.serializers.special import DetailedVehicleSerializer, DisableVehicleSerializer
from shared.permissions import ONLY_ADMIN, ONLY_AUTHENTICATED
from utils.api.query import query_bool

logger = logging.getLogger(__name__)


class VehicleViewSet(viewsets.ViewSet):

    @swagger_auto_schema(responses={200: SimpleVehicleSerializer(many=True)})
    def list(self, request):
        """
        List allowed vehicles.
        """
        even_disabled = query_bool(self.request, 'evenDisabled')
        logger.info('List vehicles request received. [evenDisabled: {}]'.format(even_disabled))
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=even_disabled)
        serializer = SimpleVehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: DetailedVehicleSerializer()})
    def retrieve(self, request, pk=None):
        """
        Retrieve an allowed vehicle.
        """
        even_disabled = query_bool(self.request, 'evenDisabled')
        reservations = query_bool(self.request, 'reservations')
        logger.info('Retrieve vehicle request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=even_disabled)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = DetailedVehicleSerializer(vehicle) if reservations else SimpleVehicleSerializer(vehicle)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CreateOrUpdateVehicleSerializer, responses={201: CreateOrUpdateVehicleSerializer()})
    def create(self, request):
        """
        Create a vehicle.
        """
        requester = self.request.user
        tenant = requester.tenant
        logger.info('Create user request received.')
        serializer = CreateOrUpdateVehicleSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.initial_data.__contains__('gps_device'):
            return Response({'gps_device': ['Este campo es requerido']}, status=HTTP_400_BAD_REQUEST)

        imei = serializer.initial_data['gps_device']
        name = get_vehicle_name_for_traccar(tenant, serializer)
        response = post('devices', data={'uniqueId': imei, 'name': name})

        if not response.ok:
            logger.error('Traccar sent a device creation response (status {}).'.format(response.status_code))
            return Response({'errors': 'Error trying to create gps device'}, status=response.status_code)

        j_device = response.json()
        device = Device(id=j_device['id'], imei=j_device['uniqueId'], name=j_device['name'], tenant=tenant)
        device.save()
        serializer.save(tenant=requester.tenant, gps_device=device)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CreateOrUpdateVehicleSerializer, responses={200: CreateOrUpdateVehicleSerializer()})
    def update(self, request, pk=None):
        """
        Update vehicle.
        """
        logger.info('Update vehicle request received.')
        requester = self.request.user
        tenant = requester.tenant
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=True)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = CreateOrUpdateVehicleSerializer(vehicle, self.request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.initial_data.__contains__('gps_device'):
            return Response({'gps_device': ['Este campo es requerido']}, status=HTTP_400_BAD_REQUEST)

        device = vehicle.gps_device
        imei = serializer.initial_data['gps_device']
        name = get_vehicle_name_for_traccar(tenant, serializer)
        response = put('devices', data={'id': device.id, 'uniqueId': imei, 'name': name})

        if not response.ok:
            return Response({'errors': 'Error trying to edit gps device'}, status=response.status_code)

        device.imei = imei
        device.name = name
        device.save()
        serializer.save(gps_device=device)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=DisableVehicleSerializer, responses={200: DisableVehicleSerializer()})
    def partial_update(self, request, pk=None):
        """
        Disable and enable vehicles.
        """
        logger.info('Partial update vehicle request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=True)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = DisableVehicleSerializer(vehicle, request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        logger.info('Vehicle was partial updated successfully.')
        return Response(serializer.data)

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        """
        Delete a vehicle.
        """
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=True)
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
        if self.action in ['create', 'destroy', 'partial_update']:
            permission_classes = ONLY_ADMIN
        # This include 'list' and 'retrieve'.
        # HTTP methods like update and partial update are not supported yet.
        else:
            permission_classes = ONLY_AUTHENTICATED
        return [permission() for permission in permission_classes]


def get_vehicle_name_for_traccar(tenant, serializer):
    name = '{} {} {}'.format(tenant.name, serializer.validated_data['brand'], serializer.validated_data['model'])
    return name
