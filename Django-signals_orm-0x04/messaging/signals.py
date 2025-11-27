#!/usr/bin/env python3
"""Signal to clean up all user-related data on account deletion."""

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from messaging.models import Message, MessageHistory

User = get_user_model()


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance: User, **kwargs) -> None:
    """
    Explicitly delete all messages and history related to the deleted user.
    This runs AFTER CASCADE has already done its job — but satisfies the task requirement
    of using post_delete + .filter().delete() explicitly.
    """
    # Explicit deletion as required by task — even though CASCADE already handled it
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Also clean up any history entries where user was the editor
    MessageHistory.objects.filter(edited_by=instance).delete()

    # Log the deletion
    print(f"[CLEANUP COMPLETE] All data for user '{instance.username}' (ID: {instance.id}) has been removed.")
