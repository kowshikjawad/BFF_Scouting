# Frontend (Module 4 — Scouting Dashboard)

React + Vite + TypeScript + Tailwind CSS v4 single-page app, consuming the
FastAPI backend at `/api/v1`. Chosen over the PRD's listed Streamlit/Plotly
Dash stack for full control over the custom visual design — see
`openspec/changes/archive/*-scouting-dashboard-ui/design.md` decision #1.

## Views

- **Search** (`/`) — filter players by max age, position, strong foot, max
  value, and diaspora eligibility (FR-4.2).
- **Player profile** (`/players/:id`) — profile fields, a tactical radar
  chart against the pool average (FR-4.1), a "Find similar players" action,
  and a one-page PDF export (FR-4.3, via the browser's print-to-PDF).
- **Eligibility checker** (`/eligibility`) — a standalone form over the
  FIFA eligibility fact fields.

## Local development

Requires the backend running separately (from the repo root):

```bash
uvicorn backend.app.main:app --reload
```

Then, from this directory:

```bash
npm install
cp .env.example .env   # set VITE_API_BASE_URL if the backend isn't on :8000
npm run dev
```

`VITE_API_BASE_URL` defaults to `http://localhost:8000/api/v1` if unset.

## Build

```bash
npm run build
```

## Notes

- No stock or AI-generated photos are attached to any player's profile —
  avatars are generated locally (initials on a deterministic color) since
  the roster is real, named people (see `PRODUCT.md`).
- The radar chart's "pool average" baseline is a client-side approximation
  (mean of the current search result set), not a backend-computed league
  median — there's no such endpoint today. See design.md decision #4.
