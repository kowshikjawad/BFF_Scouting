# Frontend (Module 4 — Scouting Dashboard)

Per PRD tech stack (`Streamlit` or `Plotly Dash`), the dashboard will expose:

- **Player Profile** (FR-4.1) — radar charts vs. league median via Plotly.
- **Search Filters** (FR-4.2) — age < 23, position, strong foot, max value, diaspora eligibility.
- **PDF Export** (FR-4.3) — 1-page automated scout summary.

Planned entrypoint (Sprint 4): `frontend/app.py` (Streamlit) consuming the FastAPI
backend at `/api/v1`.