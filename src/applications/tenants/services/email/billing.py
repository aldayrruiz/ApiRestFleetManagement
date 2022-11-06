from django.template.loader import render_to_string

from applications.tenants.models import Tenant, TenantBillingMonthlyPdfReport
from applications.users.models import Role
from utils.email.shared import EmailSender


class TenantBillingEmail(EmailSender):
    def __init__(self, tenant: Tenant, report: TenantBillingMonthlyPdfReport):
        self.tenant = tenant
        self.subject = 'Informe de facturación mensual'
        self.body = self.get_body()
        self.admins = self.get_admin_emails()
        self.report = report
        super().__init__(self.admins, self.subject)

    def get_admin_emails(self):
        admins = self.tenant.users.filter(role=Role.ADMIN)
        emails = list(map(lambda user: user.email, admins))
        emails = ', '.join(emails)
        return emails

    def get_body(self):
        body = render_to_string('tenant_billing.html')
        return body

    def attach_report(self):
        pdf = self.report.pdf
        filename = f'InformeMensualFacturacion_{self.report.month}_{self.report.year}.pdf'
        self.attach_pdf(pdf, filename)

    def send(self):
        self.attach_html(self.body)
        self.attach_report()
        super().send()
