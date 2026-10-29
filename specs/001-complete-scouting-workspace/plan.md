# Implementation Plan: Complete scouting workspace

**Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary
Keep the existing database, ML pipeline and APIs. Repair data contracts first; implement a light,
minimal scouting workspace with a sidebar, useful directory, profiles, local shortlist and clear
eligibility screening. Add real PDF exports and a reproducible same-origin deployment.

## Technical Context
- Python 3.11, FastAPI, SQLAlchemy, ReportLab; React 19, TypeScript, Vite, Tailwind and Recharts.
- SQLite remains the single persisted player store. Shortlists use versioned localStorage IDs.
- pytest for backend contracts; Playwright for actual browser journeys and responsive checks.
- Small existing dataset (113 players): one filtered API response with client-side 12-row pagination.
- Existing list response is retained for compatibility. Add optional query/sort/status parameters.
- No new runtime frontend dependencies; PDF and icon/font dependencies already exist.

## Constitution Check
All five principles pass: preserve data, complete workflows, accessible semantics, bounded inputs,
and regression plus visual verification. Existing rules engine is a limited historical ruleset;
the UI/API must identify that limitation and refer prior youth representation for review.

## Implementation Sequence
1. Restore metric fields and nullable schema parity; name/position/status/sort API support.
2. Add real PDF endpoint and improve eligibility validation and explanations.
3. Build responsive shell, unified tokens, directory/list/card views and URL state.
4. Add local shortlist, rich profile, normalized cohort radar and recoverable request states.
5. Finish eligibility flow, data-guide screen, accessibility and asset attribution.
6. Serve production frontend through FastAPI; Vite proxy in development; offline seed and Docker.
7. Add targeted regressions, browser checks, visual PDF QA; reconcile tasks and docs.

## Project Structure
- `backend/api/`: contracts, filtering, assessment and PDF route.
- `backend/reports/`: one-page ReportLab summary.
- `frontend/src/`: shell, pages, components, API and state helpers.
- `tests/backend/`: API regressions; `frontend/tests/`: browser and pure-logic checks.
- `scripts/`: offline seed and data refresh; `.github/workflows/ci.yml`: full validation.
- `specs/001-complete-scouting-workspace/`: research, design contracts, tasks and verification.

## Complexity Tracking
No extra services, UI libraries, authentication or data migrations. Reuse existing nullable columns.
