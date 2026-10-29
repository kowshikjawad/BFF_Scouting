"""FIFA eligibility endpoints — FR-2.1 / FR-2.2."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field, model_validator

from backend.eligibility.engine import EligibilityInput, NationalityPath, evaluate

router = APIRouter()


class EligibilityFacts(BaseModel):
    """Request body mirroring `EligibilityInput` (FR-2.1 facts)."""

    nationality_path: NationalityPath = NationalityPath.DUAL_NATIONAL

    born_in_territory: bool = False
    born_in_territory_documented: bool = False

    parent_born_in_territory: bool = False
    parent_born_in_territory_documented: bool = False

    grandparent_born_in_territory: bool = False
    grandparent_born_in_territory_documented: bool = False

    residency_years: int = Field(default=0, ge=0, le=100)
    residency_years_after_18: int = Field(default=0, ge=0, le=100)
    residency_documented: bool = False

    has_senior_caps_other_association: bool = False
    has_youth_caps_other_association: bool = False
    article8_switch_approved: bool = False

    @model_validator(mode="after")
    def consistent_residency(self):
        if self.residency_years_after_18 > self.residency_years:
            raise ValueError("Residency after age 18 cannot exceed total residency")
        return self


class EligibilityResponse(BaseModel):
    """FR-2.2 status plus Art. 8 switch state."""

    player_id: str
    status: str
    article8_switch_required: bool
    article8_switch_approved: bool
    reasons: list[str]
    review_required: bool
    ruleset: str = "Preliminary legacy rules screening; association confirmation required"


@router.post("/players/{player_id}/eligibility", response_model=EligibilityResponse)
async def eligibility(player_id: str, facts: EligibilityFacts) -> EligibilityResponse:
    """Evaluate national-team eligibility flags (FR-2.1 / FR-2.2).

    POST, not GET: a browser's `fetch()` cannot send a body on a GET/HEAD
    request (the Fetch spec throws `TypeError`), and this is a stateless
    evaluation over supplied facts rather than a fetch-by-id, so POST is
    also the more correct verb.
    """
    result = evaluate(EligibilityInput(**facts.model_dump()))
    reasons = []
    for key, label in (
        ("born_in_territory", "Birth in Bangladesh"),
        ("parent_born_in_territory", "Parent born in Bangladesh"),
        ("grandparent_born_in_territory", "Grandparent born in Bangladesh"),
    ):
        if getattr(facts, key):
            documented = getattr(facts, f"{key}_documented")
            reasons.append(f"{label}: {'documented' if documented else 'evidence still required'}.")
    if facts.residency_years:
        reasons.append(
            f"Residency supplied: {facts.residency_years} years total, "
            f"{facts.residency_years_after_18} after age 18. "
            "Residency pathways require association verification."
        )
    if result.article8_switch_required:
        reasons.append("Prior representation requires a change-of-association review.")
    if not reasons:
        reasons.append("No qualifying ancestry or residency link was supplied.")
    reasons.append("This screening does not establish nationality or official FIFA clearance.")
    return EligibilityResponse(
        player_id=player_id,
        status=result.status.value,
        article8_switch_required=result.article8_switch_required,
        article8_switch_approved=result.article8_switch_approved,
        reasons=reasons,
        review_required=True,
    )
