#!/usr/bin/env python3
"""Models with automatic cleanup via CASCADE."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Message(models.Model):
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
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["edited_at"]),
        ]


class MessageHistory(models.Model):
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
    )

    class Meta:
        ordering = ["-edited_at"]
        verbose_name_plural = "Message History"
