from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from applications.maintenance.serializers.itv.itv import CreateItvSerializer, SimpleItvSerializer
from applications.maintenance.services.emails.created import MaintenanceOperationCreatedEmail
from applications.maintenance.services.itv.queryset import get_itv_queryset
from utils.api.query import query_uuid


class ItvViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateItvSerializer, responses={200: CreateItvSerializer()})
    def create(self, request):
        requester = self.request.user
        serializer = CreateItvSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        itv = serializer.save()
        MaintenanceOperationCreatedEmail(requester.tenant, itv).send()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleItvSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_itv_queryset(requester, vehicle_id)
        serializer = SimpleItvSerializer(queryset, many=True)
        return Response(serializer.data)
