from django.template.loader import render_to_string

from applications.reports.models import MonthlyReport
from applications.tenants.models import Tenant
from applications.users.services.search import get_interventors
from utils.email.shared import EmailSender


class VehicleUseReportEmail(EmailSender):
    def __init__(self, tenant: Tenant, report: MonthlyReport):
        self.tenant = tenant
        self.subject = 'Informe de uso de vehículos'
        self.body = self.get_body()
        self.interventors = self.get_interventor_emails()
        self.report = report
        super().__init__(self.interventors, self.subject)

    def get_interventor_emails(self):
        interventors = get_interventors(self.tenant)
        emails = list(map(lambda user: user.email, interventors))
        emails = ', '.join(emails)
        return emails

    def get_body(self):
        body = render_to_string('use_of_vehicles.html')
        return body

    def attach_report(self):
        pdf = self.report.pdf
        filename = f'InformeDeUsoDeVehiculos{self.report.month}_{self.report.year}.pdf'
        self.attach_pdf(pdf, filename)

    def send(self):
        if not self.interventors:
            return
        self.attach_html(self.body)
        self.attach_report()
        super().send()
