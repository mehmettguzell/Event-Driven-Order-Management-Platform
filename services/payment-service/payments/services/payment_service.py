"""
Handle OrderCreated: create Payment record, simulate charge, publish PaymentAuthorized or PaymentFailed.
Demo: fail if total_amount > 10000 (simulate decline), else success.
"""

import logging
import uuid

from payments.messaging.publisher import publish_payment_authorized, publish_payment_failed
from payments.models import Payment

logger = logging.getLogger(__name__)


def process_order_created(payload: dict) -> None:
    order_id = payload.get("order_id")
    total_amount = payload.get("total_amount", "0")
    if not order_id:
        logger.warning("OrderCreated missing order_id")
        return

    try:
        amount = float(total_amount)
    except (TypeError, ValueError):
        amount = 0.0

    payment = Payment.objects.create(
        order_id=order_id,
        status=Payment.Status.PENDING,
    )

    # Demo: fail orders over 10000 to simulate decline
    if amount > 10000:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        publish_payment_failed(order_id, "Payment declined (demo: amount > 10000)")
        return

    ref = f"txn-{uuid.uuid4().hex[:16]}"
    payment.status = Payment.Status.SUCCESS
    payment.transaction_reference = ref
    payment.save(update_fields=["status", "transaction_reference"])
    publish_payment_authorized(order_id, ref)
