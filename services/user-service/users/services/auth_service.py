from django.db import transaction
from users.models import User
from users.selectors import get_user_by_email
from users.services.token_service import generate_tokens_for_user
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from users.exceptions import InvalidToken, UserAlreadyExists, InvalidCredentials, UserInactive


def register_user(*, email: str, password: str):

    if get_user_by_email(email):
        raise UserAlreadyExists()

    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=password,
        )

    tokens = generate_tokens_for_user(user)

    return {
        "user_id": str(user.id),
        "email": user.email,
        "tokens": tokens,
    }

def login_user(email, password):
    user = authenticate(username=email, password=password)

    if user is None:
        raise InvalidCredentials()

    if not user.is_active:
        raise UserInactive()

    tokens = generate_tokens_for_user(user)

    return {
        "user_id": str(user.id),
        "email": user.email,
        "tokens": tokens,
    }

def logout_user(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as exc:
        raise InvalidToken(str(exc))
    
def user_profile(user):
    data = {
        "user_id": str(user.id),
        "email": user.email,
        "is_verified": getattr(user, "is_verified", False),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
    return data