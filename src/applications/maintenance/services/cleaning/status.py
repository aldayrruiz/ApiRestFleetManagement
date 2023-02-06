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
            self.__update_itv_states_of_vehicle(vehicle)

    def __update_itv_states_of_vehicle(self, vehicle: Vehicle):
        card = vehicle.cleaning_card
        for cleaning in vehicle.cleanings.filter(status__in=[MaintenanceStatus.NEW, MaintenanceStatus.PENDING]):
            self.__update_cleaning(cleaning, card)

    def __update_cleaning(self, cleaning: Cleaning, card: CleaningCard):
        duration = parse_duration(card.date_period)
        next_cleaning = cleaning.date_stored + duration
        caution_date = next_cleaning - relativedelta(days=7)
        if caution_date < now_utc() < next_cleaning:
            cleaning.status = MaintenanceStatus.PENDING
            self.updates_to_pending.append(cleaning)
            cleaning.save()
        if now_utc() > next_cleaning:
            cleaning.status = MaintenanceStatus.EXPIRED
            self.updates_to_expired.append(cleaning)
            cleaning.save()

