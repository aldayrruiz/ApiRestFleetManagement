from rest_framework.exceptions import APIException

from applications.traccar.utils import get
from applications.vehicles.models import Vehicle


class TraccarPositions:

    @staticmethod
    def last_position(vehicle: Vehicle):
        """
        Last position of a vehicle.
        """
        device_id = vehicle.gps_device_id
        params = {'deviceId': device_id}
        response = get(target='positions', params=params)
        if not response.ok:
            raise APIException('Could not receive positions.', code=response.status_code)
        return response.json()[0]
