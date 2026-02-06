import uuid
from django.db import models


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["is_active", "created_at"], name="product_active_created_idx"),
            models.Index(fields=["price"], name="product_price_idx"),
            models.Index(fields=["sku"], name="product_sku_idx"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sku} - {self.name}"
