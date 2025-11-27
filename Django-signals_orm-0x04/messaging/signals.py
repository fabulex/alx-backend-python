#!/usr/bin/env python3
"""Signal for extra cleanup and logging on user deletion."""

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_delete, sender=User)
def log_and_cleanup_user_data(sender, instance: User, **kwargs):
    """
    Optional: Log when a user deletes their account.
    CASCADE already handles Message + MessageHistory deletion.
    This is for logging or future extensions (e.g. anonymize, soft-delete).
    """
    username = instance.username
    email = instance.email or "no-email"
    # You can log to file, send admin email, etc.
    print(f"[ACCOUNT DELETED] User '{username}' ({email}) deleted their account.")
    # Example: send_mail("User deleted", ...)
