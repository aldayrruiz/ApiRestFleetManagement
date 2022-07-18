import logging

from dateutil import parser
from dateutil.relativedelta import relativedelta
from applications.traccar.services.api import TraccarAPI


logger = logging.getLogger(__name__)


class PunctualityHelpers:

    @staticmethod
    def get_precaution_bounds(reservation):
        initial_limit = reservation.start - relativedelta(days=3)
        final_limit = reservation.end + relativedelta(days=3)
        return initial_limit, final_limit

    @staticmethod
    def get_reservation_bounds(previous, current, next_res):
        start_bound = current.start - relativedelta(hours=1)
        end_bound = current.end + relativedelta(hours=1)

        if previous:
            if start_bound < previous.end:
                start_bound = previous.end
        if next_res:
            if end_bound > next_res.start:
                end_bound = next_res.start
        return start_bound, end_bound

    @staticmethod
    def vehicle_moved_during_reservation(reservation):
        device_id = reservation.vehicle.gps_device.id
        start = reservation.start
        end = reservation.end

        summary = TraccarAPI.get(device_id, start, end, 'reports/summary').json()
        if summary[0]['distance'] == 0:
            logger.error('El vehículo no se ha movido, ergo NO HA OCURRIDO')
            return False
        return True

    @staticmethod
    def stopped_at_reservation_start(reservation, stops):
        for stop in stops:
            stop_start, stop_end = parser.parse(stop['startTime']), parser.parse(stop['endTime'])
            if stop_start < reservation.start < stop_end:
                return True
        return False

    @staticmethod
    def get_trip_at(datetime, trips):
        for trip in trips:
            start, end = parser.parse(trip['startTime']), parser.parse(trip['endTime'])
            if start < datetime < end:
                return trip

    @staticmethod
    def get_hours_difference(last, first):
        diff = last - first
        hours = diff.total_seconds() / 3600
        return hours

    @staticmethod
    def get_takes_hours_from_trips(trips, reservation):
        if not trips:
            return 0

        first_trip = trips[0]
        first_move = parser.parse(first_trip['startTime'])
        if first_move > reservation.end:
            # El primer movimiento está fuera de la reserva.
            hours = PunctualityHelpers.get_hours_difference(reservation.end, reservation.start)
            return hours
        # Por el contrario, el primer movimiento está dentro de la reserva
        hours = PunctualityHelpers.get_hours_difference(first_move, reservation.start)
        return hours

    @staticmethod
    def get_frees_hours_from_trips(trips, reservation):
        if not trips:
            return 0
        last_trip = trips[-1]
        last_trip = parser.parse(last_trip['endTime'])
        hours = PunctualityHelpers.get_hours_difference(reservation.end, last_trip)
        return hours

    @staticmethod
    def get_closer_reservations(reservations, index):
        try:
            previous_reservation = reservations[index - 1]
        except ValueError or IndexError:
            previous_reservation = None
        try:
            next_reservation = reservations[index + 1]
        except IndexError:
            next_reservation = None
        return previous_reservation, next_reservation
