# Tasks

## 1. Redesign the input data model

- [x] 1.1 In `backend/eligibility/engine.py`, add a `NationalityPath` enum
      (`DUAL_NATIONAL`, `NEW_NATIONALITY`) and verify it imports cleanly
      (`python -c "from backend.eligibility.engine import NationalityPath"`)
- [x] 1.2 Rewrite `EligibilityInput` to carry: `nationality_path:
      NationalityPath`; per-fact genuine-link fields
      (`born_in_territory`, `parent_born_in_territory`,
      `grandparent_born_in_territory`) each paired with a `documented: bool`
      sibling field; `residency_years: int`, `residency_years_after_18:
      int`, and `residency_documented: bool`; prior-representation fields
      (`has_senior_caps_other_association: bool`,
      `has_youth_caps_other_association: bool`,
      `article8_switch_approved: bool`). Verify with a quick
      instantiation smoke test in a scratch Python shell.
- [x] 1.3 Add an `EligibilityResult` dataclass with `status: Status`,
      `article8_switch_required: bool`, `article8_switch_approved: bool`,
      and verify it's importable alongside the existing `Status` enum.

## 2. Rewrite the rule engine

- [x] 2.1 Implement the Art. 6 (dual-national) genuine-link check per
      spec scenarios "Eligible via 2 years of dual-national residency" /
      "Not yet eligible via dual-national residency" — verify via a
      throwaway script exercising both branches before wiring into tests.
- [x] 2.2 Implement the Art. 7 (new-nationality) genuine-link check per
      spec scenarios "Eligible via 5 years of post-18 residency" /
      "Pre-18 residency does not count" / "Dual-national residency
      threshold does not apply to new-nationality path".
- [x] 2.3 Implement the documentation-verification branch per spec
      scenarios "Unverified ancestry claim" / "Verified ancestry claim" —
      any satisfied genuine-link fact that is undocumented yields
      `DOCUMENTATION REQUIRED` rather than `ELIGIBLE & CLEARED`.
- [x] 2.4 Implement the "no qualifying facts" branch per spec scenario
      "No qualifying facts" — yields `INELIGIBLE`.
- [x] 2.5 Implement the Art. 8 prior-representation check per spec
      scenarios "Heritage-eligible but pending association switch" /
      "Heritage-eligible with an approved association switch" / "Prior
      youth-only caps do not trigger Art. 8" — senior caps elsewhere
      without an approved switch sets `article8_switch_required=True` and
      suppresses `ELIGIBLE & CLEARED` even when heritage is otherwise
      clear and documented.
- [x] 2.6 Wire 2.1–2.5 into a single `evaluate(facts: EligibilityInput) ->
      EligibilityResult` function, replacing the old flat implementation.

## 3. Wire the API endpoint

- [x] 3.1 In `backend/api/eligibility.py`, add a Pydantic request model
      mirroring `EligibilityInput`'s fields for the request body.
- [x] 3.2 Replace the `raise NotImplementedError(...)` body of
      `/players/{player_id}/eligibility` with a call into
      `backend.eligibility.engine.evaluate()`, returning the status and
      Art. 8 fields as JSON. Verify with a manual `curl`/httpx request
      against a running `uvicorn` instance returning 200 with the expected
      shape instead of a 500.

## 4. Update and extend tests

- [x] 4.1 Update `tests/backend/test_eligibility.py`: correct
      `test_five_year_residency_is_eligible` to assert the Art. 6
      threshold is 2 years (not 5), and update the other existing tests
      to construct the new `EligibilityInput` shape. Verify with
      `pytest tests/backend/test_eligibility.py -v`.
- [x] 4.2 Add a test for the Art. 7 5-year-post-18 threshold (both the
      eligible and the "pre-18 years don't count" cases). Verify it fails
      against the old flat logic and passes against the rewritten engine.
- [x] 4.3 Add a test for the documentation-required branch (satisfied but
      undocumented fact). Verify it asserts `Status.DOCUMENTATION_REQUIRED`
      is actually reachable (closing the gap called out in proposal.md).
- [x] 4.4 Add a test for the Art. 8 branch: heritage-eligible + prior
      senior caps + no approved switch → `article8_switch_required is
      True` and status is not a bare `ELIGIBLE & CLEARED`; and the
      approved-switch counterpart. Verify with
      `pytest tests/backend/test_eligibility.py -v` showing all branches
      green.
- [x] 4.5 Run the full suite (`pytest -v`) and verify no regressions in
      `tests/test_smoke.py` or `tests/ml/test_similarity.py` from the
      import/shape changes.

## Workflow follow-up

- Run `openspec validate --change "fix-fifa-eligibility-rules" --strict`
  before archiving.
- Archive the change (`/opsx:archive`) once implementation and tests are
  complete, which syncs this delta into `openspec/specs/fifa-eligibility/spec.md`
  as the permanent capability spec.
