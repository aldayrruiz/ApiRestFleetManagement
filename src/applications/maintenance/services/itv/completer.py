from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.itv.queryset import get_itv_queryset
from applications.maintenance.services.shared.completer import OperationCompleter


class ItvCompleter:
    """
    This class manage the case when a operation is created, old ones should be updated to status completed.
    """

    def __init__(self, new_itv):
        self.new_itv = new_itv
        self.requester = new_itv.owner
        self.vehicle = new_itv.vehicle

    def update_old_ones_to_completed(self):
        queryset = get_itv_queryset(self.requester, self.vehicle.id)
        old_itvs = queryset.exclude(pk=self.new_itv.id).all()
        OperationCompleter.notify_operation_completed_if_last_one_pending_or_expired(old_itvs, self.new_itv)
        old_itvs.update(status=MaintenanceStatus.COMPLETED)
