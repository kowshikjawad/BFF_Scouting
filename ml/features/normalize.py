"""Metric normalization using z-scores relative to league-tier standard (FR-3.1).

Target metrics: Goals/90, Key Passes/90, Progressive Carries/90,
Tackles Won/90, Aerial Duel %.
"""
from __future__ import annotations

import numpy as np
from sklearn.preprocessing import StandardScaler

# FR-3.1 metric keys
TACTICAL_METRICS: tuple[str, ...] = (
    "goals_per_90",
    "key_passes_per_90",
    "progressive_carries_per_90",
    "tackles_won_per_90",
    "aerial_duel_pct",
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