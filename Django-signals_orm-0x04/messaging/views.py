#!/usr/bin/env python3
"""Views using custom unread manager."""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from .models import Message


@login_required
def inbox_unread(request):
    """
    Display only unread messages using the custom manager.
    Fully optimized with .only() and select_related.
    """
    unread_messages = Message.unread.for_user(request.user)

    context = {
        "unread_messages": unread_messages,
        "unread_count": unread_messages.count(),
    }
    return render(request, "messaging/inbox_unread.html", context)


class InboxUnreadListView(ListView):
    """Class-based version using the same custom manager."""
    template_name = "messaging/inbox_unread_cbv.html"
    context_object_name = "unread_messages"

    def get_queryset(self):
        return Message.unread.for_user(self.request.user)
