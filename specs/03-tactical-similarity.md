# Spec 03 — Tactical Similarity Engine (Module 3)

## Scope
FR-3.1, FR-3.2, FR-3.3.

## Metrics (FR-3.1)
Goals/90, Key Passes/90, Progressive Carries/90, Tackles Won/90, Aerial Duel %.

## Acceptance criteria
- [ ] Metrics z-score normalized relative to league-tier standard.
- [ ] cosine / k-NN matching on selecting a reference player.
- [ ] Top-5 ranked alternatives with percentage similarity.
- [ ] Query response < 500 ms (NFR-perf).

## Files
- `ml/features/normalize.py`
- `ml/models/similarity.py`
- `tests/ml/test_similarity.py`