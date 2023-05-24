from rest_framework.response import Response

from applications.traccar.utils import put
from applications.vehicles.models import Vehicle
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer
from applications.vehicles.services.utils import VehicleUtils


class VehicleUpdater:
    @staticmethod
    def update(vehicle: Vehicle, serializer: CreateOrUpdateVehicleSerializer):
        VehicleUtils.response_if_gps_device_is_not_on_request(serializer)
        imei = serializer.initial_data['gps_device']
        name = VehicleUtils.get_vehicle_name_for_traccar(vehicle.tenant, serializer)
        device = vehicle.gps_device
        response = put(f'devices/{device.id}', data={'id': device.id, 'uniqueId': imei, 'name': name})
        VehicleUpdater.if_traccar_update_device_raise_error(response)
        device.imei = imei
        device.name = name
        device.save()
        serializer.save(gps_device=device)

    @staticmethod
    def if_traccar_update_device_raise_error(response):
        if not response.ok:
            return Response({'errors': 'Error trying to edit gps device'}, status=response.status_code)
