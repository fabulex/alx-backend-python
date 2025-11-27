# chats/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model."""
    list_display = ('email', 'first_name', 'last_name', 'role', 'created_at', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('user_id', 'created_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at')}),
        ('Custom ID', {'fields': ('user_id',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

    # Use email for search in add/change forms
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(email__icontains=search_term)
        return queryset.distinct()


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin for Conversation model."""
    list_display = ('conversation_id', 'created_at', 'participant_count')
    list_filter = ('created_at',)
    search_fields = ('conversation_id',)
    readonly_fields = ('conversation_id', 'created_at')
    filter_horizontal = ('participants',)  # For better UX in adding/removing participants

    def participant_count(self, obj):
        """Display the number of participants."""
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin for Message model."""
    list_display = ('message_id', 'sender', 'conversation', 'sent_at', 'message_preview')
    list_filter = ('sent_at', 'sender', 'conversation')
    search_fields = ('message_body', 'sender__email', 'conversation__conversation_id')
    readonly_fields = ('message_id', 'sent_at')
    date_hierarchy = 'sent_at'

    def message_preview(self, obj):
        """Show a truncated preview of the message body."""
        return obj.message_body[:50] + '...' if len(obj.message_body) > 50 else obj.message_body
    message_preview.short_description = 'Message Preview'
