"""Cron entrypoint for the weekly scraping job (NFR-fresh).

Schedule comes from `SCRAPER_CRON_SCHEDULE` in `.env` (e.g. 0 3 * * 1).
Orchestrated by the deploy environment's cron/scheduler.

Runs the diaspora, domestic (BPL/BFL), national-team, and FBref sources
with per-source failure isolation (player-data-ingestion spec: "one
source fails, others still persist") -- each source's successful results
are persisted immediately, and failures from any source are collected
and reported together rather than aborting the whole run.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from sqlalchemy.orm import Session

from backend.models.db import SessionLocal, init_db
from backend.models.player_records import VALID_PLAYER_FIELDS, get_player, upsert_player
from scrapers.bpl import scrape_bpl_squads
from scrapers.diaspora import scrape_diaspora_listings
from scrapers.fbref import scrape_fbref_backfill
from scrapers.national_team import scrape_national_team_squad

logger = logging.getLogger(__name__)


def _persist(session: Session, records: list[dict[str, Any]]) -> int:
    """Upsert each record, dropping any key that isn't a real player field."""
    count = 0
    for record in records:
        fields = {k: v for k, v in record.items() if k != "id" and k in VALID_PLAYER_FIELDS}
        upsert_player(session, record["id"], **fields)
        count += 1
    session.commit()
    return count


def _persist_national_team(session: Session, records: list[dict[str, Any]]) -> int:
    """Upsert national-team records, but only into fields still empty.

    This source is the least specific of the three (it only ever says
    "Bangladesh National Team", never a club or foreign league) -- for a
    player already on file from the domestic or diaspora source, their
    existing `league_band`/`appearances` must win, not be overwritten by
    this one. A record this source has never seen before is still
    created in full.
    """
    count = 0
    for record in records:
        existing = get_player(session, record["id"])
        fields = {k: v for k, v in record.items() if k != "id" and k in VALID_PLAYER_FIELDS}
        if existing is not None:
            fields = {k: v for k, v in fields.items() if existing.get(k) is None}
        upsert_player(session, record["id"], **fields)
        count += 1
    session.commit()
    return count


def run(session: Session | None = None) -> dict[str, Any]:
    """Run all three ingestion sources. Never raises for a single source's
    failure -- every source is attempted, and the summary reports both
    what was persisted and what failed.
    """
    init_db()
    own_session = session is None
    session = session or SessionLocal()

    persisted: dict[str, int] = {}
    errors: dict[str, str] = {}

    diaspora_records: list[dict[str, Any]] = []
    try:
        diaspora_records = scrape_diaspora_listings()
        persisted["diaspora"] = _persist(session, diaspora_records)
    except Exception as exc:
        session.rollback()
        logger.exception("diaspora source failed")
        errors["diaspora"] = str(exc)

    try:
        bpl_records = scrape_bpl_squads()
        persisted["bpl"] = _persist(session, bpl_records)
    except Exception as exc:
        session.rollback()
        logger.exception("bpl source failed")
        errors["bpl"] = str(exc)

    try:
        national_team_records = scrape_national_team_squad()
        persisted["national_team"] = _persist_national_team(session, national_team_records)
    except Exception as exc:
        session.rollback()
        logger.exception("national_team source failed")
        errors["national_team"] = str(exc)

    try:
        # FBref coverage only ever matches a tracked player's league_band
        # against its 9-competition list (see scrapers/fbref.py) -- today
        # that's effectively only the diaspora roster, since the domestic
        # scraper's league_band is never an FBref-covered competition.
        fbref_updates = scrape_fbref_backfill(diaspora_records)
        persisted["fbref"] = _persist(session, fbref_updates)
    except Exception as exc:
        session.rollback()
        logger.exception("fbref source failed")
        errors["fbref"] = str(exc)

    if own_session:
        session.close()

    return {"persisted": persisted, "errors": errors}


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    summary = run()
    logger.info("Scraper run summary: %s", summary)
    if summary["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
