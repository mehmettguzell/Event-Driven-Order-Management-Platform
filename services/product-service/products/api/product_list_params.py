from rest_framework.request import Request


DEFAULT_ORDERING = "-created_at"


ALLOWED_ORDERINGS = {
    "created_at", "-created_at",
    "price", "-price",
    "name", "-name",
    "sku", "-sku",
}


def parse_product_list_params(request: Request) -> dict:
    only_active = request.query_params.get("only_active", "true").lower() == "true"
    min_price = _parse_float(request.query_params.get("min_price"))
    max_price = _parse_float(request.query_params.get("max_price"))
    search_query = (request.query_params.get("search") or "").strip() or None
    sku =  (request.query_params.get("sku") or "").strip() or None
    ordering = (request.query_params.get("order") or "").strip() or DEFAULT_ORDERING

    if ordering not in ALLOWED_ORDERINGS:
        ordering = DEFAULT_ORDERING

    return {
        "only_active": only_active,
        "min_price": min_price,
        "max_price": max_price,
        "search_query": search_query,
        "sku": sku,
        "ordering": ordering,
    }


def _parse_float(value) -> float | None:
    if(value is None):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None