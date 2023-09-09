import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from applications.allowed_vehicles.services.queryset import get_allowed_vehicles_queryset
from applications.traccar.services.positions import TraccarPositions
from applications.traccar.utils import delete
from applications.users.models import ActionType
from applications.vehicles.models import VehicleRegistrationHistory
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from applications.vehicles.serializers.special import DetailedVehicleSerializer, DisableVehicleSerializer
from applications.vehicles.services.commands.commands import GET_INFO_COMMAND
from applications.vehicles.services.commands.sms_sender import SmsCommandSender
from applications.vehicles.services.creator import VehicleCreator
from applications.vehicles.services.queryset import get_vehicles_queryset
from applications.vehicles.services.updater import VehicleUpdater
from shared import permissions
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
        logger.info('Create vehicle request received.')
        serializer = CreateOrUpdateVehicleSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        VehicleCreator.create(tenant, serializer)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CreateOrUpdateVehicleSerializer, responses={200: CreateOrUpdateVehicleSerializer()})
    def update(self, request, pk=None):
        """
        Update vehicle.
        """
        logger.info('Update vehicle request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(requester, even_disabled=True)
        vehicle = get_object_or_404(queryset, pk=pk)
        serializer = CreateOrUpdateVehicleSerializer(vehicle, self.request.data)
        serializer.is_valid(raise_exception=True)
        VehicleUpdater.update(vehicle, serializer)
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

        # Mark vehicle as deleted and register deleting in history..
        vehicle.is_deleted = True
        vehicle.save()
        VehicleRegistrationHistory.objects.create(vehicle=vehicle, tenant=requester.tenant, action=ActionType.DELETED)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def current_kilometers(self, request, pk=None):
        requester = self.request.user
        queryset = get_vehicles_queryset(requester)
        vehicle = get_object_or_404(queryset, pk=pk)
        # Distance is returned in meters by Traccar API. We convert it to kilometers.
        last_position = TraccarPositions.last_position(vehicle)
        kilometers = last_position['attributes']['totalDistance'] / 1000
        return Response(kilometers)

    @action(detail=False, methods=['post'])
    def send_command(self, request, pk=None):
        requester = self.request.user
        queryset = get_vehicles_queryset(requester)
        vehicle = get_object_or_404(queryset, pk=pk)
        response = SmsCommandSender.send(vehicle, GET_INFO_COMMAND)
        return Response(response)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'destroy', 'partial_update']:
            permission_classes = permissions.ONLY_ADMIN_OR_SUPER_ADMIN
        # This include 'list' and 'retrieve'.
        # HTTP methods like update and partial update are not supported yet.
        else:
            permission_classes = permissions.ONLY_AUTHENTICATED
        return [permission() for permission in permission_classes]


def get_vehicle_name_for_traccar(tenant, serializer):
    data = serializer.validated_data
    name = f"{tenant.short_name} {data['brand']} {data['model']} {data['number_plate']}"
    return name
