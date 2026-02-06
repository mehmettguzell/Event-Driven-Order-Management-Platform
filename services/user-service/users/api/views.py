from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from users.api.serializers import (
    AuthSerializer,
    RefreshTokenSerializer,
    VerifyTokenSerializer,
    UserProfileSerializer,
)
from users.common.responses import success_response
from users.services.auth_service import (
    register_user,
    login_user,
    logout_user,
    get_user_profile,
)
from users.services.token_service import (
    refresh_access_token,
    verify_token,
)


class RegisterView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = register_user(**serializer.validated_data)

        return Response(
            success_response(result),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    throttle_classes = [AnonRateThrottle]

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
        
        result = logout_user(refresh_token=refresh_token)

        return Response(
            success_response(result),
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token_str = serializer.validated_data["refresh"]
        
        tokens = refresh_access_token(refresh_token_str)

        return Response(
            success_response(tokens),
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        data = get_user_profile(user=user)
        
        serializer = UserProfileSerializer(data)
        
        return Response(
            success_response(serializer.data),
            status=status.HTTP_200_OK,
        )


class VerifyTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = VerifyTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data["token"]
        
        token_data = verify_token(token_str)

        return Response(
            success_response(token_data),
            status=status.HTTP_200_OK,
        )