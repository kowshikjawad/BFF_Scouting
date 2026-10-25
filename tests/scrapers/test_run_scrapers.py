"""Tests for the scraper orchestration script (FR-1.1 failure isolation)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import scripts.run_scrapers as run_scrapers_module
from backend.models.db import Base
from backend.models.player_records import get_player
from scripts.run_scrapers import run


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        yield s


def test_one_source_failing_does_not_block_the_others(monkeypatch: pytest.MonkeyPatch, session):
    monkeypatch.setattr(
        run_scrapers_module,
        "scrape_diaspora_listings",
        lambda: [{"id": "p1", "name": "Diaspora Player", "age": 25, "position": "MF", "league_band": "X"}],
    )

    def _fail_bpl():
        raise RuntimeError("simulated scrape failure")

    monkeypatch.setattr(run_scrapers_module, "scrape_bpl_squads", _fail_bpl)
    monkeypatch.setattr(run_scrapers_module, "scrape_fbref_backfill", lambda tracked: [])

    summary = run(session=session)

    assert summary["persisted"]["diaspora"] == 1
    assert "bpl" in summary["errors"]
    assert get_player(session, "p1") is not None


def test_summary_reports_both_successes_and_failures(monkeypatch: pytest.MonkeyPatch, session):
    monkeypatch.setattr(run_scrapers_module, "scrape_diaspora_listings", list)
    monkeypatch.setattr(
        run_scrapers_module,
        "scrape_bpl_squads",
        lambda: [{"id": "p2", "name": "Domestic Player", "age": 21, "position": "DF", "league_band": "Y"}],
    )

    def _fail_fbref(tracked):
        raise RuntimeError("simulated FBref rate-limit block")

    monkeypatch.setattr(run_scrapers_module, "scrape_fbref_backfill", _fail_fbref)

    summary = run(session=session)

    assert summary["persisted"]["bpl"] == 1
    assert "fbref" in summary["errors"]
    assert get_player(session, "p2")["name"] == "Domestic Player"
