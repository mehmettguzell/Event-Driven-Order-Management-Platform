import uuid
from django.db import models

# Create your models here.

class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED"
        PAYMENT_PENDING = "PAYMENT_PENDING"
        PAID = "PAID"
        CANCELLED = "CANCELLED"
        FAILED = "FAILED"

    id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"
    
class OrderItem(models.Model):
    id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)

    order_id = models.UUIDField

    product_id = models.UUIDField()
    product_sku = models.CharField(max_length=50)

    quantity = models.PositiveIntegerField()
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)