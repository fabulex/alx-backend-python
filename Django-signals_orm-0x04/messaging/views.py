#!/usr/bin/env python3
"""Views for messaging app — including account deletion."""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout


@login_required
def delete_user(request):
    """
    Allow authenticated user to permanently delete their account.
    All data is cleaned up automatically via CASCADE + signal.
    """
    if request.method == "POST":
        user = request.user
        username = user.username

        # Optional: require password confirmation
        # from django.contrib.auth import authenticate
        # password = request.POST.get("password")
        # if not authenticate(username=user.username, password=password):
        #     messages.error(request, "Incorrect password.")
        #     return redirect("delete_user")

        user.delete()  # Triggers CASCADE + post_delete signal

        messages.success(request, f"Account '{username}' has been permanently deleted.")
        return redirect("home")  # or login page

    return render(request, "messaging/delete_account.html")
