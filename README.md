# ShonarTalent AI

Bangladeshi Football Scouting & Talent Discovery Platform.

A lightweight, full-stack data pipeline + web interface that aggregates BPL and
global diaspora player data, applies FIFA eligibility rules, and surfaces
tactically similar players via ML vector similarity.

> See [`PRD.md`](PRD.md) for the full product spec.

## Project layout

```
backend/            FastAPI app, Pydantic models, FIFA eligibility engine
  api/              Routers: players (search), similarity, eligibility
  eligibility/      FIFA Art. 6/7 rules engine
  models/           Pydantic schemas (player)
ml/                 Feature engineering + k-NN/cosine similarity engine
  features/         z-score normalisation (FR-3.1)
  models/           similarity engine (FR-3.2/3.3)
scrapers/           Data ingestion (BPL, FBref, diaspora)
frontend/           Dashboard (Streamlit/Dash, Sprint 4)
data/               raw + processed artifacts (gitignored)
specs/              Spec-driven dev: FR/NFR traceability + acceptance criteria
tests/              pytest suites (smoke, eligibility, similarity)
```

## Quick start

```bash
# 1. Create a virtualenv
python -m venv .venv
.venv\Scripts\activate        # Windows  |  source .venv/bin/activate (macOS/Linux)

# 2. Install (editable, with dev tools)
pip install -e ".[dev]"

# 3. Configure
copy .env.example .env

# 4. Run the API
uvicorn backend.app.main:app --reload --port 8000

# 5. Run tests
pytest
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

## Spec-driven development

Every PRD requirement is traced to code and tests in [`specs/README.md`](specs/README.md)
and the numbered spec files in [`specs/`](specs/). Acceptance criteria live there;
tests prove them.

## Roadmap (PRD §8)

| Sprint | Focus |
|:--|:--|
| 1 | Data Engine — BPL/FBref/diaspora scrapers |
| 2 | Feature engineering + k-NN similarity |
| 3 | FastAPI routes + FIFA eligibility engine |
| 4 | Dashboard UI, radar charts, Docker, docs |