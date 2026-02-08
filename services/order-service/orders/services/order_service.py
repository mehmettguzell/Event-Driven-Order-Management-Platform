from typing import Any

from rest_framework.request import Request

from orders.api.serializers import OrderDetailSerializer, OrderListSerializer
from orders.common.order_detail_cache import get as get_detail_cache, set as set_detail_cache, delete as delete_detail_cache
from orders.messaging.publisher import publish_order_created
from orders.exceptions import OrderNotFound
from orders.models import Order, OrderItem
from orders.selectors import get_all_orders_by_user_id, get_order_by_id


def create_order(user_id: str, validated_data: dict[str, Any]) -> dict[str, Any]:
    total_amount = validated_data["total_amount"]
    items_data = validated_data.get("items") or []

    order = Order.objects.create(
        user_id=user_id,
        status=Order.Status.CREATED,
        total_amount=total_amount,
    )
    for item in items_data:
        OrderItem.objects.create(
            order=order,
            product_id=item["product_id"],
            product_sku=item["product_sku"],
            quantity=item["quantity"],
            price_snapshot=item["price_snapshot"],
        )

    data = OrderDetailSerializer(order).data
    set_detail_cache(str(order.id), data)
    publish_order_created(order)
    return data


def cancel_order_by_id(order_id: str) -> bool:
    """Set order status to CANCELLED (e.g. on StockFailed or PaymentFailed). Returns True if updated."""
    order = get_order_by_id(order_id)
    if not order or order.status == Order.Status.CANCELLED:
        return False
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    delete_detail_cache(order_id)
    return True


def get_order_detail(order_id: str) -> dict[str, Any]:
    cached = get_detail_cache(order_id)
    if cached:
        return cached
    
    order = get_order_by_id(order_id)
    if not order:
        raise OrderNotFound()
    
    return OrderDetailSerializer(order).data

def get_user_orders(
        user_id: str,
        request: Request,
        pagination_class: type,
    ) -> dict[str, Any]:
    
    orders_qs = get_all_orders_by_user_id(user_id)

    paginator = pagination_class()
    page = paginator.paginate_queryset(orders_qs, request)

    serializer = OrderListSerializer(page, many=True)
    
    return paginator.get_paginated_response(serializer.data).data
