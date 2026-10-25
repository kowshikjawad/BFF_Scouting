"""Tests for the FBref opportunistic backfill (FR-1.1). No real network or
Chrome/chromedriver is used: `_fetch_fbref_metrics` is mocked throughout.
"""
from __future__ import annotations

import pytest

import scrapers.fbref as fbref_module
from scrapers.fbref import resolve_fbref_competition, scrape_fbref_backfill


def test_tracked_player_outside_coverage_triggers_no_fetch(monkeypatch: pytest.MonkeyPatch):
    def _fail_if_called(*args, **kwargs):
        raise AssertionError("must not fetch for a player outside FBref's coverage")

    monkeypatch.setattr(fbref_module, "_fetch_fbref_metrics", _fail_if_called)

    tracked = [
        {"id": "hamza-choudhury", "name": "Hamza Choudhury", "league_band": "EFL Championship (England) -- Sheffield United"},
        {"id": "anisur-rahman-zico", "name": "Anisur Rahman Zico", "league_band": "Bangladesh Football League -- Bashundhara Kings"},
    ]
    results = scrape_fbref_backfill(tracked)

    assert results == []


def test_tracked_player_inside_coverage_is_fetched_and_mapped(monkeypatch: pytest.MonkeyPatch):
    def _fake_fetch(competition: str, season: str, player_name: str):
        assert competition == "ENG-Premier League"
        assert player_name == "Some Player"
        return {"goals_per_90": 0.42, "aerial_duel_pct": 55.0}

    monkeypatch.setattr(fbref_module, "_fetch_fbref_metrics", _fake_fetch)

    tracked = [{"id": "p1", "name": "Some Player", "league_band": "English Premier League"}]
    results = scrape_fbref_backfill(tracked)

    assert results == [{"id": "p1", "goals_per_90": 0.42, "aerial_duel_pct": 55.0}]


def test_a_failed_fetch_is_logged_and_skipped_not_raised(monkeypatch: pytest.MonkeyPatch):
    def _raise(*args, **kwargs):
        raise RuntimeError("simulated FBref rate-limit block")

    monkeypatch.setattr(fbref_module, "_fetch_fbref_metrics", _raise)

    tracked = [{"id": "p1", "name": "Some Player", "league_band": "English Premier League"}]
    results = scrape_fbref_backfill(tracked)  # must not raise

    assert results == []


@pytest.mark.parametrize(
    "league_band,expected",
    [
        ("English Premier League", "ENG-Premier League"),
        ("La Liga", "ESP-La Liga"),
        ("Ligue 1", "FRA-Ligue 1"),
        ("Bundesliga", "GER-Bundesliga"),
        ("2. Bundesliga", None),
        ("Serie A", "ITA-Serie A"),
        ("EFL Championship (England)", None),
        ("Bangladesh Football League", None),
        ("USL League One (USA)", None),
        ("Bhutan Premier League", None),
    ],
)
def test_competition_resolution_matches_only_fbrefs_covered_list(league_band, expected):
    assert resolve_fbref_competition(league_band) == expected
