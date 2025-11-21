# chats/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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

logger = logging.getLogger(__name__)
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management:
    - list: only current user's profile
    - create: open registration
    - retrieve/update/partial_update: only owner
    """
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return User.objects.filter(user_id=user.user_id)
        return User.objects.none()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def search(self, request):
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
        ).exclude(user_id=request.user.user_id)[:10]

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversations:
    - list: user's conversations
    - create: new conversation, auto-add current user
    - retrieve/update/destroy: only participants
    """
    serializer_class = ConversationSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action in ['list', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).prefetch_related(
            'participants', 'messages', 'messages__sender'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.participants.add(self.request.user)
        logger.info(f"User {self.request.user.email} created conversation {instance.conversation_id}")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsConversationParticipant])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
            if conversation.participants.filter(user_id=user_id).exists():
                return Response({'detail': 'User is already a participant.'}, status=status.HTTP_400_BAD_REQUEST)

            conversation.participants.add(user)
            logger.info(f"User {request.user.email} added {user.email} to conversation {conversation.conversation_id}")
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsConversationParticipant])
    def remove_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id', str(request.user.user_id))
        try:
            user = User.objects.get(user_id=user_id)

            if str(user.user_id) != str(request.user.user_id):
                return Response({'detail': 'You can only remove yourself.'}, status=status.HTTP_403_FORBIDDEN)

            if not conversation.participants.filter(user_id=user_id).exists():
                return Response({'detail': 'User is not a participant.'}, status=status.HTTP_400_BAD_REQUEST)

            conversation.participants.remove(user)
            logger.info(f"User {user.email} left conversation {conversation.conversation_id}")
            return Response({'detail': 'Successfully left the conversation.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Messages:
    - list: messages in user's conversations
    - create: send message to conversation (validate participant)
    - retrieve/update/destroy: only sender can modify
    """
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']             # Default: newest first
    filterset_class = MessageFilter
    pagination_class = MessagePagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, CanCreateMessage]
        else:
            permission_classes = [permissions.IsAuthenticated, IsMessageSender]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(conversation__participants=user).select_related(
            'sender', 'conversation'
        )

        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            queryset = queryset.filter(conversation__conversation_id=conversation_pk)

        return queryset.order_by('-sent_at')

    def create(self, request, *args, **kwargs):
        conversation_pk = self.kwargs.get('conversation_pk')

        if conversation_pk:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_pk)
                if not conversation.participants.filter(user_id=request.user.user_id).exists():
                    logger.warning(f"User {request.user.email} attempted to send message to conversation {conversation_pk} without being a participant")
                    return Response({'detail': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)
                request.data['conversation'] = str(conversation.conversation_id)
            except Conversation.DoesNotExist:
                return Response({'detail': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(f"User {request.user.email} sent message to conversation {serializer.validated_data['conversation'].conversation_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
