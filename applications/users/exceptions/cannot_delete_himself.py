from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_403_FORBIDDEN


class CannotDeleteHimselfError(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_detail = 'User cannot delete himself'
