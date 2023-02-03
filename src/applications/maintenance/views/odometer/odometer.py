from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from applications.maintenance.serializers.odometer.odometer import CreateOdometerSerializer, SimpleOdometerSerializer
from applications.maintenance.services.odometer.queryset import get_odometer_queryset
from applications.traccar.services.devices import TraccarDevices
from utils.api.query import query_uuid


class OdometerViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateOdometerSerializer, responses={200: CreateOdometerSerializer()})
    def create(self, request):
        serializer = CreateOdometerSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        vehicle = serializer.validated_data['vehicle']
        kilometers = serializer.validated_data['kilometers']
        TraccarDevices.update_total_distance(vehicle, kilometers)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleOdometerSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_odometer_queryset(requester, vehicle_id)
        serializer = SimpleOdometerSerializer(queryset, many=True)
        return Response(serializer.data)
