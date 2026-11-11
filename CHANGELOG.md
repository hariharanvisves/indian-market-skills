# Changelog

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
