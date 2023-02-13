from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.emails.completed import MaintenanceOperationCompletedEmail
from applications.maintenance.services.shared.completer import OperationCompleter
from applications.maintenance.services.wheels.queryset import get_wheels_queryset


class WheelsCompleter:
    """
    This class manage the case when a wheels operation is created, old ones should be updated to status completed.
    """

    def __init__(self, new_wheels):
        self.new_wheels = new_wheels
        self.requester = new_wheels.owner
        self.vehicle = new_wheels.vehicle

    def update_old_ones_to_completed(self):
        queryset = get_wheels_queryset(self.requester, self.vehicle.id)
        old_wheels = queryset.exclude(pk=self.new_wheels.id).all()
        OperationCompleter.notify_operation_completed_if_last_one_pending_or_expired(old_wheels, self.new_wheels)
        old_wheels.update(status=MaintenanceStatus.COMPLETED)
