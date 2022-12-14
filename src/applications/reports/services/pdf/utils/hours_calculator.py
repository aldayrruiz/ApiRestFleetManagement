from applications.reservations.models import Reservation
from applications.traccar.services.api import TraccarAPI
from applications.traccar.services.summary import SummaryReport
from utils.dates import get_hours_duration


class HoursCalculator:

    @staticmethod
    def get_theoretical_hours_reservation(reservation: Reservation, start_limit, end_limit):
        if reservation.start < start_limit:
            return get_hours_duration(start_limit, reservation.end)
        # Empieza detro del mes y termina en el mes siguiente.
        elif reservation.end > end_limit:
            return get_hours_duration(reservation.start, end_limit)
        # Empieza y termina dentro del mes.
        else:
            return get_hours_duration(reservation.start, reservation.end)

    @staticmethod
    def get_real_hours_reservation(reservation: Reservation):
        return 0

    @staticmethod
    def get_movement_hours(reservation: Reservation):
        real_start, real_end = SummaryReport(reservation).get_real_start_and_end()
        trips = TraccarAPI.trips(reservation.vehicle.gps_device_id, real_start, real_end)
        duration = 0
        for trip in trips:
            duration += trip['duration']

        hours = duration / 3600000
        return hours
