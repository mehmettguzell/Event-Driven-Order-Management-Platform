from django.core.cache import cache

CACHE_TIMEOUT = 300
VERSION_KEY = "products_list_version"


def _build_key(filters: dict, page, version: int) -> str:
    search = filters.get("search_query") or ""
    search_part = search[:50] if len(search) > 50 else search
    return (
        f"products_list_v{version}_p{page}_"
        f"{filters.get('only_active')}_{filters.get('min_price')}_{filters.get('max_price')}_"
        f"{search_part}_{filters.get('sku')}_{filters.get('ordering')}"
    )


def get_response(filters: dict, page) -> dict | None : 
    version = cache.get(VERSION_KEY) or 1
    key = _build_key(filters, page, version)
    return cache.get(key)


def set_response(filters: dict, page, response_data) -> None:
    version = cache.get(VERSION_KEY) or 1
    key = _build_key(filters, page, version)
    cache.set(key, response_data, CACHE_TIMEOUT)


def invalidate():
    cache.set(VERSION_KEY, (cache.get(VERSION_KEY) or 1) + 1)

