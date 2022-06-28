from rest_framework.exceptions import APIException

from applications.reports.generate.charts.vehicle_punctuality import PunctualityChart
from applications.reports.services.punctuality import PunctualityHelpers
from applications.reservations.models import Reservation
from dateutil.relativedelta import relativedelta

from applications.traccar.services.api import TraccarAPI
from utils.dates import from_date_to_str_date_traccar


class SummaryReport:
    def __init__(self, reservation: Reservation):
        self.reservation = reservation
        self.vehicle = reservation.vehicle

    def get_summary(self):
        device_id = self.reservation.vehicle.gps_device_id
        response = TraccarAPI.get(device_id, self.reservation.start, self.reservation.end, 'reports/summary')
        if not response.ok:
            raise APIException('Could not receive report summary.', code=response.status_code)
        summary = response.json()[0]

        real_start, real_end = self.get_real_start_and_end()

        summary['realStartTime'] = from_date_to_str_date_traccar(real_start)
        summary['realEndTime'] = from_date_to_str_date_traccar(real_end)

        return summary

    def get_real_start_and_end(self):
        start = self.reservation.start
        end = self.reservation.end
        month = start.month
        year = start.year

        reservations = Reservation.objects.filter(start__month=month, start__year=year, vehicle=self.vehicle)
        reservations = reservations.order_by('start').all()
        index = list(reservations).index(self.reservation)
        previous, nxt = PunctualityHelpers.get_closer_reservations(reservations, index)
        [t_hours_out, t_hours_in, not_taken] = PunctualityChart.get_takes_punctuality(previous, self.reservation, nxt)
        [f_hours_out, f_hours_in] = PunctualityChart.get_frees_punctuality(previous, self.reservation, nxt)

        real_start = start - relativedelta(hours=t_hours_out)
        real_start = real_start + relativedelta(hours=t_hours_in)

        real_end = end - relativedelta(hours=f_hours_in)
        real_end = real_end + relativedelta(hours=f_hours_out)

        return real_start, real_end
