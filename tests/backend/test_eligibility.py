"""Tests for FR-2.1 / FR-2.2 eligibility rules."""
from __future__ import annotations

from backend.eligibility.engine import EligibilityInput, Status, evaluate


def test_born_in_territory_is_eligible():
    assert evaluate(EligibilityInput(born_in_territory=True)) is Status.ELIGIBLE


def test_parent_born_in_territory_is_eligible():
    assert evaluate(EligibilityInput(parent_born_in_territory=True)) is Status.ELIGIBLE


def test_grandparent_born_in_territory_is_eligible():
    assert evaluate(EligibilityInput(grandparent_born_in_territory=True)) is Status.ELIGIBLE


def test_five_year_residency_is_eligible():
    assert evaluate(EligibilityInput(residency_years=5)) is Status.ELIGIBLE


def test_no_qualifying_facts_is_ineligible():
    assert evaluate(EligibilityInput()) is Status.INELIGIBLE