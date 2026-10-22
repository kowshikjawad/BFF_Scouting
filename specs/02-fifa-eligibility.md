# Spec 02 — FIFA Eligibility & Heritage Rules Engine (Module 2)

## Scope
FR-2.1, FR-2.2.

## Rules (FIFA Statutes Art. 6 & 7)
A player is eligible via any of:
1. Born in the territory.
2. Parent or grandparent born in the territory (ancestry).
3. 5 continuous years of residency.

## Acceptance criteria
- [ ] `evaluate()` returns one of the FR-2.2 statuses:
  `ELIGIBLE & CLEARED`, `DOCUMENTATION REQUIRED`, `INELIGIBLE`.
- [ ] Ancestry needing proof yields `DOCUMENTATION REQUIRED`.
- [ ] Unit tests cover every qualifying branch.

## Files
- `backend/eligibility/engine.py`
- `tests/backend/test_eligibility.py`