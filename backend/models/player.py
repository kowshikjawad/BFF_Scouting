"""Player schema — FR-1.2 attribute set."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# FR-2.2 status vocabulary
EligibilityStatus = Literal[
    "ELIGIBLE & CLEARED", "DOCUMENTATION REQUIRED", "INELIGIBLE"
]


class Player(BaseModel):
    """Structured profile of a domestic or diaspora player (FR-1.2)."""

    id: str
    name: str
    # Nullable: domestic-league source data doesn't always carry a
    # parseable date of birth for every squad member (verified during
    # scraper implementation -- see player-data-ingestion spec).
    age: int | None = None
    position: str  # primary position
    height_cm: float | None = None
    strong_foot: Literal["Left", "Right", "Both"] | None = None
    league_band: str  # e.g., BPL, Serie A, EFL Championship
    contract_expiry: str | None = None
    estimated_value_eur: float | None = None
    ancestry_eligibility: EligibilityStatus | None = Field(
        default=None, description="FR-2.2 status indicator"
    )