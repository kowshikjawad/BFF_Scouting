# Tasks

## 1. Persistence layer

- [x] 1.1 Create the SQLAlchemy engine/session module bound to
      `settings.database_url`. Verify by connecting and confirming
      `data/processed/shonartalent.db` is created.
- [x] 1.2 Define `PlayerORM`: the 8 `Player` profile fields plus 5 nullable
      tactical metric columns, keyed by player id. Verify with
      `Base.metadata.create_all()` and inspecting the resulting table's
      columns.
- [x] 1.3 Implement `upsert_player(session, player_id, **fields)` with
      create-if-missing and update-only-supplied-fields semantics (per
      design.md decision #2). Verify with tests covering both spec
      scenarios: "Upsert creates a new record" and "Upsert updates only
      the supplied fields."
- [x] 1.4 Implement a `get_player(session, player_id)` read returning
      unset tactical metrics as absent (`None`), not zero. Verify with
      tests covering "Profile present, all tactical metrics absent" and
      "Partial tactical metrics." Run
      `pytest tests/backend/test_player_records.py -v`.

## 2. Diaspora reference data

- [x] 2.1 Create `data/seed/diaspora_players.yaml` with the 6 researched
      players (Hamza Choudhury, Tariq Kazi, Jamal Bhuyan, Fahamedul Islam,
      Cuba Mitchell, Shamit Shome), each with a `last_verified_date` and an
      inline comment noting any unconfirmed detail (e.g. Cuba Mitchell's
      post-February-2026 club). Verify by hand-reviewing the file against
      the research citations in `proposal.md`.
- [x] 2.2 Implement `scrapers/diaspora.py` to load and validate the YAML
      file against the `Player` schema, with no network calls. Verify with
      a test asserting all 6 records load successfully and each has a
      `last_verified_date`, run with networking disabled/mocked to prove
      the "no network request" spec requirement.

## 3. Domestic league scraper (BPL/BFL)

- [x] 3.1 Implement the football-vs-cricket source disambiguation guard as
      a small reusable function. Verify with tests for both spec
      scenarios: "Ambiguous source rejected" (bare "BPL" reference) and
      "Football-qualified source accepted" (source naming football clubs
      e.g. Bashundhara Kings).
- [x] 3.2 Implement `scrapers/bpl.py` scraping Wikipedia's Bangladesh
      football league season article(s) via `requests` + `BeautifulSoup4`
      for bio/squad fields only (name, age, position, height, strong foot,
      club), with defensive per-row parsing that logs and skips a
      malformed row instead of aborting the scrape. Note: implementation
      verified the real source is each club's *per-season* Wikipedia
      article, not the league-wide season page (see design.md decision #4
      addendum) -- height/strong foot are not available from this source
      and stay null; not every club has a dedicated article, handled as a
      per-club skip.
- [x] 3.3 Add a fixture-based test using a captured snapshot of a
      Wikipedia season page's squad table HTML (saved under
      `tests/fixtures/`), verifying parsed bio fields and that no tactical
      metric field is populated for any domestic player. Run
      `pytest tests/scrapers/test_bpl.py -v`.

## 4. FBref opportunistic backfill

- [x] 4.1 Implement a sliding-window rate limiter (max 10 calls per
      rolling 60 seconds, per design.md decision #3) as a reusable
      utility. Verify with a unit test that asserts pacing behavior
      without making real network calls (e.g. using a fake clock).
- [x] 4.2 Implement `scrapers/fbref.py`: for a tracked player, check
      whether their current competition is one of `soccerdata.FBref`'s
      supported competitions; skip without error if not, and attempt a
      rate-limited fetch-and-persist via the upsert operation if so.
- [x] 4.3 Add tests for both coverage scenarios: a tracked player outside
      FBref's coverage (assert no fetch attempted, metrics untouched) and
      a tracked player inside coverage (mock `soccerdata.FBref` so the
      test needs neither network access nor a real Chrome install). Run
      `pytest tests/scrapers/test_fbref.py -v`.
- [x] 4.4 Make any FBref test that would require a real Chrome/chromedriver
      binary skip gracefully (`pytest.mark.skipif`) rather than fail when
      the binary isn't present, so the rest of the suite stays runnable in
      environments without it. Verify by running the full suite in this
      project's current `.venv` (no Chrome installed here) and confirming
      a skip, not a failure or error.

## 5. Orchestration

- [x] 5.1 Wire `scripts/run_scrapers.py` to run the diaspora, domestic, and
      FBref sources in sequence, each in its own try/except, persisting
      each source's successful results immediately via `upsert_player`
      rather than batching all three before any persistence.
- [x] 5.2 Collect and report failures from any source at the end of the
      run (e.g. a non-zero exit with a summary) without raising until all
      three sources have been attempted, so a later source's failure can't
      prevent an earlier source's success from being reported too.
- [x] 5.3 Add a test simulating one source raising an exception and
      asserting the other two sources' results are still persisted
      (verifies the "one source fails, others still persist" scenario),
      using an in-memory SQLite database. Run
      `pytest tests/scrapers/test_run_scrapers.py -v`.

## 6. Environment and documentation

- [x] 6.1 Add a Chrome/chromedriver install step to `Dockerfile` for the
      FBref scraper. Verify with `docker compose build` succeeding (if
      Docker is unavailable in the dev environment, verify the Dockerfile
      syntax manually and note this as a follow-up verification for a
      Docker-equipped environment). Note: Docker CLI present but daemon
      not running in this environment -- manually reviewed, live build
      verification is a follow-up for a Docker-equipped environment. Also
      added missing `COPY scripts/` and `COPY data/seed/` (the image
      previously never copied the orchestration script or the new seed
      data it depends on).
- [x] 6.2 Document the local Chrome prerequisite for the FBref scraper in
      the README's Quick Start / Prerequisites section.
- [x] 6.3 After implementation, pin the resolved `soccerdata` dependency
      chain (including its SeleniumBase/chromedriver-related
      dependencies) in `requirements.txt`. Verify with
      `pip freeze | grep -iE "soccerdata|seleniumbase|selenium"`.

## Workflow follow-up

- Run `openspec validate --changes "player-data-foundation" --strict`
  before archiving.
- Archive the change (`/opsx:archive`) once implementation and tests are
  complete, which syncs both delta specs into `openspec/specs/`.
