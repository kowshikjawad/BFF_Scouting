# player-records Specification

## Purpose

Durable storage for player profiles and their tactical per-90 metrics, so
that scraped and seeded data persists across process restarts and is
queryable by the search, similarity, and eligibility API layers.

## Requirements

### Requirement: Player profile persistence
The system SHALL persistently store, for each player, the eight attributes
defined by FR-1.2: name, age, primary position, height, strong foot, league
band, contract expiry, and estimated value, keyed by a stable player id.

#### Scenario: A stored player survives a process restart
- **WHEN** a player record has been written and the application process is
  restarted
- **THEN** querying that player's id returns the same stored attributes

### Requirement: Tactical metric storage is independent of profile storage
The system SHALL store the five tactical per-90 metrics used by the
similarity engine (goals/90, key passes/90, progressive carries/90, tackles
won/90, aerial duel %) as fields on a player record that can each be
present or absent independently of one another and independently of
whether the player's profile fields are complete.

#### Scenario: Profile present, all tactical metrics absent
- **WHEN** a player's profile fields are fully populated but none of their
  five tactical metrics have ever been recorded
- **THEN** the player record is retrievable with its profile fields intact
  and all five tactical metric fields reported as absent, not as zero and
  not as an error

#### Scenario: Partial tactical metrics
- **WHEN** a player has some but not all of the five tactical metrics
  recorded (e.g. goals/90 known, aerial duel % never recorded)
- **THEN** the player record reports the known metrics and reports the
  unrecorded ones as absent, independently

### Requirement: Absent tactical metrics are a valid state, not an error condition
The system SHALL treat a player record with zero recorded tactical metrics
as valid and ordinarily retrievable, since many tracked players (e.g.
domestic-league or diaspora players outside any covered stats source) are
expected to have no tactical metrics available.

#### Scenario: Querying a player with no tactical metrics at all
- **WHEN** a client requests a player record for a player who has never had
  any tactical metric recorded
- **THEN** the system returns the record successfully rather than raising
  an error or omitting the player

### Requirement: Upsert by player id
The system SHALL provide an operation that writes a player's profile and/or
tactical metric fields by player id, creating the record if it does not yet
exist and updating only the fields supplied if it does, leaving fields not
supplied in the call unchanged.

#### Scenario: Upsert creates a new record
- **WHEN** an upsert is called with a player id that has no existing record
  and a full or partial set of fields
- **THEN** a new record is created with the supplied fields, and any
  unsupplied profile fields are absent and any unsupplied tactical metric
  fields are absent

#### Scenario: Upsert updates only the supplied fields
- **WHEN** an upsert is called with a player id that already has a stored
  record, supplying only a subset of fields (e.g. one tactical metric)
- **THEN** the supplied fields are updated and every other previously
  stored field on that record is unchanged
