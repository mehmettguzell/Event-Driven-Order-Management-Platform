import uuid
from django.db import models


class Payment(models.Model):
    """Sipariş ödeme kaydı: OrderCreated event sonrası oluşturulur."""

    class Status(models.TextChoices):
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.UUIDField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    transaction_reference = models.CharField(max_length=100, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="payment_status_idx"),
        ]

    def __str__(self):
        return f"Payment for order id:{self.order_id} - Status: {self.status}"