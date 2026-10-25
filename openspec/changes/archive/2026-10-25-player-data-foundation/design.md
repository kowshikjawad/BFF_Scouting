# Design

## Context

No persistence exists today (`sqlalchemy` is declared but unused;
`data/processed/` and `data/raw/` are empty), and all three scrapers plus
`scripts/run_scrapers.py` are `NotImplementedError` stubs. `backend/models/player.py`
already defines the `Player` Pydantic schema (FR-1.2's 8 fields) and
`ml/features/normalize.py` already names the five `TACTICAL_METRICS` keys
this design must store. See `proposal.md` - Why for the sourcing research
(BPL/cricket naming collision, FBref's 9-competition ceiling, the
bot-detection-evasion dependency chain, and the lack of any diaspora feed)
that shapes the decisions below.

## Goals / Non-Goals

**Goals:**
- Give every later sprint (search, similarity, eligibility lookups,
  frontend) one real, queryable data store to build against.
- Make each of the three ingestion sources honestly scoped to what it can
  actually provide, rather than silently degrading or inventing data.
- Make the FBref integration's real operational constraints (rate limit,
  browser dependency, coverage ceiling) explicit in the implementation, not
  just in prose.

**Non-Goals:**
- No schema migration framework (Alembic etc.) — the schema is greenfield;
  add migrations when the first breaking schema change is actually needed.
- No historical/versioned stats (e.g. tracking a metric's value over time)
  — a player record holds current values only.
- No automated refresh of the diaspora seed file — it is hand-maintained;
  staleness is managed by the `last_verified_date` field and human review,
  not automation.
- No attempt to make FBref access more reliable against IP blocking (no
  proxy rotation, no retry-with-backoff loops that effectively act as
  evasion) — proposal.md already scopes this as an accepted risk, not a
  problem this change solves.
- No image/photo handling, no advanced metrics beyond the five already
  named in `ml/features/normalize.py`.

## Decisions

### 1. Single `players` table, not separate profile/metrics tables
Profile fields and the five tactical metrics live as columns on one
SQLAlchemy model (`PlayerORM`), with every metric column nullable.
**Why**: the spec requires that metrics be independently present/absent
per player but doesn't require historical tracking or a different
lifecycle from the profile — a 1:1 split table would only add a join for
every read with no present benefit. **Alternative considered**: a separate
`PlayerMetrics` table with a foreign key to `players`. Rejected for now;
revisit if/when metric history or multi-season tracking is actually
needed (that would be a real reason to split).

### 2. Upsert takes an explicit field dict, not a full `Player` object
The upsert operation's signature is `upsert_player(session, player_id: str,
**fields)` (or an equivalent dict parameter) — callers pass only the keys
they actually have data for. **Why**: `Player`'s Pydantic fields default to
`None`, so a full-object upsert couldn't distinguish "this scraper has no
opinion on `height_cm`" from "this scraper confirms `height_cm` is
unknown" — exactly the ambiguity the `player-records` spec's "upsert
updates only the supplied fields" requirement exists to avoid. A dict (or
`**kwargs`) with only the present keys makes that distinction explicit at
the call site. **Alternative considered**: a sentinel value (e.g.
`UNSET`) on `Player` fields instead. Rejected as a heavier change to an
existing, already-used Pydantic model for no benefit over a plain dict at
the one call site (the upsert function) that needs the distinction.

### 3. FBref rate limiting is an application-level pacing wrapper, approximate by necessity
A small limiter tracks the timestamps of the last 10 `soccerdata` calls in
a sliding 60-second window and sleeps before issuing another when at
capacity. **Why**: `soccerdata.FBref`'s high-level methods (e.g.
`read_player_season_stats`) may themselves issue more than one HTTP
request per call (e.g. to resolve a season's squad list, then each team's
page) — this design does not have visibility into that internal request
count, so pacing *calls* to at most 10/minute is a deliberately
conservative approximation of staying under FBref's documented 10
requests/minute limit, not a guarantee. **Alternative considered**:
patching/monkeypatching `soccerdata`'s internal HTTP layer to count real
requests. Rejected as fragile (coupling to the library's internals) for a
limit whose exact enforcement window FBref doesn't publish precisely
either — the conservative call-level pacing is the honest, maintainable
choice.

### 4. BPL/BFL scraper sources per-club, per-season Wikipedia articles, not the league-wide season page
Verified directly (not assumed) during implementation: the **league-wide**
season article ("2025–26 Bangladesh Football League") has no per-player
bio data at all — only clubs/standings/fixtures tables, a captains table,
and name-only tables for foreign and dual-citizenship players. The general,
evergreen club page (e.g. "Bashundhara Kings") has a "Current squad" table
with shirt number/position/nationality/name but **no date of birth**. The
actual source with usable bio data is each club's **per-season** article
(e.g. "2025–26 Bashundhara Kings season"), whose squad table has columns
No. / Nat. / Player / Position(s) / Date of Birth / Year Signed / Previous
club — this is the real scraping target, one page per club, not one page
for the whole league. **Also verified**: not every club has one of these
season-specific articles (e.g. "2025–26 Abahani Limited season" 404s) —
of the 10 clubs in the 2025–26 season (Abahani Limited, Arambagh KS,
Bangladesh Police FC, Bashundhara Kings, Brothers Union, Fakirerpool YMC,
Fortis FC, Mohammedan SC, Rahmatganj MFS, PWD Sports Club), only some will
resolve. The scraper treats a missing club season-page the same way
tasks.md's "defensive per-row parsing" already treats a malformed row:
log and skip that club for this run rather than aborting the whole scrape
or fabricating data for it — consistent with the `player-data-ingestion`
spec's "profile fields populated to the extent the source provides them"
wording, which already anticipates partial per-player/per-club coverage.
**Why Wikipedia at all**: FBref doesn't cover this league (proposal.md
#2); no structured official feed was found during research. Every
candidate page is still checked against the football-vs-cricket
disambiguation rule before use — concretely, a source must name or list
football clubs (e.g. Bashundhara Kings) rather than a bare "BPL"
reference. **Alternative considered**: BFF's official website. Not ruled
out for the future, but its structure/reliability wasn't verified during
this research; a reasonable follow-up if Wikipedia's per-club coverage
proves too sparse in practice.

### 5. Diaspora roster is a version-controlled YAML seed file, not scraped
`data/seed/diaspora_players.yaml` (new path), loaded by `scrapers/diaspora.py`
with no network calls. **Why YAML over JSON**: this file is hand-maintained
and needs inline provenance notes (e.g. "club unconfirmed as of research
date — see Wikipedia note") that JSON can't carry as comments. **Why
checked into git** (unlike `data/raw/`/`data/processed/`, which stay
gitignored scrape output per the existing `.gitignore`): this is authored
source material, not a reproducible scrape artifact — losing it would mean
re-researching real-world facts, not re-running a scraper. Each entry
carries a `last_verified_date` field per the spec requirement, given how
fast these situations change (Cuba Mitchell's club affiliation changed
three times within about eight months during this project's own research
window).

### 6. Orchestration isolates failures with per-source try/except and an aggregate report
`scripts/run_scrapers.py` runs the three sources in sequence, each wrapped
in its own exception handler; successes persist immediately via the
upsert operation (decision #2) rather than being batched and held pending
all three sources succeeding. **Why**: the spec's "one source fails,
others still persist" scenario requires this directly, and immediate
per-source persistence (rather than an all-or-nothing transaction across
all three sources) means a late-running FBref rate-limit failure can't
retroactively discard the domestic and diaspora results that already
succeeded.

## Risks / Trade-offs

- **[Risk]** FBref may be unreachable in production (cloud datacenter IP
  blocking) regardless of correct rate-limiting, as already flagged in
  proposal.md → **Mitigation**: the upsert design (decision #2) means a
  failed FBref run simply leaves tactical metrics absent rather than
  corrupting or nulling out previously-fetched data; this is the
  `player-records` spec's "absent is valid" requirement doing double duty
  as a resilience property.
- **[Risk]** Wikipedia's table structure for the Bangladesh football league
  season pages could change or be inconsistent across seasons →
  **Mitigation**: defensive per-row parsing that logs and skips a
  malformed row rather than aborting the whole scrape; implementation
  tasks include a fixture-based test against a captured page snapshot so a
  future real-world drift is caught by a failing test, not a silent gap.
- **[Risk]** The FBref rate limiter paces library *calls*, not actual HTTP
  requests (decision #3) — under heavy use this could still exceed FBref's
  real limit if a single call fans out into many requests →
  **Mitigation**: documented explicitly as a conservative approximation,
  not a guarantee; a tighter effective limit (e.g. pacing at 5 calls/minute
  instead of 10) is a one-line implementation-time adjustment if this
  proves too permissive in practice.
- **[Risk]** `Chrome`/`chromedriver` isn't currently in the `Dockerfile` or
  documented as a local prerequisite → **Mitigation**: tracked explicitly
  as an implementation task in tasks.md; the FBref scraper's tests can
  skip gracefully (not fail) when no Chrome binary is present, so CI/dev
  environments without it aren't blocked on unrelated work.
