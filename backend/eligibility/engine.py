"""FIFA eligibility rules engine.

Implements the Regulations Governing the Application of the FIFA Statutes:
Art. 6 (genuine link for a player who already holds the nationality
alongside another), Art. 7 (genuine link for a player newly acquiring the
nationality), and Art. 8 (one-time change of association for a player who
has already represented another association). Outputs the FR-2.2 status
vocabulary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# FIFA residency thresholds differ by path: Art. 6 (dual national) requires
# 2 continuous years; Art. 7 (newly acquired nationality) requires 5
# continuous years accrued after the player turns 18. Collapsing these into
# one threshold (as the earlier version of this engine did) silently
# misjudges any dual-national player evaluated between 2 and 4 years.
DUAL_NATIONAL_RESIDENCY_YEARS = 2
NEW_NATIONALITY_RESIDENCY_YEARS_AFTER_18 = 5


class Status(str, Enum):
    """FR-2.2 clearance statuses."""

    ELIGIBLE = "ELIGIBLE & CLEARED"
    DOCUMENTATION = "DOCUMENTATION REQUIRED"
    INELIGIBLE = "INELIGIBLE"


class NationalityPath(str, Enum):
    """Which FIFA provision governs this player's nationality claim."""

    DUAL_NATIONAL = "DUAL_NATIONAL"  # Art. 6: already holds the nationality
    NEW_NATIONALITY = "NEW_NATIONALITY"  # Art. 7: newly acquiring it


@dataclass
class EligibilityInput:
    """Raw heritage/residency/representation facts for a player (FR-2.1)."""

    nationality_path: NationalityPath = NationalityPath.DUAL_NATIONAL

    born_in_territory: bool = False
    born_in_territory_documented: bool = False

    parent_born_in_territory: bool = False
    parent_born_in_territory_documented: bool = False

    grandparent_born_in_territory: bool = False
    grandparent_born_in_territory_documented: bool = False

    residency_years: int = 0
    residency_years_after_18: int = 0
    residency_documented: bool = False

    # Art. 8: prior representation for another FIFA member association.
    has_senior_caps_other_association: bool = False
    has_youth_caps_other_association: bool = False
    article8_switch_approved: bool = False


@dataclass
class EligibilityResult:
    """Full evaluation outcome: overall status plus Art. 8 switch state."""

    status: Status
    article8_switch_required: bool
    article8_switch_approved: bool


def _residency_satisfied(facts: EligibilityInput) -> bool:
    if facts.nationality_path is NationalityPath.DUAL_NATIONAL:
        return facts.residency_years >= DUAL_NATIONAL_RESIDENCY_YEARS
    return facts.residency_years_after_18 >= NEW_NATIONALITY_RESIDENCY_YEARS_AFTER_18


def _genuine_link_facts(facts: EligibilityInput) -> list[tuple[bool, bool]]:
    """(satisfied, documented) pairs for every genuine-link option."""
    return [
        (facts.born_in_territory, facts.born_in_territory_documented),
        (facts.parent_born_in_territory, facts.parent_born_in_territory_documented),
        (facts.grandparent_born_in_territory, facts.grandparent_born_in_territory_documented),
        (_residency_satisfied(facts), facts.residency_documented),
    ]


def _heritage_status(facts: EligibilityInput) -> Status:
    links = _genuine_link_facts(facts)
    # A fully documented satisfied link clears heritage even if other,
    # undocumented claims are also present.
    if any(satisfied and documented for satisfied, documented in links):
        return Status.ELIGIBLE
    if any(satisfied for satisfied, _ in links):
        return Status.DOCUMENTATION
    return Status.INELIGIBLE


def evaluate(facts: EligibilityInput) -> EligibilityResult:
    """Apply FIFA Art. 6/7/8 rules and return a full clearance result."""
    heritage = _heritage_status(facts)
    article8_required = facts.has_senior_caps_other_association and not facts.article8_switch_approved

    if heritage is Status.ELIGIBLE and article8_required:
        # Heritage is fully documented and cleared, but a one-time
        # change-of-association request (Art. 8) is still outstanding --
        # never surface a bare ELIGIBLE & CLEARED in that case.
        status = Status.DOCUMENTATION
    else:
        status = heritage

    return EligibilityResult(
        status=status,
        article8_switch_required=article8_required,
        article8_switch_approved=facts.article8_switch_approved,
    )
