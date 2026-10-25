# Spec Delta

## Purpose

Lets a scout list and filter stored players by the dashboard's search
criteria, and fetch a single player's full stored record for a profile
view.

## ADDED Requirements

### Requirement: Multi-variable player search
The system SHALL provide a player listing endpoint accepting independent,
combinable filters: maximum age, position, strong foot, maximum estimated
value, and diaspora eligibility, returning only players whose stored
record matches every supplied filter. An omitted filter SHALL NOT
constrain the result.

#### Scenario: No filters supplied
- **WHEN** the listing endpoint is called with no filter parameters
- **THEN** every stored player record is returned

#### Scenario: A single filter narrows the result
- **WHEN** the listing endpoint is called with only `max_age` set
- **THEN** only players whose stored age is at or below that value are
  returned, including players whose age is unset being excluded (an unset
  age cannot be known to satisfy a maximum)

#### Scenario: Combined filters are all applied
- **WHEN** the listing endpoint is called with both `position` and
  `strong_foot` set
- **THEN** only players matching both are returned

#### Scenario: Diaspora eligibility filter
- **WHEN** the listing endpoint is called with `diaspora_eligible=true`
- **THEN** only players whose stored eligibility status is
  "ELIGIBLE & CLEARED" are returned

### Requirement: Single-player detail lookup
The system SHALL provide an endpoint that returns one player's full stored
record by id, and a not-found response when no record exists for that id.

#### Scenario: Existing player
- **WHEN** the detail endpoint is called with an id that has a stored
  record
- **THEN** that record's fields are returned, with any never-set field
  reported as absent rather than a fabricated default

#### Scenario: Unknown player id
- **WHEN** the detail endpoint is called with an id that has no stored
  record
- **THEN** the system responds with a not-found result rather than an
  empty or default player record
