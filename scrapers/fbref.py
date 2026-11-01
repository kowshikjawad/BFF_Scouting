"""FBref opportunistic tactical-metric backfill (FR-1.1, FR-3.1 source).

`soccerdata.FBref` only covers 9 competitions (verified directly against
the installed package: the "Big 5" European leagues plus four major
international tournaments) and requires a real Chrome/chromedriver
install to reach FBref at all, which sits behind bot-detection. This
module only ever attempts a fetch for a tracked player whose current
competition resolves to one of those 9 -- for every other player (which,
as of this implementation, is all of them: see
data/seed/diaspora_players.yaml and scrapers/bpl.py) it is a deliberate,
documented no-op. See openspec/specs/player-data-ingestion/spec.md and
design.md decisions #3-#4.
"""

from __future__ import annotations

import logging
from typing import Any

from ml.features.normalize import REFERENCE_METRICS, TACTICAL_METRICS
from scrapers._rate_limiter import SlidingWindowRateLimiter

logger = logging.getLogger(__name__)

# soccerdata.FBref's hard-coded competition list (verified via
# soccerdata.FBref.available_leagues() in this project's venv).
FBREF_RATE_LIMIT_CALLS_PER_MINUTE = 10

_COMPETITION_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("english premier league", "ENG-Premier League"),
    ("premier league (england)", "ENG-Premier League"),
    ("la liga", "ESP-La Liga"),
    ("ligue 1", "FRA-Ligue 1"),
    ("serie a", "ITA-Serie A"),  # must not match "Serie A" as a substring of "Serie A2" etc.
)
# Deliberately excludes anything resembling "Bundesliga" alone, since
# both "Bundesliga" and "2. Bundesliga" contain that substring and only
# the top flight is covered -- handled explicitly below instead of via
# keyword matching to avoid a false positive on the second division.


def resolve_fbref_competition(league_band: str) -> str | None:
    """Map a free-text league/competition string to a soccerdata.FBref key.

    Returns None when the competition isn't one of FBref's 9 supported
    keys (the overwhelmingly common case for this project's actual
    tracked players).
    """
    text = league_band.lower()

    if "bundesliga" in text:
        return "GER-Bundesliga" if "2." not in text and "ii" not in text else None
    if "world cup" in text and "women" in text:
        return "INT-Women's World Cup"
    if "world cup" in text:
        return "INT-World Cup"
    if "european championship" in text or "euro " in text:
        return "INT-European Championship"

    for keyword, competition in _COMPETITION_KEYWORDS:
        if keyword in text:
            return competition
    return None


def _fetch_fbref_metrics(competition: str, season: str, player_name: str) -> dict[str, float]:
    """Fetch and map a single player's per-90 metrics from FBref.

    Isolated as its own function so tests can mock it without touching
    the real `soccerdata`/Chrome dependency chain.
    """
    import soccerdata as sd  # imported lazily: not installed-equivalent to usable without Chrome

    fbref = sd.FBref(leagues=competition, seasons=season)

    standard = fbref.read_player_season_stats(stat_type="standard")
    shooting = fbref.read_player_season_stats(stat_type="shooting")
    passing = fbref.read_player_season_stats(stat_type="passing")
    possession = fbref.read_player_season_stats(stat_type="possession")
    defense = fbref.read_player_season_stats(stat_type="defense")
    misc = fbref.read_player_season_stats(stat_type="misc")

    def _row(df: Any) -> Any | None:
        matches = df[df.index.get_level_values("player") == player_name]
        return matches.iloc[0] if len(matches) else None

    metrics: dict[str, float] = {}
    if (row := _row(standard)) is not None:
        if ("Per 90 Minutes", "Gls") in row.index:
            metrics["goals_per_90"] = float(row[("Per 90 Minutes", "Gls")])
        if ("Per 90 Minutes", "Ast") in row.index:
            metrics["assists_per_90"] = float(row[("Per 90 Minutes", "Ast")])
        if ("Per 90 Minutes", "Sh") in row.index:
            metrics["shots_per_90"] = float(row[("Per 90 Minutes", "Sh")])
        if ("Playing Time", "Min") in row.index:
            metrics["minutes_played"] = float(row[("Playing Time", "Min")])
        if ("Playing Time", "MP") in row.index:
            metrics["appearances"] = float(row[("Playing Time", "MP")])
    if (row := _row(shooting)) is not None and ("Standard", "SoT%") in row.index:
        metrics["shot_accuracy_pct"] = float(row[("Standard", "SoT%")])
    if (row := _row(passing)) is not None:
        if ("Per 90 Minutes", "KP") in row.index:
            metrics["key_passes_per_90"] = float(row[("Per 90 Minutes", "KP")])
        if ("Total", "Cmp%") in row.index:
            metrics["pass_completion_pct"] = float(row[("Total", "Cmp%")])
    if (row := _row(possession)) is not None:
        if ("Per 90 Minutes", "PrgC") in row.index:
            metrics["progressive_carries_per_90"] = float(row[("Per 90 Minutes", "PrgC")])
        if ("Take-Ons", "Succ") in row.index:
            metrics["dribbles_per_90"] = float(row[("Take-Ons", "Succ")])
    if (row := _row(defense)) is not None:
        if ("Per 90 Minutes", "TklW") in row.index:
            metrics["tackles_won_per_90"] = float(row[("Per 90 Minutes", "TklW")])
        if ("Per 90 Minutes", "Int") in row.index:
            metrics["interceptions_per_90"] = float(row[("Per 90 Minutes", "Int")])
        if ("Per 90 Minutes", "Clr") in row.index:
            metrics["clearances_per_90"] = float(row[("Per 90 Minutes", "Clr")])
    if (row := _row(misc)) is not None and "Aerial Duels Won%" in row.index:
        metrics["aerial_duel_pct"] = float(row["Aerial Duels Won%"])

    return metrics


def scrape_fbref_backfill(
    tracked_players: list[dict[str, Any]], season: str = "2025-2026"
) -> list[dict[str, Any]]:
    """Opportunistically backfill tactical metrics for covered players.

    `tracked_players` is a list of dicts with at least `id` and
    `league_band`. Returns a list of `{"id": ..., **metrics}` dicts --
    only for players whose competition is covered and for whom at least
    one metric was found. A player outside FBref's coverage triggers no
    fetch attempt at all.
    """
    limiter = SlidingWindowRateLimiter(
        max_calls=FBREF_RATE_LIMIT_CALLS_PER_MINUTE, window_seconds=60.0
    )
    results: list[dict[str, Any]] = []

    for player in tracked_players:
        competition = resolve_fbref_competition(player.get("league_band", ""))
        if competition is None:
            continue  # not covered -- no fetch attempted, per spec

        limiter.acquire()
        try:
            metrics = _fetch_fbref_metrics(competition, season, player["name"])
        except Exception as exc:  # noqa: BLE001 - surfaced, not evaded
            logger.warning(
                "FBref fetch failed for %s (%s): %s -- stopping this run, not retrying",
                player.get("name"),
                competition,
                exc,
            )
            continue

        if metrics:
            results.append({"id": player["id"], **metrics})

    return results


assert set(TACTICAL_METRICS) == {
    "goals_per_90",
    "assists_per_90",
    "key_passes_per_90",
    "progressive_carries_per_90",
    "dribbles_per_90",
    "tackles_won_per_90",
    "interceptions_per_90",
    "aerial_duel_pct",
}
assert set(REFERENCE_METRICS) == {
    "shots_per_90",
    "shot_accuracy_pct",
    "pass_completion_pct",
    "clearances_per_90",
    "minutes_played",
    "appearances",
}
