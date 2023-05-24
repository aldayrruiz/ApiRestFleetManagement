import logging

from rest_framework.response import Response

from applications.tenants.models import Tenant
from applications.traccar.models import Device
from applications.traccar.utils import post
from applications.users.models import ActionType
from applications.vehicles.exceptions.number_plate_already_in_use import NumberPlateAlreadyInUse
from applications.vehicles.exceptions.was_created_again import VehicleCreatedAgainError
from applications.vehicles.models import Vehicle, VehicleRegistrationHistory
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer
from applications.vehicles.services.utils import VehicleUtils

logger = logging.getLogger(__name__)


class VehicleCreator:

    @staticmethod
    def create(tenant: Tenant, serializer: CreateOrUpdateVehicleSerializer):
        VehicleUtils.response_if_gps_device_is_not_on_request(serializer)
        VehicleCreator.raise_errors_if_already_exists(serializer)
        device = VehicleCreator.try_create_device_on_traccar(tenant, serializer)
        device.save()
        vehicle = serializer.save(tenant=tenant, gps_device=device)
        VehicleRegistrationHistory.objects.create(vehicle=vehicle, tenant=tenant, action=ActionType.CREATED)

    @staticmethod
    def raise_errors_if_already_exists(serializer: CreateOrUpdateVehicleSerializer):
        try:
            vehicle = Vehicle.objects.get(number_plate=serializer.initial_data['number_plate'])
            if vehicle.is_deleted:
                # If it is marked as deleted, mark vehicle as not deleted and register in history.
                VehicleRegistrationHistory.objects.create(vehicle=vehicle, tenant=vehicle.tenant,
                                                          action=ActionType.CREATED)
                vehicle.is_deleted = False
                vehicle.save()
                raise VehicleCreatedAgainError()
            else:
                # If it is not marked as deleted, we cannot create it. So raise Error.
                raise NumberPlateAlreadyInUse()
        except Vehicle.DoesNotExist:
            # If it does not exist, it will follow this
            return None

    @staticmethod
    def try_create_device_on_traccar(tenant: Tenant, serializer: CreateOrUpdateVehicleSerializer):
        """
        Try to create a device on traccar. And return Device model if it was created.
        """
        imei = serializer.initial_data['gps_device']
        name = VehicleUtils.get_vehicle_name_for_traccar(tenant, serializer)
        response = post('devices', data={'uniqueId': imei, 'name': name})
        VehicleCreator.if_traccar_cannot_create_device_raise_error(response)
        j_device = response.json()
        device = Device(id=j_device['id'], imei=j_device['uniqueId'], name=j_device['name'], tenant=tenant)
        return device

    @staticmethod
    def if_traccar_cannot_create_device_raise_error(response):
        if not response.ok:
            logger.error('Traccar sent a device creation response (status {}).'.format(response.status_code))
            return Response({'errors': 'Error trying to create gps device'}, status=response.status_code)
