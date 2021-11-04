from rest_framework.exceptions import APIException
from rest_framework import status

class BusinessLogicConflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('An error occured in the business logic, what you are trying to do is not allowed')
    default_code = 'invalid'