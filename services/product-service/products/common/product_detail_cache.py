from django.core.cache import cache

CACHE_TIMEOUT = 600


def _key(product_id) -> str:
    return f"product_detail_{product_id}"


def get(product_id: str) -> dict | None:
    return cache.get(_key(product_id))


def set(product_id: str, data: dict) -> None:
    cache.set(_key(product_id), data, CACHE_TIMEOUT)


def delete(product_id: str) -> None:
    cache.delete(_key(product_id))
