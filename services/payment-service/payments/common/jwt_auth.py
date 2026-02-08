from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken

class AuthenticatedServiceUser:
    def __init__(self, user_id:str):
        self.id = user_id
        self.pk = user_id
        self.is_authenticated = True
        self.is_active = True

class StatelessJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token: AccessToken) -> AuthenticatedServiceUser:
        try:
            user_id = validated_token.get("user_id")
        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification.")

        return AuthenticatedServiceUser(user_id=str(user_id))