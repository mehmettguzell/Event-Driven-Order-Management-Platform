from rest_framework import serializers


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value):
        if " " in value:
            raise serializers.ValidationError("Password should not contain spaces.")
        if value.isdigit():
            raise serializers.ValidationError("Password should not be entirely numeric.")
        return value


class RefreshTokenSerializer(serializers.Serializer):

    refresh = serializers.CharField()


class VerifyTokenSerializer(serializers.Serializer):

    token = serializers.CharField()

