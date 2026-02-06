from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api.serializers import (
    AuthSerializer,
    RefreshTokenSerializer,
    VerifyTokenSerializer
)

from users.common.responses import success_response
from users.services.auth_service import login_user, logout_user, register_user, user_profile
from users.services.token_service import refresh_access_token, verify_token


class RegisterView(APIView):
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = register_user(**serializer.validated_data)

        return Response(
            success_response(result),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = login_user(**serializer.validated_data)

        return Response(
            success_response(result),
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        logout_user(refresh_token)

        return Response(
            success_response({"message": "Logged out successfully."}),
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token_str = serializer.validated_data["refresh"]
        new_access_token = refresh_access_token(refresh_token_str)

        data = {
            "access": new_access_token,
            "refresh": refresh_token_str,
        }

        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = user_profile(user)

        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )


class VerifyTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data["token"]

        verify_token(token_str)

        return Response(
            success_response({"valid": True}),
            status=status.HTTP_200_OK,
        )