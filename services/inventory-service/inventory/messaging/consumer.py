import json
import logging
import os
import sys

import pika

from inventory.messaging.constants import (
    EXCHANGE,
    QUEUE_INVENTORY_ORDER_CREATED,
    ROUTING_ORDER_CREATED,
)
from inventory.services.inventory_service import process_order_created

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


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


def _on_message(channel, method, properties, body):
    try:
        payload = json.loads(body)
        process_order_created(payload)
    except Exception as e:
        logger.exception("Error processing order.created: %s", e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    channel.basic_ack(delivery_tag=method.delivery_tag)


def run_consumer():
    import django
    django.setup()

    while True:
        try:
            conn = pika.BlockingConnection(_get_connection_params())
            channel = conn.channel()
            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=QUEUE_INVENTORY_ORDER_CREATED, durable=True)
            channel.queue_bind(
                exchange=EXCHANGE,
                queue=QUEUE_INVENTORY_ORDER_CREATED,
                routing_key=ROUTING_ORDER_CREATED,
            )
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=QUEUE_INVENTORY_ORDER_CREATED,
                on_message_callback=_on_message,
            )
            logger.info(
                "Consuming queue=%s routing_key=%s",
                QUEUE_INVENTORY_ORDER_CREATED,
                ROUTING_ORDER_CREATED,
            )
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning("RabbitMQ connection failed, retrying: %s", e)
            continue
        except KeyboardInterrupt:
            logger.info("Consumer stopped")
            sys.exit(0)
        finally:
            try:
                conn.close()
            except Exception:
                pass
