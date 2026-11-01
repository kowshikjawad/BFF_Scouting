"""Metric normalization using z-scores relative to league-tier standard (FR-3.1).

Target metrics (radar/similarity vector): Goals/90, Assists/90, Key Passes/90,
Progressive Carries/90, Dribbles/90, Tackles Won/90, Interceptions/90,
Aerial Duel %.
"""

from __future__ import annotations

import numpy as np
from sklearn.preprocessing import StandardScaler

# FR-3.1 metric keys -- the radar/similarity comparison vector. Additional
# recorded stats that are NOT part of this vector (shots, pass completion,
# clearances, minutes, appearances) live on PlayerORM/Player as reference
# figures only; see REFERENCE_METRICS below.
TACTICAL_METRICS: tuple[str, ...] = (
    "goals_per_90",
    "assists_per_90",
    "key_passes_per_90",
    "progressive_carries_per_90",
    "dribbles_per_90",
    "tackles_won_per_90",
    "interceptions_per_90",
    "aerial_duel_pct",
)

# Recorded stats shown on a profile but excluded from the radar/similarity
# vector -- either because they're season totals (not a per-90 rate) or
# because eight axes is already a full radar.
REFERENCE_METRICS: tuple[str, ...] = (
    "shots_per_90",
    "shot_accuracy_pct",
    "pass_completion_pct",
    "clearances_per_90",
    "minutes_played",
    "appearances",
)


class MetricNormalizer:
    """Z-score normalizer fitted on a reference league tier."""

    def __init__(self) -> None:
        self._scaler = StandardScaler()

    def fit(self, matrix: np.ndarray) -> MetricNormalizer:
        """Fit the scaler on (n_players, n_metrics)."""
        self._scaler.fit(matrix)
        return self

    def transform(self, matrix: np.ndarray) -> np.ndarray:
        """Return z-scores for the input matrix."""
        return self._scaler.transform(matrix)
