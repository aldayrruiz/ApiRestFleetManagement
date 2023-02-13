from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.maintenance.serializers.revision.revision import CreateRevisionSerializer, SimpleRevisionSerializer
from applications.maintenance.services.revision.completer import RevisionCompleter
from applications.maintenance.services.revision.queryset import get_revision_queryset
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN_OR_SUPER_ADMIN
from utils.api.query import query_uuid


class RevisionViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateRevisionSerializer, responses={200: CreateRevisionSerializer()})
    def create(self, request):
        requester = self.request.user
        serializer = CreateRevisionSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        revision = serializer.save()
        RevisionCompleter(revision).update_old_ones_to_completed()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleRevisionSerializer()})
    def list(self, request):
        vehicle_id = query_uuid(self.request, 'vehicleId', required=False)
        requester = self.request.user
        queryset = get_revision_queryset(requester, vehicle_id)
        serializer = SimpleRevisionSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        requester = self.request.user
        queryset = get_revision_queryset(requester)
        revision = get_object_or_404(queryset, pk=pk)
        revision.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = ONLY_AUTHENTICATED
        elif self.action in ['destroy']:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]
