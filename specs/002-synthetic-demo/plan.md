# Plan

Use the existing SQLite table with reserved `synthetic-v1-` IDs; derive provenance from the reserved
namespace rather than migrating existing records. Add `data_source` to API responses and an optional
real/synthetic dataset parameter (API default remains real for backwards compatibility). Restrict
similarity to the reference dataset. Generate position-shaped, correlated metrics with seeded stdlib
randomness; seed offline and idempotently. Add a dataset context and selector, demo notices, eligibility
examples, and report labeling. Preserve previous OpenSpec and completion-spec history.
