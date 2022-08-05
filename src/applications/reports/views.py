import logging

from django.http import FileResponse, Http404
from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.reports.serializers.simple import SimpleReportSerializer
from applications.reports.services.queryset import get_reports_queryset
from shared.permissions import ONLY_ADMIN_OR_SUPER_ADMIN

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):
    @swagger_auto_schema(responses={200: SimpleReportSerializer()})
    def list(self, request):
        """
        List monthly reports.
        """
        logger.info('List monthly reports request received.')
        requester = self.request.user
        queryset = get_reports_queryset(requester)
        serializer = SimpleReportSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        """
        Return pdf file given its id.
        """
        logger.info('View monthly report request received.')
        requester = self.request.user
        queryset = get_reports_queryset(requester)
        report = get_object_or_404(queryset, pk=pk)
        try:
            return FileResponse(open(report.pdf, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()

    def get_permissions(self):
        permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        return [permission() for permission in permission_classes]

