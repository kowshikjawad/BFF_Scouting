"""Tests for the sliding-window rate limiter used by the FBref scraper."""
from __future__ import annotations

from scrapers._rate_limiter import SlidingWindowRateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_calls_within_the_limit_never_sleep():
    clock = FakeClock()
    sleeps: list[float] = []
    limiter = SlidingWindowRateLimiter(
        max_calls=10, window_seconds=60, clock=clock, sleep=sleeps.append
    )

    for _ in range(10):
        limiter.acquire()
        clock.advance(1.0)

    assert sleeps == []


def test_the_11th_call_within_60_seconds_sleeps_until_the_window_clears():
    clock = FakeClock()
    sleeps: list[float] = []
    limiter = SlidingWindowRateLimiter(
        max_calls=10, window_seconds=60, clock=clock, sleep=sleeps.append
    )

    for _ in range(10):
        limiter.acquire()  # at t=0, all 10 calls happen "instantly"

    limiter.acquire()  # 11th call, still within the same 60s window

    assert len(sleeps) == 1
    assert sleeps[0] == 60.0  # must wait for the oldest call to age out


def test_calls_spaced_beyond_the_window_never_sleep():
    clock = FakeClock()
    sleeps: list[float] = []
    limiter = SlidingWindowRateLimiter(
        max_calls=10, window_seconds=60, clock=clock, sleep=sleeps.append
    )

    for _ in range(25):
        limiter.acquire()
        clock.advance(10.0)  # well under 10 calls per rolling 60s

    assert sleeps == []
