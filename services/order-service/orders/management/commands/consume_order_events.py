from django.core.management.base import BaseCommand

from orders.messaging.consumer import run_consumer


class Command(BaseCommand):
    help = "Consume RabbitMQ events (StockFailed, PaymentFailed) and cancel orders."

    def handle(self, *args, **options):
        run_consumer()
