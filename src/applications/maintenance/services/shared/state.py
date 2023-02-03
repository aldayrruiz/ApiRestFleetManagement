from dateutil.relativedelta import relativedelta

from applications.maintenance.models import MaintenanceStatus
from applications.traccar.services.positions import TraccarPositions
from utils.dates import now_utc


class StateUpdater:
    @staticmethod
    def update_register(register):
        caution_date = register.next_revision - relativedelta(months=1)
        if caution_date < now_utc() < register.next_revision:
            register.status = MaintenanceStatus.PENDING
            register.save()
            return
        if now_utc() > register.next_revision:
            register.status = MaintenanceStatus.EXPIRED
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
        if current_kilometers > register.next_kilometers:
            register.status = MaintenanceStatus.EXPIRED
        register.save()
