from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.maintenance.serializers.odometer.odometer import CreateOdometerSerializer, SimpleOdometerSerializer
from applications.maintenance.services.odometer.queryset import get_odometer_queryset
from applications.traccar.services.devices import TraccarDevices
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN_OR_SUPER_ADMIN
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

    def delete(self, request, pk=None):
        requester = self.request.user
        queryset = get_odometer_queryset(requester)
        odometer = get_object_or_404(queryset, pk=pk)
        odometer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = ONLY_AUTHENTICATED
        elif self.action in ['destroy']:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]
