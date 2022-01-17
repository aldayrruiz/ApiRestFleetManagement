from rest_framework.exceptions import APIException


class IncidentAlreadySolvedError(APIException):
    status_code = 400
    default_detail = 'La incidencia ya ha sido solucionada'
