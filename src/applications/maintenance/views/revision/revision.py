from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from applications.maintenance.serializers.revision.revision import CreateRevisionSerializer, SimpleRevisionSerializer
from applications.maintenance.services.revision.queryset import get_revision_queryset
from utils.api.query import query_uuid


class RevisionViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateRevisionSerializer, responses={200: CreateRevisionSerializer()})
    def create(self, request):
        serializer = CreateRevisionSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleRevisionSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_revision_queryset(requester, vehicle_id)
        serializer = SimpleRevisionSerializer(queryset, many=True)
        return Response(serializer.data)
