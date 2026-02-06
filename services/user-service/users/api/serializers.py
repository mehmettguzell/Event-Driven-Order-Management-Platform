import re
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={"input_type": "password"},
    )

    def validate_email(self, value):
        return value.lower().strip()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if " " in value:
            raise serializers.ValidationError("Password should not contain spaces.")
        
        if value.isdigit():
            raise serializers.ValidationError("Password should not be entirely numeric.")
        
        if value.isalpha():
            raise serializers.ValidationError("Password must contain at least one digit.")
        
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages[0] if e.messages else "Password does not meet security requirements.")
        
        return value


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, help_text="Refresh token")


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="JWT token to verify")


class UserProfileSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
