# Proposal

## Why

`backend/eligibility/engine.py` currently collapses three legally distinct FIFA
provisions (Statutes/Regulations Art. 6, Art. 7, Art. 8) into a single
undifferentiated OR condition, and only ever returns `ELIGIBLE` or
`INELIGIBLE` — never the `DOCUMENTATION REQUIRED` status the PRD (FR-2.2)
requires. Two concrete defects follow from this:

1. **Wrong residency threshold.** FIFA applies **2 years** continuous
   residency as a genuine-link option for a player who already holds
   Bangladeshi nationality alongside another (Art. 6.1), but **5 years**
   continuous residency *after turning 18* when the player is newly
   acquiring Bangladeshi nationality (Art. 7). The current code applies a
   flat "5 years" to both, which would wrongly reject an already-dual-national
   player at 2–4 years residency who is in fact eligible.
2. **Missing Art. 8 (one-time change of association) check entirely.**
   Several of the actual players this platform exists to evaluate (e.g.
   Hamza Choudhury, who held England U21 caps before switching) are
   heritage-eligible under Art. 6/7 *and* separately require a one-time
   change-of-association clearance because they already represented another
   association. The engine currently has no way to represent "heritage OK,
   but a switch request is still required" — it would wrongly report
   `ELIGIBLE & CLEARED` for a player who cannot actually play until FIFA
   approves the switch.

This blocks the National Team Scout persona's core need (PRD §3): a scout
needs to know not just "is there a heritage link" but "can this specific
player be fielded right now." Fixing it now, before Sprint 3 wires this
engine into the `/api/v1/players/{id}/eligibility` endpoint, avoids shipping
an API contract built on the wrong rule.

## What Changes

- Split the single flat eligibility check into three distinct rule paths:
  Art. 6 (dual national, 2-year residency option), Art. 7 (new nationality,
  5-year post-18 residency option), and Art. 8 (one-time change of
  association, for players with prior caps elsewhere).
- Add a documentation-verification dimension: a claimed genuine-link fact
  (ancestry or residency) that lacks supporting documentation yields
  `DOCUMENTATION REQUIRED` instead of `ELIGIBLE & CLEARED`.
- Add prior-representation tracking (senior "A" caps and youth caps for
  another association) so Art. 8 clearance is evaluated and surfaced
  separately from heritage eligibility, instead of being ignored.
- **BREAKING**: `EligibilityInput`'s shape changes (new required fields for
  nationality path, documentation flags, and prior-caps facts); the old
  flat `residency_years >= 5` single-threshold contract is removed.
- **BREAKING**: `evaluate()`'s return type changes from a bare `Status` to a
  richer result that also carries the Art. 8 clearance state, since a
  player can now be heritage-eligible but still pending a switch request.
- Wire `backend/api/eligibility.py`'s `/players/{player_id}/eligibility`
  endpoint to call the corrected engine instead of raising
  `NotImplementedError`.
- Update `tests/backend/test_eligibility.py`: the existing
  `test_five_year_residency_is_eligible` test encodes the wrong threshold
  for the dual-national path and is corrected to 2 years; new tests cover
  the 5-year/post-18 new-nationality path, the documentation-required
  branch, and the Art. 8 prior-caps branch.

## Capabilities

### New Capabilities
- `fifa-eligibility`: rule-based evaluation of a player's eligibility to
  represent the Bangladesh national team, covering Art. 6 (dual national
  genuine link), Art. 7 (new nationality genuine link), Art. 8 (one-time
  association switch for players with prior representation elsewhere), and
  the documentation-verification status required to move a claimed
  genuine-link fact from "claimed" to "cleared."

### Modified Capabilities
(none — `openspec list --specs` shows no existing specs; this is the first
capability spec for the eligibility engine, replacing the informal
`specs/02-fifa-eligibility.md` note, which only documented the old,
incorrect flat rule.)

## Impact

- `backend/eligibility/engine.py` — core rule rewrite.
- `backend/models/player.py` — `EligibilityStatus` vocabulary stays the same
  three values, but the per-player facts feeding it grow.
- `backend/api/eligibility.py` — stub replaced with a real call into the
  engine.
- `tests/backend/test_eligibility.py` — existing tests corrected, new
  branches covered.
- No database, scraper, or frontend dependency — this change is backend-only
  and self-contained.
