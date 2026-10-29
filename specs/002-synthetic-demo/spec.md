# Synthetic scouting demo

Date: 2026-10-28. User asks for synthetic data, functioning features and an explanation.

## Acceptance
1. Generate 160 deterministic fictional profiles: 10 positions, four fictional leagues, four
players per position/league cohort. All five tactical metrics and profile fields are populated.
2. Retain existing real records byte-for-byte at the field level. Synthetic IDs have a reserved
prefix; demo records are never presented as measurements of named real players.
3. The default workspace opens the synthetic demo, with a source selector and explicit labels.
Real-record mode remains available, including its honest missing-data states.
4. Filtering, percentile cohort radar, top-five similarity, shortlist, eligibility examples and
one-page reports work with real API/database records, not browser mocks.
5. Real/synthetic datasets never mix in lists, radar cohorts or similarity rankings. Shortlists
retain both kinds of saved IDs while displaying/counting the selected dataset only.
6. Exports identify synthetic data prominently. Rankings are comparisons, not outcome predictions.
7. Document reproducibility, regeneration, per-90 units, percentile charts, normalization and
similarity scores. Validate API integrity and actual browser journeys with generated data.

## Assumptions
The user explicitly authorizes invented demo data. Fictional names/clubs/values/metrics/statuses
are tagged throughout. Existing real profiles and legacy screening rules are unchanged.
