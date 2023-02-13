from applications.maintenance.models import MaintenanceStatus, WheelsOperation
from applications.maintenance.services.shared.status import StateUpdater
from applications.vehicles.models import Vehicle


class WheelsStatusUpdater(StateUpdater):

    def __init__(self, tenant):
        super().__init__(tenant)
        self.tenant = tenant

    def update(self):
        vehicles = Vehicle.objects.filter(tenant=self.tenant)
        for vehicle in vehicles:
            self.__update_itv_states_of_vehicle(vehicle)

    def __update_itv_states_of_vehicle(self, vehicle):
        last_wheels = vehicle.wheels.last()
        # Si la última revisión está completa, significa que se ha eliminado previamente la última operación, quedando
        # esta última con un estado que no debería tener de revisión. Por lo tanto, se debe actualizar el estado de la
        # última revisión a PENDING o EXPIRED.
        if last_wheels.status == MaintenanceStatus.COMPLETED:
            self.update_register(last_wheels)

        for wheels in vehicle.wheels.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING],
                                            operation=WheelsOperation.Substitution):
            self.update_register(wheels)
