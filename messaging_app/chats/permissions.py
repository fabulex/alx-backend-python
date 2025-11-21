# chats/permissions.py
from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow the sender of a message to edit or delete it.
    """
    message = "You can only edit or delete your own messages."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to conversation participants
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the message sender
        is_sender = obj.sender == request.user
        if not is_sender:
            logger.warning(
                f"User {request.user.email} attempted to modify message {obj.message_id} "
                f"sent by {obj.sender.email}"
            )
        return is_sender


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    message = "You must be a participant in this conversation."

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        is_participant = obj.participants.filter(user_id=request.user.user_id).exists()

        if not is_participant:
            logger.warning(
                f"User {request.user.email} attempted to access conversation "
                f"{obj.conversation_id} without being a participant"
            )

        return is_participant


class CanCreateMessage(permissions.BasePermission):
    """
    Custom permission to ensure users can only send messages to conversations they participate in.
    """
    message = "You can only send messages to conversations you are part of."

    def has_permission(self, request, view):
        # For POST requests, check if user is participant in the target conversation
        if request.method == 'POST':
            conversation_id = view.kwargs.get('conversation_pk')
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

        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own profile.
    """
    message = "You can only access your own profile."

    def has_object_permission(self, request, view, obj):
        # Check if the user is accessing their own profile
        is_owner = obj.user_id == request.user.user_id

        if not is_owner:
            logger.warning(
                f"User {request.user.email} attempted to access profile of {obj.email}"
            )

        return is_owner
