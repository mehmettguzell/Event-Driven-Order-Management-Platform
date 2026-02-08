import logging
import uuid

from payments.api.serializers import PaymentSerializer
from payments.common.payment_detail_cache import set_cache as set_payment_cache, get_cache as get_payment_cache, delete_cache
from payments.exceptions import PaymentNotFound
from payments.messaging.publisher import publish_payment_authorized, publish_payment_failed
from payments.models import Payment
from payments.selectors import get_payment_by_order_id

logger = logging.getLogger(__name__)

def get_payment_service(order_id: str):
    cached = get_payment_cache(order_id)
    if cached is not None:
        return cached

    payment = get_payment_by_order_id(order_id)
    if not payment:
        raise PaymentNotFound() 

    data = PaymentSerializer(payment).data
    set_payment_cache(order_id, data)
    return data


def get_order_payments_by_order_id(order_id: str):
    qs = Payment.objects.all().order_by("-created_at")
    
    if order_id:
        qs = qs.filter(order_id=order_id)    
    return PaymentSerializer(qs[:50], many=True)


def process_order_created(payload: dict) -> None:
    extracted = _extract_order_id_and_amount(payload)
    if not extracted:
        return

    order_id, amount = extracted

    payment = Payment.objects.create(
        order_id=order_id,
        status=Payment.Status.PENDING,
    )

    ### fail payment scenerio to test event
    if amount > 10_000:
        _fail_payment(payment, order_id)
        return

    transaction_ref = _authorize_payment(payment)
    publish_payment_authorized(order_id, transaction_ref)



def _extract_order_id_and_amount(payload: dict) -> tuple[str, float] | None:
    order_id = payload.get("order_id")
    if not order_id:
        logger.warning("OrderCreated missing order_id")
        return None

    try:
        amount = float(payload.get("total_amount", "0"))
    except (TypeError, ValueError):
        amount = 0.0

    return order_id, amount


def _fail_payment(payment: Payment, order_id: str) -> None:
    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])

    publish_payment_failed(
        order_id,
        "Payment declined (demo rule: amount > 10000)",
    )


def _authorize_payment(payment: Payment) -> str:
    transaction_ref = f"txn-{uuid.uuid4().hex[:16]}"
    payment.status = Payment.Status.SUCCESS
    payment.transaction_reference = transaction_ref
    payment.save(update_fields=["status", "transaction_reference"])
    return transaction_ref
