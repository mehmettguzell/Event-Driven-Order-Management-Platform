"""Publish events to RabbitMQ (order.created)."""

import json
import logging
import os

import pika

from orders.messaging.constants import EXCHANGE, ROUTING_ORDER_CREATED

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
    try:
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
    except Exception as e:
        logger.exception("Failed to publish event %s: %s", routing_key, e)
        raise


def publish_order_created(order) -> None:
    """Publish OrderCreated after order is created. Consumed by inventory and payment services."""
    items = [
        {
            "product_id": str(item.product_id),
            "product_sku": item.product_sku,
            "quantity": item.quantity,
            "price_snapshot": str(item.price_snapshot),
        }
        for item in order.items.all()
    ]
    body = {
        "order_id": str(order.id),
        "user_id": str(order.user_id),
        "total_amount": str(order.total_amount),
        "items": items,
    }
    _publish(ROUTING_ORDER_CREATED, body)
    logger.info("Published order.created for order_id=%s", order.id)
