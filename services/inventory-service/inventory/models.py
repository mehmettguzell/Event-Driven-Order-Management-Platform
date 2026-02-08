import uuid
from django.db import models


class Inventory(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField(unique=True, db_index=True)
    product_sku = models.CharField(max_length=50, db_index=True)
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product_sku"]

    def __str__(self):
        return f"Product {self.product_sku} -> Quantity {self.quantity}"