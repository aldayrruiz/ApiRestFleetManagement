from dateutil.relativedelta import relativedelta

from applications.maintenance.models import MaintenanceStatus
from applications.traccar.services.positions import TraccarPositions
from utils.dates import now_utc


class StateUpdater:

    def __init__(self, tenant):
        self.tenant = tenant
        self.updates_to_pending = []
        self.updates_to_expired = []

    def update_register(self, register):
        caution_date = register.next_revision - relativedelta(months=1)
        state_changed_by_date = None
        if now_utc() < caution_date:
            state_changed_by_date = MaintenanceStatus.NEW
        if caution_date < now_utc() < register.next_revision:
            state_changed_by_date = MaintenanceStatus.PENDING
        if now_utc() > register.next_revision:
            state_changed_by_date = MaintenanceStatus.EXPIRED

        # If user has not set next kilometers, we don't need to check it. So save and return.
        if register.next_kilometers in [None, 0]:
            register.state = state_changed_by_date
            register.save()
            return

        vehicle = register.vehicle
        last_position = TraccarPositions.last_position(vehicle)
        current_kilometers = last_position['attributes']['totalDistance'] / 1000
        state_changed_by_km = None
        caution_kilometers = register.next_kilometers - 1000
        if current_kilometers < caution_kilometers:
            state_changed_by_km = MaintenanceStatus.NEW
        if caution_kilometers < current_kilometers < register.next_kilometers:
            state_changed_by_km = MaintenanceStatus.PENDING
        if current_kilometers > register.next_kilometers:
            state_changed_by_km = MaintenanceStatus.EXPIRED

        # Actualizar el estado del registro o bien por fecha o bien por kilómetros. El estado que se actualice será el
        # mayor de los dos.
        states_to_numbers = {MaintenanceStatus.NEW: 0, MaintenanceStatus.PENDING: 1, MaintenanceStatus.EXPIRED: 2,
                             MaintenanceStatus.COMPLETED: 3}
        date_number = states_to_numbers[state_changed_by_date]
        km_number = states_to_numbers[state_changed_by_km]
        max_number = max(date_number, km_number)
        new_state = list(states_to_numbers.keys())[max_number]
        register.state = new_state
        register.save()
        if new_state == MaintenanceStatus.EXPIRED:
            self.updates_to_expired.append(register)
        if new_state == MaintenanceStatus.PENDING:
            self.updates_to_pending.append(register)
