from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.cleaning.queryset import get_cleaning_queryset
from applications.maintenance.services.shared.completer import OperationCompleter


class CleaningCompleter:
    """
    This class manage the case when a operation is created, old ones should be updated to status completed.
    """

    def __init__(self, new_cleaning):
        self.new_cleaning = new_cleaning
        self.requester = new_cleaning.owner
        self.vehicle = new_cleaning.vehicle

    def update_old_ones_to_completed(self):
        queryset = get_cleaning_queryset(self.requester, self.vehicle.id)
        old_cleanings = queryset.exclude(pk=self.new_cleaning.id).all()
        OperationCompleter.notify_operation_completed_if_last_one_pending_or_expired(old_cleanings, self.new_cleaning)
        old_cleanings.update(status=MaintenanceStatus.COMPLETED)

