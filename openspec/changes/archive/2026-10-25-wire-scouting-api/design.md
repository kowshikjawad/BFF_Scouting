# Design

## Context

`backend/api/players.py` and `backend/api/similarity.py` are route shells.
`backend/api/eligibility.py` is the one already-wired route and is the
pattern to follow: a thin FastAPI handler that builds a dataclass/Pydantic
input, calls a plain-Python function, and maps the result to a response
model — no business logic in the route itself.

The persistence layer (`backend/models/player_records.py`) exposes
row-level `get_player`/`upsert_player` only; there's no existing
query/filter/list function. The ML layer (`ml/features/normalize.py`,
`ml/models/similarity.py`) operates on raw `numpy` arrays with no
awareness of player ids or persistence at all — `SimilarityEngine.query`
takes a vector and a fitted index and returns `(row_index, similarity_pct)`
pairs.

## Decisions

### 1. A new query module, not route-embedded SQL
Add `backend/models/player_records.py::list_players(session, **filters)`
rather than writing `select()` calls inline in the route. Keeps the ORM
query logic testable independently of FastAPI, matching how
`upsert_player`/`get_player` are already tested in isolation.

### 2. `diaspora_eligible` is a derived filter, not a stored boolean
There's no `diaspora_eligible` column — `ancestry_eligibility` stores the
`EligibilityStatus` string. `diaspora_eligible=true` becomes
`ancestry_eligibility == "ELIGIBLE & CLEARED"`, `false` becomes
`ancestry_eligibility != "ELIGIBLE & CLEARED"` (including `None`/unset,
since "not confirmed eligible" is the honest reading of an unset status).

### 3. `max_age` excludes players with no recorded age
An unset age cannot be known to satisfy `age <= max_age`, so a `max_age`
filter adds `PlayerORM.age.isnot(None)` to the query rather than treating
NULL as a pass. This matches the project's established "absence is not a
default" rule used throughout `player-records`.

### 4. Similarity pipeline is built per-request, not cached
Build the in-memory id→vector pool, fit `MetricNormalizer` +
`SimilarityEngine`, and query it fresh on every `/similar` call rather than
maintaining a background-refreshed index. Justification: the live dataset
is ~113 rows today (verified this session) and SQLite reads plus a 113×5
`NearestNeighbors.fit` are both sub-millisecond-to-low-millisecond — nowhere
near the NFR's 500ms budget. A cached/refreshed index is real but
premature complexity at this data scale; revisit if/when the dataset grows
by orders of magnitude.

### 5. Candidate pool = players with at least one non-null tactical metric
`MetricNormalizer`/`SimilarityEngine` need a numeric matrix with no NULLs.
A player missing some-but-not-all metrics gets 0 substituted for the
missing ones *after* normalization context is established — i.e., treat
an unrecorded metric as "average for the pool" (z-score 0) rather than 0
in raw units, so a missing metric doesn't look like a literal zero rate.
A player missing *all* five is excluded from the candidate pool entirely
(0 known metrics can't support a meaningful comparison) and, per spec, is
also rejected as a reference player.

### 6. Three response states for `/similar`, mapped to HTTP status
- Unknown player id → `404`.
- Known player, but player has zero tactical metrics OR the rest of the
  pool has zero players with any tactical metric → `200` with an empty
  list. This is a real, expected state with the live dataset today (only
  diaspora players could ever have metrics, and none currently do), not an
  error — matching the player-data-ingestion spec's framing of "absent
  tactical metrics is a valid state."
- Known player with usable data and a non-empty pool → `200` with up to
  top-K ranked results.

### 7. New `GET /api/v1/players/{id}` reuses `get_player`, adds 404 mapping
`backend/models/player_records.py::get_player` already returns `None` for
a missing id. The route maps `None` → FastAPI `404`; no new persistence
code needed beyond what `list_players` also uses for session access.

## Session lifecycle

`backend/models/db.py::session_scope()` already exists
(context-manager, commit-on-success). Routes use it as a FastAPI
dependency (`Depends`) yielding a session per request, matching the
existing commit/rollback semantics rather than inventing a second pattern.
