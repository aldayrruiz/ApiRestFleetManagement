from decouple import config

from applications.incidents.models import Incident
from applications.users.services.search import get_admins
from utils.email.shared import EmailSender
from django.template.loader import render_to_string


class IncidentCreatedEmail(EmailSender):

    def __init__(self, incident: Incident):
        self.incident = incident
        self.reservation = self.incident.reservation
        self.owner = self.incident.owner
        self.vehicle = self.reservation.vehicle
        self.subject = self.get_subject()
        self.admins = self.get_admin_emails()
        self.body = self.get_body()
        super().__init__(self.admins, self.subject)

    def get_admin_emails(self):
        admins = get_admins(self.incident.tenant)
        emails = list(map(lambda user: user.email, admins))
        emails = ', '.join(emails)
        return emails

    def get_subject(self):
        return f'Incidencia: {self.vehicle.brand} {self.vehicle.model} - {self.incident.get_type_display()}'

    def get_body(self):
        payload = {'incident': self.incident, 'vehicle': self.vehicle, 'reservation': self.reservation,
                   'base_url': config('SERVER_URL')}
        body = render_to_string('created.html', payload)
        return body

    def send(self):
        self.attach_html(self.body)
        super().send()
