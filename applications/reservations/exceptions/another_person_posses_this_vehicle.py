from rest_framework.exceptions import APIException


class AnotherPersonPossesThisVehicle(APIException):
    status_code = 400
    default_detail = 'Otra persona tiene reservado este vehículo'
