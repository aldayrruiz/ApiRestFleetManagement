from applications.traccar.services.devices import TraccarDevices
from applications.traccar.services.positions import TraccarPositions


class OdometerDestroyer:

    def __init__(self, odometer):
        self.odometer = odometer
        self.vehicle = self.odometer.vehicle

    def delete(self):
        self.__rollback_to_old_kilometers()
        self.odometer.delete()

    def __rollback_to_old_kilometers(self):
        last_position = TraccarPositions.last_position(vehicle=self.vehicle)
        current_kilometers = last_position['attributes']['totalDistance'] / 1000
        # diff_kilometers = Kilómetros que se han recorrido desde el último registro de kilometraje
        diff_kilometers = current_kilometers - int(self.odometer.kilometers)
        new_kilometers = int(self.odometer.old_kilometers) + diff_kilometers
        TraccarDevices.update_total_distance(self.vehicle, new_kilometers)
