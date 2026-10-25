"""Tactical similarity endpoints — FR-3.2 / FR-3.3."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.db import get_session
from backend.similarity.pipeline import PlayerNotFoundError, rank_similar

router = APIRouter()


class SimilarityResult(BaseModel):
    """A single similar-player row (FR-3.3)."""

    player_id: str
    name: str | None
    similarity_score: float  # 0..100 percentage


@router.get("/players/{player_id}/similar", response_model=list[SimilarityResult])
async def similar_players(
    player_id: str, top_k: int = 5, session: Session = Depends(get_session)  # noqa: B008
) -> list[SimilarityResult]:
    """Return top-K similar players for a reference player (FR-3.2 / FR-3.3).

    An unknown `player_id` is a 404. A known player with no tactical
    metrics recorded, or an empty candidate pool, returns an empty list --
    a valid result, not an error (see design.md decision #6).

    NFR: must respond in < 500ms.
    """
    try:
        matches = rank_similar(session, player_id, top_k=top_k)
    except PlayerNotFoundError:
        raise HTTPException(status_code=404, detail=f"No player found with id {player_id!r}") from None

    return [SimilarityResult(player_id=m.player_id, name=m.name, similarity_score=m.similarity_score) for m in matches]
