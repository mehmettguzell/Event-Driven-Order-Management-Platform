import logging
from typing import Any, Callable, Optional

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from inventory.exceptions import InventoryAPIException
from inventory.common.responses import error_response

logger = logging.getLogger(__name__)


def _get_request_id(request: Optional[Request]) -> Optional[str]:
    if request is None:
        return None
    return getattr(request, "request_id", None)


def exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Optional[Response]:
    if isinstance(exc, InventoryAPIException):
        request: Optional[Request] = context.get("request")
        request_id = _get_request_id(request)
        payload = error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
        )
        return Response(payload, status=exc.status_code)

    return drf_exception_handler(exc, context)
