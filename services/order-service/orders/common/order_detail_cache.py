from django.core.cache import cache

CACHE_TIMEOUT = 600


def _key(order_id) -> str:
    return f"order_detail_{order_id}"


def get(order_id: str) -> dict | None:
    return cache.get(_key(order_id))


def set(order_id: str, data: dict) -> None:
    return cache.set(_key(order_id), data , CACHE_TIMEOUT)


def delete(order_id : str) -> None:
    cache.delete(_key(order_id))