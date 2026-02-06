from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from users.exceptions import InvalidToken

def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def refresh_access_token(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        return str(token.access_token)
    except TokenError as exc:
        raise InvalidToken(str(exc))
    

def verify_token(token_str):
    try:
        AccessToken(token_str)
    except TokenError as exc:
        raise InvalidToken(str(exc))