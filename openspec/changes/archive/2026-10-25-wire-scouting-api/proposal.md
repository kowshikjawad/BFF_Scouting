# Proposal

## Why

`backend/api/players.py` and `backend/api/similarity.py` are route shells
that `raise NotImplementedError` — verified live via `TestClient` this
session: `GET /api/v1/players` and `GET /api/v1/players/{id}/similar` both
500. Meanwhile the pieces they need already exist and work: a populated
persistence layer (`backend/models/player_records.py`, 113 real players
scraped and stored this session) and a tested ML similarity engine
(`ml/features/normalize.py`, `ml/models/similarity.py`). Nothing connects
them to HTTP. This is PRD Sprint 2's remaining ML-wiring work plus all of
Sprint 3 (FR-3.2, FR-3.3, FR-4.2), and it directly blocks any frontend
(planned next) from doing anything beyond the health check and the
eligibility endpoint, which are the only two routes that currently work.

## What Changes

- `GET /api/v1/players` (FR-4.2): query `PlayerORM` with the specified
  filter vocabulary (`max_age`, `position`, `strong_foot`, `max_value_eur`,
  `diaspora_eligible`) instead of raising. `diaspora_eligible` maps to
  `ancestry_eligibility` being `ELIGIBLE & CLEARED` (verified status
  literal from `backend/eligibility/engine.py`'s `EligibilityStatus`).
- `GET /api/v1/players/{id}` (new): single-player detail fetch. Not in the
  original PRD route list, but needed by the player-profile page the next
  (frontend) change will build, and it is the natural counterpart to the
  list endpoint — scoping it here keeps the frontend change free of
  backend route design.
- `GET /api/v1/players/{id}/similar` (FR-3.2/FR-3.3): fit
  `MetricNormalizer` + `SimilarityEngine` over the subset of stored players
  that have at least one tactical metric recorded, then return the top-K
  ranked matches with percentage similarity scores. A reference player with
  zero tactical metrics, or a candidate pool too small to rank, is a
  defined response state, not a 500 — see design.md for the exact
  behavior, since the spec (FR-3.1/3.2/3.3) says what must be ranked but
  not what to do when ranking isn't possible yet, which is the live
  dataset's actual current state (107 of 113 stored players have zero
  tactical metrics — only the 6 diaspora players could ever have any, and
  today none do, since none plays in an FBref-covered competition).

## Capabilities

### New Capabilities
- `player-search`: filterable player listing and single-player lookup
  backed by the persistence layer (FR-4.2 and the detail-fetch addition).
- `tactical-similarity`: ranked similar-player lookup via the normalization
  + k-NN pipeline (FR-3.1, FR-3.2, FR-3.3).

### Modified Capabilities
(none — `player-records` and `fifa-eligibility` are read, not changed)

## Impact

- **Affected code**: `backend/api/players.py`, `backend/api/similarity.py`,
  `backend/app/main.py` (DB session lifecycle if not already wired).
- **Depends on**: `backend/models/db.py` (`session_scope`),
  `backend/models/player_records.py`, `ml/features/normalize.py`,
  `ml/models/similarity.py`. None of these are modified, only consumed.
- **Not in scope**: PDF export (FR-4.3) and radar charts (FR-4.1) are
  frontend-rendering concerns, not backend routes — out of scope here.
- **Enables**: the upcoming frontend change, which needs working
  search/detail/similarity endpoints to be more than a shell around the
  eligibility form.
