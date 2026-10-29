# ShonarTalent AI design

## Direction
A quiet scouting workspace: white surfaces on a cool off-white ground, deep pitch green for actions,
and restrained gold/red for status. One bold moment per view — a deep-green "hero band" carries the
page's key numbers in white — rather than scattering the accent color thin across many small touches.
A fixed desktop sidebar anchors navigation; mobile uses a named menu and overlay. Tables support
scanning; cards offer a more spacious alternative.

This direction deliberately removes the generic "AI dashboard" tells the previous pass had
reintroduced: an uppercase eyebrow caption floating above almost every page title (removed except
where it is the only label for a section, e.g. the sidebar's "Workspace" group), a trailing arrow
icon appended to nearly every button and link (removed everywhere except `ArrowLeft` on true
back-navigation and the pagination chevrons — ordinary links are an underline instead), and identical
card elevation applied uniformly regardless of whether a surface is clickable.

## System
Inter for interface text, Space Grotesk for titles and numeric hierarchy, now set larger and bolder
at the page-title level (36px/600, tight tracking) so headings carry the hierarchy themselves instead
of needing a caption above them. Four/eight-pixel spacing rhythm, enforced through two radius tokens
(`--radius-control: 7px` for buttons/inputs/chips-in-a-row, `--radius-panel: 10px` for cards/sections)
rather than scattered Tailwind radii.

Elevation signals interactivity, not decoration: `.panel` is flat (border only) by default; only a
genuinely clickable surface (a `PlayerCard`, a similarity result row) gets `.panel-interactive`, which
adds the neutral "beautiful sm" shadow on hover/focus only. A static information panel never lifts.

Main text #1c3027, secondary #617069, primary #176448 (`--color-pitch`), a near-black green for the
hero band (`--color-pitch-deep: #0c2e22`, with `--color-on-pitch`/`--color-on-pitch-muted` for text on
it), shell #f7f8fa, surface #fff. Recurring one-off tones are tokens, not hand-typed hex:
`--color-notice*` (gold demo/legacy-ruleset banners), `--color-chart-grid`/`--color-chart-cohort`
(radar chart lines, referenced via `var()` since Recharts needs literal color values),
`--color-table-head`.
Status indicators include words and dots. Focus rings are visible; reduced-motion preferences apply.

## Interaction
Name search, filters, sort, view and page live in URL state. Profile links retain the search return
path. Bookmark actions explicitly name the player and pressed state. Local-only shortlist storage
is disclosed and failures degrade to session state. Missing stored values remain missing.

Radar axes use percentiles within complete same-league/position cohorts. No plot is drawn if player
metrics or a useful cohort are missing. All raw recorded values remain visible below the plot.
Eligibility presents explained screening with current-rule review requirements. PDF download is a
real, one-page report, with explicit generation date and source-coverage context.

## Assets
Open-source Lucide icons (ISC / inherited Feather MIT), Inter and Space Grotesk (SIL OFL), all
self-hosted through existing dependencies. Full provenance and license copies ship in
`frontend/public/licenses/`. PDF embeds ReportLab's Bitstream Vera (license included).
Initials and the wordmark composition are project code, not substitute player photography.

The mark (`frontend/public/favicon.svg`, reused as the sidebar logo) is a two-tone scouting-radar
badge: a deep-green rounded square, a white target ring, and a small gold marker dot standing in for
a highlighted prospect — it is the one place both brand colors (pitch green and "Shonar" gold) meet,
replacing a generic icon-font glyph with something that reads as this product specifically.

Three decorative accents add visual texture without touching product truth, all flat/single-hue/no
text/no glow/no 3D, and none depicting a person:
- `accents/promo-motif.svg` — hand-authored, a quiet concentric-circle/crosshair mark on the sidebar
  promo card.
- `accents/header-motif.webp` — generated via the Codex CLI's built-in image tool: a single-hue dark
  hairline radar pattern, reused on the Guide page's first panel (light background).
- `accents/hero-pattern.webp` — generated the same way, recolored pale-sage-on-transparent so it reads
  against the dark hero band instead; same concentric-ring/crosshair motif, confirming the "radar"
  accent as one deliberate recurring idea rather than a one-off.

All three read as an abstract nod to the product's own tactical-radar chart and scouting/"scanning"
concept, not as photography, stock art, or a generic AI gradient blob.

## Review
Verification evidence and known environment limits are recorded in
`specs/001-complete-scouting-workspace/verification.md` after browser and PDF inspection.

## Synthetic demo extension

The data-source selector switches between a complete fictional demo (default) and original real
records. A persistent neutral-gold notice marks demo pages; exported reports carry the same
provenance. Dataset-scoped shortlist counts and cohort/similarity pools prevent accidental mixing.
The guide includes a walkthrough and the eligibility form offers three explicit demo scenarios.
