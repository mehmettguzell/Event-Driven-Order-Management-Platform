from typing import Optional
from payments.models import Payment


def get_payment_by_order_id(order_id :str) -> Optional[Payment]:
    return Payment.objects.filter(order_id=order_id).only(
        "id",
        "order_id",
        "status"
    ).order_by("-created_at").first()
