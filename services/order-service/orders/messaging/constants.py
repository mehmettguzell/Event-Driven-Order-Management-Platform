"""RabbitMQ exchange and routing keys (shared convention across services)."""

EXCHANGE = "events"

# Order-service publishes
ROUTING_ORDER_CREATED = "order.created"

# Order-service consumes
ROUTING_STOCK_FAILED = "inventory.stock_failed"
ROUTING_PAYMENT_FAILED = "payment.failed"

QUEUE_ORDER_FAILURES = "order_failures"
