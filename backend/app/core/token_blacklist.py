"""
In-memory token blacklist with automatic TTL-based cleanup.

Blacklisted tokens are stored with their expiration time. A background
cleanup runs periodically to evict expired entries and keep memory bounded.

For production at scale, replace the in-memory set with Redis:
    redis.setex(f"blacklist:{jti}", ttl_seconds, "1")
"""

import threading
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.core.security import decode_jwt_token

logger = logging.getLogger(__name__)


class TokenBlacklist:
    """Thread-safe in-memory token blacklist with TTL eviction."""

    def __init__(self) -> None:
        # token_str -> expiration unix timestamp
        self._store: dict[str, float] = {}
        self._lock = threading.Lock()
        self._start_cleanup_thread()

    def _start_cleanup_thread(self) -> None:
        """Start a daemon thread that periodically evicts expired entries."""
        thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        thread.start()

    def _cleanup_loop(self) -> None:
        """Remove expired tokens every 60 seconds."""
        while True:
            time.sleep(60)
            self._evict_expired()

    def _evict_expired(self) -> None:
        now = time.time()
        with self._lock:
            expired_keys = [t for t, exp in self._store.items() if exp <= now]
            for key in expired_keys:
                del self._store[key]
            if expired_keys:
                logger.debug(f"Token blacklist: evicted {len(expired_keys)} expired entries")

    def add(self, token: str) -> None:
        """
        Add a token to the blacklist.

        The token is stored until its JWT `exp` claim, after which it will
        be evicted automatically (no need to blacklist expired tokens forever).
        """
        payload = decode_jwt_token(token)
        if payload is None:
            # Token is already invalid/expired — nothing to blacklist
            return

        exp = payload.get("exp")
        if exp is None:
            return

        with self._lock:
            self._store[token] = float(exp)

        logger.info("Token added to blacklist (expires at %s)", datetime.fromtimestamp(exp, tz=timezone.utc))

    def is_blacklisted(self, token: str) -> bool:
        """Check whether a token has been blacklisted."""
        with self._lock:
            if token not in self._store:
                return False
            # Double-check: if it expired, remove it and return False
            if self._store[token] <= time.time():
                del self._store[token]
                return False
            return True

    @property
    def size(self) -> int:
        """Current number of blacklisted tokens (for monitoring)."""
        with self._lock:
            return len(self._store)


# Singleton instance used across the application
token_blacklist = TokenBlacklist()
