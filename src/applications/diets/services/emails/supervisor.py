from applications.diets.models.diet import Diet
from applications.users.services.search import get_supervisors
from utils.email.shared import EmailSender
from decouple import config
from django.template.loader import render_to_string


class DietCompletedSupervisorEmail(EmailSender):

    def __init__(self, diet: Diet):
        self.diet = diet
        self.subject = 'Dieta completada'
        self.body = self.get_body()
        supervisors = self.get_supervisors_emails()
        super().__init__(supervisors, self.subject)

    def get_supervisors_emails(self):
        supervisors = get_supervisors(self.diet.tenant)
        emails = list(map(lambda supervisor: supervisor.email, supervisors))
        emails = ', '.join(emails)
        return emails

    def get_body(self):
        body = render_to_string(
            'supervisor.html',
            {'diet': self.diet,
             'owner': self.diet.owner,
             'baseurl': config('SERVER_URL')
             })
        return body

    def send(self):
        self.attach_html(self.body)
        super().send()