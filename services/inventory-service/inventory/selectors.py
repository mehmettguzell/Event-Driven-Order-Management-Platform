from uuid import UUID
from typing import Optional

from inventory.models import Inventory

INVENTORY_LIST_FIELDS = (
    "id",
    "product_id",
    "product_sku",
    "quantity",
    "updated_at",
)


def get_inventory_by_product_id(product_id: UUID | str) -> Optional[Inventory]:
    try:
        return Inventory.objects.only(*INVENTORY_LIST_FIELDS).get(
            product_id=product_id
        )
    except Inventory.DoesNotExist:
        return None


def get_inventory_for_update(product_id: UUID | str) -> Optional[Inventory]:
    return (
        Inventory.objects.select_for_update()
        .filter(product_id=product_id)
        .first()
    )


def list_inventories():
    return Inventory.objects.only(*INVENTORY_LIST_FIELDS).order_by("product_sku")
