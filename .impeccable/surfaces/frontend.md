---
version: 1
slug: "frontend"
primary_target: "frontend"
related_targets: []
---

## Scope and visitor mode

Operate. The scouting dashboard (`frontend/`): search/filter, player profile
with tactical radar, similarity results, FIFA eligibility checker, PDF
export. Direction is brief-pinned (user: "minimalistic and sleek"), so this
runs code-led with no concept-seed roll or comp round — no image generation
tool is available in this environment, and an Operate surface is code-led by
contract regardless.

## Audience, job, action/task, proof/content, constraints

A scout scanning many players quickly, then going deep on one. Real,
named individuals throughout — no fabricated photos on a real player's
profile (generated initials avatars only). The live dataset currently has
zero players with any tactical metric recorded; "no data" is the common
state, not an edge case, and must read as calm and intentional, never
broken.

## Direction contract

**THESIS:** A football-broadcast analytics screen, not a generic SaaS
admin panel — the dense, confident stat-graphic language scouts already
read every match day (Opta/Wyscout-style on-screen data), refusing both
the grey-dashboard-with-one-accent default and over-decorated "gamified"
sports-app cliches.

**OWN-WORLD:** Near-black charcoal ground (#0B0E11 shell, #12161B
surfaces). One committed accent, pitch green (#22C55E / #16A34A active),
carrying the shell's primary actions, links, and the chart's signature
ring. A second accent, warm gold (#D4A24C — "shonar"/golden, tying to the
product name) marks eligibility/highlight states only, never competing
with green for primary actions. State colors double as semantic and
brand: green = eligible, gold/amber = documentation required, red
(#EF4444) = ineligible. Type: Space Grotesk for headings/stat numerals
(distinctive, numeral-friendly), Inter for body/UI text and data tables.
One consistent small corner radius (6px) everywhere, echoing a corner-arc
rather than a soft "bubbly" SaaS radius. Thin 2px accent-green rule as the
active/selected state, not a glow or heavy shadow.

**STORY:** A scout opens the dashboard already filtered to a useful
default view, narrows by task-relevant facts (age, position, foot, value,
diaspora eligibility), opens a player to see their tactical shape at a
glance, and either finds alternatives or exports a one-pager — never
blocked or confused by a player with incomplete data, which is the norm
here, not the exception.

**FIRST VIEWPORT:** Fixed left-rail or top bar nav (Search / Eligibility),
filter bar immediately below/beside it, dense card grid of players below
that — each card: initials avatar on a deterministic accent tint, name,
age/position/league, a small eligibility-status pill. No hero, no
marketing copy — the data pool itself is the first thing shown.

**FORM:** Standard web components throughout (real `<button>`, `<select>`,
`<input>`, a real `<table>`/grid for any tabular view) — never a costume
of a broadcast graphic chrome. The world supplies palette, type, density,
and the signature move only. seed: none (unavailable) — no concept-seed
roll was run; direction is brief-pinned and this is a code-led Operate
surface with no image-generation tool available in this environment.

**Signature move:** the tactical radar chart's background grid is drawn
as concentric pitch-green rings (like a center-circle), not a generic
grey polygon grid — the one place the world's motif appears beyond
palette/type/density, exactly as Operate mode's "name the signature move
concretely" calls for.

**FINISH:** unreviewed and undocumented is unfinished; this build ends
with the finish review, the verdict, DESIGN.md, and every shipping raster
carrying its provenance.
