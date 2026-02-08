from django.core.management.base import BaseCommand

from payments.messaging.consumer import run_consumer


class Command(BaseCommand):
    help = "Consume order.created events, process payment and publish authorized/failed."

    def handle(self, *args, **options):
        run_consumer()
