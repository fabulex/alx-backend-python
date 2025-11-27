#!/usr/bin/env python3
"""Messaging models with custom manager for unread messages."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to retrieve only unread messages for a specific user.
    Optimized with .only() to reduce memory and DB load.
    """
    def for_user(self, user):
        """
        Return unread messages where the user is the receiver.
        Uses .only() to fetch only required fields.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).only(
            "id",
            "sender",
            "content",
            "timestamp",
            "parent_message",
        ).select_related("sender")


class Message(models.Model):
    """Threaded message with read status and custom manager."""
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_messages",
    )
    is_read = models.BooleanField(default=False)  # ← Required field

    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    # Custom manager for unread messages
    unread = UnreadMessagesManager()           # ← Custom manager attached
    objects = models.Manager()                 # Default manager

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "is_read", "-timestamp"]),
            models.Index(fields=["parent_message"]),
        ]

    def __str__(self) -> str:
        status = " [UNREAD]" if not self.is_read else ""
        return f"{self.sender} → {self.receiver}: {self.content[:30]}{status}"

    def mark_as_read(self):
        """Mark message as read if not already."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])
