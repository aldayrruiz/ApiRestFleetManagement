from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.maintenance.serializers.repairment.repairment import SimpleRepairmentSerializer, CreateRepairmentSerializer
from applications.maintenance.services.repairment.queryset import get_repairment_queryset
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN_OR_SUPER_ADMIN
from utils.api.query import query_uuid


class RepairmentViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateRepairmentSerializer, responses={200: CreateRepairmentSerializer()})
    def create(self, request):
        serializer = CreateRepairmentSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleRepairmentSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_repairment_queryset(requester, vehicle_id)
        serializer = SimpleRepairmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        requester = self.request.user
        queryset = get_repairment_queryset(requester)
        repairment = get_object_or_404(queryset, pk=pk)
        repairment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = ONLY_AUTHENTICATED
        elif self.action in ['destroy']:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]
