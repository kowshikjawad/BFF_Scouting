"""Load the maintained roster offline without replacing existing recorded facts."""

from backend.models.db import init_db, session_scope
from backend.models.player_records import VALID_PLAYER_FIELDS, upsert_player
from scrapers.diaspora import scrape_diaspora_listings
from scripts.seed_synthetic import seed_synthetic


def main():
    init_db()
    records = scrape_diaspora_listings()
    with session_scope() as session:
        for record in records:
            upsert_player(
                session,
                record["id"],
                **{key: value for key, value in record.items() if key in VALID_PLAYER_FIELDS},
            )
        demo_count = seed_synthetic(session)
    print(f"Loaded {len(records)} maintained player profiles. Existing tactical data preserved.")
    print(f"Loaded {demo_count} fictional demo profiles in the synthetic dataset.")


if __name__ == "__main__":
    main()
