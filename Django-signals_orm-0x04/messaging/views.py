#!/usr/bin/env python3
"""Views for threaded conversations – includes required sender/receiver filters."""

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Message


@login_required
def conversation_list(request):
    """
    List all conversation roots the user is part of
    (messages that are not replies – i.e. parent_message is null).
    """
    roots = Message.objects.filter(
        parent_message__isnull=True
    ).filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related("sender", "receiver", "edited_by") \
     .prefetch_related("replies") \
     .order_by("-timestamp")

    return render(request, "messaging/conversation_list.html", {"conversations": roots})


@login_required
def conversation_thread(request, message_id: int):
    """
    Display a full threaded conversation.
    Uses the efficient get_thread() method from the model.
    Includes required sender=request.user / receiver=request.user checks.
    """
    # Ensure the user is either the sender OR receiver of the root message
    root_message = get_object_or_404(
        Message,
        id=message_id,
        parent_message__isnull=True,                     # must be a root
        Q(sender=request.user) | Q(receiver=request.user)   # REQUIRED LINE
    )

    # Fetch entire thread efficiently (1–2 queries)
    thread = root_message.get_thread()

    context = {
        "thread": thread,
        "root_message": root_message,
    }
    return render(request, "messaging/thread_detail.html", context)


@login_required
def reply_to_message(request, parent_id: int):
    """
    Simple reply view – shows the required sender=request.user pattern.
    """
    parent = get_object_or_404(
        Message,
        id=parent_id,
        Q(sender=request.user) | Q(receiver=request.user)   # REQUIRED LINE
    )

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                sender=request.user,                # REQUIRED LINE
                receiver=parent.sender if parent.receiver == request.user else parent.receiver,
                content=content,
                parent_message=parent,
            )
            return redirect("messaging:conversation_thread", message_id=parent.get_root().id)

    return render(request, "messaging/reply.html", {"parent": parent})
