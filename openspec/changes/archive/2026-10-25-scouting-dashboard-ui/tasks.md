# Tasks

## 1. Backend prerequisites

- [x] 1.1 Change `backend/api/eligibility.py`'s route decorator from
      `@router.get` to `@router.post` (design.md decision #5). Update
      `tests/backend/test_eligibility.py` to call `client.post(...)`
      instead of `client.get(...)`. Verify with
      `pytest tests/backend/test_eligibility.py -v`.
- [x] 1.2 Add `CORSMiddleware` to `backend/app/main.py`'s `create_app()`
      allowing `http://localhost:5173` and `http://127.0.0.1:5173`.
      Verify with a test asserting an `Access-Control-Allow-Origin` header
      is present on a request from that origin.

## 2. Frontend scaffold

- [x] 2.1 Scaffold `frontend/` as a Vite + React + TypeScript project
      (`npm create vite@latest`), add Tailwind CSS, `lucide-react`, a
      charting library for the radar chart (`recharts`), and a routing
      library (`react-router-dom`). Verify with `npm run dev` serving a
      blank app and `npm run build` succeeding.
- [x] 2.2 Add `frontend/src/api/client.ts`: typed fetch wrappers for
      `GET /players` (with filter params), `GET /players/{id}`,
      `GET /players/{id}/similar`, `POST /players/{id}/eligibility`
      (post-fix), reading the base URL from `VITE_API_BASE_URL` (default
      `http://localhost:8000/api/v1`). Verify by exercising each wrapper
      against the running backend (`uvicorn backend.app.main:app`) from a
      throwaway script or the dev console.
- [x] 2.3 Preserve `frontend/README.md`'s intent by rewriting it to
      describe the actual stack, local dev commands, and the
      `VITE_API_BASE_URL` env var.

## 3. Search view

- [x] 3.1 Build the filter bar (max age, position, strong foot, max
      value, diaspora eligibility) and wire it to re-query
      `GET /players` on change.
- [x] 3.2 Build the player card grid consuming the search results, using
      generated initials avatars (design.md decision #2), and verify the
      three spec scenarios (default unfiltered view, a filter narrowing
      results, clearing a filter restoring results) manually against the
      live backend's real ~113-player dataset from this session's scraper
      run.

## 4. Player profile view

- [x] 4.1 Build the profile route fetching `GET /players/{id}` and
      displaying its profile fields.
- [x] 4.2 Build the radar chart: on profile load, compute each tactical
      metric's pool average from the current search result set
      (design.md decision #4) and render the player's own metrics against
      it, clearly labeled "pool average," via `recharts`'s radar chart.
      Verify the "has metrics" and "no metrics recorded" scenarios
      against real players from the live dataset (diaspora players
      currently have zero recorded metrics -- verify this renders the
      explicit no-data state, not an empty or broken chart).

## 5. Similarity panel

- [x] 5.1 Add the "Find similar players" action on the profile view,
      calling `GET /players/{id}/similar`, and render the three states
      (loading, ranked results, explicit empty state) per spec. Verify the
      empty state against a real diaspora player id (today, every
      similarity lookup returns empty, since zero stored players have any
      tactical metric -- confirm the UI reads as "no similar players
      currently available," not broken or stuck loading).

## 6. Eligibility checker

- [x] 6.1 Build the `/eligibility` form mirroring `EligibilityFacts`'
      fields, submitting to the now-POST endpoint, and displaying the
      returned status and Article 8 switch-required/approved state.
      Verify against at least one case per status value using the
      existing backend test scenarios as reference inputs.

## 7. PDF export

- [x] 7.1 Implement client-side one-page PDF export from the profile view
      (design.md decision #6). Verify by exporting a real player's profile
      and confirming the produced file is a single page containing that
      player's profile fields and tactical metrics (or the "no data"
      state, for a player without them).

## 8. Design pass

- [x] 8.1 Run the `impeccable` design skill over the built views to reach
      the "minimalistic, sleek" visual bar the user asked for (design.md
      decision #7): layout, spacing, type scale, color system, and any
      warranted motion/empty-state polish.

## 9. Verification

- [x] 9.1 Run the full backend test suite (`pytest`) and `ruff check`
      after the eligibility method change, confirming no regressions.
- [x] 9.2 Run `npm run build` for a production build with no TypeScript
      errors.
- [x] 9.3 Start both servers (`uvicorn backend.app.main:app`, `npm run
      dev`) and manually exercise every view against the real, live
      113-player database end-to-end: search + filter, a domestic
      player's profile (no tactical data), a diaspora player's profile
      (no tactical data, still -- confirm this is distinguished from an
      error), the eligibility form, and a PDF export.

## Workflow follow-up

- Run `openspec validate --changes "scouting-dashboard-ui" --strict`
  before archiving.
- Archive the change (`/opsx:archive`) once implementation and tests are
  complete, which syncs the delta spec into `openspec/specs/`.
