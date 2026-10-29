"""Demonstration data must activate real workflows without contaminating sourced records."""

from collections import Counter
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.models.db import Base, get_session
from backend.models.player import Player
from backend.models.player_records import get_player, list_players, upsert_player
from backend.similarity.pipeline import rank_similar
from scripts.seed_synthetic import generate_players, seed_synthetic


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture()
def demo_client(session):
    seed_synthetic(session)
    upsert_player(
        session,
        "real-source-player",
        name="Real source record",
        position="CM",
        league_band="Demo Bangladesh League",
        goals_per_90=0.2,
        key_passes_per_90=2,
        progressive_carries_per_90=3,
        tackles_won_per_90=2,
        aerial_duel_pct=50,
    )
    session.commit()
    app.dependency_overrides[get_session] = lambda: session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_generation_is_deterministic_complete_and_position_shaped():
    records = generate_players()
    assert records == generate_players()
    assert (
        len(records) == len({p["id"] for p in records}) == len({p["name"] for p in records}) == 160
    )
    cohorts = Counter((p["league_band"].split(" -- ")[0], p["position"]) for p in records)
    assert len(cohorts) == 40 and set(cohorts.values()) == {4}
    assert all(Player(**p).data_source == "synthetic" for p in records)
    assert all(
        all(value is not None for key, value in p.items() if key != "ancestry_eligibility")
        for p in records
    )
    assert all(0 <= p["aerial_duel_pct"] <= 100 for p in records)
    assert sum(p["goals_per_90"] for p in records if p["position"] == "ST") > sum(
        p["goals_per_90"] for p in records if p["position"] == "CB"
    )


def test_seeding_is_idempotent_and_preserves_real_facts(session):
    upsert_player(session, "real-player", name="Preserve Me", goals_per_90=None, age=21)
    before = get_player(session, "real-player")
    seed_synthetic(session)
    seed_synthetic(session)
    assert len(list_players(session, dataset="synthetic")) == 160
    assert len(list_players(session)) == 1
    assert get_player(session, "real-player") == before


def test_api_dataset_filters_and_provenance(demo_client):
    real = demo_client.get("/api/v1/players").json()
    demo = demo_client.get("/api/v1/players?dataset=synthetic").json()
    assert len(real) == 1 and real[0]["data_source"] == "real"
    assert len(demo) == 160 and all(p["data_source"] == "synthetic" for p in demo)
    filtered = demo_client.get("/api/v1/players?dataset=synthetic&position=CM&max_age=23").json()
    assert filtered and all(p["age"] <= 23 and p["position"] == "CM" for p in filtered)
    assert demo_client.get("/api/v1/players?dataset=invalid").status_code == 422


def test_similarity_never_mixes_synthetic_and_real_records(demo_client):
    matches = demo_client.get("/api/v1/players/synthetic-v1-001/similar").json()
    assert len(matches) == 5
    assert all(
        p["player_id"].startswith("synthetic-v1-") and p["player_id"] != "synthetic-v1-001"
        for p in matches
    )
    assert all(0 <= p["similarity_score"] <= 100 for p in matches)
    assert [p["similarity_score"] for p in matches] == sorted(
        [p["similarity_score"] for p in matches], reverse=True
    )
    assert demo_client.get("/api/v1/players/real-source-player/similar").json() == []


def test_all_generated_players_have_five_ranked_alternatives(session):
    seed_synthetic(session)
    for record in generate_players():
        results = rank_similar(session, record["id"])
        assert len(results) == 5
        assert all(result.player_id != record["id"] for result in results)


def test_demo_report_contains_metrics_and_explicit_fiction_notice(demo_client):
    response = demo_client.get("/api/v1/players/synthetic-v1-001/report.pdf")
    assert response.status_code == 200
    reader = PdfReader(BytesIO(response.content))
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert "SYNTHETIC DEMO - FICTIONAL DATA" in text
    assert "Arian Rahman" in text and "computer-generated" in text
    assert "Not recorded" not in text
