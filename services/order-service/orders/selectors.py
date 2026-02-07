from typing import Optional
from orders.models import Order
from typing import Optional
from django.db.models import QuerySet, Q

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

def get_all_orders_by_user_id(user_id :str) -> QuerySet[Order]:
    ## TODO: 
    pass