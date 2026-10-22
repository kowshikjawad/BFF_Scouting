"""FIFA eligibility rules engine.

Implements FIFA Statutes Articles 6 & 7 (FR-2.1) and outputs the FR-2.2
status vocabulary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    """FR-2.2 clearance statuses."""

    ELIGIBLE = "ELIGIBLE & CLEARED"
    DOCUMENTATION = "DOCUMENTATION REQUIRED"
    INELIGIBLE = "INELIGIBLE"


@dataclass
class EligibilityInput:
    """Raw heritage/residency facts for a player (FR-2.1)."""

    born_in_territory: bool = False
    parent_born_in_territory: bool = False
    grandparent_born_in_territory: bool = False
    residency_years: int = 0


def evaluate(facts: EligibilityInput) -> Status:
    """Apply FIFA Art. 6/7 rules and return a clearance status.

    - Born in territory, or parent/grandparent born in territory, or
      >= 5 years residency -> ELIGIBLE (FR-2.1).
    - Otherwise INELIGIBLE.
    """
    # Stub implementation: full rule encoding (including ancestry doc
    # requirements) lands in Sprint 3.
    if (
        facts.born_in_territory
        or facts.parent_born_in_territory
        or facts.grandparent_born_in_territory
        or facts.residency_years >= 5
    ):
        return Status.ELIGIBLE
    return Status.INELIGIBLE