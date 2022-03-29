from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.tenant.serializers.simple import TenantSerializer
from applications.tenant.services.queryset import get_tenants_queryset
from shared.permissions import ONLY_SUPER_ADMIN


class TenantViewSet(viewsets.ViewSet):

    @swagger_auto_schema(responses={200: TenantSerializer(many=True)})
    def list(self, request):
        """
        List tenants.
        """
        queryset = get_tenants_queryset()
        serializer = TenantSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: TenantSerializer()})
    def retrieve(self, request, pk=None):
        """
        Retrieve a tenant.
        """
        queryset = get_tenants_queryset()
        tenant = get_object_or_404(queryset, pk=pk)
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def change_user_tenant(self, request, pk=None):
        """
        Change super admin tenant
        """
        queryset = get_tenants_queryset()
        tenant = get_object_or_404(queryset, pk=pk)
        requester = self.request.user
        requester.tenant = tenant
        requester.save()
        return Response()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'change_user_tenant']:
            permission_classes = ONLY_SUPER_ADMIN
        # If new endpoints are added, by default add them to ONLY ADMIN
        else:
            permission_classes = ONLY_SUPER_ADMIN
        return [permission() for permission in permission_classes]
