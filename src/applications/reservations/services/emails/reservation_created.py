from django.template.loader import render_to_string

from applications.reservations.models import Reservation
from applications.users.services.search import get_supervisors
from utils.email.shared import EmailSender


class ReservationCreatedSupervisorEmail(EmailSender):
    def __init__(self, reservation: Reservation):
        self.reservation = reservation
        self.owner = self.reservation.owner
        self.tenant = reservation.tenant
        self.subject = 'Reserva creada'
        self.body = self.get_body()
        self.supervisors = self.get_supervisors_emails()
        super().__init__(self.supervisors, self.subject)

    def get_supervisors_emails(self):
        supervisors = get_supervisors(self.tenant)
        emails = list(map(lambda supervisor: supervisor.email, supervisors))
        emails = ', '.join(emails)
        return emails

    def get_future_recurrent_reservations(self):
        recurrent_id = self.reservation.recurrent_id
        start = self.reservation.start
        future_reservations = Reservation.objects.filter(owner=self.owner, recurrent_id=recurrent_id,
                                                         start__gt=start).reverse()
        return future_reservations

    def get_body(self):
        future_reservations = self.get_future_recurrent_reservations()
        body = render_to_string(
            'reservation_created.html',
            {'reservation': self.reservation,
             'owner': self.owner,
             'vehicle': self.reservation.vehicle,
             'future_reservations': future_reservations
             })
        return body

    def send(self):
        if not self.tenant.diet or not self.supervisors:
            return None
        self.attach_html(self.body)
        super().send()
