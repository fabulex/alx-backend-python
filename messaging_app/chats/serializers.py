from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Excludes sensitive fields like password and permissions.
    """
    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at',
        ]
        read_only_fields = ['user_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes nested sender (User) for full details.
    Conversation is represented by ID for simplicity (avoids deep nesting here).
    """
    sender = UserSerializer(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())
    message_body = serializers.CharField(max_length=1000, required=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',
            'message_body',
            'sent_at',
        ]
        read_only_fields = ['message_id', 'sent_at']

    def validate_message_body(self, value):
        """
        Custom validation to ensure message body is not empty.
        """
        if not value or value.strip() == '':
            raise serializers.ValidationError("Message body cannot be empty.")
        if len(value) > 1000:  # Example max length
            raise serializers.ValidationError("Message body too long (max 1000 chars).")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Includes nested participants (Users) and messages (Messages) for full details.
    Uses SerializerMethodField for computed fields like participant_count and last_message_preview.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    # For creating a conversation, allow adding participants via IDs
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,  # Require at least some participants
        help_text="List of participant user_ids to add when creating/updating."
    )
    participant_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    def get_participant_count(self, obj):
        """
        Computed field: Number of participants in the conversation.
        """
        return obj.participants.count()

    def get_last_message_preview(self, obj):
        """
        Computed field: Preview of the last message in the conversation.
        """
        if obj.messages.exists():
            last_msg = obj.messages.order_by('-sent_at').first()
            return last_msg.message_body[:50] + '...' if len(last_msg.message_body) > 50 else last_msg.message_body
        return None

    def validate_participant_ids(self, value):
        """
        Custom validation to ensure at least 2 participants and they exist.
        """
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        existing_ids = set(User.objects.filter(user_id__in=value).values_list('user_id', flat=True))
        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid participant IDs: {list(invalid_ids)}")
        return value

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)
        return conversation

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop('participant_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            instance.participants.set(participants)
        return instance

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',  # Write-only for adding participants
            'participant_count',
            'last_message_preview',
            'messages',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at', 'participants', 'messages', 'participant_count', 'last_message_preview']
