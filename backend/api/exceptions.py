from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    status_code = 400
    detail = 'Неудачный запрос'
