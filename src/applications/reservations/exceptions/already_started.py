from rest_framework.exceptions import APIException


class ReservationAlreadyStarted(APIException):
    status_code = 400
    default_detail = 'La reserva ya ha comenzado'
