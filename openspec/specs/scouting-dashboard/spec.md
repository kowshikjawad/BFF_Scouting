# scouting-dashboard Specification

## Purpose

Gives a scout a visual interface over the backend's player data: searching
and filtering the player pool, viewing an individual player's tactical
profile against the pool, finding similar players, checking FIFA
eligibility, and exporting a one-page summary — the PRD's Module 4
(Scouting Dashboard & UI).

## Requirements

### Requirement: Player search and filtering
The system SHALL present a search view that lists players returned by the
backend search endpoint and lets the user set, clear, and combine filters
for maximum age, position, strong foot, maximum value, and diaspora
eligibility, re-querying the backend whenever a filter changes.

#### Scenario: Default view shows the unfiltered player pool
- **WHEN** the search view first loads with no filters set
- **THEN** it displays the full set of players returned by the backend

#### Scenario: Setting a filter narrows the displayed results
- **WHEN** the user sets any one filter (e.g. maximum age)
- **THEN** the displayed results update to only the players the backend
  returns for that filter

#### Scenario: Clearing filters restores the full result set
- **WHEN** the user clears a previously set filter
- **THEN** the displayed results update to no longer exclude players on
  that criterion

### Requirement: Player profile with tactical radar chart
The system SHALL present a profile view for a selected player showing
their stored profile fields and a radar chart comparing their five
tactical metrics against the pool's average for each metric, and SHALL
indicate when a shown metric is unavailable rather than rendering a
fabricated value.

#### Scenario: Player with recorded tactical metrics
- **WHEN** a profile view is opened for a player who has at least one
  tactical metric recorded
- **THEN** the radar chart renders that player's recorded metrics against
  the pool average for each of the five metrics

#### Scenario: Player with no recorded tactical metrics
- **WHEN** a profile view is opened for a player with no tactical metrics
  recorded
- **THEN** the view indicates that no tactical data is available rather
  than rendering a radar chart with fabricated values

### Requirement: Find similar players from a profile
The system SHALL let the user request similar players from a profile view,
display the backend's ranked results with their similarity scores, and
distinguish an empty result (no similar players found) from a loading or
error state.

#### Scenario: Similar players found
- **WHEN** the user requests similar players for a profile whose backend
  similarity lookup returns ranked matches
- **THEN** the view lists each match with its name and similarity score

#### Scenario: No similar players available
- **WHEN** the user requests similar players for a profile whose backend
  similarity lookup returns an empty result
- **THEN** the view clearly states that no similar players are currently
  available, rather than showing an empty list indistinguishable from a
  loading state

### Requirement: FIFA eligibility checker
The system SHALL present a form covering the eligibility fact fields the
backend's eligibility endpoint accepts, submit it to that endpoint, and
display the returned status and any Article 8 switch-required state.

#### Scenario: Submitting eligibility facts shows the resulting status
- **WHEN** the user fills in the eligibility form and submits it
- **THEN** the view displays the status the backend returns (e.g.
  "ELIGIBLE & CLEARED", "DOCUMENTATION REQUIRED", or "INELIGIBLE")

### Requirement: One-page PDF scout summary export
The system SHALL let the user export a player's profile view as a one-page
PDF document containing that player's profile fields and tactical metrics.

#### Scenario: Exporting a player's profile
- **WHEN** the user triggers the export action from a player's profile view
- **THEN** a one-page PDF containing that player's profile information is
  produced
