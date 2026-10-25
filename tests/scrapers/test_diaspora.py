"""Tests for the diaspora reference-data loader (FR-1.1)."""
from __future__ import annotations

import socket

import pytest

from scrapers.diaspora import scrape_diaspora_listings


def test_loads_all_six_known_players():
    records = scrape_diaspora_listings()
    assert len(records) == 6
    ids = {r["id"] for r in records}
    assert ids == {
        "hamza-choudhury",
        "tariq-kazi",
        "jamal-bhuyan",
        "fahamedul-islam",
        "cuba-mitchell",
        "shamit-shome",
    }


def test_every_record_has_a_last_verified_date():
    records = scrape_diaspora_listings()
    for record in records:
        assert record["last_verified_date"] is not None


def test_no_network_request_is_made(monkeypatch: pytest.MonkeyPatch):
    def _blocked(*args, **kwargs):
        raise AssertionError("diaspora loader must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", _blocked)
    monkeypatch.setattr(socket.socket, "connect", _blocked)

    records = scrape_diaspora_listings()
    assert len(records) == 6
