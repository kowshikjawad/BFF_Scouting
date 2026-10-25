# Design

## Context

`frontend/` today has one file: a README describing a planned Streamlit
app that was never built. The backend (`backend/app/main.py`) exposes,
as of `wire-scouting-api`: `GET /api/v1/players` (search), `GET
/api/v1/players/{id}` (detail), `GET /api/v1/players/{id}/similar`
(ranked matches), and `GET /api/v1/players/{id}/eligibility` (eligibility,
GET-with-body — see decision #5). No auth exists anywhere in the project;
this change doesn't add any.

## Decisions

### 1. Stack: React + Vite + TypeScript + Tailwind, not Streamlit/Dash
PRD lists "Streamlit or Plotly Dash"; Sprint 4's roadmap line says
"Streamlit/**React** dashboard," naming React as an accepted alternative.
The user explicitly asked for a minimalistic, sleek, custom visual design
with imagery — Streamlit's component model makes that materially harder
to achieve than a custom web frontend with full CSS control. Vite gives a
fast dev loop; TypeScript catches API-shape drift against the backend's
Pydantic models early; Tailwind is the fastest path to a consistent,
custom design system without hand-rolling a CSS architecture.

### 2. No icon/photo dependency on external image hosts
The player roster includes real, named people (e.g. Hamza Choudhury,
Jamal Bhuyan). Attaching stock photos of unrelated people to real players'
names would misrepresent them — not acceptable regardless of visual
payoff. Player avatars are generated locally (initials on a deterministic
color, derived from the player id) using CSS/SVG only. All icons come from
a bundled icon set (`lucide-react` — MIT-licensed, tree-shakeable SVGs,
no network fetch at runtime). Any larger decorative imagery (e.g. a
landing hero) uses a CSS gradient / generated SVG pattern checked into the
repo, not a fetched stock photo — this keeps the app's visual polish
fully reproducible with no external asset dependency, while leaving room
for the user to later drop a real photo into `frontend/public/images/`
behind a `<picture>` element with the generated version as fallback, if
they obtain rights to one.

### 3. State/data: a thin fetch-based API client, no global state library
The dashboard's state is almost entirely "what did the backend just
return for this query" — React Query-style server-state caching would be
reasonable but is a dependency this app's small page count doesn't
justify. A single `frontend/src/api/client.ts` wrapping `fetch` against a
`VITE_API_BASE_URL` env var, plus React's built-in `useState`/`useEffect`
per view, is simpler and sufficient at this scope.

### 4. Pool-average radar baseline is a documented client-side approximation
FR-4.1 calls for "league median." The backend only exposes individual
player records and a similarity ranking — there's no per-position-median
endpoint, and `player-search`'s delta spec never promised one. Rather than
expand the already-merged `wire-scouting-api` change's scope, or block
this change on a new backend endpoint, the radar chart computes the
**average** (not median — simpler, and the dataset is small enough that
mean vs. median rarely diverges meaningfully) of each tactical metric
across whatever players the current search result set already includes,
and labels the comparison line "pool average" rather than claiming
"league median." This is an accepted, labeled approximation, not a
silent substitution.

### 5. Eligibility endpoint: GET → POST
`backend/api/eligibility.py`'s `@router.get(...)` handler takes a Pydantic
`facts: EligibilityFacts` request body. FastAPI/OpenAPI permit this, but
the Fetch API's request-construction algorithm throws `TypeError: Request
with GET/HEAD method cannot have body` for any such call from a browser.
Verified directly against the Fetch spec's "request body" validation step.
Since this is a stateless evaluation (no resource is being fetched by id;
facts are supplied and a computed status is returned), `POST` is also the
more semantically correct verb, not just a workaround. The change is a
one-line decorator edit (`@router.get` → `@router.post`); the function
body, request/response models, and existing tests' assertions on behavior
are unaffected (only the test client's HTTP method call needs updating).

### 6. PDF export: client-side, not a new backend endpoint
`FR-4.3` asks for a one-page PDF. Generating it client-side (e.g.
rendering the already-visible profile view to canvas and emitting a PDF
in-browser) needs no new backend code, no server-side rendering
dependency, and no new API surface — appropriate since the PDF's content
is exactly what the profile view already displays.

### 7. Design execution
The actual visual design (layout, spacing, type scale, color system,
motion) is produced using this project's installed `impeccable` design
skill during implementation, not hand-specified requirement-by-requirement
here — design.md fixes the *information architecture* (what views exist,
what each shows, what state each can be in per the spec's scenarios); the
skill owns translating that into the "minimalistic, sleek" visual
execution the user asked for.

## Pages / components (information architecture)

- **Search** (`/`): filter bar + responsive player card grid.
- **Player profile** (`/players/:id`): profile fields, radar chart (or
  "no tactical data" state), "Find similar" action, "Export PDF" action.
- **Similarity panel**: rendered within the profile view (not a separate
  route) once "Find similar" is triggered, per spec's scenarios being
  profile-view-scoped actions.
- **Eligibility checker** (`/eligibility`): standalone form + result,
  since it's not tied to a specific stored player (the form supplies all
  facts directly, matching `EligibilityFacts`).

## Backend changes in this file's scope

- `backend/api/eligibility.py`: `@router.get` → `@router.post` on the one
  route; update its existing test(s) to call `client.post(...)`.
- `backend/app/main.py`: add `fastapi.middleware.cors.CORSMiddleware`
  allowing the Vite dev server origin(s) (`http://localhost:5173` and
  `http://127.0.0.1:5173`) for local development.
