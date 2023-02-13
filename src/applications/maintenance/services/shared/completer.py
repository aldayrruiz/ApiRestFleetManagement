from applications.maintenance.models import MaintenanceStatus
from applications.maintenance.services.emails.completed import MaintenanceOperationCompletedEmail


class OperationCompleter:
    @staticmethod
    def notify_operation_completed_if_last_one_pending_or_expired(queryset, new_operation):
        last_operation = queryset.last()
        if last_operation.status in [MaintenanceStatus.PENDING, MaintenanceStatus.EXPIRED]:
            MaintenanceOperationCompletedEmail(new_operation.tenant, last_operation).send()
