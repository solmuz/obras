"""
Rate limiting configuration using slowapi.

Applies configurable rate limits to protect sensitive endpoints
(login, refresh) against brute-force attacks.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=[],  # No default limit; apply per-endpoint
    storage_uri="memory://",  # Explicit in-memory store (required for limits >= 3.0)
)

# Pre-built limit strings from config
LOGIN_RATE_LIMIT = f"{settings.RATE_LIMIT_LOGIN_ATTEMPTS}/{settings.RATE_LIMIT_LOGIN_WINDOW_MINUTES}minute"
# Refresh is slightly more generous than login
REFRESH_RATE_LIMIT = f"{settings.RATE_LIMIT_LOGIN_ATTEMPTS * 2}/{settings.RATE_LIMIT_LOGIN_WINDOW_MINUTES}minute"
