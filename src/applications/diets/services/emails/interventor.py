from applications.tenants.models import Tenant
from applications.users.services.search import get_interventors
from utils.email.shared import EmailSender
from decouple import config
from django.template.loader import render_to_string


class DietCompletedInterventorEmail(EmailSender):

    def __init__(self, tenant: Tenant):
        self.tenant = tenant
        self.subject = 'Reporte mensual de dietas'
        self.body = self.get_body()
        interventors = self.get_interventor_emails()
        super().__init__(interventors, self.subject)

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

    def send(self):
        self.attach_html(self.body)
        super().send()
