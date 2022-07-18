from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from applications.traccar.utils import get
from utils.dates import from_date_to_str_date_traccar

PRECAUTION_DAYS = 3


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
        precaution_start, precaution_end = TraccarAPI.precautions(start, end)
        response = TraccarAPI.get(device_id, precaution_start, precaution_end, 'reports/trips')
        trips = response.json()
        trips = list(filter(lambda trip:
                            parse(trip['startTime']) >= start and
                            parse(trip['endTime']) <= end, trips))
        return trips

    @staticmethod
    def stops(device_id, start, end):
        precaution_start, precaution_end = TraccarAPI.precautions(start, end)
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
