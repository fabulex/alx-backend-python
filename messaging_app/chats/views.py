# chats/views.py
from rest_framework import (
    viewsets,
    permissions,
    status,
    filters
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    ConversationSerializer,
    MessageSerializer
)
from .permissions import (
    IsMessageSender,
    IsConversationParticipant,
    CanCreateMessage,
    IsOwner
)
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    - list: Only returns current user's profile
    - create: User registration (open to all)
    - retrieve, update, partial_update: Only allow users to access/modify their own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Allow anyone to register
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only owner can update/delete their profile
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            # All other actions require authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Use different serializer for registration
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Filter to only show authenticated user's profile for list/retrieve
        """
        if self.request.user.is_authenticated:
            return self.queryset.filter(user_id=self.request.user.user_id)
        return self.queryset.none()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def search(self, request):
        """
        Search for users by email, first name, or last name
        """
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response(
                {'detail': 'Search query must be at least 2 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(user_id=request.user.user_id)[:10]  # Limit to 10 results

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Conversations.
    - List: User's conversations (where they are participants).
    - Create: New conversation (automatically adds current user as participant).
    - Retrieve, Update, Destroy: Only for conversations user participates in.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['list', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter conversations to only those the current user is participating in.
        Optimize with prefetch_related to avoid N+1 queries.
        """
        return self.queryset.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            'messages',
            'messages__sender'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Automatically add the current user as a participant after creation.
        """
        instance = serializer.save()
        instance.participants.add(self.request.user)
        logger.info(
            f"User {self.request.user.email} created conversation {instance.conversation_id}"
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsConversationParticipant])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'detail': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user_id=user_id)
            if conversation.participants.filter(user_id=user_id).exists():
                return Response(
                    {'detail': 'User is already a participant.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            conversation.participants.add(user)
            logger.info(
                f"User {request.user.email} added {user.email} to conversation {conversation.conversation_id}"
            )

            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsConversationParticipant])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation (or leave conversation)
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id', str(request.user.user_id))

        try:
            user = User.objects.get(user_id=user_id)

            # Only allow removing self or if user is conversation creator
            if str(user.user_id) != str(request.user.user_id):
                return Response(
                    {'detail': 'You can only remove yourself from conversations.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if not conversation.participants.filter(user_id=user_id).exists():
                return Response(
                    {'detail': 'User is not a participant.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            conversation.participants.remove(user)
            logger.info(
                f"User {user.email} left conversation {conversation.conversation_id}"
            )

            return Response({'detail': 'Successfully left the conversation.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Messages.
    - List: Messages from conversations the user is participating in.
    - Create: Send a new message to an existing conversation (validates participation).
    - Retrieve: View message details.
    - Update, Destroy: Only message sender can update/delete their messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sent_at']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, CanCreateMessage]
        else:  # update, partial_update, destroy
            permission_classes = [permissions.IsAuthenticated, IsMessageSender]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter messages to only those in conversations the current user is participating in.
        If nested under a conversation, filter by that conversation.
        """
        queryset = self.queryset.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')

        # If this is a nested route, filter by conversation
        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            queryset = queryset.filter(conversation__conversation_id=conversation_pk)

        return queryset.order_by('-sent_at')

    def create(self, request, *args, **kwargs):
        """
        Override create to validate participation and set conversation from URL.
        """
        conversation_pk = self.kwargs.get('conversation_pk')

        if conversation_pk:
            # Nested route: get conversation from URL
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_pk)

                # Check if user is a participant
                if not conversation.participants.filter(user_id=request.user.user_id).exists():
                    logger.warning(
                        f"User {request.user.email} attempted to send message to "
                        f"conversation {conversation_pk} without being a participant"
                    )
                    return Response(
                        {'detail': 'You are not a participant in this conversation.'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Add conversation to request data
                request.data['conversation'] = str(conversation.conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {'detail': 'Conversation not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(
                f"User {request.user.email} sent message to conversation "
                f"{serializer.validated_data['conversation'].conversation_id}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """
        Set the sender to the current user.
        """
        serializer.save(sender=self.request.user)
