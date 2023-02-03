from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from applications.maintenance.models import WheelsOperation, MaintenanceStatus
from applications.maintenance.serializers.wheels.wheels import SimpleWheelsSerializer, CreateWheelsSerializer
from applications.maintenance.services.wheels.queryset import get_wheels_queryset
from utils.api.query import query_uuid


class WheelsViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateWheelsSerializer, responses={200: CreateWheelsSerializer()})
    def create(self, request):
        serializer = CreateWheelsSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        wheels = serializer.save()
        if wheels.operation == WheelsOperation.Inspection and not wheels.passed:
            wheels.status = MaintenanceStatus.EXPIRED
            wheels.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleWheelsSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_wheels_queryset(requester, vehicle_id)
        serializer = SimpleWheelsSerializer(queryset, many=True)
        return Response(serializer.data)
