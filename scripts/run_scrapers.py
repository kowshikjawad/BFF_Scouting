"""Cron entrypoint for the weekly scraping job (NFR-fresh).

Schedule comes from `SCRAPER_CRON_SCHEDULE` in `.env` (e.g. 0 3 * * 1).
Orchestrated by the deploy environment's cron/scheduler.
"""
from __future__ import annotations


def main() -> None:
    # Stub: invokes scrapers.bpl / fbref / diaspora and persists to data/raw.
    raise NotImplementedError("Scraping orchestration lands in Sprint 1 (Data Engine).")


if __name__ == "__main__":
    main()