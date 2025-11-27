#!/usr/bin/env python3
"""Signal to log full edit history including editor."""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from messaging.models import Message, MessageHistory


@receiver(pre_save, sender=Message)
def log_message_edit_history(sender, instance: Message, **kwargs) -> None:
    """Log old content + who edited before saving changes."""
    if not instance.pk:  # New message → no history
        return

    try:
        old = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    # Only proceed if content actually changed
    if old.content != instance.content:
        # You can pass the current user via request in views, but for now:
        # We'll assume it's set in the view (common pattern)
        # Or fall back to sender if not provided
        editor = getattr(instance, "_current_user", None) or instance.sender

        MessageHistory.objects.create(
            message=instance,
            old_content=old.content,
            edited_by=editor,
        )

        instance.edited_at = timezone.now()
        instance.edited_by = editor
