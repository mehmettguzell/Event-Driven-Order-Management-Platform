import json
import logging
import os
import sys

import pika

from orders.messaging.constants import (
    EXCHANGE,
    QUEUE_ORDER_FAILURES,
    ROUTING_PAYMENT_FAILED,
    ROUTING_STOCK_FAILED,
)
from orders.services.order_service import cancel_order_by_id

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
        order_id = payload.get("order_id")

        if not order_id:
            logger.warning("Message missing order_id: %s", payload)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        if cancel_order_by_id(order_id):
            logger.info("Cancelled order_id=%s (routing_key=%s)", order_id, method.routing_key)
        else:
            logger.debug("Order %s already cancelled or not found", order_id)
            
    except Exception as e:
        logger.exception("Error processing message: %s", e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    channel.basic_ack(delivery_tag=method.delivery_tag)


def run_consumer():
    import django
    django.setup()

    routing_keys = [ROUTING_STOCK_FAILED, ROUTING_PAYMENT_FAILED]

    while True:
        try:
            conn = pika.BlockingConnection(_get_connection_params())
            channel = conn.channel()

            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=QUEUE_ORDER_FAILURES, durable=True)

            for rk in routing_keys:
                channel.queue_bind(exchange=EXCHANGE, queue=QUEUE_ORDER_FAILURES, routing_key=rk)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_ORDER_FAILURES, on_message_callback=_on_message)

            logger.info("Consuming queue=%s routing_keys=%s", QUEUE_ORDER_FAILURES, routing_keys)
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
