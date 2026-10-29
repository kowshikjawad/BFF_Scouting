# Product

## Platform and stack
Web scouting workspace. React + Vite + TypeScript + Tailwind CSS v4, FastAPI, SQLAlchemy/SQLite,
scikit-learn similarity, ReportLab exports. See README.md for reproducible setup and deployment.

## Users and purpose
Football scouts, club technical staff and Bangladesh-focused association analysts discovering
domestic and diaspora talent. Users search/filter the pool, inspect records and tactical coverage,
save a shortlist, screen supplied heritage facts and download one-page reports.

## Current scope
Minimal light UI, desktop sidebar/mobile navigation, URL-preserved search/filter/sort/view/page,
card/table results, race-safe profiles, local shortlist, actual PDF downloads and explained
preliminary eligibility. The application has no authentication; deploy within trusted environments.

## Data constraints
The preserved real dataset has 113 records and zero tactical metrics. An explicitly labelled
synthetic demo adds 160 fictional profiles with complete metrics and four peers in every
league/position cohort. Fresh clones load six maintained real profiles plus the demo offline.
The data-source selector switches views; analytics never mix them. Source coverage varies and records are snapshots. Unknown
facts remain null. Initials identify players; no stock or generated photo impersonates a player.

Tactical charts require complete metrics and same-league/position peers and use percentile axes
against the cohort median. Similarity uses standardized metrics with mean imputation for partial
profiles. Both features expose honest coverage states when data is absent.

Eligibility uses a simplified legacy ruleset, not complete current FIFA regulations. Prior youth
or senior representation triggers association review. Stored status vocabulary is retained for
compatibility and does not certify official clearance. Guidance links point to FIFA’s documentation.

## Product principles
1. Preserve truth: never fabricate real-player facts. Explicitly authorized synthetic demo data
uses reserved IDs and visible labels in the UI, API and PDFs.
2. Complete workflows: discover, inspect, shortlist, screen and export all have recovery paths.
3. Scan quickly: readable data, familiar controls, restrained visual hierarchy.
4. Accessible by default: semantic labels, keyboard navigation, focus rings and mobile layouts.
5. Keep delivery traceable: active Spec Kit acceptance criteria and verification alongside source.

## Brand and assets
ShonarTalent AI. Deep pitch green, neutral light surfaces, restrained semantic gold/red. Inter UI,
Space Grotesk headings, Lucide icons. Self-hosted open-source assets and full notices in
frontend/public/licenses/. See DESIGN.md.
