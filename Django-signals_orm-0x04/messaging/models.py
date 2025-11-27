#!/usr/bin/env python3
"""Models for the messaging application."""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    """Represents a private message with edit tracking."""
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
    edited_at = models.DateTimeField(null=True, blank=True)  # Tracks last edit
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
        ]

    def __str__(self) -> str:
        edited = " (edited)" if self.edited_at else ""
        return f"{self.sender} → {self.receiver}: {self.content[:30]}{edited}"


class MessageHistory(models.Model):
    """Stores previous versions of edited messages."""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history",
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name_plural = "Message History"

    def __str__(self) -> str:
        return f"History #{self.pk} for Message #{self.message.id} ({self.edited_at.date()})"
