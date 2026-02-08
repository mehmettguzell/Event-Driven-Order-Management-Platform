"""Publish payment.authorized and payment.failed."""

import json
import logging
import os

import pika

from payments.messaging.constants import (
    EXCHANGE,
    ROUTING_PAYMENT_AUTHORIZED,
    ROUTING_PAYMENT_FAILED,
)

logger = logging.getLogger(__name__)


def _get_connection_params():
    return pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "guest"),
            os.getenv("RABBITMQ_PASSWORD", "guest"),
        ),
        heartbeat=600,
        blocked_connection_timeout=300,
    )


def _publish(routing_key: str, body: dict) -> None:
    conn = pika.BlockingConnection(_get_connection_params())
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conn.close()


def publish_payment_authorized(order_id: str, transaction_reference: str) -> None:
    _publish(
        ROUTING_PAYMENT_AUTHORIZED,
        {"order_id": order_id, "transaction_reference": transaction_reference},
    )
    logger.info("Published payment.authorized for order_id=%s", order_id)


def publish_payment_failed(order_id: str, reason: str) -> None:
    _publish(ROUTING_PAYMENT_FAILED, {"order_id": order_id, "reason": reason})
    logger.info("Published payment.failed for order_id=%s reason=%s", order_id, reason)
