from applications.maintenance.serializers.odometer.odometer import CreateOdometerSerializer
from applications.traccar.services.devices import TraccarDevices
from applications.traccar.services.positions import TraccarPositions


class OdometerCreator:
    def __init__(self, serializer: CreateOdometerSerializer):
        self.serializer = serializer
        self.vehicle = self.serializer.validated_data['vehicle']

    def save(self):
        # Get current_kilometers kilometers & save it because of rollback
        last_position = TraccarPositions.last_position(vehicle=self.vehicle)
        current_kilometers = last_position['attributes']['totalDistance'] / 1000
        self.serializer.save(old_kilometers=current_kilometers)
        self.__update_total_distance()

    def __update_total_distance(self):
        kilometers = self.serializer.validated_data['kilometers']
        TraccarDevices.update_total_distance(self.vehicle, kilometers)
