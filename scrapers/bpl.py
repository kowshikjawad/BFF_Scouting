"""Bangladesh domestic football league squad scraper (FR-1.1).

Sources per-club, per-season Wikipedia articles (e.g. "2025-26 Bashundhara
Kings season"), verified directly during implementation to be the only
examined source with per-player bio data (name, position, date of birth);
the league-wide season article and clubs' general pages were checked and
do not carry this. See openspec/specs/player-data-ingestion/spec.md and
design.md decision #4.

"BPL" is ambiguous in Bangladesh (see the disambiguation guard below) --
every source this module touches is pinned to a specific football
competition/club, never a bare "BPL" lookup.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests
from bs4 import BeautifulSoup

from backend.app.config import settings
from backend.models.player import Player

logger = logging.getLogger(__name__)

# The 2025-26 Bangladesh Football League's 10 clubs (verified via
# Wikipedia's league season article). Not every club has a dedicated
# per-season article -- see `scrape_bpl_squads`.
SEASON = "2025–26"  # "2025–26"
LEAGUE_BAND = "Bangladesh Football League"
CLUBS: tuple[str, ...] = (
    "Abahani Limited",
    "Arambagh KS",
    "Bangladesh Police FC",
    "Bashundhara Kings",
    "Brothers Union",
    "Fakirerpool YMC",
    "Fortis FC",
    "Mohammedan SC",
    "Rahmatganj MFS",
    "PWD Sports Club",
)

_REQUEST_DELAY_SECONDS = 1.0  # polite pacing; Wikipedia has no strict limit like FBref's

# Disambiguation: "BPL" alone is the Bangladesh Premier League *cricket*
# tournament in most search results. A candidate source must explicitly
# identify as football to be used.
_CRICKET_MARKERS = ("cricket", "wicket", "odi", "t20", "bangladesh cricket board")
_FOOTBALL_MARKERS = (
    "football",
    "bangladesh football federation",
    "bff",
    *(" ".join(c.lower().split()) for c in CLUBS),
)


def is_football_source(identifier: str) -> bool:
    """True only if `identifier` explicitly identifies as football.

    A bare "BPL" reference with no qualifier returns False -- it's
    ambiguous with the Bangladesh Premier League cricket tournament.
    """
    text = identifier.lower()
    if any(marker in text for marker in _CRICKET_MARKERS):
        return False
    return any(marker in text for marker in _FOOTBALL_MARKERS)


def _wikipedia_url(club: str) -> str:
    title = f"{SEASON} {club} season".replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/{title}"


def _parse_age(date_of_birth_text: str) -> int | None:
    # Wikipedia's "Birth date and age" template renders as "(age N)" on
    # some pages and "(aged N)" on others (verified: Bashundhara Kings
    # uses "age", Fortis FC uses "aged") -- both must match.
    match = re.search(r"\(aged?\s*(\d+)\)", date_of_birth_text)
    return int(match.group(1)) if match else None


def _clean_name(raw_name: str) -> str:
    # Strip trailing annotations like "(Vice-captain)" or "(c)".
    return re.sub(r"\s*\([^)]*\)\s*$", "", raw_name).strip()


def _find_squad_table(soup: BeautifulSoup) -> Any | None:
    for table in soup.find_all("table"):
        header_cells = [c.get_text(strip=True).lower() for c in table.find_all("th")[:7]]
        if "date of birth" in header_cells or "date of birth" in " ".join(header_cells):
            return table
    return None


def _parse_squad_table(table: Any, club: str) -> list[dict[str, Any]]:
    rows = table.find_all("tr")
    if not rows:
        return []

    # Header casing varies across clubs' pages (verified: Bashundhara Kings
    # uses "Date Of Birth", Bangladesh Police FC / PWD Sports Club use
    # "Date of birth") -- compare case-insensitively.
    header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
    header_lower = [h.lower() for h in header_cells]
    try:
        name_idx = header_lower.index("player")
        position_idx = header_lower.index("position(s)")
        dob_idx = header_lower.index("date of birth")
    except ValueError:
        logger.warning("Unrecognized squad table header for %s: %s", club, header_cells)
        return []

    players: list[dict[str, Any]] = []
    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        if len(cells) <= max(name_idx, position_idx, dob_idx):
            continue  # section-divider row (e.g. "Goalkeepers"), not a player row

        name = _clean_name(cells[name_idx].get_text(" ", strip=True))
        position = cells[position_idx].get_text(" ", strip=True)
        age = _parse_age(cells[dob_idx].get_text(" ", strip=True))

        if not name or not position or age is None:
            logger.info("Skipping incomplete squad row for %s: name=%r position=%r age=%r",
                        club, name, position, age)
            continue

        player_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        fields = {
            "id": player_id,
            "name": name,
            "age": age,
            "position": position,
            "league_band": f"{LEAGUE_BAND} -- {club}",
        }
        players.append(Player(**fields).model_dump())
    return players


def scrape_bpl_squads(clubs: tuple[str, ...] = CLUBS) -> list[dict]:
    """Scrape BPL/BFL club squads into structured player profiles.

    Only bio fields are populated (name, age, position, league band) --
    no tactical per-90 metrics exist publicly for this league. A club
    with no dedicated per-season Wikipedia article (not every club has
    one) is logged and skipped, not treated as a fatal error.
    """
    headers = {"User-Agent": settings.scraper_user_agent}
    all_players: list[dict] = []

    for club in clubs:
        if not is_football_source(club):
            logger.warning("Refusing ambiguous source for club %r", club)
            continue

        url = _wikipedia_url(club)
        try:
            response = requests.get(url, headers=headers, timeout=15)
        except requests.RequestException as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
            continue
        finally:
            time.sleep(_REQUEST_DELAY_SECONDS)

        if response.status_code == 404:
            logger.info("No dedicated season article for %s (%s) -- skipping", club, url)
            continue
        if response.status_code != 200:
            logger.warning("Unexpected status %s for %s", response.status_code, url)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        table = _find_squad_table(soup)
        if table is None:
            logger.info("No squad table found on %s -- skipping", url)
            continue

        all_players.extend(_parse_squad_table(table, club))

    return all_players
