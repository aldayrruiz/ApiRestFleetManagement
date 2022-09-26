from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_403_FORBIDDEN


class CompletedDietError(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_detail = 'La dieta ya ha sido completada.'
