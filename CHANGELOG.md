# Changelog

## 1.3.0 — 2026-11-26

### Added
- `non-equity-capital-gains`: capital gains on land, buildings, gold, unlisted
  shares and depreciable assets. Covers:
  - the 24-month test;
  - the 23 Jul 2024 choose-the-lower option for resident individuals and HUFs;
  - indexation and the 1 Apr 2001 FMV, including the previous owner's FMV for
    inherited assets;
  - stamp-duty value with its 110% tolerance;
  - the §74 block;
  - the §82, §85 and §86 exemptions and the deposit scheme.
- `nps-taxation`: NPS deductions by regime, the 14% and 10% employer limits, the
  ₹7.5 lakh aggregate perquisite, exit and partial-withdrawal exemptions, and the
  PFRDA 80% lump-sum option. The 60% exemption is read as a condition, so the
  most cautious figure treats the whole lump sum as taxable.
- Engineering rules:
  - `kite-connect-safety`: a risk verdict is bound to a fingerprint of the exact
    order.
  - `indian-broker-api-safety`: entry-side limits never block an exit.
  - `nse-trading-calendar`: entry and flatten times come from the session for the
    date.
  - `backtest-engine-correctness`: a stop that is gapped through fills at the gap
    price.

### Fixed
- The enacted Finance Act 2026 (Act No. 4 of 2026) replaces the Bill-as-introduced
  citations. Rows checked against it: the MAT rate and credit cap, the ₹400 crore
  reference year, the §263(1)(c) due-date table and the §428(b) fee.
- `itr-filing-schedules`:
  - No §234A interest on self-assessment tax paid before the due date (CBDT
    Circular 2/2015).
  - The foreign tax credit uses Indian tax on that income, not a "marginal rate".
  - CBDT Circular 07/2026 dates are confirmed.
- `fno-tax-and-charges`: the SEBI fee on exercised or assigned options also counts
  notional value.
- `indian-capital-gains-tax`:
  - The ₹1.25 lakh limit covers FY 2024-25 gains from before and after 23 Jul 2024.
  - The pre-2026 definition of a specified mutual fund is now stated.
- `corporate-action-taxation`:
  - Listed buybacks are keyed to the public announcement date (5 Jul 2019).
  - The Finance Act 2026 surcharge citation is corrected to §3(6).
- `foreign-equity-for-residents`:
  - The Black Money Act carve-out cites the enacted Finance (No. 2) Act 2024 §164.
  - The LRS TCS threshold counts per remitter; PAN is not named in the statute.
  - Schedule FA exchange rates and FAST-DS dates are now confirmed.
- `nse-bhavcopy-corporate-actions`:
  - The IL series was discontinued in 2018.
  - Yahoo `chartPreviousClose` matches the first bar for `1mo` too.
- `nse-options-mechanics`: the settlement rule before 3 Aug 2026 is now sourced.
- `backtest-engine-correctness`:
  - The closing-auction ±3% band is confirmed.
  - The iceberg rule starts on 8 Feb 2027.
- `indian-broker-api-safety`: Dhan sandbox and token facts now come from Dhan's own
  documentation.
- `docs/unverified-claims.md`: 24 rows resolved or reworded, and 28 open questions
  added. Most of the new ones come from the two new skills.

## 1.2.1 — 2026-11-26

### Fixed
- Code sketches that failed their own rules:
  - `kite-connect-safety`:
    - The order-value ceiling now fails closed on NaN, negative and missing values.
    - `place_once` claims the intent key atomically before sending, so concurrent
      presses and crashes cannot re-send.
    - Every exception after a send is treated as an unknown outcome.
    - Reconcile matches the tag that was sent.
  - `mf-scheme-matching`:
    - Dedupe tolerance now survives float error, and matching is one to one.
    - Unparseable names no longer merge with each other.
    - An empty or "-" ISIN no longer matches the first row of the AMFI file.
    - The folio normaliser no longer merges distinct folios.
  - `indian-broker-statement-formats`: format detection now accepts CAMS JSON,
    CSV and the ITD wrapper.
  - `indian-broker-api-safety`: the rate limiter is thread-safe and shared per
    API key.
  - `itr-filing-schedules`:
    - The loss reconciliation counts brought-forward losses.
    - TDS dedupe keeps credits that carry different TANs.
  - `foreign-equity-for-residents`: TCS uses the cumulative ₹10 lakh threshold.
  - `backtest-engine-correctness`: the look-ahead test now catches a fill at the
    bar's own close.
  - `nse-trading-calendar`: the settlement function refuses dates before T+1.
  - `nse-universe-survivorship`: the ISIN issuer check rejects placeholders.
  - `indian-equity-charges`: STT rounding is half-up.
- Meaning lost in the 1.2.0 restructure:
  - `indian-capital-gains-tax`: the SGB date regime and the debt-fund definition
    are back.
  - `fno-tax-and-charges`: the Core rules on loss carry-forward and exercise STT
    match the body again.
  - `itr-filing-schedules`: the belated-return loss rule is narrow again.
  - `nse-official-mcp`: the Terms of Use simulation clause is not narrowed.
- Primary sources added, with rows removed or narrowed in
  `docs/unverified-claims.md`:
  - 2025 Act §200, §201, §206 and the bonus holding period (Gazette text).
  - F&O ban exit at 80% (SEBI Master Circular).
  - Market-wide halt durations.
  - T+0 batch dates. This corrects "top 500 from 31 Jan 2025".
  - FBIL publication time.
  - NSE circular 62424.
  - The BL series meaning.
  - BSE weekly-expiry weekdays (BSE notices 20241128-70, 20250617-11, 20250623-59).
  - The hosted Kite MCP is read-only.
  - The MAT credit-cap base is corrected to "tax payable on total income".
- Reviewer agents: new checklist items for status maps, market orders, shared
  limiters, tag length, static IP, price-free dedupe keys and ETF-before-INF order.

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

- Eight Income-tax Act 2025 section numbers are now confirmed against the Gazette
  text (Act No. 30 of 2025). §115BBH maps to §194(1) Table Sl. 4. The 31 August
  due date and the §428(b) revised-return fee are marked as Finance Act 2026
  changes; the enacted text of that Act was not read.
- `nse-official-mcp`: added three limits from NSE's general Terms of Use. They bar
  scraping the website, storing or redistributing its content, and using its data
  for virtual trading or simulation.

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
