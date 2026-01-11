# core/management/commands/generate_api_key.py
import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.models import ApiKey


class Command(BaseCommand):
    help = "Generate an API key for a user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Username to generate API key for"
        )
        parser.add_argument(
            "--name",
            type=str,
            default="Generated API Key",
            help="Descriptive name for the API key"
        )
        parser.add_argument(
            "--expires",
            type=str,
            default=None,
            help="Expiration date (YYYY-MM-DD HH:MM:SS), optional"
        )
        parser.add_argument(
            "--output",
            type=str,
            choices=["text", "json"],
            default="text",
            help="Output format (text or json)"
        )

    def handle(self, *args, **options):
        user_model = get_user_model()

        try:
            user = user_model.objects.get(username=options["username"])
        except user_model.DoesNotExist:
            raise CommandError(f"User '{options['username']}' does not exist") from None

        # Parse expiration date if provided
        expires_at = None
        if options["expires"]:
            from django.utils.dateparse import parse_datetime
            expires_at = parse_datetime(options["expires"])
            if expires_at is None:
                raise CommandError(f"Invalid datetime format: {options['expires']}")

        # Create API key
        api_key = ApiKey.objects.create(
            user=user,
            name=options["name"],
            expires_at=expires_at,
            is_active=True
        )

        result = {
            "id": api_key.public_id,
            "key": api_key.key,
            "user": api_key.user.username,
            "name": api_key.name,
            "expires_at": (
                api_key.expires_at.isoformat() if api_key.expires_at else None
            ),
            "created_at": api_key.created_at.isoformat(),
        }

        if options["output"] == "json":
            self.stdout.write(json.dumps(result, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS("API Key generated successfully!"))
            self.stdout.write(f"Key ID: {api_key.public_id}")
            self.stdout.write(f"API Key: {api_key.key}")
            self.stdout.write(f"User: {api_key.user.username}")
            self.stdout.write(f"Name: {api_key.name}")
            if api_key.expires_at:
                self.stdout.write(f"Expires: {api_key.expires_at}")
            self.stdout.write(self.style.WARNING(
                "Store this key securely. It will not be shown again."
            ))
