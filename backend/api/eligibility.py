"""FIFA eligibility endpoints — FR-2.1 / FR-2.2."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

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

    residency_years: int = 0
    residency_years_after_18: int = 0
    residency_documented: bool = False

    has_senior_caps_other_association: bool = False
    has_youth_caps_other_association: bool = False
    article8_switch_approved: bool = False


class EligibilityResponse(BaseModel):
    """FR-2.2 status plus Art. 8 switch state."""

    player_id: str
    status: str
    article8_switch_required: bool
    article8_switch_approved: bool


@router.get("/players/{player_id}/eligibility", response_model=EligibilityResponse)
async def eligibility(player_id: str, facts: EligibilityFacts) -> EligibilityResponse:
    """Evaluate national-team eligibility flags (FR-2.1 / FR-2.2)."""
    result = evaluate(EligibilityInput(**facts.model_dump()))
    return EligibilityResponse(
        player_id=player_id,
        status=result.status.value,
        article8_switch_required=result.article8_switch_required,
        article8_switch_approved=result.article8_switch_approved,
    )
