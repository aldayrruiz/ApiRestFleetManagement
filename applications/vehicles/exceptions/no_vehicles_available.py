from rest_framework.exceptions import APIException


class NoVehiclesAvailable(APIException):
    status_code = 409
    default_detail = 'Ningún vehículo disponible'
