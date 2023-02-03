from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.shared.state import StateUpdater
from applications.vehicles.models import Vehicle


class RevisionStatusUpdater:

    def __init__(self, tenant):
        self.tenant = tenant

    def update(self):
        vehicles = Vehicle.objects.filter(tenant=self.tenant)
        for vehicle in vehicles:
            self.__update_itv_states_of_vehicle(vehicle)

    @staticmethod
    def __update_itv_states_of_vehicle(vehicle):
        for revision in vehicle.revisions.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            StateUpdater.update_register(revision)
