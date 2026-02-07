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
