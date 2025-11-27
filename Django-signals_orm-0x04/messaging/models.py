#!/usr/bin/env python3
"""Models for the messaging application — with full edit history."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Message(models.Model):
    """Private message with full edit tracking."""
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
        help_text="Last user who edited this message",
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["edited_at"]),
        ]

    def __str__(self) -> str:
        edited = " (edited)" if self.edited_at else ""
        return f"{self.sender} → {self.receiver}: {self.content[:30]}{edited}"


class MessageHistory(models.Model):
    """Complete audit trail — every edit saves old content + who edited."""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history",
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_edits",
        help_text="User who made this edit",
    )

    class Meta:
        ordering = ["-edited_at"]
        verbose_name_plural = "Message History"

    def __str__(self) -> str:
        editor = self.edited_by or "Unknown"
        return f"Edit by {editor} on {self.edited_at.date()}"
