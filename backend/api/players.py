"""Player search + detail — FR-4.2."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.models.db import get_session
from backend.models.player import Player
from backend.models.player_records import get_player, list_players
from backend.models.provenance import Dataset

router = APIRouter()


@router.get("/players", response_model=list[Player])
async def search_players(
    # FR-4.2 filter vocabulary
    max_age: int | None = Query(default=None, ge=0, le=100),
    position: str | None = Query(default=None, max_length=50),
    strong_foot: Literal["Left", "Right", "Both"] | None = None,
    max_value_eur: float | None = Query(default=None, ge=0, allow_inf_nan=False),
    diaspora_eligible: bool | None = None,
    q: str | None = Query(default=None, max_length=100),
    eligibility_status: Literal[
        "ELIGIBLE & CLEARED", "DOCUMENTATION REQUIRED", "INELIGIBLE", "NOT_ASSESSED"
    ]
    | None = None,
    sort: Literal["name", "age_asc", "value_desc"] = "name",
    dataset: Dataset = "real",
    session: Session = Depends(get_session),  # noqa: B008 -- FastAPI's documented DI pattern
) -> list[Player]:
    """Search players by multi-variable filters (FR-4.2)."""
    records = list_players(
        session,
        max_age=max_age,
        position=position,
        strong_foot=strong_foot,
        max_value_eur=max_value_eur,
        diaspora_eligible=diaspora_eligible,
        q=q,
        eligibility_status=eligibility_status,
        sort=sort,
        dataset=dataset,
    )
    return [
        Player(**{k: v for k, v in record.items() if k in Player.model_fields})
        for record in records
    ]


@router.get("/players/{player_id}", response_model=Player)
async def player_detail(player_id: str, session: Session = Depends(get_session)) -> Player:  # noqa: B008
    """Fetch a single player's stored record by id."""
    record = get_player(session, player_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No player found with id {player_id!r}")
    return Player(**{k: v for k, v in record.items() if k in Player.model_fields})


@router.get("/players/{player_id}/report.pdf", response_class=Response)
def player_report(player_id: str, session: Session = Depends(get_session)) -> Response:  # noqa: B008
    from backend.reports.player import render_report, report_filename

    record = get_player(session, player_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return Response(
        render_report(record),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report_filename(player_id)}"'},
    )
