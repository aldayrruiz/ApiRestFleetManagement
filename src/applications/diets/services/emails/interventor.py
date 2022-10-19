from applications.diets.models import DietMonthlyPdfReport
from applications.tenants.models import Tenant
from applications.users.services.search import get_interventors
from utils.email.shared import EmailSender
from decouple import config
from django.template.loader import render_to_string


class DietCompletedInterventorEmail(EmailSender):

    def __init__(self, tenant: Tenant, report: DietMonthlyPdfReport):
        self.tenant = tenant
        self.subject = 'Reporte mensual de dietas'
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
        body = render_to_string(
            'interventor.html',
            {'users': self.tenant.users.all(),
             'baseurl': config('SERVER_URL')
             })
        return body

    def attach_report(self):
        pdf = self.report.pdf
        filename = f'ReporteMensualDietas_{self.report.month}_{self.report.year}.pdf'
        self.attach_pdf(pdf, filename)

    def send(self):
        if not self.tenant.diet:
            return
        self.attach_html(self.body)
        self.attach_report()
        super().send()
