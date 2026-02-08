from django.core.cache import cache

CACHE_TIMEOUT = 600

def _key(product_id : str) -> str:
    return f"Inventory_detail_{product_id}"

def get_cache(product_id : str)  -> dict | None:
    return cache.get(_key(product_id))

def set_cache(product_id : str, data: dict) -> None:
    cache.set(_key(product_id), data, CACHE_TIMEOUT)

def delete_cache(product_id : str) -> None:
    cache.delete(_key(product_id))