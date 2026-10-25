# Tasks

## 1. Query layer

- [x] 1.1 Add `list_players(session, *, max_age=None, position=None,
      strong_foot=None, max_value_eur=None, diaspora_eligible=None)` to
      `backend/models/player_records.py`, building a SQLAlchemy query with
      each supplied filter AND-combined (design.md decisions #2, #3).
      Verify with tests: no filters returns all; each filter alone narrows
      correctly; `max_age` excludes NULL ages; combined filters AND
      together.
- [x] 1.2 Add a FastAPI dependency (e.g. `get_session` in
      `backend/models/db.py` or `backend/app/deps.py`) that yields a
      `session_scope()` session for route injection. Verify by importing
      it from a route module without circular-import errors.

## 2. Player search + detail routes

- [x] 2.1 Wire `GET /api/v1/players` in `backend/api/players.py` to
      `list_players`, removing the `NotImplementedError`. Verify with a
      `TestClient` test per spec scenario (no filters, single filter,
      combined filters, diaspora filter).
- [x] 2.2 Add `GET /api/v1/players/{player_id}` returning the stored
      record via `get_player`, with a 404 when `get_player` returns
      `None`. Verify with tests for both the existing-player and
      unknown-player scenarios.

## 3. Similarity pipeline

- [x] 3.1 Implement a pure function (e.g.
      `backend/similarity/pipeline.py::rank_similar(session, player_id,
      top_k)`) that: loads all players with at least one non-null tactical
      metric, builds the normalized matrix substituting z-score 0 for any
      individual missing metric (design.md decision #5), fits
      `MetricNormalizer` + `SimilarityEngine`, and returns ranked
      `(player_id, name, similarity_pct)` results excluding the reference
      player. Keep this free of FastAPI types so it's unit-testable
      directly.
- [x] 3.2 Implement the three response states from design.md decision #6:
      unknown id, no-usable-data (empty result), and ranked result. Verify
      with tests for all three spec scenarios on the "insufficient data"
      requirement plus the "fewer candidates than top-K" scenario.
- [x] 3.3 Wire `GET /api/v1/players/{player_id}/similar` in
      `backend/api/similarity.py` to the pipeline function, mapping
      unknown-id to 404 and the other two states to 200 responses. Verify
      with a `TestClient` test per spec scenario, including a response
      under the 500ms NFR budget at the current (~113-row) dataset size.

## 4. Verification

- [x] 4.1 Run the full test suite (`pytest`) and `ruff check`, confirming
      no regressions in the eligibility/persistence/scraper tests already
      in place.
- [x] 4.2 Live-verify against the actual populated database (
      `data/processed/shonartalent.db`, ~113 real players from this
      session's scraper run): hit `/api/v1/players` with a few real filter
      combinations and `/api/v1/players/{id}/similar` for both a diaspora
      player id and a domestic player id, and confirm the responses match
      the expected state (e.g. domestic players currently yield the
      empty/insufficient-data state, since none have tactical metrics
      today).

## Workflow follow-up

- Run `openspec validate --changes "wire-scouting-api" --strict` before
  archiving.
- Archive the change (`/opsx:archive`) once implementation and tests are
  complete, which syncs both delta specs into `openspec/specs/`.
