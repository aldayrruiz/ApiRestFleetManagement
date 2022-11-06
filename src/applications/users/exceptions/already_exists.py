from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_403_FORBIDDEN


class UserAlreadyExistsError(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_detail = 'El usuario ya existe'
