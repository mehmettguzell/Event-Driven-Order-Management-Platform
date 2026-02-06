"""
Custom exception handler for consistent error responses.
All errors are formatted in the same structure for frontend compatibility.

Response Format:
{
    "success": false,
    "data": null,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {...}  # Optional, for validation errors
    }
}
"""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.exceptions import DomainException


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all errors consistently.
    
    Handles:
    1. DomainException - Custom domain errors (UserAlreadyExists, InvalidCredentials, etc.)
    2. ValidationError - DRF serializer validation errors
    3. Other DRF exceptions - PermissionDenied, NotAuthenticated, etc.
    4. Unexpected errors - 500 Internal Server Error
    """
    # Handle custom domain exceptions
    if isinstance(exc, DomainException):
        error_response = {
            "success": False,
            "data": None,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        }
        return Response(error_response, status=exc.status_code)

    # Let DRF handle its own exceptions (ValidationError, PermissionDenied, etc.)
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Format DRF exceptions consistently
        error_code = "VALIDATION_ERROR"
        error_message = "Validation failed."
        error_details = None

        # Handle ValidationError specifically
        if isinstance(exc, ValidationError):
            error_code = "VALIDATION_ERROR"
            if isinstance(exc.detail, dict):
                # Field-level errors: {"field": ["error1", "error2"]}
                error_message = "One or more fields failed validation."
                error_details = exc.detail
            elif isinstance(exc.detail, list):
                # Non-field errors: ["error1", "error2"]
                error_message = exc.detail[0] if exc.detail else "Validation failed."
                error_details = exc.detail if len(exc.detail) > 1 else None
            else:
                error_message = str(exc.detail)
        else:
            # Other DRF exceptions (PermissionDenied, NotAuthenticated, etc.)
            error_code = exc.__class__.__name__.upper()
            if isinstance(exc.detail, dict):
                error_message = exc.detail.get("detail", str(exc.detail))
                error_details = exc.detail
            elif isinstance(exc.detail, list):
                error_message = exc.detail[0] if exc.detail else str(exc)
            else:
                error_message = str(exc.detail) if exc.detail else str(exc)

        error_obj = {
            "code": error_code,
            "message": error_message,
        }
        
        if error_details:
            error_obj["details"] = error_details

        return Response(
            {
                "success": False,
                "data": None,
                "error": error_obj,
            },
            status=response.status_code,
        )

    # Unexpected server errors (500)
    return Response(
        {
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
