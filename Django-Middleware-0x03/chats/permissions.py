# chats/permissions.py
from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow owners to edit; anyone can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        # Explicitly check unsafe methods
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.owner == request.user
        return False


class IsMessageSender(permissions.BasePermission):
    """
    Only the sender of a message can edit/delete it.
    """
    message = "You can only edit or delete your own messages."

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        if request.method in ["PUT", "PATCH", "DELETE"]:
            is_sender = obj.sender == request.user
            if not is_sender:
                logger.warning(
                    f"User {request.user.email} attempted to modify message {obj.message_id} "
                    f"sent by {obj.sender.email}"
                )
            return is_sender
        return False


class IsConversationParticipant(permissions.BasePermission):
    """
    Only participants of a conversation can access it.
    """
    message = "You must be a participant in this conversation."

    def has_object_permission(self, request, view, obj):
        is_participant = obj.participants.filter(user_id=request.user.user_id).exists()
        if not is_participant:
            logger.warning(
                f"User {request.user.email} attempted to access conversation "
                f"{obj.conversation_id} without being a participant"
            )
        return is_participant


class CanCreateMessage(permissions.BasePermission):
    """
    Ensure users can only send messages to conversations they participate in.
    """
    message = "You can only send messages to conversations you are part of."

    def has_permission(self, request, view):
        if request.method == "POST":
            conversation_id = view.kwargs.get("conversation_pk")
            if conversation_id:
                from chats.models import Conversation
                try:
                    conversation = Conversation.objects.get(conversation_id=conversation_id)
                    is_participant = conversation.participants.filter(
                        user_id=request.user.user_id
                    ).exists()
                    if not is_participant:
                        logger.warning(
                            f"User {request.user.email} attempted to send message to "
                            f"conversation {conversation_id} without being a participant"
                        )
                    return is_participant
                except Conversation.DoesNotExist:
                    return False
        # Allow other methods by default
        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Only admins can edit; others can read.
    """
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user and request.user.is_authenticated
        if request.method in ["PUT", "PATCH", "DELETE", "POST"]:
            return request.user and request.user.is_authenticated and request.user.role == 'admin'
        return False


class IsOwner(permissions.BasePermission):
    """
    Only allow users to access their own profile.
    """
    message = "You can only access your own profile."

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        if request.method in ["PUT", "PATCH", "DELETE"]:
            is_owner = obj.user_id == request.user.user_id
            if not is_owner:
                logger.warning(
                    f"User {request.user.email} attempted to access profile of {obj.email}"
                )
            return is_owner
        return False
