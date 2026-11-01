"""Bangladesh national team current squad scraper (FR-1.1).

Sources the "Current squad" table on Wikipedia's "Bangladesh national
football team" article -- the only table on that page scoped to players
presently in the squad (a second table, "Recent call-ups", lists players
who are not; this module is anchored to the "Current squad" heading, not
a table index, so it never reads that second table by accident).

Only bio fields plus international caps are populated here -- no
tactical per-90 metrics exist publicly for international call-ups,
matching the same minimal-bio-only approach as `scrapers/bpl.py`.

A player already on file from a more specific source (a domestic club
roster, or FBref) keeps that source's `league_band`/`appearances`
unchanged -- this source only fills fields that are still empty, so it
never downgrades, say, Hamza Choudhury's "EFL Championship (England) --
Sheffield United" to the generic "Bangladesh National Team" band. See
`scripts/run_scrapers.py::_persist_national_team`.
"""

from __future__ import annotations

import csv
import logging
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from backend.app.config import settings
from backend.models.player import Player

logger = logging.getLogger(__name__)

SOURCE_URL = "https://en.wikipedia.org/wiki/Bangladesh_national_football_team"
LEAGUE_BAND = "Bangladesh National Team"
_SQUAD_HEADING = "current squad"
_REQUEST_TIMEOUT_SECONDS = 15

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "seed" / "national_team_players.csv"
CSV_FIELDS = ("id", "name", "age", "position", "league_band", "appearances")

_POSITION_GROUPS: dict[str, str] = {
    "gk": "Goalkeeper",
    "df": "Defender",
    "mf": "Midfielder",
    "fw": "Forward",
}


def _clean_name(name_cell: Any) -> str:
    # Footnote markers (e.g. a "TRP" superscript) aren't part of the name.
    for sup in name_cell.find_all("sup"):
        sup.decompose()
    raw = name_cell.get_text(" ", strip=True)
    # Strip trailing annotations like "(captain)".
    return re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()


def _parse_age(date_of_birth_text: str) -> int | None:
    match = re.search(r"\(aged?\s*(\d+)\)", date_of_birth_text)
    return int(match.group(1)) if match else None


def _parse_position(position_text: str) -> str | None:
    # Cells read like "1 GK", "2 DF", "3 MF", "4 FW" -- a sort key plus
    # a short code identifying the position group.
    match = re.search(r"([A-Za-z]{2})\s*$", position_text)
    return _POSITION_GROUPS.get(match.group(1).lower()) if match else None


def _parse_caps(caps_text: str) -> int | None:
    caps_text = caps_text.strip()
    return int(caps_text) if caps_text.isdigit() else None


def _find_squad_table(soup: BeautifulSoup) -> Any | None:
    heading = soup.find(
        lambda tag: tag.name in ("h2", "h3") and _SQUAD_HEADING in tag.get_text(strip=True).lower()
    )
    if heading is None:
        return None
    return heading.find_next("table")


def _parse_squad_table(table: Any) -> list[dict[str, Any]]:
    rows = table.find_all("tr")
    if not rows:
        return []

    header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
    header_lower = [h.lower() for h in header_cells]
    try:
        position_idx = header_lower.index("pos.")
        name_idx = header_lower.index("player")
        dob_idx = next(i for i, h in enumerate(header_lower) if h.startswith("date of birth"))
        caps_idx = header_lower.index("caps")
    except (ValueError, StopIteration):
        logger.warning("Unrecognized national squad table header: %s", header_cells)
        return []

    players: list[dict[str, Any]] = []
    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        if len(cells) <= max(position_idx, name_idx, dob_idx, caps_idx):
            continue  # section-divider row (blank row between position groups)

        name = _clean_name(cells[name_idx])
        position = _parse_position(cells[position_idx].get_text(" ", strip=True))
        age = _parse_age(cells[dob_idx].get_text(" ", strip=True))
        caps = _parse_caps(cells[caps_idx].get_text(" ", strip=True))

        if not name or not position or age is None:
            logger.info(
                "Skipping incomplete national squad row: name=%r position=%r age=%r",
                name,
                position,
                age,
            )
            continue

        player_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        fields: dict[str, Any] = {
            "id": player_id,
            "name": name,
            "age": age,
            "position": position,
            "league_band": LEAGUE_BAND,
        }
        if caps is not None:
            fields["appearances"] = caps
        players.append(Player(**fields).model_dump(exclude_unset=True))
    return players


def scrape_national_team_squad(url: str = SOURCE_URL) -> list[dict[str, Any]]:
    """Scrape the current Bangladesh national team squad into player profiles."""
    headers = {"User-Agent": settings.scraper_user_agent}
    try:
        response = requests.get(url, headers=headers, timeout=_REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return []

    if response.status_code != 200:
        logger.warning("Unexpected status %s for %s", response.status_code, url)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = _find_squad_table(soup)
    if table is None:
        logger.info("No '%s' table found on %s -- skipping", _SQUAD_HEADING, url)
        return []

    return _parse_squad_table(table)


def write_csv(records: list[dict[str, Any]], path: Path = CSV_PATH) -> None:
    """Write a versioned snapshot of scraped records (a point-in-time capture,
    not an ingestion source -- the live scrape above is what feeds the DB).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in CSV_FIELDS})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    squad = scrape_national_team_squad()
    write_csv(squad)
    print(f"Scraped {len(squad)} national-team players -> {CSV_PATH}")
