#!/usr/bin/env python3
"""Views for threaded conversations."""

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from .models import Message


@login_required
def conversation_thread(request, message_id):
    """Display full conversation thread with optimized queries."""
    root_message = get_object_or_404(
        Message,
        id=message_id,
        receiver=request.user  # or sender — adjust logic as needed
    )

    # Get root + all replies in ONE optimized query
    thread = root_message.get_thread()

    # Alternative: Use prefetch_related for tree structure (advanced)
    # messages = Message.objects.filter(
    #     parent_message__isnull=True,
    #     receiver=request.user
    # ).prefetch_related(
    #     Prefetch("replies", queryset=Message.objects.select_related("sender", "receiver"))
    # )

    context = {
        "thread": thread,
        "root_message": root_message.get_root(),
    }
    return render(request, "messaging/thread.html", context)
