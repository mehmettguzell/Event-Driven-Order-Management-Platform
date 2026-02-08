from django.core.management.base import BaseCommand

from inventory.messaging.consumer import run_consumer


class Command(BaseCommand):
    help = "Consume order.created events, reserve stock and publish stock_reserved / stock_failed."

    def handle(self, *args, **options):
        run_consumer()
