from django.db import transaction
from users.models import User
from users.selectors import get_user_by_email
from users.services.token_service import generate_tokens_for_user
from django.contrib.auth import authenticate

from users.exceptions import UserAlreadyExists, InvalidCredentials, UserInactive


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
    user = authenticate(email=email, password=password)

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
