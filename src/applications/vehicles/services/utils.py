from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from applications.tenants.models import Tenant
from applications.vehicles.serializers.create import CreateOrUpdateVehicleSerializer


class VehicleUtils:
    @staticmethod
    def response_if_gps_device_is_not_on_request(serializer: CreateOrUpdateVehicleSerializer):
        if not serializer.initial_data.__contains__('gps_device'):
            return Response({'gps_device': ['Este campo es requerido']}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_vehicle_name_for_traccar(tenant: Tenant, serializer: CreateOrUpdateVehicleSerializer):
        data = serializer.validated_data
        name = f"{tenant.short_name} {data['brand']} {data['model']} {data['number_plate']}"
        return name
