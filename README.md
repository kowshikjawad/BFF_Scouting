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
  <a href="https://react.dev/">
    <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
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

A **full-stack data pipeline and scouting dashboard** that:

1. **Aggregates** player data from the Bangladesh Football League (BFL) and a maintained global diaspora reference set into one searchable database
2. **Matches talent** using ML (z-score normalization + cosine k-NN) to surface players with comparable tactical profiles
3. **Validates eligibility** — evaluates FIFA national-team eligibility under Statutes Art. 6, 7, and 8 (genuine link / residency / one-time association switch)
4. **Visualizes it all** in a dedicated web dashboard — search/filter, player profiles with radar charts, similarity results, and one-page PDF scout summaries

> 📖 Full product specification: [`PRD.md`](PRD.md) · Behavior contracts: [`openspec/specs/`](openspec/specs/)

---

## ✨ Features

| Module | What It Does | Status |
|:--|:--|:--:|
| **🌍 Data Ingestion** | Scrapes BFL squads (Wikipedia, with football/cricket source disambiguation), FBref tactical stats (for tracked players in FBref's 9 covered competitions), and a maintained diaspora reference set | ✅ Live |
| **⚖️ FIFA Eligibility Engine** | Rule-based evaluation of Art. 6 (dual national, 2yr residency), Art. 7 (new nationality, 5yr post-18 residency), and Art. 8 (one-time association switch) → `ELIGIBLE & CLEARED`, `DOCUMENTATION REQUIRED`, or `INELIGIBLE` | ✅ Live |
| **🧠 Tactical Similarity Engine** | z-score normalization + cosine k-NN matching over 5 per-90 metrics (Goals, Key Passes, Progressive Carries, Tackles Won, Aerial Duel %) | ✅ Live |
| **🔌 RESTful API** | Player search/detail/similarity/eligibility, all via FastAPI with auto-generated OpenAPI docs | ✅ Live |
| **📊 Scouting Dashboard** | React web app: filterable search, player profiles with tactical radar charts, similarity results, an eligibility checker form, and 1-page PDF export | ✅ Live |

A live run of the scrapers (as of this writing) populates **113 real players** (6 diaspora + 107 domestic) into the local database.

---

## 🏗️ Architecture

```
  [External Data Sources]
    (Wikipedia BFL squad pages / FBref / maintained diaspora reference set)
               │
               ▼
    [• BFL Squad Scraper]     [• FBref Scraper]     [• Diaspora Loader]
               │                      │                       │
               └──────────────────────┼───────────────────────┘
                                      ▼
                      [ SQLite persistence layer ]
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
          [ Similarity Engine ]  [ Eligibility Engine ]  [ Search/Filter ]
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                           [ FastAPI / Uvicorn API ]
                                      │
                                      ▼
                   [ React + Vite + Tailwind Dashboard ]
```

---

## 🧰 Tech Stack

| Layer | Technology |
|:--|:--|
| **Backend language** | Python 3.10+ |
| **Data ingestion** | `requests` + `BeautifulSoup4` (Wikipedia), `soccerdata` (FBref), `PyYAML` (diaspora reference set) |
| **ML / analytics** | `scikit-learn` (StandardScaler, NearestNeighbors), `NumPy` |
| **Backend API** | FastAPI + Pydantic + SQLAlchemy (auto-generated OpenAPI docs) |
| **Frontend** | React 19 + Vite + TypeScript + Tailwind CSS v4 + Recharts |
| **Data storage** | SQLite (dev) / PostgreSQL-ready via `DATABASE_URL` |
| **Container** | Docker & docker-compose |
| **CI/CD** | GitHub Actions (lint + test on every push) |
| **Planning** | [OpenSpec](openspec/) — spec-driven change proposals, specs, and design docs |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** and `pip`
- **Node.js 18+** and `npm` (for the frontend)
- Git
- **Google Chrome** (desktop install, not just the CLI) — required *only*
  to run the FBref scraper (`scrapers/fbref.py`), which drives a real
  browser session via `soccerdata`/SeleniumBase because FBref sits behind
  bot-detection that blocks plain HTTP requests. Not needed to run the API,
  the frontend, the other two scrapers, or the test suite — FBref-dependent
  tests skip gracefully when Chrome isn't present.

### 1. Clone and set up the backend

```bash
git clone https://github.com/kowshikjawad/BFF_Scouting.git
cd BFF_Scouting

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

cp .env.example .env
```

### 2. Populate the database (optional, but the dashboard is much more
interesting with real data in it)

```bash
python scripts/run_scrapers.py
```

This scrapes the Bangladesh Football League's per-club squad pages, loads
the maintained diaspora reference set, and attempts an FBref backfill for
any tracked player in one of FBref's 9 covered competitions. Each source
fails independently — a blocked or missing source doesn't stop the others
from persisting. Results land in `data/processed/shonartalent.db` (SQLite,
gitignored).

### 3. Run the API

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** for the interactive Swagger UI.

### 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env    # defaults to http://localhost:8000/api/v1
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)** — the dashboard talks to the API you started in step 3.

### Run tests

```bash
# Backend (from the repo root, with .venv active)
pytest -v
ruff check .

# Frontend (from frontend/)
npm run build
```

### Docker

```bash
docker compose up --build
```

---

## 📂 Project Structure

```
.
├── backend/                 # FastAPI app, models, eligibility & similarity engines
│   ├── api/                 #   Routers: players (search/detail), similarity, eligibility
│   ├── app/                 #   App factory, config, CORS
│   ├── eligibility/         #   FIFA Art. 6/7/8 rules engine
│   ├── models/               #   Pydantic schema + SQLAlchemy persistence (player_records.py)
│   └── similarity/           #   Similarity pipeline wiring persistence to the ML layer
├── ml/                      # Machine learning pipeline
│   ├── features/            #   z-score normalization
│   └── models/               #   k-NN / cosine similarity engine
├── scrapers/                # Data ingestion (BFL squads, FBref, diaspora)
├── frontend/                # React + Vite + Tailwind scouting dashboard
│   └── src/
│       ├── api/              #   Typed fetch client
│       ├── components/       #   Avatar, FilterBar, PlayerCard, TacticalRadar, ...
│       └── pages/             #   SearchPage, ProfilePage, EligibilityPage
├── openspec/                # Spec-driven change proposals, specs, and design docs
│   ├── specs/                #   Current behavior contracts per capability
│   └── changes/archive/      #   Completed, archived change proposals
├── data/                    # Raw scraped data + processed DB (gitignored)
├── scripts/                 # Scraper orchestration entrypoint
├── tests/                   # pytest suites (backend, scrapers, ml)
├── .github/workflows/       # CI pipeline
├── pyproject.toml           # Python packaging
├── Dockerfile               # Container image
└── docker-compose.yml       # Local orchestration
```

---

## 📊 API Endpoints

| Method | Path | Description |
|:--|:--|:--|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/players` | Multi-variable player search (age, position, foot, value, diaspora eligibility) |
| `GET` | `/api/v1/players/{id}` | Single player detail lookup |
| `GET` | `/api/v1/players/{id}/similar` | Top-K tactically similar players |
| `POST` | `/api/v1/players/{id}/eligibility` | FIFA eligibility status evaluation |

---

## 📐 Spec-Driven Development

This project uses [OpenSpec](openspec/) for planning: every change is proposed as a spec delta, design doc, and task list before implementation, then archived with its spec synced into [`openspec/specs/`](openspec/specs/) — the current source of truth for each capability's behavior.

| Capability | Covers | Spec |
|:--|:--|:--|
| **player-data-ingestion** | Scraper sourcing rules, rate limits, failure isolation | `openspec/specs/player-data-ingestion/` |
| **player-records** | Persistence semantics (partial records, upserts) | `openspec/specs/player-records/` |
| **fifa-eligibility** | Art. 6/7/8 evaluation rules | `openspec/specs/fifa-eligibility/` |
| **player-search** | Search/filter and detail lookup behavior | `openspec/specs/player-search/` |
| **tactical-similarity** | Similarity ranking rules and edge cases | `openspec/specs/tactical-similarity/` |
| **scouting-dashboard** | Frontend user-facing behavior | `openspec/specs/scouting-dashboard/` |

---

## 🤝 Contributing

This project is in active development. Contributions, bug reports, and feature ideas are welcome!

1. Check [`openspec/specs/`](openspec/specs/) for current behavior contracts and [open issues](https://github.com/kowshikjawad/BFF_Scouting/issues)
2. Fork the repo and create a feature branch
3. Run `pytest`, `ruff check .`, and (if touching the frontend) `npm run build` before opening a PR
4. Open a pull request against `master`

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  <sub>Made with ❤️ for the Bangladesh Football Federation & the future of Bangladeshi football scouting 🇧🇩</sub>
</p>
