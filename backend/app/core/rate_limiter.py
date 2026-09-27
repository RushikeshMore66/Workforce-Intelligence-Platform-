"""
Small process-local login rate limiter.

Purpose:
    - protect local development
    - protect single-process deployments
    - provide deterministic tests

Important:
    This is NOT a distributed production rate limiter.

For production with multiple API workers or multiple machines,
use a shared rate-limit store or enforce rate limits at the edge
(reverse proxy / API gateway / Redis-backed service).
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from math import ceil


class LoginRateLimiter:
    """
    Sliding-window limiter for login attempts.

    Each key tracks timestamps for failed authentication attempts.

    Example:

        maximum_attempts = 5
        window_seconds = 60

    After five failures inside sixty seconds, the caller receives
    a retry interval.
    """

    def __init__(
        self,
        maximum_attempts: int = 5,
        window_seconds: int = 60,
    ):
        if maximum_attempts < 1:
            raise ValueError(
                "maximum_attempts must be >= 1"
            )

        if window_seconds < 1:
            raise ValueError(
                "window_seconds must be >= 1"
            )

        self.maximum_attempts = maximum_attempts
        self.window_seconds = window_seconds

        self._attempts = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(
        self,
        key: str,
    ) -> tuple[bool, int]:
        """
        Return:

            (True, 0)
                if another login attempt is allowed.

            (False, retry_after_seconds)
                if the key is rate limited.
        """

        now = time.monotonic()

        with self._lock:
            attempts = self._attempts[key]

            self._prune(
                attempts,
                now,
            )

            if len(attempts) < self.maximum_attempts:
                return True, 0

            retry_after = (
                attempts[0]
                + self.window_seconds
                - now
            )

            return (
                False,
                max(1, ceil(retry_after)),
            )

    def record_failure(
        self,
        key: str,
    ) -> None:
        """
        Record a failed login attempt.
        """

        now = time.monotonic()

        with self._lock:
            attempts = self._attempts[key]

            self._prune(
                attempts,
                now,
            )

            attempts.append(now)

    def reset(
        self,
        key: str,
    ) -> None:
        """
        Clear the failed-attempt history after a successful login.
        """

        with self._lock:
            self._attempts.pop(
                key,
                None,
            )

    def _prune(
        self,
        attempts: deque[float],
        now: float,
    ) -> None:
        cutoff = now - self.window_seconds

        while attempts and attempts[0] <= cutoff:
            attempts.popleft()