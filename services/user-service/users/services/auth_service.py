from django.db import transaction
from django.core.cache import cache
from django.contrib.auth import authenticate

from users.models import User
from users.selectors import user_exists, get_user_by_email
from users.services.token_service import (
    generate_tokens_for_user,
    blacklist_token,
)
from users.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    UserInactive,
)


def register_user(*, email: str, password: str) -> dict:
    email = email.lower().strip()
    
    if user_exists(email):
        raise UserAlreadyExists()

    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=password,
        )
        
        cache.delete(f"user_email_{email}")
        cache.delete(f"user_id_{user.id}")

    tokens = generate_tokens_for_user(user)

    return {
        "user_id": str(user.id),
        "email": user.email,
        "tokens": tokens,
    }


def login_user(*, email: str, password: str) -> dict:
    email = email.lower().strip()
    
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


def logout_user(*, refresh_token: str) -> dict:
    blacklist_token(refresh_token)
    
    return {
        "message": "Logged out successfully.",
    }


def get_user_profile(*, user: User) -> dict:
    return {
        "user_id": str(user.id),
        "email": user.email,
        "is_verified": getattr(user, "is_verified", False),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }