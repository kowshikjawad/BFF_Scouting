"""Tests for FR-2.1 / FR-2.2 eligibility rules (Art. 6/7/8)."""

from __future__ import annotations

from backend.eligibility.engine import EligibilityInput, NationalityPath, Status, evaluate

# -- Art. 6: dual national (already holds Bangladeshi nationality) --


def test_born_in_territory_is_eligible():
    result = evaluate(EligibilityInput(born_in_territory=True, born_in_territory_documented=True))
    assert result.status is Status.ELIGIBLE


def test_parent_born_in_territory_is_eligible():
    result = evaluate(
        EligibilityInput(parent_born_in_territory=True, parent_born_in_territory_documented=True)
    )
    assert result.status is Status.ELIGIBLE


def test_grandparent_born_in_territory_is_eligible():
    result = evaluate(
        EligibilityInput(
            grandparent_born_in_territory=True, grandparent_born_in_territory_documented=True
        )
    )
    assert result.status is Status.ELIGIBLE


def test_two_year_dual_national_residency_is_eligible():
    """Art. 6 genuine-link residency threshold is 2 years, not 5."""
    result = evaluate(
        EligibilityInput(
            nationality_path=NationalityPath.DUAL_NATIONAL,
            residency_years=2,
            residency_documented=True,
        )
    )
    assert result.status is Status.ELIGIBLE


def test_one_year_dual_national_residency_is_not_eligible():
    result = evaluate(
        EligibilityInput(
            nationality_path=NationalityPath.DUAL_NATIONAL,
            residency_years=1,
            residency_documented=True,
        )
    )
    assert result.status is Status.INELIGIBLE


# -- Art. 7: newly acquired nationality --


def test_five_year_post_18_residency_is_eligible():
    result = evaluate(
        EligibilityInput(
            nationality_path=NationalityPath.NEW_NATIONALITY,
            residency_years=5,
            residency_years_after_18=5,
            residency_documented=True,
        )
    )
    assert result.status is Status.ELIGIBLE


def test_pre_18_residency_does_not_count_toward_new_nationality_threshold():
    result = evaluate(
        EligibilityInput(
            nationality_path=NationalityPath.NEW_NATIONALITY,
            residency_years=5,
            residency_years_after_18=3,
            residency_documented=True,
        )
    )
    assert result.status is Status.INELIGIBLE


def test_dual_national_threshold_does_not_apply_to_new_nationality_path():
    """2 years post-18 would clear the Art. 6 bar but not the Art. 7 one."""
    result = evaluate(
        EligibilityInput(
            nationality_path=NationalityPath.NEW_NATIONALITY,
            residency_years_after_18=2,
            residency_documented=True,
        )
    )
    assert result.status is Status.INELIGIBLE


# -- Documentation verification --


def test_unverified_ancestry_claim_requires_documentation():
    result = evaluate(
        EligibilityInput(parent_born_in_territory=True, parent_born_in_territory_documented=False)
    )
    assert result.status is Status.DOCUMENTATION


def test_documented_ancestry_claim_is_cleared():
    result = evaluate(
        EligibilityInput(parent_born_in_territory=True, parent_born_in_territory_documented=True)
    )
    assert result.status is Status.ELIGIBLE


# -- No qualifying facts --


def test_no_qualifying_facts_is_ineligible():
    result = evaluate(EligibilityInput())
    assert result.status is Status.INELIGIBLE


# -- Art. 8: one-time change of association --


def test_prior_senior_caps_without_approved_switch_blocks_clearance():
    result = evaluate(
        EligibilityInput(
            born_in_territory=True,
            born_in_territory_documented=True,
            has_senior_caps_other_association=True,
            article8_switch_approved=False,
        )
    )
    assert result.article8_switch_required is True
    assert result.status is not Status.ELIGIBLE


def test_prior_senior_caps_with_approved_switch_is_cleared():
    result = evaluate(
        EligibilityInput(
            born_in_territory=True,
            born_in_territory_documented=True,
            has_senior_caps_other_association=True,
            article8_switch_approved=True,
        )
    )
    assert result.article8_switch_required is False
    assert result.status is Status.ELIGIBLE


def test_prior_youth_caps_require_association_review():
    result = evaluate(
        EligibilityInput(
            born_in_territory=True,
            born_in_territory_documented=True,
            has_youth_caps_other_association=True,
        )
    )
    assert result.article8_switch_required is True
    assert result.status is Status.DOCUMENTATION
