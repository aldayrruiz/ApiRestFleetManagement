import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.tenants.serializers.simple import TenantSerializer, CreateTenantSerializer
from applications.tenants.services.queryset import get_tenants_queryset
from shared.permissions import ONLY_SUPER_ADMIN


logger = logging.getLogger(__name__)


class TenantViewSet(viewsets.ViewSet):

    @swagger_auto_schema(responses={200: TenantSerializer(many=True)})
    def list(self, request):
        logger.info('List tenants request received.')
        queryset = get_tenants_queryset()
        serializer = TenantSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: TenantSerializer()})
    def retrieve(self, request, pk=None):
        logger.info('Retrieve tenant request received.')
        queryset = get_tenants_queryset()
        tenant = get_object_or_404(queryset, pk=pk)
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CreateTenantSerializer, responses={201: TenantSerializer()})
    def create(self, request):
        logger.info('Create tenant request received.')
        serializer = CreateTenantSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def change_user_tenant(self, request, pk=None):
        logger.info('Change superadmin tenant request received.')
        queryset = get_tenants_queryset()
        tenant = get_object_or_404(queryset, pk=pk)
        requester = self.request.user
        requester.tenant = tenant
        requester.save()
        return Response()

    def get_permissions(self):
        permission_classes = ONLY_SUPER_ADMIN
        return [permission() for permission in permission_classes]
