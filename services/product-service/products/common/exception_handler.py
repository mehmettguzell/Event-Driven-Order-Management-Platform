import logging
from typing import Any

from django.http import Http404
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    NotFound,
    PermissionDenied,
    NotAuthenticated,
    AuthenticationFailed,
    Throttled,
    MethodNotAllowed,
    ParseError,
    UnsupportedMediaType,
)

from products.exceptions import DomainException
from products.common.responses import error_response

logger = logging.getLogger(__name__)

DRF_CODE_MAP = {
    ValidationError: "VALIDATION_ERROR",
    NotFound: "NOT_FOUND",
    PermissionDenied: "PERMISSION_DENIED",
    NotAuthenticated: "NOT_AUTHENTICATED",
    AuthenticationFailed: "AUTHENTICATION_FAILED",
    Throttled: "THROTTLED",
    MethodNotAllowed: "METHOD_NOT_ALLOWED",
    ParseError: "PARSE_ERROR",
    UnsupportedMediaType: "UNSUPPORTED_MEDIA_TYPE",
}


def _get_request_id(context: dict) -> str | None:
    request = context.get("request")
    return getattr(request, "request_id", None) if request else None


def _build_response(
    code: str,
    message: str,
    status_code: int,
    details: Any = None,
    request_id: str | None = None,
) -> Response:
    payload = error_response(code=code, message=message, details=details, request_id=request_id)
    return Response(payload, status=status_code)


def _handle_domain(exc: DomainException, context: dict) -> Response | None:
    if not isinstance(exc, DomainException):
        return None
    code = getattr(exc, "code", "DOMAIN_ERROR")
    msg = getattr(exc, "message", str(exc))
    status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
    return _build_response(code, msg, status_code, request_id=_get_request_id(context))


def _handle_http404(exc: Exception, context: dict) -> Response | None:
    if not isinstance(exc, Http404):
        return None
    msg = str(exc) if str(exc) else "The requested resource was not found."
    return _build_response("NOT_FOUND", msg, status.HTTP_404_NOT_FOUND, request_id=_get_request_id(context))


def _handle_does_not_exist(exc: Exception, context: dict) -> Response | None:
    if not isinstance(exc, ObjectDoesNotExist):
        return None
    return _build_response(
        "NOT_FOUND",
        "The requested resource was not found.",
        status.HTTP_404_NOT_FOUND,
        request_id=_get_request_id(context),
    )


def _handle_integrity_error(exc: Exception, context: dict) -> Response | None:
    if not isinstance(exc, IntegrityError):
        return None
    return _build_response(
        "CONFLICT",
        "A conflict occurred. The resource may already exist or constraints were violated.",
        status.HTTP_409_CONFLICT,
        request_id=_get_request_id(context),
    )


def _drf_detail_to_message(detail: Any) -> str:
    if detail is None:
        return "An error occurred."
    if isinstance(detail, dict):
        return detail.get("detail", "One or more fields failed validation.")
    if isinstance(detail, list):
        return detail[0] if detail else "An error occurred."
    return str(detail)


def _normalize_drf_response(exc: APIException, drf_response: Response, context: dict) -> Response:
    """DRF'nin döndürdüğü response'u servis standardına çevirir."""
    code = DRF_CODE_MAP.get(type(exc), type(exc).__name__.upper().replace(" ", "_"))
    detail = getattr(exc, "detail", None)
    message = _drf_detail_to_message(detail)
    details = None

    if isinstance(exc, ValidationError):
        if isinstance(detail, dict):
            message = "One or more fields failed validation."
            details = detail
        elif isinstance(detail, list) and len(detail) > 1:
            details = detail
    elif isinstance(detail, dict) and ("detail" not in detail or len(detail) > 1):
        details = {k: v for k, v in detail.items() if k != "detail"} or detail

    return _build_response(
        code,
        message,
        drf_response.status_code,
        details=details,
        request_id=_get_request_id(context),
    )


def _handle_unhandled(exc: Exception, context: dict) -> Response:
    request = context.get("request")
    path = getattr(request, "path", "") or ""
    method = getattr(request, "method", "") or ""
    request_id = _get_request_id(context)

    logger.exception(
        "Unhandled exception: %s %s | request_id=%s | exc=%s",
        method,
        path,
        request_id,
        type(exc).__name__,
        exc_info=True,
    )

    return _build_response(
        "INTERNAL_SERVER_ERROR",
        "An unexpected error occurred. Please try again later.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


_HANDLERS = [
    _handle_domain,
    _handle_http404,
    _handle_does_not_exist,
    _handle_integrity_error,
]


def custom_exception_handler(exc: Exception, context: dict) -> Response:
    for handler in _HANDLERS:
        response = handler(exc, context)
        if response is not None:
            return response

    drf_response = drf_exception_handler(exc, context)
    if drf_response is not None:
        return _normalize_drf_response(exc, drf_response, context)

    return _handle_unhandled(exc, context)
