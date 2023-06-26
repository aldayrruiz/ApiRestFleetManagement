from dateutil.relativedelta import relativedelta
from applications.maintenance.models import MaintenanceStatus, Itv
from applications.vehicles.models import Vehicle
from utils.dates import now_utc


class ItvStatusUpdater:

    def __init__(self, tenant):
        self.tenant = tenant
        self.updates_to_pending = []
        self.updates_to_expired = []

    def update(self):
        vehicles = Vehicle.objects.filter(tenant=self.tenant)
        for vehicle in vehicles:
            self.__update_itv_states_of_vehicle(vehicle)

    def __update_itv_states_of_vehicle(self, vehicle):
        last_itv = vehicle.itvs.order_by('date').last()
        # Si la última ITV está completa, significa que se ha eliminado previamente la última operación, quedando
        # esta última con un estado que no debería tener de ITV. Por lo tanto, se debe actualizar el estado de la
        # última ITV a PENDING o EXPIRED.
        if last_itv and last_itv.status == MaintenanceStatus.COMPLETED:
            self.__update_itv(last_itv)
        for itv in vehicle.itvs.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            self.__update_itv(itv)

    def __update_itv(self, itv: Itv):
        caution_date = itv.next_revision - relativedelta(months=1)
        new_status = None
        if now_utc() < caution_date:
            new_status = MaintenanceStatus.NEW
        if caution_date < now_utc() < itv.next_revision:
            new_status = MaintenanceStatus.PENDING
            self.updates_to_pending.append(itv)
        if now_utc() > itv.next_revision:
            new_status = MaintenanceStatus.EXPIRED
            self.updates_to_expired.append(itv)
        if new_status == itv.status:
            return
        itv.status = new_status
        itv.save()
