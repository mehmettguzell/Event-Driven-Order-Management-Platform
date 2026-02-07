from rest_framework import serializers
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "price",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "description",
            "price",
            "is_active",
        ]
    
    def validate_sku(self, value):
        return value.upper() if value else value


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "is_active",
        ]
        def validate(self, attrs):
            if not attrs:
                raise serializers.ValidationError("At least one field must be provided.")