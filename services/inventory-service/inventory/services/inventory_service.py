import logging
from uuid import UUID
from typing import Any

from django.db import transaction

from inventory.api.serializers import InventorySerializer
from inventory.common.inventory_detail_cache import delete_cache, get_cache, set_cache
from inventory.exceptions import InventoryNotFoundError
from inventory.messaging.publisher import publish_stock_failed, publish_stock_reserved
from inventory.models import Inventory
from inventory.selectors import (
    get_inventory_by_product_id,
    get_inventory_for_update,
    list_inventories,
)

logger = logging.getLogger(__name__)

def _parse_order_items(payload: dict) -> tuple[Any, list[tuple[Any, int]]]:
    order_id = payload.get("order_id")
    raw_items = payload.get("items") or []
    line_items: list[tuple[Any, int]] = []
    for item in raw_items:
        product_id = item.get("product_id")
        try:
            need = int(item.get("quantity", 0))
        except (TypeError, ValueError):
            need = 0
        if product_id and need > 0:
            line_items.append((product_id, need))
    return order_id, line_items


def _stock_failure_reason(product_id: Any, has_inventory: bool) -> str:
    if has_inventory:
        return f"Insufficient stock for product_id={product_id}"
    return f"No inventory for product_id={product_id}"


def _check_line_fulfillable(product_id: Any, need: int) -> tuple[bool, str | None]:

    inv = get_inventory_by_product_id(product_id)
    if not inv:
        return False, _stock_failure_reason(product_id, False)
    if inv.quantity < need:
        return False, _stock_failure_reason(product_id, True)
    return True, None


def _reserve_stock(line_items: list[tuple[Any, int]]) -> str | None:
    with transaction.atomic():
        for product_id, need in line_items:
            inv = get_inventory_for_update(product_id)
            if not inv or inv.quantity < need:
                return _stock_failure_reason(product_id, inv is not None)
            inv.quantity -= need
            inv.save(update_fields=["quantity"])
    return None


def process_order_created(payload: dict) -> None:
    order_id, line_items = _parse_order_items(payload)

    if not order_id:
        logger.warning("OrderCreated missing order_id")
        return
    if not line_items:
        publish_stock_reserved(order_id)
        return

    for product_id, need in line_items:
        ok, failure_reason = _check_line_fulfillable(product_id, need)
        if not ok:
            publish_stock_failed(order_id, failure_reason)
            return

    try:
        failure_reason = _reserve_stock(line_items)
        if failure_reason:
            publish_stock_failed(order_id, failure_reason)
            return
        publish_stock_reserved(order_id)
    except Exception as e:
        logger.exception("Failed to reserve stock for order_id=%s: %s", order_id, e)
        publish_stock_failed(order_id, str(e))


def create_or_update_inventory(validated_data: dict) -> tuple[dict[str, Any], bool]:
    product_id = validated_data["product_id"]
    product_sku = validated_data["product_sku"]
    quantity = validated_data["quantity"]

    inv, created = Inventory.objects.update_or_create(
        product_id=product_id,
        defaults={"product_sku": product_sku, "quantity": quantity},
    )
    return InventorySerializer(inv).data, created


def get_inventory_detail_by_product_id(product_id: UUID | str) -> dict[str, Any]:
    cached = get_cache(str(product_id))
    if cached:
        return cached

    inventory = get_inventory_by_product_id(product_id)
    if not inventory:
        raise InventoryNotFoundError()

    data = InventorySerializer(inventory).data
    set_cache(str(product_id), data)
    return data


def list_all_inventories() -> list[dict[str, Any]]:
    qs = list_inventories()
    return InventorySerializer(qs, many=True).data


def update_inventory_quantity(product_id: UUID | str, validated_data: dict) -> dict[str, Any]:
    quantity = validated_data.get("quantity")
    if quantity is None:
        raise InventoryNotFoundError()

    with transaction.atomic():
        inv = get_inventory_for_update(product_id=product_id)
        if not inv:
            raise InventoryNotFoundError()
        inv.quantity = quantity
        inv.save(update_fields=["quantity"])

    delete_cache(str(product_id))
    return InventorySerializer(inv).data
