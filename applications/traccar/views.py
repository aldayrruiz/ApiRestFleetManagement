import logging

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from applications.allowed_vehicles.services import get_allowed_vehicles_queryset
from applications.traccar.utils import get

logger = logging.getLogger(__name__)


class PositionViewSet(viewsets.ViewSet):

    def list(self, request):
        logger.info('List positions request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(user=requester, even_disabled=True)
        # in IS0 8601 format. eg. 1963-11-22T18:30:00Z
        vehicle_id = self.request.query_params.get('vehicleId')
        date_from = self.request.query_params.get('from')
        date_to = self.request.query_params.get('to')
        params = {'from': date_from, 'to': date_to}
        if vehicle_id:
            vehicle = get_object_or_404(queryset, pk=vehicle_id)
            params['uniqueId'] = vehicle.gps_device.id
        response = get(target='positions', params=params)
        if not response.ok:
            return Response({'errors': 'Could not receive positions.'}, status=response.status_code)
        return Response(response.json())

