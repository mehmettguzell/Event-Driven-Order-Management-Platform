def success_response(data):
    return {
        "success": True,
        "data": data,
    }


def error_response(code: str, message: str, details=None):
    error_obj = {
        "code": code,
        "message": message,
    }
    
    if details is not None:
        error_obj["details"] = details
    
    return {
        "success": False,
        "data": None,
        "error": error_obj,
    }
