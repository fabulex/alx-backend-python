# chats/filters.py
import django_filters
from django_filters import rest_framework as filters
from .models import Message


class MessageFilter(filters.FilterSet):
    """
    Filter messages by specific users (sender) and time range.
    Optional: filter by conversation.
    """
    sender = filters.CharFilter(field_name="sender__user_id", lookup_expr="exact")
    conversation = filters.CharFilter(field_name="conversation__conversation_id", lookup_expr="exact")

    sent_after = filters.IsoDateTimeFilter(field_name="sent_at", lookup_expr="gte")
    sent_before = filters.IsoDateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["sender", "conversation", "sent_after", "sent_before"]
