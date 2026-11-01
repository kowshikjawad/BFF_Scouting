# ShonarTalent AI design

## Direction
A dark "pro sports data" workspace: near-black charcoal ground, bright emerald accent, broadcast-style
condensed display type. One bold moment per view — an emerald "hero band" carries the page's key
numbers in white, popping clearly against the dark shell around it — rather than scattering the accent
color thin across many small touches. A fixed desktop sidebar anchors navigation; mobile uses a named
menu and overlay. Tables support scanning; cards offer a more spacious alternative.

This supersedes an earlier light-theme pass (white surfaces, Space Grotesk headings) that the person
running the project said no longer fit — they wanted something closer to professional sports-analytics
tooling (Wyscout/Opta-style broadcast graphics) than a light SaaS dashboard, with the player stat model
genuinely expanded rather than just restyled. It keeps the prior pass's anti-generic-AI-dashboard
discipline: no uppercase eyebrow caption floating above a page title unless it is the section's only
label (e.g. the sidebar's "Workspace" group), no trailing arrow icon appended to buttons/links (only
`ArrowLeft` on true back-navigation and the pagination chevrons — ordinary links are an underline
instead), and elevation that signals interactivity rather than decorating every card identically.

## System
Inter for interface text, Oswald for titles and numeric hierarchy — a condensed, bold, broadcast-grade
display face that reads as sports data rather than a generic SaaS product, set large at the page-title
level (40px/600, -0.01em tracking) so headings carry hierarchy on their own. Four/eight-pixel spacing
rhythm, enforced through two radius tokens (`--radius-control: 6px` for buttons/inputs/chips-in-a-row,
`--radius-panel: 8px` for cards/sections) — tighter and more technical-feeling than a soft SaaS corner
radius, rather than scattered Tailwind radii.

Elevation signals interactivity, not decoration: `.panel` is flat (border only) by default; only a
genuinely clickable surface (a `PlayerCard`, a similarity result row) gets `.panel-interactive`, which
lightens to `--color-surface-raised` and adds a soft emerald glow on hover/focus only — a flat black
drop-shadow would be invisible against a near-black shell, so the hover cue is a lighter surface plus a
brand-colored glow instead. A static information panel never lifts.

Near-black shell (`--color-shell: #0a0c0e`), lifted dark surfaces (`--color-surface`,
`--color-surface-raised`, `--color-chip`), near-white ink (`--color-ink: #eef1f0`) with muted/faint
tiers for secondary text. Bright emerald primary (`--color-pitch: #34d399`) — a dark label on this
fill (`#06120d`), not white, since white-on-emerald fails WCAG AA contrast. A richer mid-dark emerald
for the hero band (`--color-pitch-deep: #0e4a34`, with `--color-on-pitch`/`--color-on-pitch-muted` for
text on it) so it reads as a lifted glowing panel rather than blending into the shell. Gold brightened
for dark-ground legibility (`--color-gold: #f2b84b`); ineligible red likewise (`--color-ineligible:
#f87171`), with a new `--color-ineligible-tint` wash replacing a leftover light-mode `bg-red-50`.
Recurring one-off tones stay tokens, not hand-typed hex: `--color-notice*` (gold demo/legacy-ruleset
banners), `--color-chart-grid`/`--color-chart-cohort` (radar chart lines, referenced via `var()` since
Recharts needs literal color values), `--color-table-head`. Status indicators include words and dots.
Focus rings are visible (now the emerald accent, for contrast against dark surfaces); reduced-motion
preferences apply.

## Interaction
Name search, filters, sort, view and page live in URL state. Profile links retain the search return
path. Bookmark actions explicitly name the player and pressed state. Local-only shortlist storage
is disclosed and failures degrade to session state. Missing stored values remain missing.

Radar axes use percentiles within complete same-league/position cohorts, now across eight tactical
metrics (goals, assists, key passes, progressive carries, dribbles, tackles won, interceptions, aerial
duel % per 90) instead of five — a deliberately fuller statistical picture, matched by a six-stat
"Additional stats" grid underneath (shots/90, shot accuracy %, pass completion %, clearances/90,
minutes played, appearances) for recorded figures that don't need a ninth radar axis. No plot is drawn
if player metrics or a useful cohort are missing. All raw recorded values remain visible below the
plot. Eligibility presents explained screening with current-rule review requirements. PDF download is
a real, one-page report, with explicit generation date and source-coverage context, now covering the
full eight-metric set plus a compact additional-stats line.

## Assets
Open-source Lucide icons (ISC / inherited Feather MIT), Inter and Oswald (SIL OFL), all self-hosted
through existing dependencies. Full provenance and license copies ship in `frontend/public/licenses/`.
PDF embeds ReportLab's Bitstream Vera (license included). Initials and the wordmark composition are
project code, not substitute player photography.

The mark (`frontend/public/favicon.svg`, reused as the sidebar logo) is a two-tone scouting-radar
badge: a deep-green rounded square, a white target ring, and a small gold marker dot standing in for
a highlighted prospect — it is the one place both brand colors (pitch green and "Shonar" gold) meet,
replacing a generic icon-font glyph with something that reads as this product specifically.

Two decorative accents add visual texture without touching product truth, flat/single-hue/no text/no
glow/no 3D, and neither depicting a person:
- `accents/promo-motif.svg` — hand-authored, a quiet concentric-circle/crosshair mark on the sidebar
  promo card, recolored to the bright emerald accent so it still reads against a dark raised panel.
- `accents/hero-pattern.webp` — generated via the Codex CLI's built-in image tool: a pale-sage,
  single-hue hairline radar pattern, used on both the hero band and the Guide page's first panel —
  the same recurring motif rather than a one-off, chosen because it reads against dark surfaces
  (the earlier dark-green-on-transparent variant, `header-motif.webp`, was retired: it relied on a
  light panel underneath that no longer exists now every surface is dark).

Both read as an abstract nod to the product's own tactical-radar chart and scouting/"scanning"
concept, not as photography, stock art, or a generic AI gradient blob.

## Review
Verification evidence and known environment limits are recorded in
`specs/001-complete-scouting-workspace/verification.md` after browser and PDF inspection.

## Synthetic demo extension

The data-source selector switches between a complete fictional demo (default) and original real
records. A persistent neutral-gold notice marks demo pages; exported reports carry the same
provenance. Dataset-scoped shortlist counts and cohort/similarity pools prevent accidental mixing.
The guide includes a walkthrough and the eligibility form offers three explicit demo scenarios.
