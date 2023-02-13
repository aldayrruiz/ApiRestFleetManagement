from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.response import Response

from applications.maintenance.models import WheelsOperation, MaintenanceStatus
from applications.maintenance.serializers.wheels.wheels import SimpleWheelsSerializer, CreateWheelsSerializer
from applications.maintenance.services.wheels.completer import WheelsCompleter
from applications.maintenance.services.wheels.queryset import get_wheels_queryset
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN_OR_SUPER_ADMIN
from utils.api.query import query_uuid
from utils.dates import now_utc


class WheelsViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateWheelsSerializer, responses={200: CreateWheelsSerializer()})
    def create(self, request):
        requester = self.request.user
        serializer = CreateWheelsSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        wheels = serializer.save()
        if wheels.operation == WheelsOperation.Inspection and not wheels.passed:
            wheels.next_revision = now_utc()
            wheels.status = MaintenanceStatus.EXPIRED
            wheels.save()
        WheelsCompleter(wheels).update_old_ones_to_completed()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleWheelsSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_wheels_queryset(requester, vehicle_id)
        serializer = SimpleWheelsSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        requester = self.request.user
        queryset = get_wheels_queryset(requester)
        wheels = queryset.get(pk=pk)
        wheels.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = ONLY_AUTHENTICATED
        elif self.action in ['destroy']:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]
