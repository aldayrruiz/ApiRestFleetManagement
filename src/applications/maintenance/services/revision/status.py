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
            self.__update_revision_states_of_vehicle(vehicle)

    def __update_revision_states_of_vehicle(self, vehicle):
        last_revision = vehicle.revisions.order_by('date').last()
        # Si la última revisión está completa, significa que se ha eliminado previamente la última operación, quedando
        # esta última con un estado que no debería tener de revisión. Por lo tanto, se debe actualizar el estado de la
        # última revisión a PENDING o EXPIRED.
        if last_revision and last_revision.status == MaintenanceStatus.COMPLETED:
            self.update_register(last_revision)

        for revision in vehicle.revisions.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            self.update_register(revision)
