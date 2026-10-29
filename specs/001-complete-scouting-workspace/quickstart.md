# Quickstart

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m scripts.seed_data
.venv/bin/uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:
```sh
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open http://localhost:5173. Vite proxies /api to port 8000. For one-server production,
run `npm run build` in frontend and serve FastAPI; the UI is at http://localhost:8000.

Validation: `pytest`, `ruff check .`, then `npm run build`, `npm run lint`, `npm test`,
and `npm run test:e2e` in frontend. Browser tests require Playwright Chromium installed.
