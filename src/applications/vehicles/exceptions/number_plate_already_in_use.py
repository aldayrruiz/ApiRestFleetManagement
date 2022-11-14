from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_403_FORBIDDEN


class NumberPlateAlreadyInUse(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_detail = 'Ya existe un vehículo con esa matricula'
