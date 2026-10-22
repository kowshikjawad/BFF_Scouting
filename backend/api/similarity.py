"""Tactical similarity endpoints — FR-3.2 / FR-3.3."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SimilarityResult(BaseModel):
    """A single similar-player row (FR-3.3)."""

    player_id: str
    name: str
    similarity_score: float  # 0..100 percentage


@router.get("/players/{player_id}/similar", response_model=list[SimilarityResult])
async def similar_players(player_id: str, top_k: int = 5) -> list[SimilarityResult]:
    """Return top-K similar players for a reference player (FR-3.2 / FR-3.3).

    NFR: must respond in < 500ms.
    """
    raise NotImplementedError("Similarity engine lands in Sprint 2 (ML).")