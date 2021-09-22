import logging

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from applications.reservations.models import Reservation
from applications.reservations.serializers.create import CreateReservationSerializer
from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.reservations.utils import is_reservation_already_started, delete_reservation
from applications.users.models import Role
from shared.permissions import IsVehicleAllowedOrAdmin, IsNotDisabled
from utils.dates import is_after_now
from utils.api.query import query_bool, query_date, query_str

logger = logging.getLogger(__name__)


class ReservationViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is present as True, it will return all reservations.
        Otherwise, if take_all is False or is not present, it will return only requester reservations.
        :param request:
        :return: Returns a list of reservations.
        """
        take_all = query_bool(self.request, 'takeAll')
        vehicle_id = query_str(self.request, 'vehicleId')
        _from = query_date(self.request, 'from')
        _to = query_date(self.request, 'to')

        logger.info('List reservations request received. [takeAll: {}, vehicleId: {}, from: {}, to: {}]'
                    .format(take_all, vehicle_id, _from, _to))
        requester = self.request.user
        queryset = get_reservations(requester, take_all, vehicle_id, _from, _to)
        serializer = SimpleReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Creates a reservation.
        :param request:
        :return:
        """
        logger.info('Create reservation request received.')
        requester = self.request.user
        serializer = CreateReservationSerializer(data=self.request.data)

        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        self.check_reservation_creation(request, serializer.validated_data)

        serializer.save(owner=requester)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_repetitive(self, request):
        force = query_bool(self.request, 'force')
        logger.info('Query force: {}'.format(force))
        return Response({'status': 'Ok it works.'})

    def retrieve(self, request, pk=None):
        logger.info('Retrieve reservation request received.')
        requester = self.request.user
        if requester.role == Role.ADMIN:
            queryset = Reservation.objects.all()
        else:
            queryset = requester.reservations.all()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = SimpleReservationSerializer(reservation)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        logger.info('Destroy reservation request received.')
        requester = self.request.user
        if requester == Role.ADMIN:
            queryset = Reservation.objects.all()
        else:
            queryset = requester.reservations.all()
        reservation = get_object_or_404(queryset, pk=pk)

        if is_reservation_already_started(reservation):
            return Response({'errors': 'La reserva ya ha comenzado.'}, status=HTTP_400_BAD_REQUEST)

        delete_reservation(reservation)
        return Response(status=HTTP_204_NO_CONTENT)

    # THIS RESTRICT TO REQUESTER MAKE A RESERVATION OF VEHICLE TYPES THAT HE DOESN'T HAVE ACCESS.
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled, IsVehicleAllowedOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled]
        return [permission() for permission in permission_classes]

    def check_reservation_creation(self, request, validated_data):
        if not is_after_now(validated_data['start']):
            raise ValidationError('No se puede reservar para una fecha anterior a la actual')

        vehicle = validated_data['vehicle']
        if vehicle.is_disabled:
            logger.error('Cannot reserve a vehicle disabled: {} {}'.format(vehicle.brand, vehicle.model))
            raise ValidationError('No se puede reservar un vehículo deshabilitado')


def log_error_serializing(serializer):
    logger.error("Reservation couldn't be serialized with {} because of {}."
                 .format(serializer.__class__.__name__, serializer.errors))


def get_reservations(requester, take_all=False, vehicle_id=None, _from=None, _to=None):
    if requester.role == Role.ADMIN and take_all:
        queryset = Reservation.objects.all()
    else:
        queryset = requester.reservations.all()

    if vehicle_id:
        queryset = Reservation.objects.filter(vehicle_id=vehicle_id)

    if _from and _to:
        queryset = queryset.filter(start__gte=_from, start__lte=_to)
    else:
        queryset = queryset[:50]
    return queryset
