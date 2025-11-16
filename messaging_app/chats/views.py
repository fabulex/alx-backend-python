# chats/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):  # Read-only for profiles; extend if needed
    """
    ViewSet for User profiles (read-only for security).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.user_id)  # Only own profile


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversations.
    - List: User's conversations (where they are participants).
    - Create: New conversation (automatically adds current user as participant).
    - Retrieve, Update, Destroy: Standard CRUD for owned conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter conversations to only those the current user is participating in.
        """
        return self.queryset.filter(participants=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Automatically add the current user as a participant after creation.
        """
        instance = serializer.save()
        instance.participants.add(self.request.user)
        instance.save()
        # Re-serialize to include the updated participants
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Messages.
    - List: Messages from conversations the user is participating in.
    - Create: Send a new message to an existing conversation (validates participation).
    - Retrieve, Update, Destroy: Standard CRUD for user's sent messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter messages to only those in conversations the current user is participating in.
        """
        return self.queryset.filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')

    def create(self, request, *args, **kwargs):
        """
        Override create to validate participation before saving.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.validated_data['conversation']
            if not conversation.participants.filter(user_id=request.user.user_id).exists():
                return Response(
                    {'detail': 'You are not a participant in this conversation.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """
        Set the sender to the current user.
        """
        serializer.save(sender=self.request.user)
