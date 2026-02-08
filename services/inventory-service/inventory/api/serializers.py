from rest_framework import serializers

from inventory.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["id", "product_id", "product_sku", "quantity", "updated_at"]
        read_only_fields = ["id", "product_id", "updated_at"]


class CreateInventorySerializer(serializers.Serializer):

    product_id = serializers.UUIDField()
    product_sku = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField(min_value=0)


class UpdateInventorySerializer(serializers.Serializer):

    quantity = serializers.IntegerField(min_value=0)
