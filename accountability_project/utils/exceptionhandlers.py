import uuid
from rest_framework.exceptions import APIException
from rest_framework import status

class BusinessLogicConflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('An error occured in the business logic, what you are trying to do is not allowed')
    default_code = 'invalid'


class LimitReachedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Limit reached'
    default_code = 'limit_reached'

    def __init__(self, *, code: str, current: int, limit: int, detail: str | None = None, instance: str | None = None, status_code: int | None = None):
        # build a request-ish instance id if none provided
        if instance is None:
            instance = f"/requests/{uuid.uuid4()}"
        body = {
            "detail": detail or "Cannot create more items.",
            "instance": instance,
            "error": {
                "code": code,
                "meta": {"limit": limit, "current": current}
            }
        }
        self.detail = body
        if status_code:
            self.status_code = status_code