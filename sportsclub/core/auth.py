# core/auth.py
"""Authentication classes for Django Ninja API."""

from django.contrib.auth.models import User
from ninja import Header
from ninja.security import HttpBearer

from core.models import ApiKey


class ApiKeyAuth(HttpBearer):
    """API Key authentication using Bearer token format."""

    def authenticate(self, request, token: str) -> User | None:
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

    def __call__(self, request, key: str = Header(...)) -> User | None:
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


class DynamicAuth:
    """Dynamic authentication that checks DEBUG mode at runtime."""

    def __init__(self):
        self.header_auth = ApiKeyHeaderAuth()

    def __call__(self, request, key: str | None = Header(None)) -> User | None:
        """
        Authenticate user, bypassing authentication in DEBUG mode.

        In DEBUG mode, returns a dummy user for testing.
        In production mode, uses X-API-Key header authentication.
        """
        from django.conf import settings
        key_provided = 'yes' if key else 'no'
        print(f"[DynamicAuth] DEBUG={settings.DEBUG}, key provided={key_provided}")

        if settings.DEBUG:
            # Return a dummy user for testing
            # Get or create a test user (username='test', email='test@example.com')
            from django.contrib.auth import get_user_model
            user_model = get_user_model()
            user, _ = user_model.objects.get_or_create(
                username='test',
                defaults={'email': 'test@example.com'}
            )
            print(f"[DynamicAuth] DEBUG mode, returning user: {user.username}")
            return user

        # Use header authentication
        if key is None:
            print("[DynamicAuth] No API key provided in production mode")
            return None
        print("[DynamicAuth] Attempting API key authentication")
        return self.header_auth(request, key)


def get_api_key_auth():
    """Get the appropriate authentication class based on configuration."""
    # Return DynamicAuth which handles DEBUG mode at runtime
    return DynamicAuth()
