from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.api.serializers import AuthSerializer
from users.services.auth_service import register_user, login_user
from users.common.responses import success_response


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
    pass

class RefreshTokenView(APIView):
    pass

class UserProfileView(APIView):
    pass

class verifyTokenView(APIView):
    pass
