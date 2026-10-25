# Proposal

## Why

Nothing downstream of data ingestion currently works: `scrapers/bpl.py`,
`scrapers/fbref.py`, `scrapers/diaspora.py`, and `scripts/run_scrapers.py`
all `raise NotImplementedError`, and there is no database wiring at all —
`sqlalchemy` is a declared dependency and `DATABASE_URL` is already
configured in `backend/app/config.py`, but nothing ever opens a session or
defines a table. `data/processed/` and `data/raw/` are empty. This blocks
every later sprint: the Sprint 3 search/similarity endpoints have nothing
to query, and the Sprint 4 dashboard has nothing to display.

Building this now, with real sourcing research behind it rather than
building against the PRD's assumptions at face value, surfaces three
corrections the PRD's tech-stack section doesn't account for:

1. **"BPL" is ambiguous.** The Bangladesh Premier League that dominates
   search results is a cricket tournament (12th season ran 2025-26, won by
   Rajshahi Warriors). Bangladesh's top football division — Bashundhara
   Kings' league, 10 clubs, 5 straight Bashundhara titles through 2024 —
   has been called "Bangladesh Premier League (football)" historically and
   "Bangladesh Football League" as of 2025-26 on Wikipedia. A scraper doing
   naive "BPL" lookups will silently pull cricket data.
2. **`soccerdata.FBref` cannot reach the leagues this project actually
   needs.** Verified directly in this project's venv: `soccerdata.FBref`
   accepts exactly 9 competition keys (the "Big 5" European top leagues
   plus four major international tournaments) and raises `ValueError` for
   anything else, including `ENG-Championship`. None of the known diaspora
   players (see #3) currently play in a covered competition, and Bangladesh's
   domestic league was never going to be covered either. This is a hard
   ceiling on what this data source can return for this project's actual
   population, not a soft limitation to work around.
3. **Reaching FBref at all requires browser-based bot-detection evasion.**
   Verified directly: instantiating `soccerdata.FBref` attempts to launch
   `undetected-chromedriver` via SeleniumBase, because FBref returns HTTP
   403 to plain requests (confirmed independently — direct fetches to
   fbref.com and sports-reference.com both 403'd, even for `robots.txt`).
   This was raised explicitly to the user, who chose (informed, this
   session) to keep `soccerdata` as-is rather than drop FBref or look for
   an alternative source. That decision carries three accepted
   consequences this proposal must make explicit rather than hide: Chrome/
   chromedriver must exist in the runtime environment; FBref enforces a
   documented 10-requests/minute limit with a resulting multi-hour IP block
   on violation; and cloud-hosted deployments (the PRD's own NFR specifies
   AWS/GCP/Render) commonly have their datacenter IP ranges blocked by
   sites like this regardless of request-rate compliance, so FBref data
   availability in production is a real, unresolved risk.
4. **There is no scrapeable source for "Bangladeshi diaspora player."**
   This is a curated-knowledge problem, not a data-feed problem. The
   players who matter here (Hamza Choudhury, Tariq Kazi, Jamal Bhuyan,
   Fahamedul Islam, Cuba Mitchell, Shamit Shome) were found through
   football journalism, not a structured feed, and their situations change
   fast — Cuba Mitchell's club affiliation alone changed three times within
   about eight months. Treating this as a "scraper" misdescribes the
   actual engineering problem, which is a maintained reference dataset.

## What Changes

- Add a SQLAlchemy persistence layer bound to the already-configured
  `DATABASE_URL`, with a table mirroring `Player` (FR-1.2) plus nullable
  columns for the five tactical per-90 metrics `ml/features/normalize.py`
  already expects, and an upsert operation scrapers call into.
- Implement `scrapers/bpl.py` as a real scraper over Wikipedia's Bangladesh
  football league season pages: bio/squad fields only (name, age, position,
  height, strong foot, club). No per-90 stats — none exist publicly for
  this league, and the field stays null rather than estimated.
- Implement `scrapers/fbref.py` as a real, narrowly-scoped `soccerdata`
  integration limited to its 9 supported competitions, rate-limited to
  FBref's documented 10 requests/minute, used opportunistically to backfill
  per-90 stats for any tracked player who happens to appear in a covered
  competition. On the known roster today, that's expected to match zero
  players — this ships as correct, tested infrastructure, not a populated
  feature.
- Replace `scrapers/diaspora.py`'s stub with a loader over a new maintained
  seed file (not a scraper) covering the 6 known real diaspora players,
  each with a last-verified-date field.
- Wire `scripts/run_scrapers.py` to run all three and persist through the
  new persistence layer, with per-scraper failure isolation so one
  scraper's failure (e.g. FBref hitting its rate limit) doesn't block the
  other two from persisting.
- **BREAKING**: none — all three scraper modules and the orchestration
  script currently raise `NotImplementedError` unconditionally, so there is
  no existing behavior to break.

## Capabilities

### New Capabilities
- `player-records`: durable storage for player profiles (FR-1.2's 8
  attributes) and their tactical per-90 metrics, including the standing
  rule that a metric being absent is a valid, expected state rather than
  missing data to flag.
- `player-data-ingestion`: the three data-acquisition paths (domestic
  league scraping, opportunistic FBref backfill for covered competitions,
  and the maintained diaspora reference set) and their orchestration into
  persistence, including the Bangladesh-football-vs-cricket disambiguation
  rule and FBref's rate-limit/scope constraints.

### Modified Capabilities
(none)

## Impact

- `backend/models/` — new persistence module (e.g. `db.py` for
  engine/session, `player_orm.py` or similar for the table).
- `scrapers/bpl.py`, `scrapers/fbref.py`, `scrapers/diaspora.py`,
  `scripts/run_scrapers.py` — stubs replaced with real implementations.
- New seed data file under `data/` (exact path decided in design.md) for
  the diaspora roster — this is checked into git (unlike `data/raw/` and
  `data/processed/`, which stay gitignored scrape output), since it's
  hand-maintained source material, not a scrape artifact.
- `Dockerfile` — needs a Chrome/chromedriver install step added for the
  FBref scraper to function in a container; tracked as an implementation
  task, not done in this proposal.
- `requirements.txt` — `soccerdata`'s SeleniumBase/chromedriver dependency
  chain should be pinned once implemented and verified.
- No API or frontend changes — `backend/api/players.py` and
  `backend/api/similarity.py` remain stubs; wiring them to query this new
  persistence layer is Sprint 3 follow-on work, out of scope here.
