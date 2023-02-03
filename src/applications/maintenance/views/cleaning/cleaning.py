from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from applications.maintenance.serializers.cleaning.cleaning import SimpleCleaningSerializer, CreateCleaningSerializer
from applications.maintenance.services.cleaning.queryset import get_cleaning_queryset
from utils.api.query import query_uuid


class CleaningViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateCleaningSerializer, responses={200: CreateCleaningSerializer()})
    def create(self, request):
        serializer = CreateCleaningSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleCleaningSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_cleaning_queryset(requester, vehicle_id)
        serializer = SimpleCleaningSerializer(queryset, many=True)
        return Response(serializer.data)
