from rest_framework.exceptions import APIException


class ReservationHasNotYetStarted(APIException):
    status_code = 400
    default_detail = 'La reserva aún no ha comenzado'
