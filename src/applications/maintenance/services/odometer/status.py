from applications.maintenance.models import MaintenanceStatus, Odometer, OdometerCard
from applications.traccar.services.positions import TraccarPositions
from applications.vehicles.models import Vehicle


class OdometerStatusUpdater:

    def __init__(self, tenant):
        self.tenant = tenant
        self.updates_to_pending = []
        self.updates_to_expired = []

    def update(self):
        try:
            card = self.tenant.odometer_card
        except OdometerCard.DoesNotExist:
            return
        vehicles = Vehicle.objects.filter(tenant=self.tenant)
        for vehicle in vehicles:
            self.__update_odometer_states_of_vehicle(vehicle, card)

    def __update_odometer_states_of_vehicle(self, vehicle: Vehicle, card: OdometerCard):
        last_odometer = vehicle.odometers.order_by('date').last()
        # Si la última limpieza está completa, significa que se ha eliminado previamente la última operación, quedando
        # esta última con un estado que no debería tener de limpieza. Por lo tanto, se debe actualizar el estado de la
        # última limpieza a PENDING o EXPIRED.
        if last_odometer and last_odometer.status == MaintenanceStatus.COMPLETED:
            self.__update_odometer(last_odometer, card)

        # Se actualizan los estados de las limpiezas NEW o PENDING. Los estados EXPIRED o COMPLETED no se actualizan.
        for odometer in vehicle.odometers.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            self.__update_odometer(odometer, card)

    def __update_odometer(self, odometer: Odometer, card: OdometerCard):
        km_period = card.km_period
        km_limit = odometer.old_kilometers + km_period
        km_caution = km_limit - 1000
        last_position = TraccarPositions.last_position(odometer.vehicle)
        current_kilometers = last_position['attributes']['totalDistance'] / 1000

        # Get new status
        new_status = None
        if current_kilometers < km_caution:
            new_status = MaintenanceStatus.NEW
        if km_caution <= current_kilometers <= km_limit:
            new_status = MaintenanceStatus.PENDING
        elif current_kilometers > km_limit:
            new_status = MaintenanceStatus.EXPIRED

        # Send email
        if new_status == odometer.status:
            # Si el estado no ha cambiado, no se envía el email
            return
        elif new_status == MaintenanceStatus.PENDING:
            self.updates_to_pending.append(odometer)
        elif new_status == MaintenanceStatus.EXPIRED:
            self.updates_to_expired.append(odometer)

        # Update status
        odometer.status = new_status
        odometer.save()
