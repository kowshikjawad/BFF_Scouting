# Design

## Context

`backend/eligibility/engine.py` currently exposes a flat `EligibilityInput`
dataclass (four booleans/int, no path distinction, no documentation or
prior-caps facts) and an `evaluate()` function returning a bare `Status`
enum with only `ELIGIBLE`/`INELIGIBLE` ever produced. `backend/api/eligibility.py`
is an unimplemented stub. No other module depends on the current
`EligibilityInput` shape yet (the API layer never wired it up), so this is a
model redesign with no live callers to migrate. See `proposal.md` - Why for
the two underlying rule defects this corrects.

## Goals / Non-Goals

**Goals:**
- Represent Art. 6 vs Art. 7 as genuinely distinct evaluation paths with
  their own residency thresholds, rather than one combined check.
- Represent per-fact documentation state so `DOCUMENTATION REQUIRED` can
  actually be produced.
- Represent Art. 8 (prior representation / one-time switch) as an
  orthogonal fact set to heritage eligibility, and decide now how the two
  combine into what a caller sees.

**Non-Goals:**
- Submitting or tracking the actual FIFA Art. 8 switch request process
  (paperwork, FIFA Players' Status Committee workflow). This change only
  evaluates and reports eligibility state from facts already on record; it
  does not model the request lifecycle itself.
- Persistence of `EligibilityInput` facts (no DB wiring in this change —
  the engine remains a pure function over an input object, same as today;
  DB-backed player facts land with the Sprint 1 data-foundation work).
- Changing the three-value `EligibilityStatus` vocabulary in
  `backend/models/player.py` (`ELIGIBLE & CLEARED` / `DOCUMENTATION
  REQUIRED` / `INELIGIBLE`) — FR-2.2 fixes this at three values.

## Decisions

### 1. `EligibilityInput` gains an explicit nationality path
Add a `NationalityPath` enum (`DUAL_NATIONAL`, `NEW_NATIONALITY`) as a
required field, rather than inferring the path from which facts are set.
**Why**: the same residency fact (e.g., "3 years residency") means
something different depending on path (insufficient for Art. 6, further
from sufficient for Art. 7) — inferring the path from fact presence alone
is ambiguous and would hide the real distinction the proposal exists to
fix. **Alternative considered**: two separate input dataclasses
(`DualNationalInput`, `NewNationalityInput`). Rejected — `evaluate()` would
need two entry points and callers (the API layer, tests) would need to
know which to construct before they know the answer; a single input with a
path discriminant is simpler for callers and still lets `evaluate()`
branch internally.

### 2. Residency facts carry an explicit `residency_years_after_18` alongside `residency_years`
Rather than only tracking total residency years, the input tracks both
total years and years accrued after age 18, since Art. 7's 5-year
threshold is specifically post-18. **Why**: collapsing to one number would
force an implicit assumption (e.g., "assume all residency was post-18"),
silently mis-evaluating any player naturalized partly as a minor — exactly
the kind of silent error this change exists to remove.

### 3. Each genuine-link fact gets its own `documented: bool`, not one global flag
Ancestry facts (`born_in_territory`, `parent_born_in_territory`,
`grandparent_born_in_territory`) and the qualifying residency fact can each
independently be documented or not. **Why**: real cases (e.g., a player
with both a documented birth-registration gap and an undocumented
grandparent claim) need per-fact granularity; a single
`facts_documented: bool` would force treating a multi-fact case as
all-or-nothing. **Alternative considered**: a single document-verified
flag on the whole input. Rejected for the reason above.

### 4. Art. 8 state is a separate field on the result, not a fourth status value
`evaluate()` returns a small result object: the existing 3-value `Status`
for heritage eligibility, plus `article8_switch_required: bool` and
`article8_switch_approved: bool` describing prior-representation state
independently. The heritage `Status` is only reported as `ELIGIBLE &
CLEARED` when heritage is clear **and** (no prior senior caps elsewhere,
or the switch is approved) — otherwise it stays whatever the heritage-only
evaluation would say, with `article8_switch_required=True` carried
alongside. **Why**: FR-2.2 fixes the status vocabulary at exactly three
values (`ELIGIBLE & CLEARED` / `DOCUMENTATION REQUIRED` / `INELIGIBLE`);
adding a fourth ("SWITCH PENDING") would be a second breaking change to
that vocabulary beyond what this proposal already scopes, and would ripple
into the frontend's planned status-indicator UI (Sprint 4, FR-4.1) before
that UI exists to absorb it. Carrying Art. 8 as a side field lets today's
three-value contract hold while still making the pending-switch case
impossible to silently miss (a caller reading only `status` without the
new field will see a non-`ELIGIBLE & CLEARED` outcome in exactly the cases
that matter — see spec scenario "Heritage-eligible but pending association
switch").
**Alternative considered**: add a fourth status value. Deferred — if the
frontend work in Sprint 4 later shows a 4th UI state is genuinely needed,
that's a separate, explicit proposal against the then-existing frontend
spec, not a silent addition here.

### 5. `backend/api/eligibility.py` takes facts via request body, not query params alone
The endpoint accepts a JSON body matching (a Pydantic mirror of)
`EligibilityInput`'s fields, since the fact set is now too large for
clean query-string encoding. **Why**: this mirrors how `similarity.py`
already separates path params (the player id) from richer request data,
and keeps the endpoint testable with simple JSON fixtures. **Alternative
considered**: load facts from a (not-yet-existing) persisted player
record by id alone. Rejected for this change — no DB layer exists yet
(Non-Goals above); wiring eligibility lookups to stored facts is Sprint 3
DB-integration work, tracked separately.

## Risks / Trade-offs

- **[Risk]** The `EligibilityInput` redesign is a breaking Python-level API
  change (already called out as BREAKING in proposal.md), but since
  `backend/api/eligibility.py` was never implemented, no real caller
  exists yet → **Mitigation**: none needed beyond updating the one
  existing test file in this same change.
- **[Risk]** FIFA's actual commentary text was not fetched in full (only
  secondary summaries and the regulations' general structure were
  reviewed) → **Mitigation**: thresholds and article numbers used here
  (2-year / Art. 6, 5-year-post-18 / Art. 7, one-time switch / Art. 8) are
  corroborated by multiple independent secondary sources researched for
  this change; flagged as a residual accuracy risk worth a follow-up legal
  review before this logic is relied on for a real federation decision,
  not just a portfolio/demo tool.
- **[Risk]** Modeling Art. 8 as "any prior senior cap blocks CLEARED status
  until an approved switch is on record" is a simplification of a process
  that in practice involves FIFA discretion and historical exceptions
  (e.g., the 2016 Kosovo cases) → **Mitigation**: explicitly scoped as a
  Non-Goal to model the request process itself; the engine only reports
  the fact-based signal "a switch is required/outstanding," which is the
  correct, honest scope for an automated tool advising a scout, not a
  binding legal determination.

## Migration Plan

No live data or deployed callers exist for the current shape (the API
stub never constructed `EligibilityInput`), so this ships directly:
update `engine.py`, update the one test file, wire the API stub. No
rollback concerns beyond normal version control.
