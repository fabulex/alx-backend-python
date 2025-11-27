#!/usr/bin/env python3
"""Models for the messaging application."""

from typing import TYPE_CHECKING

from django.db import models
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import User


User = get_user_model()


class Message(models.Model):
    """Represents a private message sent between users."""

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
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["sender", "-timestamp"]),
        ]

    def __str__(self) -> str:
        """Return a short representation of the message."""
        return f"{self.sender} → {self.receiver}: {self.content[:30]}..."



class Notification(models.Model):
    """Notification generated when a user receives a new message."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "message"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_seen"]),
        ]

    def __str__(self) -> str:
        """Return string representation of the notification."""
        sender = self.message.sender
        return f"Notification → {self.user}: New message from {sender}"


# Required final newline
