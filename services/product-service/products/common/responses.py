from rest_framework.pagination import PageNumberPagination


def success_response(data):
    return {
        "success": True,
        "data": data,
    }


def paginated_product_list_data(products_data: list, paginator : PageNumberPagination) -> dict:
    return {
        "products": products_data,
        "pagination": {
            "page": paginator.page.number,
            "page_size": paginator.page_size,
            "total_pages": paginator.page.paginator.num_pages,
            "total_items": paginator.page.paginator.count,
            "has_next": paginator.page.has_next(),
            "has_previous": paginator.page.has_previous(),
        },
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
