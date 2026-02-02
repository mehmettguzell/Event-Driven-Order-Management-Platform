from django.db import models
import uuid
# Create your models here.

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order_id = models.UUIDField()
    event_type = models.CharField(max_length=50)

    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
