from rest_framework.exceptions import APIException


class CannotTicketOwnReservationError(APIException):
    status_code = 403
    default_detail = 'No puedes crear un ticket de tu propia reserva'
