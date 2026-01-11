# core/auth.py
"""Authentication classes for Django Ninja API."""

from typing import Optional

from django.contrib.auth.models import User
from django.utils import timezone
from ninja import Header
from ninja.security import HttpBearer

from core.models import ApiKey


class ApiKeyAuth(HttpBearer):
    """API Key authentication using Bearer token format."""

    def authenticate(self, request, token: str) -> Optional[User]:
        """
        Authenticate user using API key token.

        The token should be in the format: "Bearer <key>" or just "<key>"
        """
        # Strip "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            api_key = ApiKey.objects.select_related("user").get(
                key=token,
                is_active=True
            )
        except ApiKey.DoesNotExist:
            return None

        # Check expiration
        if api_key.is_expired:
            return None

        # Update last used timestamp
        api_key.mark_used()

        return api_key.user


class ApiKeyHeaderAuth:
    """API Key authentication using X-API-Key header."""

    def __init__(self):
        self.param_name = "X-API-Key"

    def __call__(self, request, key: str = Header(...)) -> Optional[User]:
        """
        Authenticate user using X-API-Key header.

        Args:
            request: Django request object
            key: API key from X-API-Key header

        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            api_key = ApiKey.objects.select_related("user").get(
                key=key,
                is_active=True
            )
        except ApiKey.DoesNotExist:
            return None

        # Check expiration
        if api_key.is_expired:
            return None

        # Update last used timestamp
        api_key.mark_used()

        return api_key.user


def get_api_key_auth():
    """Get the appropriate authentication class based on configuration."""
    # For now, return the header-based auth
    return ApiKeyHeaderAuth()