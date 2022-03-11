import logging

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_409_CONFLICT

from applications.reservations.exceptions.already_started import ReservationAlreadyStarted
from applications.reservations.exceptions.cannot_reserve_to_past import CannotReserveToPastError
from applications.reservations.exceptions.cannot_reserve_vehicle_disabled import CannotReserveVehicleDisabled
from applications.reservations.serializers.create import CreateReservationSerializer, CreateRecurrentSerializer
from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.reservations.serializers.special import RecurrentSerializer, CreateByDate
from applications.reservations.services.bydate.creator import ReservationByDateCreator
from applications.reservations.services.destroyer import delete_reservation
from applications.reservations.services.queryset import get_reservation_queryset
from applications.reservations.services.recurrent.recurrent import RecurrentReservationCreator
from applications.reservations.services.recurrent.recurrent_config import RecurrentConfiguration
from applications.reservations.services.timer import reservation_already_started
from applications.vehicles.exceptions.no_vehicles_available import NoVehiclesAvailableError
from shared.permissions import IsVehicleAllowedOrAdmin, IsNotDisabled, ONLY_AUTHENTICATED
from utils.api.query import query_bool, query_date, query_str
from utils.dates import is_after_now

logger = logging.getLogger(__name__)


class ReservationViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        List own reservations. If takeAll is given, it lists all reservations from everyone.
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

    def retrieve(self, request, pk=None):
        """
        Retrieve a reservation.
        """
        logger.info('Retrieve reservation request received.')
        requester = self.request.user
        queryset = get_reservation_queryset(requester, take_all=True)
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = SimpleReservationSerializer(reservation)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a reservation.
        """
        logger.info('Create reservation request received.')
        requester = self.request.user
        tenant = requester.tenant
        serializer = CreateReservationSerializer(data=self.request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        self.check_reservation_creation(request, serializer.validated_data)
        serializer.save(tenant=tenant)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_by_date(self, request):
        """
        Create a reservation by date. An ordered list of vehicles (by priority) is needed,
        so a reservation can be created if a vehicle is not available.
        """
        requester = self.request.user
        logger.info('Create reservation by date')

        serializer = CreateByDate(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        creator = ReservationByDateCreator.from_serializer(serializer, requester)
        reservation = creator.create()
        if not reservation:
            raise NoVehiclesAvailableError()

        response = SimpleReservationSerializer(reservation)
        return Response(response.data)

    @action(detail=False, methods=['post'])
    def create_repetitive(self, request):
        """
        Create many reservations at once. An ordered list of vehicles (by priority) is needed,
        so a reservation can be created if a vehicle is not available.
        Make sure you call /create_recurrent endpoint before calling this endpoint.
        """
        tenant = self.request.user.tenant
        force = query_bool(self.request, 'force')
        logger.info(f'Query force: {force}')

        serializer = RecurrentSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        rec_config = RecurrentConfiguration.from_serializer(serializer, self.request.user)

        creator = RecurrentReservationCreator(config=rec_config)
        [valid_reservations, invalid_reservations] = creator.try_create()

        invalid_reservations_serializer = SimpleReservationSerializer(invalid_reservations, many=True)
        at_least_one_invalid_reservation = len(invalid_reservations) > 0
        if not force and at_least_one_invalid_reservation:
            response = {
                'description': 'There are reservations that cannot be saved.',
                'errorReservations': invalid_reservations_serializer.data
            }
            return Response(response, status=HTTP_409_CONFLICT)

        RecurrentReservationCreator.create(valid_reservations=valid_reservations, tenant=tenant)
        valid_reservations_serializer = SimpleReservationSerializer(valid_reservations, many=True)
        response = {
            'description': 'You have forced the reservations',
            'successfulReservations': valid_reservations_serializer.data,
            'errorReservations': invalid_reservations_serializer.data
        }
        return Response(response)

    @action(detail=False, methods=['post'])
    def create_recurrent(self, request):
        """
        Create a recurrent instance.
        So you can make reference to recurrent instance in /create_repetitive endpoint.
        """
        logger.info('Create recurrent request received')
        requester = self.request.user
        tenant = requester.tenant
        serializer = CreateRecurrentSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=requester, tenant=tenant)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Cancel a reservation. Only reservations that have not started can be cancelled.
        If reservation is a recurrent reservation and deletePost query is given. Reservation passed and its
        future recurrent reservations will be cancelled. Reservations that already happened will not be deleted.
        """
        logger.info('Destroy reservation request received.')
        delete_future_reservations = query_bool(self.request, 'deletePost')
        requester = self.request.user
        queryset = get_reservation_queryset(requester, take_all=True)
        reservation = get_object_or_404(queryset, pk=pk)

        if reservation_already_started(reservation):
            raise ReservationAlreadyStarted()

        if delete_future_reservations and reservation.is_recurrent:
            queryset = queryset.filter(recurrent_id=reservation.recurrent_id, start__gte=reservation.start)
            for future_reservation in queryset:
                delete_reservation(future_reservation)
            return Response(status=HTTP_204_NO_CONTENT)

        delete_reservation(reservation)
        return Response(status=HTTP_204_NO_CONTENT)

    # THIS RESTRICT TO REQUESTER MAKE A RESERVATION OF VEHICLE TYPES THAT HE DOESN'T HAVE ACCESS.
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled, IsVehicleAllowedOrAdmin]
        else:
            permission_classes = ONLY_AUTHENTICATED
        return [permission() for permission in permission_classes]

    def check_reservation_creation(self, request, validated_data):
        if not is_after_now(validated_data['start']):
            raise CannotReserveToPastError()

        vehicle = validated_data['vehicle']
        if vehicle.is_disabled:
            logger.error('Cannot reserve a vehicle disabled: {} {}'.format(vehicle.brand, vehicle.model))
            raise CannotReserveVehicleDisabled()
