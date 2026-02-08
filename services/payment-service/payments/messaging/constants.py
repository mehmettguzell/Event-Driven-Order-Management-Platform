"""RabbitMQ exchange and routing keys."""

EXCHANGE = "events"

ROUTING_ORDER_CREATED = "order.created"
ROUTING_PAYMENT_AUTHORIZED = "payment.authorized"
ROUTING_PAYMENT_FAILED = "payment.failed"

QUEUE_PAYMENT_ORDER_CREATED = "payment_order_created"
