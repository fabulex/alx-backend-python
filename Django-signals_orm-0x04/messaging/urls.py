#!/usr/bin/env python3
"""URL configuration for messaging app."""

from django.urls import path
from messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.conversation_list, name="conversation_list"),
    path("thread/<int:message_id>/", views.conversation_thread, name="conversation_thread"),
    path("reply/<int:parent_id>/", views.reply_to_message, name="reply"),
    path("account/delete/", views.delete_user, name="delete_user"),
]
