"""Sliding-window call rate limiter, used to pace FBref access (FR-1.1).

See openspec/specs/player-data-ingestion/spec.md "FBref requests respect
the documented rate limit" and design.md decision #3: this paces *calls*
to at most `max_calls` per rolling `window_seconds`, which is a
conservative approximation of FBref's real per-request limit since a
single high-level `soccerdata` call may issue more than one HTTP request.
"""
from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable


class SlidingWindowRateLimiter:
    """Blocks (sleeps) as needed to keep calls within a rolling window."""

    def __init__(
        self,
        max_calls: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._max_calls = max_calls
        self._window_seconds = window_seconds
        self._clock = clock
        self._sleep = sleep
        self._call_times: deque[float] = deque()

    def acquire(self) -> None:
        """Block until another call is allowed within the window, then record it."""
        now = self._clock()
        self._evict_expired(now)

        if len(self._call_times) >= self._max_calls:
            oldest = self._call_times[0]
            wait_for = (oldest + self._window_seconds) - now
            if wait_for > 0:
                self._sleep(wait_for)
            now = self._clock()
            self._evict_expired(now)

        self._call_times.append(now)

    def _evict_expired(self, now: float) -> None:
        cutoff = now - self._window_seconds
        while self._call_times and self._call_times[0] <= cutoff:
            self._call_times.popleft()
