def success_response(data):
    return {
        "success": True,
        "data": data,
    }


def error_response(code, data=None):
    return {
        "success": False,
        "error_code": code,
        "detail": data,
    }
