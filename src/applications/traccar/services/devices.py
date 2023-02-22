from rest_framework.exceptions import APIException

from applications.traccar.utils import get, put
from applications.vehicles.models import Vehicle


class TraccarDevices:
    @staticmethod
    def get(vehicle: Vehicle):
        """
        List of devices.
        """
        device_id = vehicle.gps_device_id
        params = {'id': device_id}
        response = get(target='devices', params=params)
        if not response.ok:
            raise APIException('Could not receive devices.', code=response.status_code)
        return response.json()[0]

    @staticmethod
    def update_total_distance(vehicle: Vehicle, kilometers: int):
        """
        Update total distance of a device.
        """
        device_id = vehicle.gps_device_id
        target = f'devices/{device_id}/accumulators'
        # Distance must be passed to Traccar in meters
        data = {'deviceId': device_id, 'totalDistance': int(kilometers) * 1000}
        response = put(target=target, data=data)
        if not response.ok:
            raise APIException('Could not update device.', code=response.status_code)
        return response
