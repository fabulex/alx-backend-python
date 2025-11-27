#!/usr/bin/env python3
"""Messaging models with threaded conversations."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Message(models.Model):
    """Threaded message with replies and edit history."""
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

    # Threading: self-referential FK for replies
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["parent_message"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        prefix = f"↳ Reply to #{self.parent_message.id} " if self.parent_message else ""
        edited = " (edited)" if self.edited_at else ""
        return f"{prefix}{self.sender} → {self.receiver}: {self.content[:30]}{edited}"

    # Helper: get root message of thread
    def get_root(self):
        message = self
        while message.parent_message:
            message = message.parent_message
        return message

    # Helper: get all descendants (replies, replies to replies, etc.)
    def get_thread(self):
        """Return all messages in this thread (root + replies recursively)."""
        return Message.objects.filter(
            id__in=self._get_descendant_ids()
        ).select_related("sender", "receiver", "edited_by").order_by("timestamp")

    def _get_descendant_ids(self):
        """Recursive helper to collect all reply IDs."""
        ids = {self.id}
        for reply in self.replies.all():
            ids.update(reply._get_descendant_ids())
        return ids
