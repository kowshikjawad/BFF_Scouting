# Spec 04 — Scouting Dashboard & UI (Module 4)

FR-4.1, FR-4.2 and FR-4.3 are delivered through the React/Vite workspace. Current acceptance
criteria and evidence are in [the Spec Kit completion specification](001-complete-scouting-workspace/spec.md)
and [verification record](001-complete-scouting-workspace/verification.md).

- Radar: percentile axes against same-league/position cohort median, with explicit missing-data states.
- Search: name, age, canonical position, foot, maximum value and recorded eligibility; URL state,
sort, table/cards and paging.
- Export: actual one-page PDF endpoint and browser download.
- Additional completion flows: browser-local shortlist, explained screening, retry and not-found states.

Historical OpenSpec behavior records remain in `openspec/`. The prior global-average radar
approximation is superseded by the cohort-median comparison above.
