import json
import logging
import os

import pika

from inventory.messaging.constants import EXCHANGE, ROUTING_STOCK_FAILED, ROUTING_STOCK_RESERVED

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


def publish_stock_reserved(order_id: str) -> None:
    _publish(ROUTING_STOCK_RESERVED, {"order_id": order_id})
    logger.info("Published inventory.stock_reserved for order_id=%s", order_id)


def publish_stock_failed(order_id: str, reason: str) -> None:
    _publish(ROUTING_STOCK_FAILED, {"order_id": order_id, "reason": reason})
    logger.info("Published inventory.stock_failed for order_id=%s reason=%s", order_id, reason)
