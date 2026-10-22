"""FIFA eligibility endpoints — FR-2.1 / FR-2.2."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/players/{player_id}/eligibility")
async def eligibility(player_id: str) -> dict:
    """Evaluate national-team eligibility flags (FR-2.1 / FR-2.2).

    Stub: wires into backend.eligibility engine in Sprint 3.
    """
    raise NotImplementedError("Eligibility engine lands in Sprint 3 (backend).")