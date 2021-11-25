import logging

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_409_CONFLICT

from applications.reservations.serializers.create import CreateReservationSerializer
from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.reservations.serializers.special import RecurrentSerializer, CreateByDate
from applications.reservations.services.bydate.creator import ReservationByDateCreator
from applications.reservations.services.destroyer import delete_reservation
from applications.reservations.services.queryset import get_reservation_queryset
from applications.reservations.services.recurrent.recurrent import RecurrentReservationCreator
from applications.reservations.services.recurrent.recurrent_config import RecurrentConfiguration
from applications.reservations.services.timer import reservation_already_started
from shared.permissions import IsVehicleAllowedOrAdmin, IsNotDisabled
from utils.api.query import query_bool, query_date, query_str
from utils.dates import is_after_now

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
        queryset = get_reservation_queryset(requester, take_all, vehicle_id, _from, _to)
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
        tenant = requester.tenant
        serializer = CreateReservationSerializer(data=self.request.data)

        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        self.check_reservation_creation(request, serializer.validated_data)

        serializer.save(owner=requester, tenant=tenant)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_by_date(self, request):
        requester = self.request.user
        logger.info('Create reservation by date')

        serializer = CreateByDate(data=self.request.data)
        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        creator = ReservationByDateCreator.from_serializer(serializer, requester)
        reservation = creator.create()
        if not reservation:
            return Response({'errors': 'Ningun vehículo disponible.'}, status=HTTP_409_CONFLICT)

        response = SimpleReservationSerializer(reservation)
        return Response(response.data)

    @action(detail=False, methods=['post'])
    def create_repetitive(self, request):
        tenant = self.request.user.tenant
        force = query_bool(self.request, 'force')
        logger.info('Query force: {}'.format(force))

        serializer = RecurrentSerializer(data=self.request.data)
        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        rec_config = RecurrentConfiguration.from_serializer(serializer, self.request.user)

        creator = RecurrentReservationCreator(config=rec_config)
        [valid_reservations, invalid_reservations] = creator.try_create()

        invalid_reservations_serializer = SimpleReservationSerializer(invalid_reservations, many=True)

        if not force and len(invalid_reservations) > 0:
            response = {
                'description': 'There are reservations that cannot be saved.',
                'errorReservations': invalid_reservations_serializer.data
            }
            return Response(response, status=HTTP_409_CONFLICT)

        RecurrentReservationCreator.create(valid_reservations, tenant)
        valid_reservations_serializer = SimpleReservationSerializer(valid_reservations, many=True)
        response = {
            'description': 'You have forced the reservations',
            'successfulReservations': valid_reservations_serializer.data,
            'errorReservations': invalid_reservations_serializer.data
        }
        return Response(response)

    def retrieve(self, request, pk=None):
        logger.info('Retrieve reservation request received.')
        requester = self.request.user
        queryset = get_reservation_queryset(requester, take_all=True)
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = SimpleReservationSerializer(reservation)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        logger.info('Destroy reservation request received.')
        delete_post = query_bool(self.request, 'deletePost')
        requester = self.request.user
        queryset = get_reservation_queryset(requester, take_all=True)
        reservation = get_object_or_404(queryset, pk=pk)

        if reservation_already_started(reservation):
            return Response({'errors': 'La reserva ya ha comenzado.'}, status=HTTP_400_BAD_REQUEST)

        if delete_post and reservation.is_recurrent:
            queryset = queryset.filter(recurrent_id=reservation.recurrent_id, start__gte=reservation.start)
            for res in queryset:
                delete_reservation(res)
            return Response(status=HTTP_204_NO_CONTENT)

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
    serializer_cls = serializer.__class__.__name__
    logger.error("Reservation couldn't be serialized with {} because of {}."
                 .format(serializer_cls, serializer.errors))
