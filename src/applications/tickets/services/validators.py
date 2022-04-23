from applications.tickets.exceptions.cannot_ticket_own_reservation import CannotTicketOwnReservationError


def check_if_not_mine(requester, obj):
    if requester is obj.owner:
        raise CannotTicketOwnReservationError()
