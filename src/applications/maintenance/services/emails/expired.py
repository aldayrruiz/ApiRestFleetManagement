from django.template.loader import render_to_string

from applications.maintenance.services.emails.helper import MaintenanceOperationEmailSender
from applications.tenants.models import Tenant
from applications.users.services.search import get_admins
from utils.email.shared import EmailSender


class MaintenanceOperationExpiredEmail(EmailSender, MaintenanceOperationEmailSender):

    def __init__(self, tenant: Tenant, operation, operation_label: str, cause_label: str = None):
        self.tenant = tenant
        self.operation = operation
        self.operation_label = operation_label
        self.cause_label = cause_label
        self.vehicle_label = self.get_vehicle_label(self.operation.vehicle)
        self.subject = f'Operación de mantenimiento caducada'
        self.body = self.get_body()
        self.admins = self.get_admin_emails()

        super().__init__(self.admins, self.subject)

    def get_admin_emails(self):
        admins = get_admins(self.tenant)
        emails = list(map(lambda user: user.email, admins))
        emails = ', '.join(emails)
        return emails

    def get_body(self):
        body = render_to_string('maintenance/expired.html',
                                {'vehicle': self.operation.vehicle,
                                 'operation_label': self.operation_label,
                                 'cause_label': self.cause_label,
                                 'url': self.get_maintenance_url()})
        return body

    def send(self):
        if not self.admins:
            return
        self.attach_html(self.body)
        super().send()
