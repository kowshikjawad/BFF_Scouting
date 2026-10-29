# ShonarTalent AI frontend

React, TypeScript, Vite and Tailwind. Node.js 24+ is recommended.

```sh
npm ci
npm run dev
```

The backend must run on port 8000. Vite proxies `/api` locally. Production defaults to same-origin
`/api/v1`; use `VITE_API_BASE_URL` only for a deliberate separate API deployment.

```sh
npm run lint
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

Build output is served by FastAPI from `frontend/dist`. Browser tests use port 8015 and an isolated
seeded database. See the root README and `DESIGN.md` for product, coverage and asset details.
