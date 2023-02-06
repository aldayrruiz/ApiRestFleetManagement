from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.shared.status import StateUpdater
from applications.vehicles.models import Vehicle


class RevisionStatusUpdater(StateUpdater):

    def __init__(self, tenant):
        super().__init__(tenant)
        self.tenant = tenant

    def update(self):
        vehicles = Vehicle.objects.filter(tenant=self.tenant)
        for vehicle in vehicles:
            self.__update_itv_states_of_vehicle(vehicle)

    def __update_itv_states_of_vehicle(self, vehicle):
        for revision in vehicle.revisions.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            self.update_register(revision)
