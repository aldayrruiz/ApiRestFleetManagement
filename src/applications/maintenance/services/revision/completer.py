from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.revision.queryset import get_revision_queryset
from applications.maintenance.services.shared.completer import OperationCompleter


class RevisionCompleter:
    """
    This class manage the case when a revision operation is created, old ones should be updated to status completed.
    """

    def __init__(self, new_revision):
        self.new_revision = new_revision
        self.requester = new_revision.owner
        self.vehicle = new_revision.vehicle

    def update_old_ones_to_completed(self):
        queryset = get_revision_queryset(self.requester, self.vehicle.id)
        old_revisions = queryset.exclude(pk=self.new_revision.id).all()
        OperationCompleter.notify_operation_completed_if_last_one_pending_or_expired(old_revisions, self.new_revision)
        old_revisions.update(status=MaintenanceStatus.COMPLETED)
