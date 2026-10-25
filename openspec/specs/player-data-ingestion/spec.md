# player-data-ingestion Specification

## Purpose

Acquires player data for the platform from three distinct sources —
Bangladesh's domestic football league, FBref for any tracked player in a
covered competition, and a maintained diaspora reference set — and
persists it through the player-records capability, each source scoped
honestly to what it can actually provide.

## Requirements

### Requirement: Domestic league scraping targets football, not cricket
The system SHALL source Bangladesh domestic league squad data only from
sources identified as the Bangladesh football top division (historically
"Bangladesh Premier League (football)", currently also referred to as
"Bangladesh Football League"), and SHALL NOT rely on an unqualified "BPL"
search or source that could resolve to the unrelated Bangladesh Premier
League cricket tournament.

#### Scenario: Ambiguous source rejected
- **WHEN** a candidate data source for domestic squad data does not
  explicitly identify itself as football (e.g. a bare "BPL" reference with
  no sport qualifier)
- **THEN** the system does not use that source for domestic player records

#### Scenario: Football-qualified source accepted
- **WHEN** a candidate data source explicitly identifies itself as the
  Bangladesh football top division (by name or by content, e.g. listing
  football clubs such as Bashundhara Kings)
- **THEN** the system may use that source for domestic player records

### Requirement: Domestic scraping populates bio fields only
The system SHALL populate, for each domestic league player, only the
profile fields obtainable from public squad-list sources (name, age,
position, height where available, strong foot where available, club/league
band), and SHALL NOT populate or estimate tactical per-90 metrics for
domestic players, since no public source of such metrics exists for this
league.

#### Scenario: Domestic player record has no tactical metrics
- **WHEN** a domestic league player is scraped and persisted
- **THEN** their stored record has profile fields populated to the extent
  the source provides them, and all five tactical metric fields absent

### Requirement: FBref backfill is scoped to its covered competitions
The system SHALL attempt to source tactical per-90 metrics from FBref only
for players associated with one of FBref's supported competitions, and
SHALL leave a tracked player's tactical metrics absent (not an error, not
an estimate) when that player is not associated with a supported
competition.

#### Scenario: Tracked player outside FBref's coverage
- **WHEN** a tracked player's current club/competition is not one of
  FBref's supported competitions
- **THEN** the system does not attempt to fetch tactical metrics for that
  player from FBref, and their record's tactical metric fields remain
  whatever they already were (absent, if never otherwise set)

#### Scenario: Tracked player inside FBref's coverage
- **WHEN** a tracked player's current club/competition is one of FBref's
  supported competitions
- **THEN** the system attempts to fetch and persist that player's
  available tactical per-90 metrics from FBref

### Requirement: FBref requests respect the documented rate limit
The system SHALL limit its FBref requests to no more than 10 requests per
minute per scraping session, matching FBref's documented limit, and SHALL
NOT attempt to defeat an IP-level block from FBref (e.g. via proxy
rotation or additional evasion beyond what the underlying library already
performs) if one occurs.

#### Scenario: Request pacing stays within the documented limit
- **WHEN** the FBref scraper issues a sequence of requests in a single
  session
- **THEN** no more than 10 requests are issued within any rolling 60-second
  window

#### Scenario: A rate-limit or access block is surfaced, not silently retried around
- **WHEN** FBref responds with a rate-limit or access-denied condition
- **THEN** the system logs the failure and stops that scraping run for the
  affected competition rather than retrying through proxy rotation or
  other access-evasion techniques

### Requirement: Diaspora players are sourced from a maintained reference set, not scraped
The system SHALL source the diaspora player roster from a maintained local
data file rather than from a live scrape, since no structured feed
identifies Bangladeshi diaspora/dual-national players, and SHALL record a
last-verified-date for each entry given how quickly these players' club
situations change.

#### Scenario: Loading the diaspora roster
- **WHEN** the diaspora data source is loaded
- **THEN** it returns the maintained set of diaspora player records, each
  including a last-verified-date, without making any network request

### Requirement: Scraper orchestration isolates per-source failures
The system SHALL run the domestic, FBref, and diaspora data sources
independently such that a failure in one source does not prevent the
successful results of the other sources from being persisted.

#### Scenario: One source fails, others still persist
- **WHEN** the FBref source fails (e.g. due to a rate-limit block) during
  an orchestrated run that also includes the domestic and diaspora sources
- **THEN** the domestic and diaspora sources' results are still persisted,
  and the failure is reported rather than silently swallowed
