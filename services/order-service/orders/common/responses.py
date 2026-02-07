from rest_framework.pagination import PageNumberPagination


def success_response(data):
    return {
        "success": True,
        "data": data,
    }


def error_response(code: str, message: str, details=None, *, request_id: str | None = None):
    error_obj = {
        "code": code,
        "message": message,
    }
    if details is not None:
        error_obj["details"] = details
    if request_id is not None:
        error_obj["request_id"] = request_id

    return {
        "success": False,
        "data": None,
        "error": error_obj,
    }
