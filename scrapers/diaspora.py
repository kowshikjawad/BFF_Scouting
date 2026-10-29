"""Diaspora player roster -- maintained reference data, not a scraper.

See openspec/specs/player-data-ingestion/spec.md: there is no structured
feed for "Bangladeshi diaspora player," so this loads a hand-maintained,
version-controlled seed file (FR-1.1) instead of making any network
request.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from backend.models.player import Player

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed" / "diaspora_players.yaml"


def scrape_diaspora_listings(seed_path: Path = SEED_PATH) -> list[dict[str, Any]]:
    """Load and validate the maintained diaspora roster. No network calls.

    Each returned dict holds the validated `Player` fields plus a
    `last_verified_date` key (not part of the `Player` schema -- callers
    that persist these records should drop it before upserting).
    """
    with seed_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    records: list[dict[str, Any]] = []
    for entry in data["players"]:
        player_fields = {
            key: value for key, value in entry.items() if key not in ("notes", "last_verified_date")
        }
        validated = Player(**player_fields)
        # A roster refresh must not erase tactical metrics collected by another source.
        record = validated.model_dump(exclude_unset=True)
        record.pop("data_source", None)
        record["last_verified_date"] = entry["last_verified_date"]
        records.append(record)
    return records
