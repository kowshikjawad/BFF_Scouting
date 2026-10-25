"""Tests for the player-records capability (FR-1.2)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.models.db import Base
from backend.models.player_records import PlayerORM, get_player, list_players, upsert_player


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        yield s


def test_player_table_has_profile_and_metric_columns():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    columns = {c.name for c in PlayerORM.__table__.columns}
    assert {"id", "name", "age", "position", "league_band"}.issubset(columns)
    assert {
        "goals_per_90",
        "key_passes_per_90",
        "progressive_carries_per_90",
        "tackles_won_per_90",
        "aerial_duel_pct",
    }.issubset(columns)


def test_stored_player_survives_a_session_reopen(session: Session):
    upsert_player(session, "p1", name="Hamza Choudhury", age=27)
    session.commit()

    record = get_player(session, "p1")
    assert record["name"] == "Hamza Choudhury"
    assert record["age"] == 27


def test_profile_present_all_tactical_metrics_absent(session: Session):
    upsert_player(session, "p1", name="Hamza Choudhury", age=27, position="DM")
    session.commit()

    record = get_player(session, "p1")
    assert record["name"] == "Hamza Choudhury"
    for metric in (
        "goals_per_90",
        "key_passes_per_90",
        "progressive_carries_per_90",
        "tackles_won_per_90",
        "aerial_duel_pct",
    ):
        assert record[metric] is None


def test_partial_tactical_metrics_are_independent(session: Session):
    upsert_player(session, "p1", name="Hamza Choudhury", goals_per_90=0.3)
    session.commit()

    record = get_player(session, "p1")
    assert record["goals_per_90"] == 0.3
    assert record["aerial_duel_pct"] is None


def test_player_with_no_tactical_metrics_is_still_retrievable(session: Session):
    upsert_player(session, "p1", name="No Stats Yet")
    session.commit()

    record = get_player(session, "p1")
    assert record is not None
    assert record["name"] == "No Stats Yet"


def test_unknown_player_returns_none(session: Session):
    assert get_player(session, "does-not-exist") is None


def test_upsert_creates_a_new_record(session: Session):
    upsert_player(session, "p1", name="New Player", age=20)
    session.commit()

    record = get_player(session, "p1")
    assert record["name"] == "New Player"
    assert record["age"] == 20
    assert record["league_band"] is None


def test_upsert_updates_only_the_supplied_fields(session: Session):
    upsert_player(session, "p1", name="Existing", age=22, league_band="BPL/BFL")
    session.commit()

    upsert_player(session, "p1", age=23)
    session.commit()

    record = get_player(session, "p1")
    assert record["age"] == 23
    assert record["name"] == "Existing"
    assert record["league_band"] == "BPL/BFL"


def test_upsert_rejects_unknown_fields(session: Session):
    with pytest.raises(ValueError):
        upsert_player(session, "p1", not_a_real_field=True)


def _seed_search_fixture(session: Session) -> None:
    upsert_player(
        session, "young-lb", name="Young Left Back", age=19, position="LB",
        strong_foot="Left", estimated_value_eur=500_000, ancestry_eligibility="ELIGIBLE & CLEARED",
    )
    upsert_player(
        session, "old-st", name="Veteran Striker", age=32, position="ST",
        strong_foot="Right", estimated_value_eur=2_000_000, ancestry_eligibility="DOCUMENTATION REQUIRED",
    )
    upsert_player(session, "no-age", name="No Age On Record", position="CB")
    session.commit()


def test_list_players_with_no_filters_returns_everyone(session: Session):
    _seed_search_fixture(session)
    assert {p["id"] for p in list_players(session)} == {"young-lb", "old-st", "no-age"}


def test_list_players_max_age_excludes_unset_ages(session: Session):
    _seed_search_fixture(session)
    results = list_players(session, max_age=25)
    assert {p["id"] for p in results} == {"young-lb"}


def test_list_players_combined_filters_are_anded(session: Session):
    _seed_search_fixture(session)
    results = list_players(session, position="ST", strong_foot="Right")
    assert {p["id"] for p in results} == {"old-st"}

    results = list_players(session, position="ST", strong_foot="Left")
    assert results == []


def test_list_players_diaspora_eligible_filter(session: Session):
    _seed_search_fixture(session)
    eligible = list_players(session, diaspora_eligible=True)
    assert {p["id"] for p in eligible} == {"young-lb"}

    not_eligible = list_players(session, diaspora_eligible=False)
    assert {p["id"] for p in not_eligible} == {"old-st", "no-age"}
