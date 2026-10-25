# Spec Delta

## Purpose

Ranks stored players by tactical similarity to a chosen reference player,
so a scout can find alternatives with a comparable playing profile.

## ADDED Requirements

### Requirement: Similarity ranking over available tactical metrics
The system SHALL compute similarity by z-score normalizing the five
tactical per-90 metrics across the pool of stored players that have at
least one tactical metric recorded, then ranking that pool by cosine
distance to a reference player, returning up to the requested top-K most
similar players (excluding the reference player itself) each with a
percentage similarity score.

#### Scenario: Reference player has tactical metrics and the pool is large enough
- **WHEN** a similarity request is made for a player who has at least one
  tactical metric recorded, and at least one other player in the pool also
  has tactical metrics recorded
- **THEN** the response contains up to top-K other players ranked by
  similarity, each with a percentage score, and never includes the
  reference player itself

#### Scenario: Fewer eligible candidates than the requested top-K
- **WHEN** a similarity request asks for more results than there are other
  players with tactical metrics recorded
- **THEN** the system returns as many ranked matches as exist, rather than
  erroring or fabricating additional results

### Requirement: Reference player without usable tactical data is a defined, non-error response
The system SHALL return a defined "not enough data" result, not an
unhandled error, when the requested reference player has no tactical
metrics recorded or when the pool of other players with recorded tactical
metrics is empty.

#### Scenario: Reference player has no tactical metrics recorded
- **WHEN** a similarity request is made for a stored player who has never
  had any tactical metric recorded
- **THEN** the system responds with an explicit empty/insufficient-data
  result rather than a server error

#### Scenario: No other players have tactical metrics recorded
- **WHEN** a similarity request is made for a player who does have tactical
  metrics, but no other stored player has any tactical metric recorded
- **THEN** the system responds with an explicit empty result rather than a
  server error

### Requirement: Similarity request for an unknown player is rejected
The system SHALL respond with a not-found result, not a ranking attempt,
when the requested reference player id has no stored record at all.

#### Scenario: Unknown reference player id
- **WHEN** a similarity request is made with a player id that has no
  stored record
- **THEN** the system responds with a not-found result
