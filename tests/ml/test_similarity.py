"""Tests for the FR-3.2 / FR-3.3 similarity engine."""
from __future__ import annotations

import numpy as np

from ml.models.similarity import SimilarityEngine


def test_query_returns_top_k_minus_self():
    rng = np.random.default_rng(0)
    vectors = rng.normal(size=(20, 5))
    engine = SimilarityEngine(top_k=5).fit(vectors)

    results = engine.query(vectors[3], exclude_index=3)
    # FR-3.3: exactly top-K *other* players, percentage scores in 0..100
    assert len(results) == 5
    assert all(idx != 3 for idx, _ in results)
    assert all(0.0 <= score <= 100.0 for _, score in results)