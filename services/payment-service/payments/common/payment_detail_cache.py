from django.core.cache import cache

CACHE_TIMEOUT = 600

def _key(order_id :str) -> str:
    return f"payment_detail_{order_id}"


def get_cache(order_id :str) -> dict | None:
    return cache.get(_key(order_id=order_id))


def set_cache(order_id :str, value: dict) -> dict:
    return cache.set(_key(order_id), value, CACHE_TIMEOUT)


def delete_cache(order_id :str) -> None:
    cache.delete(_key(order_id=order_id))
