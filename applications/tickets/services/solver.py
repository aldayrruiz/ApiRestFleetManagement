from applications.tickets.models import TicketStatus
from utils.email.emailtickets import send_accepted_ticket_email, send_denied_ticket_email, \
    send_reservation_deleted_email


def solve_ticket(ticket, new_status):
    if new_status == TicketStatus.UNSOLVED:
        print("You can't solve a ticket to unsolved")
        return None
    elif new_status == TicketStatus.ACCEPTED:
        send_reservation_deleted_email(ticket.reservation)
        send_accepted_ticket_email(ticket)
        ticket.reservation.delete()
    elif new_status == TicketStatus.DENIED:
        send_denied_ticket_email(ticket)

    ticket.status = new_status
