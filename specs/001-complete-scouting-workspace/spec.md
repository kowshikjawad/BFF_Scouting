# Feature Specification: Complete scouting workspace

**Created**: 2026-10-28
**Status**: Accepted for implementation
**Input**: Complete the existing project, improve UI/UX with a minimal standard design, use
open-source assets, and enhance specifications with Spec Kit before implementation.

## User Scenarios & Testing

### User Story 1 - Discover players (Priority: P1)
A scout searches the database by name, position, age, preferred foot, value and assessment status,
then opens a profile without losing the search.

**Independent Test**: Search a known name, combine filters, clear them, change view and page,
open a result, then return to the same query.

**Acceptance Scenarios**:
1. Given stored players, searching a case-insensitive name fragment returns only matches.
2. Given mixed position vocabulary, a canonical position filter matches full names and secondary roles.
3. Given an active search, filters and sort survive reload and browser Back via the URL.
4. Given no results or an unavailable API, the page shows an honest state with reset or retry.
5. Given desktop or 360px mobile, all controls remain usable and the page does not overflow.

### User Story 2 - Inspect and export (Priority: P1)
A scout views the recorded profile, understands data coverage and tactical comparison, retrieves
similar players, and downloads a one-page report.

**Independent Test**: Open players with and without tactical data, inspect missing values,
request similarity and download a PDF.

**Acceptance Scenarios**:
1. Stored tactical metrics reach the profile unchanged; missing values remain unknown.
2. Radar charts use comparable normalized axes against the same league and position cohort's
median. Incomplete metrics or absent peers show an explanation instead of fabricated zeros.
3. Unknown player IDs produce a not-found state; server failures produce retryable errors.
4. PDF download returns an actual one-page PDF with player facts, assessment, tactical values,
generation date and data limitations. Unknown IDs return 404.

### User Story 3 - Keep a scouting shortlist (Priority: P2)
A scout saves players from the directory or profile and returns to a shortlist on this browser.

**Independent Test**: Save, reload, visit shortlist, remove, and confirm state survives navigation.

**Acceptance Scenarios**:
1. Saving toggles a clearly named button and navigation count.
2. Shortlist IDs persist locally, malformed/unavailable storage does not crash the application,
and unavailable saved IDs are identified with a remove action.
3. Empty shortlist explains how to add players and links to discovery.

### User Story 4 - Screen eligibility facts (Priority: P1)
A scout enters ancestry, residency and prior-representation facts and receives an explained
preliminary screening result.

**Independent Test**: Evaluate documented ancestry, missing documentation, prior caps and
invalid residency values; edit a fact after evaluating.

**Acceptance Scenarios**:
1. Facts are grouped and labelled; numeric years reject negative, non-integer and inconsistent values.
2. Results show reasons, evidence to collect, and whether association review is still needed.
3. Editing any input invalidates the old assessment; failed requests can be retried.
4. Existing legacy rules remain explicitly labelled as preliminary, not a current FIFA ruling.
Prior youth representation must not produce unqualified automatic clearance.

### Edge Cases
Unknown player ID, absent ages/values/positions, partial records, API failures, fast navigation,
empty database, corrupted local storage, missing tactical cohorts, long player names and mobile.

## Requirements

- **FR-001**: Search by name and combined filters; deterministic sorting and paged display.
- **FR-002**: URL-persisted search, card/table views, clear/reset and recoverable states.
- **FR-003**: Truthful metrics, cohort median comparison and similarity availability explanation.
- **FR-004**: Download a one-page scout PDF, safe filenames and missing-player handling.
- **FR-005**: Browser-local shortlist with accessible toggles and persistence recovery.
- **FR-006**: Validated, explained preliminary eligibility screening with stale-result protection.
- **FR-007**: Responsive, keyboard-accessible UI with licensed local assets and consistent tokens.
- **FR-008**: Same-origin production UI/API, fresh-database initialization, documented seed/refresh,
container configuration, and frontend plus backend CI.
- **FR-009**: Preserve partial data during ingestion and recover failed source transactions.

### Key Entities
Player: stored profile and nullable tactical metrics. Search: query, filters, sort and page.
Shortlist: local player IDs. Assessment: submitted facts, screening status, reasons and limitations.
Report: downloadable snapshot of recorded player data.

## Success Criteria
- All 4 user stories complete in automated/API and browser checks without dead controls.
- Search and profile work at 360px and 1440px with no document-level horizontal overflow.
- No fabricated player photos, statistical values or live-update claims.
- Every PDF test report is one page with readable, non-overlapping content.
- Existing regression suite stays green; new contract and workflow regressions pass.
- Similarity fixture responds within the existing 500ms requirement.

## Assumptions
- Existing PRD scope defines completion; no login, paid feeds or collaborative server storage added.
- Real 113-player local dataset is preserved. Fresh installs can load the maintained seed offline.
- Open-source Lucide icons and self-hosted Inter/Space Grotesk fonts satisfy asset needs; no
unnecessary stock photography in a scouting data workspace.
- Current tactical source coverage is zero; completeness means truthful working pipelines and states,
not invented metrics. Current legal-rule certification requires association review and is not claimed.
- New Spec Kit specification governs this delivery; historical OpenSpec records remain intact.
