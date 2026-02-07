from typing import Optional

from django.db.models import QuerySet
from orders.models import Order

def get_order_by_id(order_id : str) -> Optional[Order]:
    try:
        return Order.objects.only(
            "id",
            "user_id",
            "status",
            "total_amount",
            "created_at"
        ).get(id=order_id)
    except Order.DoesNotExist:
        return None

def get_all_orders_by_user_id(
        user_id :str = None
        ) -> QuerySet[Order]:
    
    qs = Order.objects.all()

    if user_id:
        qs = qs.filter(user_id = user_id)
    
    return qs.only(
        "id",
        "status",
        "created_at",
        "total_amount",
    )