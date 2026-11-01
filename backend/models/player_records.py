"""Player persistence: ORM table + upsert/read operations (FR-1.2).

See openspec/specs/player-records/spec.md. Every column besides `id` is
nullable: a record can be created with only a partial field set (e.g. a
scraper that only has a tactical metric for a player not yet fully
profiled), and an unsupplied field must read back as absent, not a
fabricated default.
"""

from __future__ import annotations

from sqlalchemy import Float, Integer, String, func, or_, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from backend.models.db import Base
from backend.models.provenance import SYNTHETIC_PREFIX, Dataset
from ml.features.normalize import REFERENCE_METRICS, TACTICAL_METRICS


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

    # Tactical per-90 metrics (FR-3.1 keys from ml.features.normalize) -- the
    # radar/similarity comparison vector.
    goals_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    assists_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    key_passes_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    progressive_carries_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    dribbles_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    tackles_won_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    interceptions_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    aerial_duel_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Reference stats (not part of the radar/similarity vector).
    shots_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    shot_accuracy_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    pass_completion_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    clearances_per_90: Mapped[float | None] = mapped_column(Float, nullable=True)
    minutes_played: Mapped[int | None] = mapped_column(Integer, nullable=True)
    appearances: Mapped[int | None] = mapped_column(Integer, nullable=True)


VALID_PLAYER_FIELDS = {c.name for c in PlayerORM.__table__.columns if c.name != "id"}

assert set(TACTICAL_METRICS).issubset(VALID_PLAYER_FIELDS)
assert set(REFERENCE_METRICS).issubset(VALID_PLAYER_FIELDS)


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


_DIASPORA_ELIGIBLE_STATUS = "ELIGIBLE & CLEARED"  # backend.eligibility.engine.Status.ELIGIBLE.value


def list_players(
    session: Session,
    *,
    max_age: int | None = None,
    position: str | None = None,
    strong_foot: str | None = None,
    max_value_eur: float | None = None,
    diaspora_eligible: bool | None = None,
    q: str | None = None,
    eligibility_status: str | None = None,
    sort: str = "name",
    dataset: Dataset = "real",
) -> list[dict[str, object]]:
    """List stored players matching every supplied filter (FR-4.2).

    An omitted filter does not constrain the result. `max_age` excludes
    players with no recorded age -- an absent age can't be known to
    satisfy a maximum (see design.md decision #3). `diaspora_eligible` is
    derived from `ancestry_eligibility` since there is no separate stored
    boolean (design.md decision #2).
    """
    query = select(PlayerORM)
    generated = PlayerORM.id.startswith(SYNTHETIC_PREFIX, autoescape=True)
    query = query.where(generated if dataset == "synthetic" else ~generated)

    if q and q.strip():
        query = query.where(PlayerORM.name.icontains(q.strip(), autoescape=True))

    if max_age is not None:
        query = query.where(PlayerORM.age.isnot(None), PlayerORM.age <= max_age)
    if position is not None:
        aliases = {
            "GK": ["GK", "Goalkeeper"],
            "CB": ["CB", "Centre-Back", "Center-Back"],
            "LB": ["LB", "Left-Back"],
            "RB": ["RB", "Right-Back"],
            "DM": ["DM", "Defensive Midfielder", "Defensive Midfield"],
            "CM": ["CM", "Midfielder", "Central Midfield"],
            "AM": ["AM", "Attacking Midfield", "Attacking Midfielder"],
            "LW": ["LW", "Left Winger"],
            "RW": ["RW", "Right Winger"],
            "ST": ["ST", "CF", "Forward", "Centre-Forward", "Striker"],
        }
        normalized = "/" + func.replace(func.lower(PlayerORM.position), " ", "") + "/"
        query = query.where(
            or_(
                *[
                    normalized.contains(f"/{alias.lower().replace(' ', '')}/", autoescape=True)
                    for alias in aliases.get(position.upper(), [position])
                ]
            )
        )
    if strong_foot is not None:
        query = query.where(PlayerORM.strong_foot == strong_foot)
    if max_value_eur is not None:
        query = query.where(
            PlayerORM.estimated_value_eur.isnot(None),
            PlayerORM.estimated_value_eur <= max_value_eur,
        )
    if diaspora_eligible is True:
        query = query.where(PlayerORM.ancestry_eligibility == _DIASPORA_ELIGIBLE_STATUS)
    elif diaspora_eligible is False:
        query = query.where(
            (PlayerORM.ancestry_eligibility != _DIASPORA_ELIGIBLE_STATUS)
            | (PlayerORM.ancestry_eligibility.is_(None))
        )

    if eligibility_status == "NOT_ASSESSED":
        query = query.where(PlayerORM.ancestry_eligibility.is_(None))
    elif eligibility_status:
        query = query.where(PlayerORM.ancestry_eligibility == eligibility_status)

    if sort == "age_asc":
        query = query.order_by(PlayerORM.age.is_(None), PlayerORM.age.asc())
    elif sort == "value_desc":
        query = query.order_by(
            PlayerORM.estimated_value_eur.is_(None), PlayerORM.estimated_value_eur.desc()
        )
    query = query.order_by(func.lower(PlayerORM.name), PlayerORM.id)

    records = session.execute(query).scalars().all()
    return [
        {column.name: getattr(record, column.name) for column in PlayerORM.__table__.columns}
        for record in records
    ]
