"""Tests for the Bangladesh national team squad scraper (FR-1.1)."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.national_team import LEAGUE_BAND, _find_squad_table, _parse_squad_table

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
FIXTURE = FIXTURES / "bangladesh_national_team_squad.html"


def _load_fixture_table(path: Path = FIXTURE):
    with path.open(encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup, _find_squad_table(soup)


def test_finds_the_current_squad_table_not_the_call_ups_table():
    _soup, table = _load_fixture_table()
    assert table is not None
    # "Recent call-ups" is a real second table on this page with the same
    # columns -- the fixture includes it to prove it's never picked.
    players = _parse_squad_table(table)
    names = {p["name"] for p in players}
    assert "Jamal Bhuyan" in names  # current squad member
    assert "Anisur Rahman Zico" not in names  # only appears in call-ups


def test_captain_annotation_is_stripped_from_name():
    _, table = _load_fixture_table()
    players = _parse_squad_table(table)
    by_name = {p["name"]: p for p in players}
    assert "Jamal Bhuyan" in by_name
    assert "Jamal Bhuyan ( captain )" not in by_name


def test_footnote_superscript_is_stripped_from_name():
    """Two real squad rows carry a "TRP" footnote marker as a <sup>
    glued onto the name -- it must not leak into the stored name."""
    _, table = _load_fixture_table()
    players = _parse_squad_table(table)
    names = {p["name"] for p in players}
    assert "Abdullah Omar Sajib" in names
    assert not any("TRP" in name for name in names)


def test_position_group_codes_map_to_full_names():
    _, table = _load_fixture_table()
    players = _parse_squad_table(table)
    by_name = {p["name"]: p for p in players}
    assert by_name["Mitul Marma"]["position"] == "Goalkeeper"
    assert by_name["Tariq Kazi"]["position"] == "Defender"
    assert by_name["Jamal Bhuyan"]["position"] == "Midfielder"
    assert by_name["Rakib Hossain"]["position"] == "Forward"


def test_caps_are_captured_as_appearances():
    _, table = _load_fixture_table()
    players = _parse_squad_table(table)
    by_name = {p["name"]: p for p in players}
    assert by_name["Jamal Bhuyan"]["appearances"] == 96


def test_no_tactical_metrics_are_populated():
    _, table = _load_fixture_table()
    players = _parse_squad_table(table)
    assert players, "fixture should yield at least one player"
    for player in players:
        assert player["league_band"] == LEAGUE_BAND
        assert "goals_per_90" not in player
