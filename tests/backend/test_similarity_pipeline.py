"""Tests for the tactical similarity pipeline (FR-3.1/3.2/3.3)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.models.db import Base
from backend.models.player_records import upsert_player
from backend.similarity.pipeline import PlayerNotFoundError, rank_similar


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        yield s


def test_unknown_reference_player_raises(session: Session):
    with pytest.raises(PlayerNotFoundError):
        rank_similar(session, "does-not-exist")


def test_reference_player_with_no_metrics_returns_empty(session: Session):
    upsert_player(session, "p1", name="No Stats", position="CB")
    upsert_player(session, "p2", name="Has Stats", goals_per_90=0.4)
    session.commit()

    assert rank_similar(session, "p1") == []


def test_no_other_player_has_metrics_returns_empty(session: Session):
    upsert_player(session, "p1", name="Only One With Stats", goals_per_90=0.4)
    upsert_player(session, "p2", name="No Stats", position="CB")
    session.commit()

    assert rank_similar(session, "p1") == []


def test_ranks_similar_players_and_excludes_self(session: Session):
    # p1 and p2 are near-identical attacking profiles; p3 is a very
    # different defensive profile -- p1's nearest match should be p2.
    upsert_player(
        session, "p1", name="Striker A", goals_per_90=0.6, key_passes_per_90=1.0,
        progressive_carries_per_90=2.0, tackles_won_per_90=0.2, aerial_duel_pct=40.0,
    )
    upsert_player(
        session, "p2", name="Striker B", goals_per_90=0.58, key_passes_per_90=1.1,
        progressive_carries_per_90=2.1, tackles_won_per_90=0.25, aerial_duel_pct=42.0,
    )
    upsert_player(
        session, "p3", name="Destroyer", goals_per_90=0.0, key_passes_per_90=0.1,
        progressive_carries_per_90=0.3, tackles_won_per_90=3.5, aerial_duel_pct=70.0,
    )
    session.commit()

    results = rank_similar(session, "p1", top_k=5)
    assert [r.player_id for r in results] != ["p1"]  # never includes self
    assert "p1" not in {r.player_id for r in results}
    assert results[0].player_id == "p2"
    assert len(results) == 2  # only 2 other candidates exist


def test_fewer_candidates_than_requested_top_k(session: Session):
    upsert_player(session, "p1", name="A", goals_per_90=0.5)
    upsert_player(session, "p2", name="B", goals_per_90=0.4)
    session.commit()

    results = rank_similar(session, "p1", top_k=5)
    assert len(results) == 1
    assert results[0].player_id == "p2"


def test_partial_metrics_do_not_crash_the_pipeline(session: Session):
    upsert_player(session, "p1", name="Partial A", goals_per_90=0.5)
    upsert_player(session, "p2", name="Partial B", aerial_duel_pct=55.0)
    session.commit()

    results = rank_similar(session, "p1", top_k=5)
    assert len(results) == 1
    assert results[0].player_id == "p2"
