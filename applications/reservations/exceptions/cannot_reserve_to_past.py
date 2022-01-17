from rest_framework.exceptions import APIException


class CannotReserveToPastError(APIException):
    status_code = 400
    default_detail = 'No se puede reservar para una fecha anterior a la actual'
