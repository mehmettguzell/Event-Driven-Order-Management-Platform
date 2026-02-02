from django.db import models
import uuid

# Create your models here.

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order_id = models.UUIDField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    transaction_reference = models.CharField(
        max_length=100, null=True, unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for order id:{self.order_id} - Status: {self.status}"