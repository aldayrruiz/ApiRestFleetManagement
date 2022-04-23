from rest_framework.exceptions import APIException


class NotAllVehiclesWereFoundError(APIException):
    status_code = 400
    default_detail = 'No todos los vehículos fueron encontrados'
