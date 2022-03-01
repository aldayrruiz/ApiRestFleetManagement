from rest_framework.exceptions import APIException


class YouAlreadyPossesOtherReservationAtSameTime(APIException):
    status_code = 400
    default_detail = 'Ya tienes una reserva para este momento'
