# Proposal

## Why

`frontend/` contains only a README describing a planned Streamlit app —
there is no frontend at all (verified: `frontend/` has exactly one file).
PRD Module 4 (FR-4.1 player profile, FR-4.2 search filters, FR-4.3 PDF
export) is entirely unimplemented, and with `wire-scouting-api` now
merged, the backend has working search, detail, and similarity endpoints
with nothing to consume them. The user explicitly asked for a
minimalistic, sleek, image-capable UI — which drives the stack choice
below.

## What Changes

- Scaffold `frontend/` as a React + Vite + TypeScript + Tailwind
  single-page app, replacing the planned Streamlit/Dash stack. PRD lists
  "Streamlit or Plotly Dash" as the Module 4 stack, but the Sprint 4
  roadmap line itself says "Streamlit/**React** dashboard," naming React
  as an accepted alternative — chosen here because a custom web frontend
  gives far more control over visual design than Streamlit, which the
  user's "minimalistic and sleek" requirement calls for.
- **Search view** (FR-4.2): filter controls for max age, position, strong
  foot, max value, and diaspora eligibility, querying `GET
  /api/v1/players`, rendering results as a responsive card grid.
- **Player profile view** (FR-4.1): fetches `GET /api/v1/players/{id}`,
  renders a radar chart of the five tactical metrics. No backend "league
  median" endpoint exists — the median is computed client-side from the
  already-fetched player list and documented as an approximation (see
  design.md).
- **Similarity view**: a "Find similar players" action on the profile view
  calling `GET /api/v1/players/{id}/similar` and listing ranked matches.
- **Eligibility checker**: a form over the FIFA eligibility fact fields
  (mirroring `EligibilityFacts`), calling the eligibility endpoint and
  displaying the returned status.
- **PDF scout summary export** (FR-4.3): a client-side, one-page PDF
  generated from a player's profile view.
- **Backend fix required for integration**: `backend/api/eligibility.py`
  declares its endpoint as `GET` with a Pydantic request body. FastAPI
  accepts this, but it is not callable from a browser's `fetch()` — the
  Fetch spec throws a `TypeError` on any `GET`/`HEAD` request given a body.
  Verified by inspecting the route and cross-checking the Fetch
  specification's request-construction algorithm. Changing the method to
  `POST` is required for the frontend to call it at all; this is a pure
  evaluation endpoint with no stored state, so the change is behavior-
  preserving aside from the HTTP verb.
- **CORS**: add `CORSMiddleware` to `backend/app/main.py` so the Vite dev
  server (a different origin) can call the API during development.

## Capabilities

### New Capabilities
- `scouting-dashboard`: the frontend's search, profile, similarity,
  eligibility-checker, and PDF-export user-facing behavior (FR-4.1,
  FR-4.2, FR-4.3).

### Modified Capabilities
- `fifa-eligibility`: the existing requirements describe evaluation
  *logic* and output statuses, not transport; no requirement text changes,
  but noting here for traceability that the HTTP method of its endpoint
  changes from GET to POST as an implementation fix enabling this change.
  (No delta spec entry needed — see design.md for why this is judged an
  implementation detail, not a spec-level behavior change.)

## Impact

- **New code**: `frontend/` (entire app), replacing the placeholder
  README's described approach.
- **Affected existing code**: `backend/api/eligibility.py` (GET → POST),
  `backend/app/main.py` (add CORS middleware).
- **Consumed, not modified**: `backend/api/players.py`,
  `backend/api/similarity.py`, `backend/models/player_records.py`.
- **Not in scope**: any new backend "league median" endpoint (the radar
  chart's baseline is computed client-side as a documented approximation
  instead); authentication/authorization (PRD does not specify any);
  server-side PDF rendering (done client-side instead, since there's no
  spec requirement for the PDF to be generated server-side and client-side
  avoids adding a backend rendering dependency).
