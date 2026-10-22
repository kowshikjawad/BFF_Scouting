"""Player CRUD + search filters — FR-4.2."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from backend.models.player import Player

router = APIRouter()


@router.get("/players", response_model=list[Player])
async def list_players(
    # FR-4.2 filter vocabulary
    max_age: int | None = Query(default=None, lt=40, description="Age filter (< 23)"),
    position: str | None = None,
    strong_foot: Literal["Left", "Right", "Both"] | None = None,
    max_value_eur: float | None = None,
    diaspora_eligible: bool | None = None,
) -> list[Player]:
    """Search players by multi-variable filters (FR-4.2).

    Stub: integration with the data store lands in Sprint 3.
    """
    raise NotImplementedError("Player search lands in Sprint 3 (backend).")