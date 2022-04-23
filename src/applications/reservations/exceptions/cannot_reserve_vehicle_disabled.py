from rest_framework.exceptions import APIException


class CannotReserveVehicleDisabled(APIException):
    status_code = 400
    default_detail = 'No se puede reservar un vehículo deshabilitado'
