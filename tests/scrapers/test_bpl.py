"""Tests for the domestic (BPL/BFL) squad scraper (FR-1.1)."""
from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.bpl import _find_squad_table, _parse_squad_table, is_football_source

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
FIXTURE = FIXTURES / "bashundhara_kings_2025_26_squad.html"


def _load_fixture_table(path: Path = FIXTURE):
    with path.open(encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return _find_squad_table(soup)


def test_ambiguous_bpl_source_is_rejected():
    assert is_football_source("BPL") is False
    assert is_football_source("Bangladesh Premier League") is False


def test_football_qualified_source_is_accepted():
    assert is_football_source("Bashundhara Kings") is True
    assert is_football_source("Bangladesh Football League") is True


def test_cricket_source_is_rejected_even_with_bff_like_text():
    assert is_football_source("Bangladesh Cricket Board BPL") is False


def test_finds_the_squad_table_in_a_real_captured_page():
    table = _load_fixture_table()
    assert table is not None


def test_parses_bio_fields_from_real_squad_rows():
    table = _load_fixture_table()
    players = _parse_squad_table(table, "Bashundhara Kings")

    by_name = {p["name"]: p for p in players}
    assert "Anisur Rahman Zico" in by_name  # vice-captain annotation stripped
    assert by_name["Anisur Rahman Zico"]["age"] == 29
    assert by_name["Anisur Rahman Zico"]["position"] == "GK"
    assert by_name["Emmanuel Tony Agbaji"]["position"] == "RB / CB"


def test_row_with_missing_date_of_birth_is_skipped_not_fabricated():
    table = _load_fixture_table()
    players = _parse_squad_table(table, "Bashundhara Kings")
    names = {p["name"] for p in players}
    assert "Shahin Molla" not in names  # real row has no parseable DOB


def test_no_tactical_metrics_are_populated_for_domestic_players():
    table = _load_fixture_table()
    players = _parse_squad_table(table, "Bashundhara Kings")
    assert players, "fixture should yield at least one player"
    for player in players:
        assert player["league_band"].startswith("Bangladesh Football League")


def test_parses_the_aged_n_wording_variant():
    """Fortis FC's real page uses "(aged N)" instead of "(age N)" -- a live
    run against both clubs found this exact mismatch (regression test)."""
    table = _load_fixture_table(FIXTURES / "fortis_fc_2025_26_squad.html")
    players = _parse_squad_table(table, "Fortis FC")

    by_name = {p["name"]: p for p in players}
    assert by_name["Sujan Perera"]["age"] == 32
    assert by_name["Md Omer Faruk Linkcon"]["age"] == 28


def test_parses_lowercase_date_of_birth_header_casing():
    """Bangladesh Police FC's real page uses "Date of birth" (lowercase)
    where Bashundhara Kings uses "Date Of Birth" -- a live run against
    both clubs found this exact mismatch (regression test)."""
    table = _load_fixture_table(FIXTURES / "bangladesh_police_fc_2025_26_squad.html")
    assert table is not None

    players = _parse_squad_table(table, "Bangladesh Police FC")
    by_name = {p["name"]: p for p in players}
    assert by_name["Rakibul Hasan Tushar"]["age"] == 28
    assert by_name["Kiran Chemjong"]["age"] == 35
