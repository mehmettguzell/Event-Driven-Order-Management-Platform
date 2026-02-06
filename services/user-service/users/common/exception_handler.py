from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

from users.exceptions import DomainException

DOMAIN_EXCEPTION_STATUS_MAP = {
    "INVALID_CREDENTIALS": status.HTTP_401_UNAUTHORIZED,
    "USER_INACTIVE": status.HTTP_403_FORBIDDEN,
}


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainException):
        status_code = DOMAIN_EXCEPTION_STATUS_MAP.get(exc.code, status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": exc.code,
                    "message": exc.message
                }
            },
            status=status_code
        )

    response = drf_exception_handler(exc, context)

    if response is not None:
        return Response(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": response.data
                }
            },
            status=response.status_code
        )

    return Response(
        {
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Unexpected error"
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
