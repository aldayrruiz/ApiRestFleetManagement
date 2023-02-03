from applications.maintenance.models import MaintenanceStatus, WheelsOperation
from applications.maintenance.services.shared.state import StateUpdater
from applications.vehicles.models import Vehicle


class WheelsStatusUpdater:

    def __init__(self, tenant):
        self.tenant = tenant

    def update(self):
        vehicles = Vehicle.objects.filter(tenant=self.tenant)
        for vehicle in vehicles:
            self.__update_itv_states_of_vehicle(vehicle)

    @staticmethod
    def __update_itv_states_of_vehicle(vehicle):
        for wheels in vehicle.wheels.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING],
                                            operation=WheelsOperation.Substitution):
            StateUpdater.update_register(wheels)
