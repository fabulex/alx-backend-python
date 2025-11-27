#!/usr/bin/env python3
"""URL configuration for messaging app."""

from django.urls import path
from messaging import views

app_name = "messaging"

urlpatterns = [
    # ... your other URLs
    path("delete-account/", views.delete_user, name="delete_user"),
]
