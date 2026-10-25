"""Player persistence: ORM table + upsert/read operations (FR-1.2).

See openspec/specs/player-records/spec.md. Every column besides `id` is
nullable: a record can be created with only a partial field set (e.g. a
scraper that only has a tactical metric for a player not yet fully
profiled), and an unsupplied field must read back as absent, not a
fabricated default.
"""
from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from backend.models.db import Base
from ml.features.normalize import TACTICAL_METRICS


class PlayerORM(Base):
    """Player profile (FR-1.2) plus tactical per-90 metrics."""

    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[str | None] = mapped_column(String, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    strong_foot: Mapped[str | None] = mapped_column(String, nullable=True)
    league_band: Mapped[str | None] = mapped_column(String, nullable=True)
    contract_expiry: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_value_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    ancestry_eligibility: Mapped[str | None] = mapped_column(String, nullable=True)

    # Tactical per-90 metrics (FR-3.1 keys from ml.features.normalize).
    goals_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    key_passes_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    progressive_carries_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    tackles_won_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    aerial_duel_pct: Mapped[float | None] = mapped_column(Float, nullable=True)


VALID_PLAYER_FIELDS = {c.name for c in PlayerORM.__table__.columns if c.name != "id"}

assert set(TACTICAL_METRICS).issubset(VALID_PLAYER_FIELDS)


def upsert_player(session: Session, player_id: str, **fields: object) -> PlayerORM:
    """Create or update a player record, touching only the supplied fields.

    A field absent from `fields` is left exactly as it was (or absent, on
    create) -- it is never reset to a default.
    """
    unknown = set(fields) - VALID_PLAYER_FIELDS
    if unknown:
        raise ValueError(f"Unknown player field(s): {sorted(unknown)}")

    record = session.get(PlayerORM, player_id)
    if record is None:
        record = PlayerORM(id=player_id, **fields)
        session.add(record)
    else:
        for key, value in fields.items():
            setattr(record, key, value)
    session.flush()
    return record


def get_player(session: Session, player_id: str) -> dict[str, object] | None:
    """Return a player's stored fields, or None if no record exists.

    Any field never set (including every tactical metric by default)
    comes back as `None`, which is the valid "absent" state, not an error.
    """
    record = session.get(PlayerORM, player_id)
    if record is None:
        return None
    return {column.name: getattr(record, column.name) for column in PlayerORM.__table__.columns}
