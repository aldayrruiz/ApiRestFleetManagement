from rest_framework.exceptions import APIException


class NoVehiclesAvailableError(APIException):
    status_code = 409
    default_detail = 'Ningún vehículo disponible'
