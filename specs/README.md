# Specs (Spec-Driven Development)

This directory is the single source of truth for **traceability**: every PRD
requirement is mapped to the code that will implement it and the tests that
prove it. When a requirement changes, update the relevant file here and the
mapping stays consistent.

## Traceability matrix

| ID | Requirement | Module | Code (planned/live) | Test |
|:--|:--|:--|:--|:--|
| FR-1.1 | Scrape BPL + global diaspora profiles | Data Ingestion | `scrapers/bpl.py`, `scrapers/fbref.py`, `scrapers/diaspora.py` | `tests/scrapers/` |
| FR-1.2 | Store 8 structured player attributes | Database | `backend/models/player.py` | — |
| FR-2.1 | FIFA Art. 6/7 eligibility calc | Eligibility | `backend/eligibility/engine.py` | `tests/backend/test_eligibility.py` |
| FR-2.2 | Output 3 status indicators | Eligibility | `backend/eligibility/engine.py::Status` | `tests/backend/test_eligibility.py` |
| FR-3.1 | z-score normalize event metrics | ML | `ml/features/normalize.py` | `tests/ml/` |
| FR-3.2 | cosine / k-NN matching | ML | `ml/models/similarity.py` | `tests/ml/test_similarity.py` |
| FR-3.3 | Top-5 ranked + % similarity | ML | `ml/models/similarity.py` | `tests/ml/test_similarity.py` |
| FR-4.1 | Radar chart vs. league median | UI | `frontend/` (Sprint 4) | — |
| FR-4.2 | Multi-variable search filters | API | `backend/api/players.py` | — |
| FR-4.3 | 1-page PDF scout export | UI | `frontend/` (Sprint 4) | — |
| NFR-perf | Similarity < 500ms | API/ML | `backend/api/similarity.py` | — |
| NFR-fresh | Weekly cron scrapers | Data | `scripts/` + `.env.example` | — |
| NFR-port | Docker containerised | Infra | `Dockerfile`, `docker-compose.yml` | — |

See the numbered spec files below for acceptance criteria per module.
## Active completion specification (2026-10-28)

New work is governed by [001-complete-scouting-workspace/spec.md](001-complete-scouting-workspace/spec.md),
with its plan, contracts, tasks and verification. It supersedes the original UI placeholders and
global-average approximation while retaining the original PRD requirement IDs and OpenSpec history.

The authorized fictional-data extension is specified in [002-synthetic-demo/spec.md](002-synthetic-demo/spec.md).
It adds an explicitly labelled demo without changing sourced real-player facts.
