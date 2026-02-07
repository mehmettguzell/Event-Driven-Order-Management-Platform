import uuid

def RequestIDMiddleware(get_response):
    def middleware(request):
        request.request_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        response = get_response(request)
        response["X-Request-ID"] = request.request_id
        return response

    return middleware
