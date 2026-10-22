<h1 align="center">🏆 <b><span style="color:#006747;">Shonar</span><span style="color:#C60C30;">Talent</span> AI</b></h1>
<h3 align="center">🇧🇩 Bangladeshi Football Scouting & Talent Discovery Platform</h3>

<p align="center">
  <a href="https://github.com/kowshikjawad/BFF_Scouting/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/kowshikjawad/BFF_Scouting/ci.yml?branch=master&style=for-the-badge&logo=github&label=CI" alt="CI"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python"/>
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.110+-teal?style=for-the-badge" alt="FastAPI"/>
  </a>
  <a href="https://scikit-learn.org/">
    <img src="https://img.shields.io/badge/ML-scikit--learn-orange?style=for-the-badge" alt="scikit-learn"/>
  </a>
</p>

<p align="center">
  <b>
    <span>🗃️ Data Ingestion</span> •
    <span>🧠 ML Similarity Engine</span> •
    <span>⚖️ FIFA Eligibility</span> •
    <span>📊 Scout Dashboard</span>
  </b>
</p>

---

## 🎯 The Problem

Bangladeshi football clubs (Bashundhara Kings, Abahani Limited, Fortis FC) and the **Bangladesh Football Federation (BFF)** face a structural data void:

- **No match tracking data** — optical tracking, heatmaps, event-level metrics are practically non-existent in South Asian domestic leagues due to $100k+ hardware costs.
- **No diaspora pipeline** — identifying Bangladeshi-origin players in lower European/North American leagues relies entirely on manual word-of-mouth scouting.

## 💡 Our Solution

A **lightweight, full-stack data pipeline** that:

1. **Aggregates** player data from BPL + global diaspora sources into one searchable database
2. **Matches talent** using ML (Vector Similarity / k-NN) to surface domestic players who match tactical profiles from higher-tier leagues
3. **Validates eligibility** — automatically evaluates FIFA national-team eligibility (ancestry, passport, residency)

> 📖 Full product specification: [`PRD.md`](PRD.md)

---

## ✨️ Features

| Module | What It Does | Status |
|:--|:--|:--:|
| **🌍 Global Diaspora Database** | Scrape BPL squads + FBref stats + diaspora listings into structured player profiles | 🏗️ Sprint 1 |
| **⚖️ FIFA Eligibility Engine** | Rule-based evaluation using FIFA Art. 6 & 7 → `ELIGIBLE & CLEARED`, `DOCUMENTATION REQUIRED`, or `INELIGIBLE` | ✅ Live |
| **🧠 Tactical Similarity Engine** | z-score normalization + cosine k-NN matching (Goals/90, Key Passes/90, Tackles Won/90, Aerial Duel %) | ✅ Live |
| **📊 Scouting Dashboard** | Interactive radar charts, filterable search, 1-page PDF scout reports | 🏗️ Sprint 4 |
| **🔌 RESTful API** | Multi-variable search (age, position, foot, value, eligibility) — all via FastAPI | 🏗️ Sprint 3 |

---

## 🏗️ Architecture

```
  [External Data Sources]
    (Transfermarkt / FBref / News)
               │
               ▼
    [• BPL Squad Scraper]     [• FBref Scraper]     [• Diaspora Scraper]
               │                      │                       │
               └──────────────────────┼───────────────────────┘
                                      ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Feature Pipeline & Vector Engine            │
    │                        │                                 │
    │              FIFA Eligibility Logic Engine                │
    └──────────────────────────┬──────────────────────────────┘
                               │
                               ▼
                      [ FastAPI / Uvicorn ]
                               │
                               ▼
                   [ Streamlit / Plotly Dashboard ]
```

---

## 🧰 Tech Stack

| Layer | Technology |
|:--|:--|
| **Language** | Python 3.10+ |
| **Data Ingestion** | `soccerdata`, `BeautifulSoup4`, `Pandas` |
| **ML / Analytics** | `scikit-learn` (StandardScaler, NearestNeighbors), `NumPy` |
| **Backend API** | FastAPI + Pydantic (auto-generated OpenAPI docs) |
| **Frontend UI** | Streamlit or Plotly Dash *(Sprint 4)* |
| **Data Storage** | SQLite (dev) / PostgreSQL (prod) |
| **Container** | Docker & docker-compose |
| **CI/CD** | GitHub Actions (lint + test on every push) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ and `pip` / `uv`
- Git

### Setup (3 minutes)

```bash
# 1. Clone the repo
git clone https://github.com/kowshikjawad/BFF_Scouting.git
cd BFF_Scouting

# 2. Create virtual environment
python -m venv .venv

# Windows
source .venv/Scripts/activate
# macOS / Linux
# source .venv/bin/activate

# 3. Install (editable, with dev tools)
pip install -e ".[dev]"

# or, using uv (much faster)
# uv venv .venv --python 3.12
# uv pip install -e ".[dev]" --python .venv/Scripts/python.exe

# 4. Configure environment
cp .env.example .env
```

### Run the API

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** for the interactive Swagger UI.

### Run Tests

```bash
pytest -v
```

```
collected 7 items

tests/backend/test_eligibility.py .....     [ 71%]  ✅
tests/ml/test_similarity.py .               [ 85%]  ✅
tests/test_smoke.py .                       [100%]  ✅
```

### Docker

```bash
docker compose up --build
```

---

## 📂 Project Structure

```
.
├── backend/                 # FastAPI app, models, eligibility engine
│   ├── api/                 #   API routers (players, similarity, eligibility)
│   ├── app/                 #   App factory, config
│   ├── eligibility/         #   FIFA Art. 6/7 rules engine
│   └── models/               #   Pydantic schemas
├── ml/                      # Machine learning pipeline
│   ├── features/            #   z-score normalization
│   ├── models/              #   k-NN / cosine similarity engine
│   └── evaluation/          #   Benchmarking & notebooks
├── scrapers/                # Data ingestion (BPL, FBref, diaspora)
├── frontend/                # Dashboard (Streamlit / Dash — Sprint 4)
├── specs/                   # Spec-driven development traceability
├── tests/                   # pytest suites
├── scripts/                 # Cron entrypoints & utilities
├── data/                    # Raw scraped data + processed artifacts (gitignored)
├── .github/workflows/       # CI pipeline
├── pyproject.toml           # Python packaging
├── Dockerfile               # Container image
└── docker-compose.yml       # Local orchestration
```

---

## 📊 API Endpoints

| Method | Path | Description | Module |
|:--|:--|:--|:--:|
| `GET` | `/health` | Health check | — |
| `GET` | `/api/v1/players` | Multi-variable player search | FR-4.2 |
| `GET` | `/api/v1/players/{id}/similar` | Top-K tactical lookalikes | FR-3.2/3.3 |
| `GET` | `/api/v1/players/{id}/eligibility` | FIFA eligibility status | FR-2.1/2.2 |

---

## 📐 Spec-Driven Development

Every requirement in the PRD is traced to code and tests via the [`specs/`](specs/) directory:

| ID | Requirement | Code | Tests |
|:--|:--|:--|:--:|
| **FR-1.1** | Scrape BPL + global diaspora profiles | `scrapers/bpl.py`, `fbref.py`, `diaspora.py` | Sprint 1 |
| **FR-1.2** | Store 8 structured player attributes | `backend/models/player.py` | — |
| **FR-2.1** | FIFA Art. 6/7 eligibility calc | `backend/eligibility/engine.py` | `tests/backend/test_eligibility.py` |
| **FR-2.2** | Output 3 status indicators | `backend/eligibility/engine.py::Status` | `tests/backend/test_eligibility.py` |
| **FR-3.1** | z-score normalize event metrics | `ml/features/normalize.py` | — |
| **FR-3.2** | cosine / k-NN matching | `ml/models/similarity.py` | `tests/ml/test_similarity.py` |
| **FR-3.3** | Top-5 ranked + % similarity | `ml/models/similarity.py` | `tests/ml/test_similarity.py` |
| **FR-4.1** | Radar chart vs. league median | `frontend/` | Sprint 4 |
| **FR-4.2** | Multi-variable search filters | `backend/api/players.py` | Sprint 3 |
| **FR-4.3** | 1-page PDF scout export | `frontend/` | Sprint 4 |

---

## 🗺️ Roadmap

| Sprint | Focus | Planned Deliverables |
|:--:|:--|:--|
| **1** | 🗃️ Data Engine | BPL squad scraper, FBref stat scraper, diaspora listing scraper |
| **2** | 📊 Feature Engineering & ML | z-score normalization pipeline, k-NN vector similarity engine |
| **3** | 🔌 Backend & Eligibility | FastAPI routes, FIFA heritage logic, SQLite/PostgreSQL persistence |
| **4** | 🎨 UI & Polish | Streamlit dashboard, radar charts, PDF export, Docker, docs |

---

## 🤝 Contributing

This project is in early development. Contributions, bug reports, and feature ideas are welcome!

1. Check the [specs](specs/) and [open issues](https://github.com/kowshikjawad/BFF_Scouting/issues)
2. Fork the repo and create a feature branch
3. Run `pytest` and `ruff check .` before opening a PR
4. Open a pull request against `main`

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  <sub>Made with ❤️ for the Bangladesh Football Federation & the future of Bangladeshi football scouting 🇧🇩</sub>
</p>