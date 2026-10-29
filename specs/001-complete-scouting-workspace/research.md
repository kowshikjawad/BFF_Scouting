# Research and audit

- Baseline: 77 backend tests pass, 1 external integration test skipped. Frontend build passes;
lint reports two effect-state warnings. No browser workflow tests exist.
- Player ORM stores tactical data but response schema strips every metric. Schema also rejects
partial records that the ingestion design explicitly permits.
- Existing position filter uses exact strings although storage mixes abbreviations, full names
and multiple positions. Existing eligibility filter is incorrectly labelled diaspora-only.
- Existing PDF action calls browser print; no downloadable report endpoint exists.
- Radar compares raw incompatible units with global means and converts missing values to zero.
- Profile request races can display the wrong player; all fetch failures are labelled not found.
- Docker only serves API, forces amd64 Chrome and does not build UI. API defaults to localhost URL.
- Fresh database does not initialize on app startup. Failed scraper transactions lack rollback.
- Source coverage: 113 real local records, no tactical metrics. Preserve and disclose this.

## Decisions and sources
- Official Spec Kit CLI installed via PyPI; initialized generic commands into `.specify/commands`.
Use constitution → spec → plan → tasks → implement → converge.
https://github.github.io/spec-kit/existing-projects.html
https://github.github.io/spec-kit/quickstart.html
- Open-source icons: Lucide (ISC; inherited Feather icons MIT), https://lucide.dev/license.
Fonts: Inter and Space Grotesk (SIL OFL), https://rsms.me/inter/ and
https://github.com/floriankarsten/space-grotesk. Retain bundled license texts and self-host fonts.
- No invented photography or filler imagery. Sport identity comes from typography, pitch-green
accent, an open-source football mark and real scouting records.
- Eligibility: preserve historical rules for compatibility, explicitly disclose simplified screening;
require review for youth representation instead of presenting automatic official clearance.
