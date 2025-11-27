#!/usr/bin/env python3
"""Signal handlers for automatic notification creation."""

from messaging.models import Message, Notification
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Message)
def create_message_notification(
    sender,
    instance: Message,
    created: bool,
    **kwargs,
) -> None:
    """
    Create a notification when a new message is sent to another user.

    Skips creation if:
    - The save is an update (not creation)
    - The sender and receiver are the same user
    """
    if not created:
        return

    if instance.sender == instance.receiver:
        return

    Notification.objects.create(
        user=instance.receiver,
        message=instance,
    )


# Required final newline
