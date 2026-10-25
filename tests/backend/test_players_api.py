"""API tests for player search, detail, and similarity routes (FR-3.2/3.3, FR-4.2)."""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.models.db import Base, get_session
from backend.models.player_records import upsert_player


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=__import__("sqlalchemy").pool.StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)

    def _override_session():
        session = factory()
        try:
            yield session
            session.commit()
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_session

    seed_session = factory()
    upsert_player(
        seed_session, "young-lb", name="Young Left Back", age=19, position="LB",
        strong_foot="Left", league_band="Bangladesh Football League",
        estimated_value_eur=500_000, ancestry_eligibility="ELIGIBLE & CLEARED",
    )
    upsert_player(
        seed_session, "old-st", name="Veteran Striker", age=32, position="ST",
        strong_foot="Right", league_band="Bangladesh Football League",
        goals_per_90=0.5, key_passes_per_90=0.4, progressive_carries_per_90=1.2,
        tackles_won_per_90=0.3, aerial_duel_pct=55.0,
    )
    upsert_player(
        seed_session, "similar-st", name="Similar Striker", age=27, position="ST",
        strong_foot="Right", league_band="EFL Championship",
        goals_per_90=0.48, key_passes_per_90=0.42, progressive_carries_per_90=1.25,
        tackles_won_per_90=0.28, aerial_duel_pct=53.0,
    )
    seed_session.commit()
    seed_session.close()

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_search_with_no_filters_returns_all(client):
    resp = client.get("/api/v1/players")
    assert resp.status_code == 200
    assert {p["id"] for p in resp.json()} == {"young-lb", "old-st", "similar-st"}


def test_search_max_age_filter(client):
    resp = client.get("/api/v1/players", params={"max_age": 25})
    assert resp.status_code == 200
    assert {p["id"] for p in resp.json()} == {"young-lb"}


def test_search_combined_filters(client):
    resp = client.get("/api/v1/players", params={"position": "ST", "strong_foot": "Right"})
    assert resp.status_code == 200
    assert {p["id"] for p in resp.json()} == {"old-st", "similar-st"}


def test_search_diaspora_eligible_filter(client):
    resp = client.get("/api/v1/players", params={"diaspora_eligible": True})
    assert resp.status_code == 200
    assert {p["id"] for p in resp.json()} == {"young-lb"}


def test_player_detail_found(client):
    resp = client.get("/api/v1/players/young-lb")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Young Left Back"


def test_player_detail_not_found(client):
    resp = client.get("/api/v1/players/does-not-exist")
    assert resp.status_code == 404


def test_similarity_unknown_player_is_404(client):
    resp = client.get("/api/v1/players/does-not-exist/similar")
    assert resp.status_code == 404


def test_similarity_no_metrics_returns_empty_list(client):
    resp = client.get("/api/v1/players/young-lb/similar")
    assert resp.status_code == 200
    assert resp.json() == []


def test_similarity_ranks_the_closer_profile_first(client):
    start = time.monotonic()
    resp = client.get("/api/v1/players/old-st/similar")
    elapsed_ms = (time.monotonic() - start) * 1000
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["player_id"] == "similar-st"
    assert elapsed_ms < 500  # NFR-perf
