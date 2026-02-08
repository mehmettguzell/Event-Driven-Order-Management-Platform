from rest_framework import serializers

from orders.models import Order


class OrderDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order

        fields = [
            "id", 
            "user_id", 
            "status", 
            "total_amount", 
            "created_at"
            ]

        read_only_fields = fields


class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order

        fields = [
            "id", 
            "status", 
            "total_amount", 
            "created_at"
            ]

        read_only_fields = fields


class CreateOrderItemSerializer(serializers.Serializer):

    product_id = serializers.UUIDField()
    product_sku = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField(min_value=1)
    price_snapshot = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class CreateOrderSerializer(serializers.Serializer):
    
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    items = CreateOrderItemSerializer(many=True, required=False, default=list)

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("total_amount must be positive.")
        return value
