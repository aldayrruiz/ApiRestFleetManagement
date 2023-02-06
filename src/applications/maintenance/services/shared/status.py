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
        if caution_date < now_utc() < register.next_revision:
            register.status = MaintenanceStatus.PENDING
            self.updates_to_pending.append(register)
            register.save()
            return
        if now_utc() > register.next_revision:
            register.status = MaintenanceStatus.EXPIRED
            self.updates_to_expired.append(register)
            register.save()
            return

        # If user has not set next kilometers, we don't need to check it
        if register.next_kilometers in [None, 0]:
            return

        vehicle = register.vehicle
        last_position = TraccarPositions.last_position(vehicle)
        current_kilometers = last_position['attributes']['totalDistance'] / 1000

        caution_kilometers = register.next_kilometers - 1000
        if caution_kilometers < current_kilometers < register.next_kilometers:
            register.status = MaintenanceStatus.PENDING
            self.updates_to_pending.append(register)
            register.save()
            return
        if current_kilometers > register.next_kilometers:
            register.status = MaintenanceStatus.EXPIRED
            self.updates_to_expired.append(register)
            register.save()
            return
