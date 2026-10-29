"""Tactical similarity engine — cosine / k-NN (FR-3.2, FR-3.3).

Takes normalized vectors and returns the top-K most similar players
with percentage similarity scores.
"""

from __future__ import annotations

import numpy as np
from sklearn.neighbors import NearestNeighbors


class SimilarityEngine:
    """k-NN engine over normalized player vectors."""

    def __init__(self, metric: str = "cosine", top_k: int = 5) -> None:
        self._metric = metric
        self._top_k = top_k
        self._nn = NearestNeighbors(n_neighbors=top_k + 1, metric=metric)

    def fit(self, vectors: np.ndarray) -> SimilarityEngine:
        self._nn.fit(vectors)
        return self

    def query(
        self, vector: np.ndarray, exclude_index: int | None = None
    ) -> list[tuple[int, float]]:
        """Return [(index, similarity_pct), ...] for the top_K most similar players.

        ``exclude_index`` drops the self-match when the query point is part of
        the fitted index (FR-3.3: top-5 *other* players). Distance-to-percentage
        mapping is finalised in Sprint 2.
        """
        distances, indices = self._nn.kneighbors(vector.reshape(1, -1))
        results: list[tuple[int, float]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if exclude_index is not None and int(idx) == exclude_index:
                continue
            similarity = min(1.0, max(0.0, 1.0 - float(dist))) * 100.0
            results.append((int(idx), similarity))
        return results[: self._top_k]
