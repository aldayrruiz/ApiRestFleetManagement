import logging

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from applications.traccar.utils import get
from utils.dates import from_date_to_str_date_traccar

PRECAUTION_DAYS = 1
PRECAUTION_HOURS = 3

logger = logging.getLogger(__name__)


class TraccarAPI:
    @staticmethod
    def get(device_id, _from, _to, route: str):
        start_str = from_date_to_str_date_traccar(_from)
        end_str = from_date_to_str_date_traccar(_to)
        params = {'deviceId': device_id, 'from': start_str, 'to': end_str}
        response = get(target=route, params=params)
        return response

    @staticmethod
    def trips(device_id, start, end):
        precaution_start, precaution_end = TraccarAPI.new_precautions(start, end)
        response = TraccarAPI.get(device_id, precaution_start, precaution_end, 'reports/trips')
        all_trips = response.json()
        trips = list(
            filter(lambda trip: parse(trip['startTime']) >= start and parse(trip['endTime']) <= end, all_trips))
        return trips

    @staticmethod
    def new_trips(device_id, start, end):
        precaution_start, precaution_end = TraccarAPI.new_precautions(start, end)
        response = TraccarAPI.get(device_id, precaution_start, precaution_end, 'reports/trips')
        trips = response.json()
        return trips

    @staticmethod
    def new_stops(device_id, start, end):
        precaution_start, precaution_end = TraccarAPI.new_precautions(start, end)
        response = TraccarAPI.get(device_id, precaution_start, precaution_end, 'reports/stops', )
        stops = response.json()
        return stops

    @staticmethod
    def filter_routes(arr, start, end):
        return list(filter(lambda trip: parse(trip['startTime']) >= start and parse(trip['endTime']) <= end, arr))

    @staticmethod
    def stops(device_id, start, end):
        precaution_start, precaution_end = TraccarAPI.new_precautions(start, end)
        response = TraccarAPI.get(device_id, precaution_start, precaution_end, 'reports/stops')
        stops = response.json()
        stops = list(filter(lambda stop:
                            parse(stop['startTime']) >= start and
                            parse(stop['endTime']) <= end, stops))
        return stops

    @staticmethod
    def precautions(start, end):
        precaution_start = start - relativedelta(days=PRECAUTION_DAYS)
        precaution_end = end + relativedelta(days=PRECAUTION_DAYS)
        return precaution_start, precaution_end

    @staticmethod
    def new_precautions(start, end):
        precaution_start = start - relativedelta(hours=PRECAUTION_HOURS)
        precaution_end = end + relativedelta(hours=PRECAUTION_HOURS)
        return precaution_start, precaution_end
