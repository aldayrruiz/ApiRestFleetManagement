from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.odometer.queryset import get_odometer_queryset
from applications.maintenance.services.shared.completer import OperationCompleter


class OdometerCompleter:
    """
    This class manage the case when a operation is created, old ones should be updated to status completed.
    """

    def __init__(self, new_odometer):
        self.new_odometer = new_odometer
        self.requester = new_odometer.owner
        self.vehicle = new_odometer.vehicle

    def update_old_ones_to_completed(self):
        queryset = get_odometer_queryset(self.requester, self.vehicle.id)
        old_odometers = queryset.exclude(pk=self.new_odometer.id, status=MaintenanceStatus.COMPLETED).all()
        OperationCompleter.notify_operation_completed_if_last_one_pending_or_expired(old_odometers, self.new_odometer)
        old_odometers.update(status=MaintenanceStatus.COMPLETED)
