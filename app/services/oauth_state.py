from __future__ import annotations

import secrets
import time
from threading import Lock


class OAuthStateStore:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self.ttl_seconds = ttl_seconds
        self._states: dict[str, float] = {}
        self._lock = Lock()

    def issue_state(self) -> str:
        state = secrets.token_urlsafe(32)
        now = time.monotonic()
        with self._lock:
            self._purge_expired_locked(now)
            self._states[state] = now + self.ttl_seconds
        return state

    def validate_and_consume(self, state: str) -> bool:
        now = time.monotonic()
        with self._lock:
            self._purge_expired_locked(now)
            expires_at = self._states.pop(state, None)
        return expires_at is not None and expires_at >= now

    def _purge_expired_locked(self, now: float) -> None:
        expired = [state for state, expires_at in self._states.items() if expires_at < now]
        for state in expired:
            self._states.pop(state, None)
