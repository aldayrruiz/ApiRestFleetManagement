from applications.traccar.utils import get
from utils.dates import from_date_to_str_date_traccar


class TraccarAPI:
    @staticmethod
    def get(device_id, _from, _to, route: str):
        start_str = from_date_to_str_date_traccar(_from)
        end_str = from_date_to_str_date_traccar(_to)
        params = {'deviceId': device_id, 'from': start_str, 'to': end_str}
        response = get(target=route, params=params)
        return response
