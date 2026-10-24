# Spec Delta

## Purpose

Determines whether a given player can currently represent the Bangladesh
national team under FIFA's eligibility rules (Statutes/Regulations
Governing the Application of the FIFA Statutes, Art. 6, 7 and 8), and
reports the specific status a scout or federation analyst needs to act on.

## ADDED Requirements

### Requirement: Dual-national genuine-link eligibility (Art. 6)
The system SHALL evaluate a player who already holds Bangladeshi nationality
alongside another nationality as heritage-eligible when at least one of the
following genuine-link facts holds: born in Bangladesh; a biological parent
born in Bangladesh; a biological grandparent born in Bangladesh; or at least
2 continuous years of residency in Bangladesh.

#### Scenario: Eligible via 2 years of dual-national residency
- **WHEN** a dual-national player's facts show 2 continuous years of
  residency in Bangladesh and no other genuine-link fact
- **THEN** the player is reported heritage-eligible under Art. 6

#### Scenario: Not yet eligible via dual-national residency
- **WHEN** a dual-national player's facts show fewer than 2 continuous
  years of residency in Bangladesh and no other genuine-link fact
- **THEN** the player is reported not heritage-eligible

### Requirement: New-nationality genuine-link eligibility (Art. 7)
The system SHALL evaluate a player who is newly acquiring Bangladeshi
nationality (not previously held) as heritage-eligible when at least one of
the following genuine-link facts holds: born in Bangladesh; a biological
parent born in Bangladesh; a biological grandparent born in Bangladesh; or
at least 5 continuous years of residency in Bangladesh accrued after the
player turned 18.

#### Scenario: Eligible via 5 years of post-18 residency
- **WHEN** a newly-naturalizing player's facts show 5 continuous years of
  residency in Bangladesh accrued after turning 18, and no other
  genuine-link fact
- **THEN** the player is reported heritage-eligible under Art. 7

#### Scenario: Pre-18 residency does not count toward the Art. 7 threshold
- **WHEN** a newly-naturalizing player's facts show 5 continuous years of
  residency in Bangladesh but fewer than 5 of those years occurred after
  turning 18, and no other genuine-link fact
- **THEN** the player is reported not heritage-eligible

#### Scenario: Dual-national residency threshold does not apply to new-nationality path
- **WHEN** a newly-naturalizing player's facts show 2 continuous years of
  residency in Bangladesh accrued after turning 18, and no other
  genuine-link fact
- **THEN** the player is reported not heritage-eligible

### Requirement: Documentation verification of claimed genuine-link facts
The system SHALL report a status of `DOCUMENTATION REQUIRED` instead of
`ELIGIBLE & CLEARED` when a player satisfies a genuine-link fact under Art.
6 or Art. 7 but that specific fact is not marked as supported by
verifying documentation on file.

#### Scenario: Unverified ancestry claim
- **WHEN** a player's facts show a biological parent born in Bangladesh but
  that fact is marked as undocumented
- **THEN** the system reports `DOCUMENTATION REQUIRED`

#### Scenario: Verified ancestry claim
- **WHEN** a player's facts show a biological parent born in Bangladesh and
  that fact is marked as documented, with no other outstanding checks
- **THEN** the system reports `ELIGIBLE & CLEARED`

### Requirement: No qualifying facts yields ineligible
The system SHALL report a status of `INELIGIBLE` when a player satisfies no
genuine-link fact under either Art. 6 or Art. 7, regardless of documentation
state.

#### Scenario: No qualifying facts
- **WHEN** a player's facts show no birth, parental, grandparental, or
  sufficient residency link under the applicable article
- **THEN** the system reports `INELIGIBLE`

### Requirement: One-time association change clearance (Art. 8)
The system SHALL separately track whether a player has prior senior ("A")
international caps for another FIFA member association, and SHALL report
that a one-time change-of-association request is required and outstanding
whenever such prior senior caps exist and no approved switch is on record —
regardless of the player's Art. 6/7 heritage status.

#### Scenario: Heritage-eligible but pending association switch
- **WHEN** a player is heritage-eligible under Art. 6 or Art. 7 and has a
  recorded prior senior international cap for another association with no
  approved switch on record
- **THEN** the system reports that the player is heritage-eligible AND that
  an Art. 8 change-of-association request is required and outstanding, and
  does NOT report a bare `ELIGIBLE & CLEARED` status for that player

#### Scenario: Heritage-eligible with an approved association switch
- **WHEN** a player is heritage-eligible under Art. 6 or Art. 7, has a
  recorded prior senior international cap for another association, and also
  has an approved switch on record
- **THEN** the system reports `ELIGIBLE & CLEARED`

#### Scenario: Prior youth-only caps do not trigger Art. 8
- **WHEN** a player has prior youth-level (non-"A") international caps for
  another association only, and is otherwise heritage-eligible with
  documented facts
- **THEN** the system reports `ELIGIBLE & CLEARED` with no Art. 8 request
  flagged

### Requirement: Eligibility lookup is exposed via the API
The system SHALL expose a player's current eligibility evaluation, including
the heritage status and any outstanding Art. 8 requirement, through the
`/api/v1/players/{player_id}/eligibility` endpoint.

#### Scenario: Endpoint returns a real evaluation
- **WHEN** a client requests eligibility for a known player id
- **THEN** the endpoint responds with that player's evaluated status rather
  than an unimplemented error
