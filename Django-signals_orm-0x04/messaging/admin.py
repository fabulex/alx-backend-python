#!/usr/bin/env python3
"""Admin configuration for messaging app."""

from messaging.models import Message, Notification
from django.contrib import admin


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = ("id", "sender", "receiver", "timestamp", "is_read")
    list_filter = ("is_read", "timestamp")
    search_fields = (
        "sender__username",
        "receiver__username",
        "content",
    )
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""

    list_display = ("id", "user", "message", "is_seen", "created_at")
    list_filter = ("is_seen", "created_at")
    search_fields = (
        "user__username",
        "message__content",
        "message__sender__username",
    )
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


# Required final newline
