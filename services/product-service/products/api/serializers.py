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
        if Product.objects.filter(sku__iexact=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value.upper()
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "is_active",
        ]
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
