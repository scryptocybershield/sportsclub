# core/models/api_key.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from nanoid_field import NanoidField

from core.models.auditory import Auditory


class ApiKey(Auditory):
    """API Key for authenticating API requests."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False, db_index=True)
    key = NanoidField(unique=True, editable=False, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys"
    )
    name = models.CharField(
        max_length=100, help_text="Descriptive name for this API key"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Optional expiration date"
    )
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.user.username})"

    @property
    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired

    def mark_used(self):
        """Update last_used_at timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])
