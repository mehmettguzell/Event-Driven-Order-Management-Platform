from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

from users.exceptions import DomainException

def custom_exception_handler(exc, context):
    if isinstance(exc, DomainException):
        return Response(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": exc.code,
                    "message": exc.message
                }
            },
            status=status.HTTP_400_BAD_REQUEST
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
