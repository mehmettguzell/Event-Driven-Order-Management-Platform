from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.api.serializers import RegisterSerializer
from users.services.auth_service import UserAlreadyExists, register_user
from users.services.token_service import generate_tokens_for_user


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = register_user(**serializer.validated_data)
        except UserAlreadyExists as e:
        ## EXCEPTION HANDLER YAZ
            return Response(
                {"detail": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            result,
            status=status.HTTP_201_CREATED
        )


        