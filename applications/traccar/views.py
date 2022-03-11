import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.allowed_vehicles.services.queryset import get_allowed_vehicles_queryset
from applications.reservations.services.queryset import get_reservation_queryset
from applications.reservations.services.timer import raise_error_if_reservation_has_not_ended
from applications.traccar.utils import get
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN
from utils.api.query import query_str
from utils.dates import from_date_to_str_date_traccar

logger = logging.getLogger(__name__)

# TODO: Only return positions from requester tenant.
# How? Filter before response

# 1. Maybe, having multiple Traccar admins.
# Add some fields like email and plain password of traccar. Clean and dirty solution...
# 2. Just filter by properties of devices and vehicles.


class PositionViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        List last known positions of vehicles.
        """
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

    def get_permissions(self):
        permission_classes = ONLY_AUTHENTICATED
        return [permission() for permission in permission_classes]


def send_get_to_traccar(reservation, route: str):
    device_id = reservation.vehicle.gps_device.id
    start_str = from_date_to_str_date_traccar(reservation.start)
    end_str = from_date_to_str_date_traccar(reservation.end)
    params = {'deviceId': device_id, 'from': start_str, 'to': end_str}
    response = get(target=route, params=params)
    return response


class ReservationReportViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def positions(self, request):
        """
        List of positions from a reservation.
        """
        requester = self.request.user
        reservation_id = query_str(self.request, 'reservationId', True)
        logger.info('List positions of reservation with id {}.'.format(reservation_id))

        queryset = get_reservation_queryset(requester, take_all=True)
        reservation = get_object_or_404(queryset, pk=reservation_id)
        raise_error_if_reservation_has_not_ended(reservation)

        response = send_get_to_traccar(reservation, 'reports/route')
        if not response.ok:
            raise APIException('Could not receive positions.', code=response.status_code)
        return Response(response.json())

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retrieve a report summary from a reservation.
        """
        requester = self.request.user
        reservation_id = query_str(self.request, 'reservationId', True)
        logger.info('Get reservation summary report')

        queryset = get_reservation_queryset(requester, take_all=True)
        reservation = get_object_or_404(queryset, pk=reservation_id)
        raise_error_if_reservation_has_not_ended(reservation)

        response = send_get_to_traccar(reservation, 'reports/summary')
        if not response.ok:
            raise APIException('Could not receive report summary.', code=response.status_code)
        summary = response.json()[0]
        return Response(summary)

    def get_permissions(self):
        permission_classes = ONLY_ADMIN
        return [permission() for permission in permission_classes]
