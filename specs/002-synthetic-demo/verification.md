# Verification

Date: 2026-10-28.

- Generated 160 deterministic profiles across 40 league/position groups, four profiles per group.
- Seeded the running main database. Compared every original real row before/after: 113 records
with all fields identical (SHA-256 ef022a499e53a9af665af4b6ba5d23e6ba10543d8db22375ffa6e46ce1e82afa).
- API/back-end suite: 102 passed, one external FBref test skipped. New regressions check generation,
idempotence, source scoping/provenance, combined filters, all 160 similarity queries, real-data
isolation and prominently labeled one-page PDF contents.
- Frontend logic: four passed, including preventing cross-source radar cohorts.
- TypeScript/production build, strict lint, formatting and backend lint pass.
- Visual review of actual local demo profile: complete raw metrics, cohort radar and five ranked
results. Mobile profile has zero document overflow at 360px. Screenshot: docs/screenshots/synthetic-profile.png.
- Generated a demo report, confirmed one page with pypdf, rendered with Poppler and visually
inspected: no overlap/clipping; fictional-data notice and values are readable.

Browser workflows: **12 passed**, including the complete synthetic discovery → chart → five
similarity results → shortlist → PDF flow, source switching, all three eligibility examples,
mobile rendering and the previous nine real-data/recovery checks.

Convergence: all seven acceptance criteria and four implementation tasks are satisfied within
the documented demo scope.

Limits: all demo data is fictional, based on illustrative role templates and seeded variation.
These are not empirically validated performance distributions or predictions. Real source coverage
and the legacy eligibility-screening limits remain unchanged.
