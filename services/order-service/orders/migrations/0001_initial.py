import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CREATED", "Created"),
                            ("PAYMENT_PENDING", "Payment Pending"),
                            ("PAID", "Paid"),
                            ("CANCELLED", "Cancelled"),
                            ("FAILED", "Failed"),
                        ],
                        default="CREATED",
                        max_length=20,
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("product_id", models.UUIDField()),
                ("product_sku", models.CharField(max_length=50)),
                ("quantity", models.PositiveIntegerField()),
                ("price_snapshot", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="items",
                        to="orders.order",
                        db_column="order_id",
                    ),
                ),
            ],
        ),
    ]
