from typing import Optional
from django.db.models import QuerySet
from django.core.cache import cache

from users.models import User


def get_user_by_email(email: str) -> Optional[User]:
    email = email.lower().strip()
    
    cache_key = f"user_email_{email}"
    cached_user = cache.get(cache_key)
    if cached_user:
        return cached_user
    
    user = User.objects.only(
        "id",
        "email",
        "is_active",
        "is_verified",
        "created_at",
        "updated_at",
    ).filter(email__iexact=email).first()
    
    if user:
        cache.set(cache_key, user, 300)
    
    return user


def get_user_by_id(user_id: str) -> Optional[User]:
    cache_key = f"user_id_{user_id}"
    cached_user = cache.get(cache_key)
    if cached_user:
        return cached_user
    
    try:
        user = User.objects.only(
            "id",
            "email",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ).get(id=user_id)
        
        cache.set(cache_key, user, 600)
        return user
    except User.DoesNotExist:
        return None


def user_exists(email: str) -> bool:
    email = email.lower().strip()
    return User.objects.filter(email__iexact=email).exists()


def get_active_users() -> QuerySet[User]:

    return User.objects.filter(is_active=True).only(
        "id",
        "email",
        "is_verified",
        "created_at",
    ).order_by("-created_at")