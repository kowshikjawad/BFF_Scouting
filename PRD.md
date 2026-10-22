# Product Requirement Document (PRD)

## 1. Document Overview
* **Product Name:** ShonarTalent AI (Bangladeshi Football Scouting & Talent Discovery Platform)
* **Document Status:** Draft v1.0
* **Target Audience:** Head of Recruitment, Technical Directors, BFF (Bangladesh Football Federation) Analysts, Regional Talent Scouts

---

## 2. Product Summary & Problem Statement

### 2.1 Background & Problem
Bangladeshi football clubs (e.g., Bashundhara Kings, Abahani Limited, Fortis FC) and the national team face a structural data void. Match tracking data (optical tracking, heatmaps, event-level metrics) is practically non-existent in South Asian domestic leagues due to high hardware costs ($100k+ setups). Additionally, identifying Bangladeshi-origin diaspora players in lower European/North American leagues relies entirely on manual word-of-mouth scouting.

### 2.2 Objective
Build a lightweight, full-stack data pipeline and web interface that:
1. Aggregates data on domestic BPL players alongside dual-national/diaspora players globally.
2. Uses machine learning (Vector Similarity / KNN) to identify domestic talent matching tactical profiles in higher-tier leagues.
3. Automatically evaluates national team eligibility under FIFA rules (ancestry, passport status).

---

## 3. Target User Personas

| Persona | Core Need | Key Feature Used |
| :--- | :--- | :--- |
| **National Team Scout** | Find dual-nationality players abroad eligible for Bangladesh. | Diaspora Eligibility Filter & Verification Radar. |
| **BPL Recruitment Director** | Find low-cost replacement players matching specific tactical traits. | Tactical Similarity Engine (KNN / Cosine Score). |
| **Performance Analyst** | Evaluate domestic player performance relative to league baselines. | Percentile Radar Charts & Metric Normalization. |

---

## 4. System Architecture

```
[ External Data Sources ]
(Transfermarkt / FBref / News)
           │
           ▼
[ Data Ingestion Engine (Scraper) ]
           │
           ▼
[ Feature Pipeline & Vector Engine ] ──► [ FIFA Eligibility Logic Engine ]
           │                                          │
           └───────────────────┬──────────────────────┘
                               │
                               ▼
                    [ RESTful API (FastAPI) ]
                               │
                               ▼
               [ Interactive Streamlit / React UI ]
```

---

## 5. Key Functional Requirements

### Module 1: Global Diaspora & Domestic Database
* **FR-1.1:** System shall scrape and maintain structured profiles of players across the Bangladesh Premier League (BPL) and global leagues (UK, Europe, North America) who hold Bangladeshi citizenship or heritage (e.g., Hamza Choudhury, Tariq Kazi, Zidane Yousuf).
* **FR-1.2:** Store attributes: Name, Age, Primary Position, Height, Strong Foot, Current League Band, Contract Expiry, Estimated Value, and Ancestry Eligibility Status.

### Module 2: FIFA Eligibility & Heritage Rules Engine
* **FR-2.1:** Calculate eligibility flags for the Bangladesh National Team based on FIFA Statutes (Article 6 & 7: Born in territory, parent/grandparent born in territory, or 5-year residency).
* **FR-2.2:** Output clear status indicators: `ELIGIBLE & CLEARED`, `DOCUMENTATION REQUIRED`, or `INELIGIBLE`.

### Module 3: Tactical Similarity Engine (Machine Learning)
* **FR-3.1:** Normalize player event metrics (Goals/90, Key Passes/90, Progressive Carries/90, Tackles Won/90, Aerial Duel %) using z-scores relative to league tier standard.
* **FR-3.2:** Execute cosine similarity / k-Nearest Neighbors (k-NN) vector matching when a user selects a reference player.
* **FR-3.3:** Return a ranked list of top 5 similar domestic or diaspora options with percentage similarity scores.

### Module 4: Scouting Dashboard & UI
* **FR-4.1 (Player Profile):** Render interactive radar charts comparing a player's metrics against the league median for their position.
* **FR-4.2 (Search Filters):** Provide multi-variable filtering: *Age (< 23), Position, Strong Foot, Max Value, Diaspora Eligibility*.
* **FR-4.3 (PDF Export):** Allow users to export a 1-page automated scout summary report.

---

## 6. Non-Functional Requirements (NFRs)

* **Performance:** API query response time for similarity searches must be under **500ms**.
* **Data Freshness:** Scrapers to run on an automated cron job weekly during active football seasons.
* **Portability:** Containerized using Docker for deployment on cloud hosts (AWS/GCP/Render).

---

## 7. Recommended Tech Stack

| Layer | Technology Choice |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Data Ingestion** | `soccerdata`, `BeautifulSoup4`, `Pandas` |
| **ML / Analytics** | `scikit-learn` (StandardScaler, NearestNeighbors), `NumPy` |
| **Backend API** | `FastAPI` + `Pydantic` |
| **Frontend UI** | `Streamlit` or `Plotly Dash` |
| **Data Storage** | `SQLite` or `PostgreSQL` |

---

## 8. Development Roadmap (4-Week Sprints)

* **Sprint 1 (Data Engine):** Build scrapers for BPL squad profiles, FBref player stats, and diaspora listings.
* **Sprint 2 (Feature Engineering & ML):** Implement z-score metric normalization and build the k-NN vector similarity engine.
* **Sprint 3 (Backend & Eligibility Engine):** Construct the FastAPI routes and encode FIFA heritage eligibility logic.
* **Sprint 4 (UI & Portfolio Polish):** Design the Streamlit/React dashboard, implement interactive radar charts, containerize with Docker, and publish GitHub documentation.