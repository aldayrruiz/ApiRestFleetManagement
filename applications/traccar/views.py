import logging

from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from applications.allowed_vehicles.services.queryset import get_allowed_vehicles_queryset
from applications.reservations.models import Reservation
from applications.reservations.services.timer import reservation_already_ended
from applications.traccar.utils import get
from utils.api.query import query_str
from utils.dates import from_date_to_str_date_traccar

logger = logging.getLogger(__name__)


class PositionViewSet(viewsets.ViewSet):

    def list(self, request):
        # TODO: Only return positions from requester tenant.
        # How? Filter before response

        # 1. Maybe, having multiple Traccar admins.
        # Add some fields like email and plain password of traccar. Clean and dirty solution...

        # 2. Just filter by properties of devices and vehicles.
        logger.info('List positions request received.')
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(user=requester, even_disabled=True)
        # in IS0 8601 format. eg. 1963-11-22T18:30:00Z
        vehicle_id = query_str(self.request, 'vehicleId')
        date_from = query_str(self.request, 'from')
        date_to = query_str(self.request, 'to')
        params = {'from': date_from, 'to': date_to}
        if vehicle_id:
            vehicle = get_object_or_404(queryset, pk=vehicle_id)
            params['uniqueId'] = vehicle.gps_device.id
        response = get(target='positions', params=params)
        if not response.ok:
            return Response({'errors': 'Could not receive positions.'}, status=response.status_code)
        return Response(response.json())


class ReportsRouteViewSet(viewsets.ViewSet):

    def list(self, request):
        reservation_id = query_str(self.request, 'reservationId')
        logger.info('List positions of reservation with id {}.'.format(reservation_id))
        if reservation_id in [None, '', 'undefined']:
            return Response({'errors': 'You did not pass reservationId param.'}, status=HTTP_400_BAD_REQUEST)

        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=reservation_id)
        if not reservation_already_ended(reservation):
            return Response({'errors': 'Reservation has not ended already.'}, status=HTTP_400_BAD_REQUEST)

        device_id = reservation.vehicle.gps_device.id
        start_str = from_date_to_str_date_traccar(reservation.start)
        end_str = from_date_to_str_date_traccar(reservation.end)
        params = {'deviceId': device_id, 'from': start_str, 'to': end_str}
        response = get(target='reports/route', params=params)
        if not response.ok:
            return Response({'error': 'Could not receive positions form Traccar.'}, status=response.status_code)
        return Response(response.json())
