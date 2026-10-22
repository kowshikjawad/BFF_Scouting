# Spec 01 — Global Diaspora & Domestic Database (Module 1)

## Scope
FR-1.1, FR-1.2.

## Acceptance criteria
- [ ] BPL squad profiles scraped into structured records.
- [ ] FBref per-90 stats scraped per league/season.
- [ ] Diaspora/dual-national listings aggregated.
- [ ] Each player stores Name, Age, Primary Position, Height, Strong Foot,
      League Band, Contract Expiry, Estimated Value, Ancestry Eligibility Status.
- [ ] Scrapers idempotent and scheduled weekly (NFR-fresh).

## Files
- `scrapers/bpl.py`
- `scrapers/fbref.py`
- `scrapers/diaspora.py`
- `data/raw/` (output artifacts, gitignored)