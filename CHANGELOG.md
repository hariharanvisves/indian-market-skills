# Changelog

## 1.2.0 — 2026-11-26

### Added
- New skill `nse-official-mcp`: NSE's two cash-market MCP servers
  (`nse-bhavcopy`, `cm-market`) and their 36 read-only tools. It covers the
  non-commercial and no-AI-training terms, history prices that are not adjusted
  for splits or bonuses, empty results as failures, holiday date snapping,
  3-month history chunks, freshness outside market hours, and the absence of any
  F&O or option-chain server. With eval cases.
- `indian-capital-gains-tax`: STT is not deductible in computing capital gains.
  The specified-mutual-fund test now covers the fund-of-funds limb, the order of
  classification checks, and failing closed on an unknown sub-category.
  Grandfathering explicitly covers equity-oriented fund units.
- `itr-filing-schedules`: a new section on the filing window. It covers due dates
  (31 Jul, 31 Aug, 31 Oct, 30 Nov), belated returns that cannot opt out of the new
  regime, and the 12-month revised-return window with its fee. The §87A rebate is
  resident-only, so a missing residential status must be an error. Schedule CG
  must use the same netted records as the tax engine.
- `indian-broker-statement-formats` and `mf-scheme-matching`: Groww reversal
  twins, rejecting a capital-gains report uploaded as a transaction ledger, CAS
  PDF folio and stamp-duty traps, and matching a CAS scheme by ISIN first. Also
  one shared folio normaliser, whole-word plan detection, and unit-dust tolerance.
- `kite-connect-safety`: planning separated from approved execution, with one
  sole order-placing function. Owned quantity counts final-status rows only. A
  test trap where SQL `SUM` skips NULL.
- `momentum-factor-research`: rank only symbols priced on the latest session.
- `backtest-engine-correctness`: what a cached backtest result must be keyed on.
- `nse-bhavcopy-corporate-actions`: the observed `www.nseindia.com` to
  `www.nseindia.in` redirect, and a caveat that Yahoo's `chartPreviousClose` is
  not the previous session's close.

### Changed
- All 19 skills were restructured to one standard:
  - descriptions written to trigger the skill, with real task wording and symptoms;
  - a numbered Core rules block at the top, linking to each section;
  - Rule, Why and Detector sections;
  - worked examples and short Python sketches for the rules most often got wrong.
- Long catalogues and dated history moved to `references/` files in 11 skills.
  Facts asserted by the evals and rates listed in `data/rates.json` stay in
  SKILL.md.
- A token diff confirmed that no rate, date, section, circular ID or URL was lost.
- `CONTRIBUTING.md` now has a "Skill structure" section, and `scripts/validate.py`
  checks links in `references/` files.
- Five eval regexes were loosened. They had rejected correct wording such as
  "applies only to the buy side".
- `indian-broker-api-safety`: Fyers API rate limits from 16 Oct 2026. The NSE
  10-orders-per-second threshold now cites NSE/INVG/67858.
- `itr-filing-schedules`: ITR-1 allows up to two house properties for AY 2026-27.
- Primary citations were added for NSE/FA/73061, NSE/FATAX/73524, NSE/FAOP/68747
  and the 2020 SEBI circular that introduced the IDCW name.
- `docs/unverified-claims.md`: three rows resolved and removed, and two narrowed.
  New rows cover the NSE host redirect, Yahoo `chartPreviousClose`, the
  specified-mutual-fund definition before 1 Apr 2026, the Income-tax Act 2025
  section numbers read only on mirror sites, and Circular 07/2026.

### Fixed
- `indian-capital-gains-tax` said all transaction charges never net against a
  gain. Only STT is barred.

## 1.1.3 — 2026-11-11

### Fixed
- Cursor loaded the skills but no reviewers. `.cursor-plugin/plugin.json` now
  points `agents` at `reviewers/`.
- Reviewers set `readonly: true`. Cursor ignores `tools:` and uses that flag to
  block writes. `scripts/validate.py` requires it.

## 1.1.2 — 2026-11-11

### Fixed
- Gemini CLI install printed four "Error loading agent" warnings. Gemini loads
  every file in `agents/` and rejects Claude Code tool names. The reviewers now
  live in `reviewers/`, and `.claude-plugin/plugin.json` lists them under
  `agents`, so Claude Code loads them and Gemini skips them.
- `scripts/validate.py` fails if a root `agents/` folder returns or if the
  plugin's `agents` list and `reviewers/` disagree.

## 1.1.1 — 2026-11-11

### Added
- `scripts/sync_issues.py` opens one GitHub issue (label `unverified-claim`) for
  each row of `docs/unverified-claims.md` that has none. It is a dry run unless
  you pass `--apply`.
- README: results of running the evals with and without the plugin.

### Changed
- `scripts/run_evals.py` calls `claude` from an empty folder, so a `--baseline`
  run can't read the skills from the repo. `--out DIR` saves every answer.

### Fixed
- `backtest-engine-correctness` eval 2 no longer fails a correct answer that
  says "`1/years` is too large".

## 1.1.0 — 2026-11-11

### Added
- Five skills: `fno-tax-and-charges`, `corporate-action-taxation`,
  `foreign-equity-for-residents`, `nse-trading-calendar` and
  `indian-broker-api-safety`.
- Packaging as a Claude Code plugin and marketplace, a Codex plugin, a Cursor plugin
  and a Gemini CLI extension. Also installable with `npx skills add`.
- `/review-tax`, `/review-ingestion`, `/review-backtest` and `/review-broker`
  commands, each dispatching the matching reviewer agent.
- Trigger and answer evals for every skill (`evals/cases/`) and a runner,
  `scripts/run_evals.py`, with a `--baseline` mode.
- `data/rates.json`, a dated, machine-readable rate table checked against the
  skill that owns each rate.
- `docs/unverified-claims.md`, `scripts/validate.py` with CI, issue and pull
  request templates, an icon, `CONTRIBUTING.md`, `CLAUDE.md` and `AGENTS.md`.

### Changed
- Every existing skill was re-checked against primary sources and now carries a
  `metadata.verified` date. Corrections include:
  - LTCG holding period counted in calendar months, not `days_held > 365`.
  - Form 67 renamed Form 44 under the Income-tax Rules 2026.
  - Schedule AL threshold of ₹1 crore.
  - §288A and §288B are one rounding rule.
  - Intraday STT is sell-only.
  - DP charges by broker.
  - Settlement-price and session-time rules from SEBI's 2026 circulars.
  - Weekly expiries limited to one benchmark index per exchange.
  - Bhavcopy date ranges and columns.
  - AMFI NAVAll.txt now has 8 columns.
  - Kite static-IP requirement from 2026-04-01.
- Reviewer agents are read-only (`Read, Glob, Grep`) and load the new skills.
- Facts owned by one skill are linked from others instead of restated.

## 1.0.0

- Initial release: 13 skills and 4 reviewer agents.
