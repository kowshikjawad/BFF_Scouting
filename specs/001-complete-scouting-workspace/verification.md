# Verification and convergence

**Date**: 2026-10-28
**Scope**: Spec Kit completion specification, 4 user stories, FR-001 through FR-009.
**Verdict**: Converged for the documented local scouting-workspace scope.

## Automated evidence

- Backend: **96 passed, 1 skipped** (external FBref integration).
- Backend lint: passed (`ruff check .`).
- Frontend TypeScript + production build: passed; routes split into separate chunks, no bundle warning.
- Frontend lint: passed with warnings denied.
- Frontend formatting check: passed.
- Frontend logic: **3 passed** (corrupt storage, missing metrics, cohort/percentile semantics).
- Browser: **9 passed**, Chromium, isolated server on port 8015 with offline roster seed.
- Git diff whitespace check: passed.

Browser checks cover name search → profile → shortlist → reload → PDF download; URL filter/sort/view
restoration; empty-search reset; eligibility explanation and stale-result invalidation; API error
retry; distinct not-found handling; pagination and reload; 360px navigation/no document overflow;
complete-cohort radar rendering; and unavailable-storage session fallback.

Backend regressions cover metric/null parity, partial records, literal case-insensitive search,
secondary/full-name positions, sorting/status, input bounds, one-page PDF/readable contents/404,
markup and filename escaping, youth-representation review, production SPA/API/asset routing,
rollback after actual database write failure, and preserving tactical data through roster refresh.
Existing similarity fixture stays within the 500ms requirement.

## Visual evidence

Reviewed final desktop directory (1440px), player profile and mobile directory (360px). Final desktop
capture: `docs/screenshots/discovery.png`. No overlap or document overflow observed; mobile uses
cards and a collapsible navigation menu. Focus and reduced-motion styles are implemented.

Generated an actual Hamza Choudhury report, checked one page with pypdf, rendered with Poppler and
visually reviewed after the final report change. Header, profile facts, eligibility, metrics, notes
and footer are aligned and readable; no overlap/clipping observed. PDF source notes remain complete.

## Traceability

| Requirement | Delivery | Evidence |
| --- | --- | --- |
| FR-001/002 | API search/positions/sort; URL state; cards/table/paging/recovery | API + browser tests |
| FR-003 | Nullable metrics; same-league/position percentile radar; similarity states | API + logic + browser |
| FR-004 | ReportLab one-page endpoint and actual download | PDF parser, visual QA, browser |
| FR-005 | Local ID shortlist, persistence notice and recovery | Browser + logic |
| FR-006 | Bounded facts, explained screening, prior-youth review and stale reset | API + browser |
| FR-007 | Light responsive system, semantic labels/focus, local licensed assets | Visual + mobile/browser |
| FR-008 | Offline seed, fresh-db startup, same-origin app, Docker and CI configuration | Isolated browser startup + routing tests |
| FR-009 | Supplied-fields-only roster writes and source rollback | Scraper regression tests |

## Known limits and environment constraints

- Docker files and Compose configuration are implemented. Image build/start was **not runtime-tested**:
Docker's daemon is unavailable on this host. This is an environment verification limit.
- Live third-party source refresh was not repeated or used to fabricate data. The preserved main
SQLite database still has 113 real records and no tactical metrics. Fresh clones load six roster
profiles; browser fixtures that demonstrate chart coverage remain test-only.
- Eligibility is an explicitly identified simplified legacy screen, with current official guidance
linked. It is not a full current FIFA adjudication model or proof of nationality/clearance.
- Tests emit a dependency deprecation warning and expected SQLAlchemy warnings for the deliberately
invalid write used to prove rollback recovery. No test failure is hidden.
- Weekly refresh is supported by the command and documented deployment cron example. No host
scheduler was installed, and no public deployment or authentication was added.

## Convergence assessment

All 9 completion requirements, 4 story acceptance groups, 7 plan steps and 5 constitution principles
were reconciled with the implemented code and evidence. No actionable implementation gaps remain
within this specification. The documented source, official-rule and Docker-runtime limitations
remain explicit and must not be described as verified production integrations.
