"""Tactical similarity pipeline: wires persistence to the ML layer (FR-3.1/3.2/3.3).

Built fresh per request rather than cached (design.md decision #4) -- the
live dataset is small enough (~100s of rows) that an in-memory fit is far
under the 500ms NFR budget, and a background-refreshed index would be
premature complexity at this scale.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from sqlalchemy.orm import Session

from backend.models.player_records import get_player, list_players
from backend.models.provenance import data_source
from ml.features.normalize import TACTICAL_METRICS, MetricNormalizer
from ml.models.similarity import SimilarityEngine


class PlayerNotFoundError(Exception):
    """Raised when the requested reference player has no stored record at all."""


@dataclass(frozen=True)
class SimilarityMatch:
    """One ranked result (FR-3.3)."""

    player_id: str
    name: str | None
    similarity_score: float


def _has_any_metric(record: dict[str, object]) -> bool:
    return any(record.get(metric) is not None for metric in TACTICAL_METRICS)


def _impute_matrix(pool: list[dict[str, object]]) -> np.ndarray:
    """Raw metric matrix with missing cells filled at the column's observed
    mean. Since the overall mean of a column is unchanged by imputing its
    own missing entries at that mean (see design.md decision #5), each
    imputed cell normalizes to an exact z-score of 0 -- "average for the
    pool" rather than a fabricated zero rate.
    """
    raw = np.array(
        [
            [p.get(metric) if p.get(metric) is not None else np.nan for metric in TACTICAL_METRICS]
            for p in pool
        ],
        dtype=float,
    )
    with np.errstate(invalid="ignore"), warnings.catch_warnings():
        # A column with zero observed values pool-wide (e.g. no player has
        # any aerial_duel_pct recorded) is a real, expected case, not a
        # bug -- nanmean's "Mean of empty slice" warning is suppressed and
        # the resulting NaN is handled by the fallback below.
        warnings.simplefilter("ignore", category=RuntimeWarning)
        col_means = np.nanmean(raw, axis=0)
    col_means = np.where(np.isnan(col_means), 0.0, col_means)
    missing_rows, missing_cols = np.where(np.isnan(raw))
    raw[missing_rows, missing_cols] = col_means[missing_cols]
    return raw


def rank_similar(session: Session, player_id: str, top_k: int = 5) -> list[SimilarityMatch]:
    """Rank stored players by tactical similarity to `player_id` (FR-3.2/FR-3.3).

    Raises `PlayerNotFoundError` if `player_id` has no stored record.
    Returns an empty list (a valid, non-error result) if the reference
    player has no tactical metrics recorded, or if no other pooled player
    has any either -- see design.md decision #6.
    """
    reference = get_player(session, player_id)
    if reference is None:
        raise PlayerNotFoundError(player_id)
    if not _has_any_metric(reference):
        return []

    pool = [p for p in list_players(session, dataset=data_source(player_id)) if _has_any_metric(p)]
    others = [p for p in pool if p["id"] != player_id]
    if not others:
        return []

    matrix = _impute_matrix(pool)
    normalized = MetricNormalizer().fit(matrix).transform(matrix)

    ref_index = next(i for i, p in enumerate(pool) if p["id"] == player_id)
    effective_top_k = min(top_k, len(pool) - 1)
    if effective_top_k <= 0:
        return []

    engine = SimilarityEngine(metric="cosine", top_k=effective_top_k).fit(normalized)
    matches = engine.query(normalized[ref_index], exclude_index=ref_index)

    return [
        SimilarityMatch(player_id=pool[idx]["id"], name=pool[idx]["name"], similarity_score=pct)
        for idx, pct in matches
    ]
