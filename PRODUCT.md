# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated: React + Vite + TypeScript + Tailwind CSS v4, chosen by the
assistant this session over the PRD's listed "Streamlit or Plotly Dash"
because the end user explicitly asked for a minimalistic, sleek, custom
visual design with room for imagery — a custom web frontend gives far
more control over that than Streamlit. The PRD's own Sprint 4 roadmap
line ("Streamlit/React dashboard") names React as an accepted alternative.

## Users

Football scouts, club technical staff, and the Bangladesh Football
Federation (or diaspora-focused football associations) evaluating two
pools of players: domestic Bangladesh Football League talent and
diaspora/dual-national players abroad who may be eligible to represent
Bangladesh internationally. (Source: PRD.md Executive Summary / Target
Users.)

## Product Purpose

ShonarTalent AI aggregates domestic league and diaspora player data,
evaluates FIFA international-eligibility status for diaspora players, and
surfaces tactically similar players via a k-NN similarity engine over
normalized per-90 metrics — so a scout can find and vet talent that would
otherwise require manual cross-referencing of scattered sources. (Source:
PRD.md Modules 1-3.)

## Positioning

No existing tool combines Bangladesh-specific domestic league data,
a maintained diaspora/dual-national reference set, a FIFA Article 6/7/8
eligibility engine, and tactical similarity search in one place. The
eligibility engine specifically (Art. 6 two-year vs. Art. 7 five-year
residency paths, Art. 8 one-time switch) is this project's most
differentiated piece of domain logic. (Source: PRD.md, and this session's
FIFA Statutes research during the `fix-fifa-eligibility-rules` change.)

## Operating Context

A scout searches/filters the player pool, opens a player's profile to see
their tactical radar chart and FIFA eligibility status, optionally finds
similar players, and exports a one-page PDF summary for offline scouting
reports. The eligibility checker is also used standalone for a player not
yet in the database, by entering their FIFA-relevant facts directly.

## Capabilities and Constraints

- Backend: FastAPI, SQLite, endpoints for player search/detail,
  similarity ranking, and eligibility evaluation (all implemented and
  live-verified this session against a real ~113-player dataset).
- No authentication exists anywhere in the project; none is in scope.
- The live dataset currently has **zero** players with any tactical
  metric recorded (FBref only covers 9 major competitions none of the
  tracked diaspora players currently play in) — the UI must degrade
  gracefully to an explicit "no tactical data" state, which is the
  common case today, not an edge case.
- Real, named individuals (the diaspora and domestic players) appear
  throughout the product. No stock or AI-generated photos may be
  attached to a real player's name or profile — avatars are generated
  (initials on a deterministic color) rather than photographic.

## Brand Commitments

Product name: "ShonarTalent AI" ("shonar" = Bengali for "golden"). No
existing logo, color system, or typography has been established — this
is this product's first visual surface.

## Evidence on Hand

- `PRD.md`: full product requirements (FR-1 through FR-4, NFRs).
- A real, live SQLite database (`data/processed/shonartalent.db`) with
  113 real players (6 diaspora, 107 domestic) scraped and verified this
  session.
- No existing design assets, logo, or brand marks exist.

## Product Principles

1. Never fabricate data or imagery for a real, named player — absence
   (no photo, no tactical metric, no club) is shown explicitly, not
   papered over.
2. The eligibility and similarity engines are the product's core
   intellectual property — the UI should make their reasoning legible
   (why a status was reached, why a match ranked where it did), not just
   show a final number.
3. Built for a scout working quickly across many players — scanability
   and low-friction filtering outrank decorative flourish.

## Accessibility & Inclusion

No formal standard specified by the user; build to ordinary WCAG AA
contrast and keyboard-navigability as a baseline default, not a specified
requirement.
