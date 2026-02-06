from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from users.api.serializers import (
    AuthSerializer,
    RefreshTokenSerializer,
    VerifyTokenSerializer,
)
from users.common.responses import success_response
from users.services.auth_service import login_user, register_user


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
        return Response(
            success_response({"message": "Logged out successfully."}),
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token_str = serializer.validated_data["refresh"]

        try:
            refresh = RefreshToken(refresh_token_str)
        except TokenError as exc:
            raise InvalidToken(str(exc))

        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):


    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "user_id": str(user.id),
            "email": user.email,
            "is_verified": getattr(user, "is_verified", False),
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )


class verifyTokenView(APIView):

    def post(self, request):
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data["token"]

        try:
            AccessToken(token_str)
        except TokenError as exc:
            raise InvalidToken(str(exc))

        return Response(
            success_response({"valid": True}),
            status=status.HTTP_200_OK,
        )

