import uuid
from django.db import models

# Create your models here.
class Inventory(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    product_id = models.UUIDField()
    product_sku = models.CharField(max_length=50)

    quantity = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Product {self.product_sku} -> Quantity {self.quantity}"