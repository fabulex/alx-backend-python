#!/usr/bin/env python3
"""Signal handler for logging message edit history."""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from messaging.models import Message, MessageHistory


@receiver(pre_save, sender=Message)
def log_message_edit_history(sender, instance: Message, **kwargs) -> None:
    """Save old content before update and mark message as edited."""
    if not instance.pk:  # New message
        return

    try:
        old = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=old.content,
        )
        instance.edited_at = timezone.now()
