import logging

from django.http import FileResponse, Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from applications.reservation_templates.models import ReservationTemplate
from applications.tenants.serializers.billings import SimpleTenantBillingMonthlyPdfReportSerializer
from applications.tenants.serializers.simple import TenantSerializer, CreateTenantSerializer
from applications.tenants.services.queryset import get_tenants_queryset, get_billing_reports
from shared.permissions import ONLY_SUPER_ADMIN, ONLY_ADMIN_OR_SUPER_ADMIN

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
        tenant = serializer.save()
        ReservationTemplate.objects.create(tenant=tenant, title='Otro')
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


class TenantBillingMonthlyPdfReportViewSet(viewsets.ViewSet):
    @swagger_auto_schema(responses={200: SimpleTenantBillingMonthlyPdfReportSerializer()})
    def list(self, request):
        """
        List monthly reports.
        """
        requester = self.request.user
        queryset = get_billing_reports(requester)
        print(queryset)
        serializer = SimpleTenantBillingMonthlyPdfReportSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        """
        Return pdf file given its id.
        """
        requester = self.request.user
        queryset = get_billing_reports(requester)
        report = get_object_or_404(queryset, pk=pk)
        try:
            return FileResponse(open(report.pdf, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()

    def get_permissions(self):
        permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        return [permission() for permission in permission_classes]
