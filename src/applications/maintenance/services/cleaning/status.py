from dateutil.relativedelta import relativedelta
from isoduration import parse_duration
from applications.maintenance.models import MaintenanceStatus, Cleaning, CleaningCard
from applications.vehicles.models import Vehicle
from utils.dates import now_utc


class CleaningStatusUpdater:

    def __init__(self, tenant):
        self.tenant = tenant
        self.updates_to_pending = []
        self.updates_to_expired = []

    def update(self):
        vehicles = Vehicle.objects.filter(tenant=self.tenant, cleaning_card__isnull=False)
        for vehicle in vehicles:
            self.__update_cleaning_states_of_vehicle(vehicle)

    def __update_cleaning_states_of_vehicle(self, vehicle: Vehicle):
        card = vehicle.cleaning_card
        last_cleaning = vehicle.cleanings.last()
        # Si la última limpieza está completa, significa que se ha eliminado previamente la última operación, quedando
        # esta última con un estado que no debería tener de limpieza. Por lo tanto, se debe actualizar el estado de la
        # última limpieza a PENDING o EXPIRED.
        if last_cleaning and last_cleaning.status == MaintenanceStatus.COMPLETED:
            self.__update_cleaning(last_cleaning, card)

        # Se actualizan los estados de las limpiezas NEW o PENDING. Los estados EXPIRED o COMPLETED no se actualizan.
        for cleaning in vehicle.cleanings.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            self.__update_cleaning(cleaning, card)

    def __update_cleaning(self, cleaning: Cleaning, card: CleaningCard):
        duration = parse_duration(card.date_period)
        next_cleaning = cleaning.date + duration
        caution_date = next_cleaning - relativedelta(days=7)
        if now_utc() < caution_date:
            cleaning.status = MaintenanceStatus.NEW
        if caution_date < now_utc() < next_cleaning:
            cleaning.status = MaintenanceStatus.PENDING
            self.updates_to_pending.append(cleaning)
        if now_utc() > next_cleaning:
            cleaning.status = MaintenanceStatus.EXPIRED
            self.updates_to_expired.append(cleaning)
        cleaning.save()
