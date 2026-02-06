from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import TokenError as SimpleJWTTokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from users.models import User
from users.exceptions import InvalidToken, TokenBlacklisted


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def refresh_access_token(refresh_token_str: str):
    try:
        old_refresh = RefreshToken(refresh_token_str)
        
        if BlacklistedToken.objects.filter(token__token=str(old_refresh)).exists():
            raise TokenBlacklisted()
        
        user_id = old_refresh.get("user_id")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise InvalidToken("User not found.")
        
        old_refresh.blacklist()
        
        new_refresh = RefreshToken.for_user(user)
        
        return {
            "access": str(new_refresh.access_token),
            "refresh": str(new_refresh),
        }
    except (TokenError, SimpleJWTTokenError) as exc:
        raise InvalidToken(str(exc))


def verify_token(token_str: str) -> dict:
    try:
        token = AccessToken(token_str)
        return {
            "valid": True,
            "user_id": str(token["user_id"]),
            "token_type": token.get("token_type", "access"),
        }
    except (TokenError, SimpleJWTTokenError) as exc:
        raise InvalidToken(str(exc))


def blacklist_token(refresh_token_str: str):
    try:
        refresh = RefreshToken(refresh_token_str)
        refresh.blacklist()
    except (TokenError, SimpleJWTTokenError) as exc:
        raise InvalidToken(str(exc))