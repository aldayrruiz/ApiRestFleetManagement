import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.allowed_vehicles.services.queryset import get_allowed_vehicles_queryset
from applications.reservations.services.queryset import get_reservation_queryset
from applications.reservations.services.timer import raise_error_if_reservation_has_not_ended
from applications.traccar.services.api import TraccarAPI
from applications.traccar.services.summary import SummaryReport
from applications.traccar.utils import get
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN_OR_SUPER_ADMIN
from utils.api.query import query_str, query_date

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
        requester = self.request.user
        queryset = get_allowed_vehicles_queryset(user=requester, even_disabled=True)
        # in IS0 8601 format. eg. 1963-11-22T18:30:00Z
        vehicle_id = query_str(self.request, 'vehicleId')
        date_from = query_str(self.request, 'from')
        date_to = query_str(self.request, 'to')
        params = {'from': date_from, 'to': date_to}
        logger.info(f'List positions request received. {params}')
        if vehicle_id:
            vehicle = get_object_or_404(queryset, pk=vehicle_id)
            params['uniqueId'] = vehicle.gps_device.id
        response = get(target='positions', params=params)
        if not response.ok:
            return Response({'errors': 'Could not receive positions.'}, status=response.status_code)
        return Response(response.json())

    @action(detail=False, methods=['get'])
    def route(self, request):
        """
        List of positions from a vehicle or vehicles at a range of time.
        """
        requester = self.request.user
        vehicles = self.request.query_params.getlist('vehicleId')
        start = query_date(self.request, 'start')
        end = query_date(self.request, 'end')

        queryset = get_allowed_vehicles_queryset(requester, even_disabled=True)
        queryset = queryset.filter(pk__in=vehicles)
        gps_devices = [vehicle.gps_device.id for vehicle in queryset]
        response = TraccarAPI.get(gps_devices, start, end, 'reports/route')
        if not response.ok:
            raise APIException('Could not receive positions.', code=response.status_code)
        return Response(response.json())

    def get_permissions(self):
        permission_classes = ONLY_AUTHENTICATED
        return [permission() for permission in permission_classes]


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

        device_id = reservation.vehicle.gps_device.id
        response = TraccarAPI.get(device_id, reservation.start, reservation.end, 'reports/route')
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

        summary = SummaryReport(reservation).get_summary()
        return Response(summary)

    def get_permissions(self):
        permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        return [permission() for permission in permission_classes]
