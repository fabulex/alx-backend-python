# chats/middleware.py
import logging
from datetime import datetime
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone

# -----------------------------
# Logger setup – FIXED: log file in PROJECT ROOT
# -----------------------------
logger = logging.getLogger("request_logger")
logger.setLevel(logging.INFO)

# ← CORRECT PATH: requests.log in project root (not inside chats/)
handler = logging.FileHandler("requests.log")
handler.setFormatter(logging.Formatter("%(message)s"))

# Prevent duplicate handlers during development reload
if not logger.handlers:
    logger.addHandler(handler)


# -----------------------------
# Middleware:
# -----------------------------
class RequestLoggingMiddleware:
    """
    Logs each user's request with timestamp, user, and path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = (
            request.user.email
            if request.user.is_authenticated and hasattr(request.user, "email")
            else "Anonymous"
        )
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"{timestamp} - User: {user} - Path: {request.path}")

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Blocks access outside 6:00 AM – 9:00 PM (21:00).
    Returns clean 403 JSON response.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = timezone.localtime()
        current_hour = now.hour

        # Allowed: 6 AM (6) to 8:59 PM (20:59) → < 21
        if not (6 <= current_hour < 21):
            user = (
                request.user.email
                if request.user.is_authenticated and hasattr(request.user, "email")
                else "Anonymous"
            )
            logger.warning(
                f"ACCESS DENIED - Outside allowed hours: {now.strftime('%Y-%m-%d %H:%M:%S')} - "
                f"User: {user} - Path: {request.path}"
            )
            return JsonResponse(
                {
                    "detail": "Access to the messaging app is restricted outside 6:00 AM - 9:00 PM.",
                    "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "allowed_hours": "06:00 - 21:00",
                },
                status=403,
            )

        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and "/messages/" in request.path:
            ip = request.META.get("REMOTE_ADDR", "unknown")
            key = f"rate_limit:{ip}"
            now = timezone.now()
            timestamps = cache.get(key, [])
            timestamps = [t for t in timestamps if (now - t).total_seconds() < 60]

            if len(timestamps) >= 5:
                logger.warning(f"RATE LIMIT EXCEEDED: IP={ip}")
                return JsonResponse({"detail": "You can only send 5 messages per minute."}, status=429)

            timestamps.append(now)
            cache.set(key, timestamps, timeout=60)

        return self.get_response(request)


class RolepermissionMiddleware:
    """
    Blocks non-admin/non-moderator users from accessing protected endpoints.
    Returns 403 Forbidden if user role is not 'admin' or 'moderator'.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check for unauthenticated users (let auth middleware handle it)
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Get user role (assuming your User model has a 'role' field)
        user_role = getattr(request.user, 'role', None)

        allowed_roles = ['admin', 'moderator']

        if user_role not in allowed_roles:
            logger.warning(
                f"ACCESS DENIED (Role): User {request.user.email} (role: {user_role}) "
                f"tried to access {request.path}"
            )
            return JsonResponse({
                "detail": "You do not have permission to perform this action.",
                "required_role": "admin or moderator",
                "your_role": user_role or "none"
            }, status=403)

        # User has correct role → proceed
        return self.get_response(request)
