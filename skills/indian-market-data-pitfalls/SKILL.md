---
name: indian-market-data-pitfalls
description: Failure modes specific to Indian market and broker data — timezone date shifts from IST, survivorship bias in index universes, corporate-action price breaks, broker statement format drift, cross-source duplicate transactions, and scheme-name matching for mutual funds. Use when ingesting bhavcopy, broker statements, CAS/CAMS files or NAV history, when building a backtest universe, or when debugging wrong holdings, duplicate transactions or an implausible return figure.
license: MIT
compatibility: Applies to NSE/BSE market data and Indian broker/RTA statement formats.
metadata:
  author: hariharanvisves
  version: "1.0"
  jurisdiction: India
---

# Indian Market Data Pitfalls

Each item below is a defect class that passes tests, produces plausible numbers,
and is found only by looking for it. Ordered by how much damage it does silently.

## 1. IST → UTC date shift

`new Date('06 Mar 2025')` builds **local midnight**; `.toISOString()` renders it
in UTC. Under IST (UTC+5:30) that emits the **previous day**.

The tell is a **uniform** off-by-one across every row. A genuine semantic
difference — trade date vs settlement date — varies by instrument and weekend. A
constant one-day offset is your own transform.

Two consequences that make it expensive:

- It moves a holding across the **12-month capital-gains boundary**, changing the
  tax rate.
- A test suite pinned to `TZ=UTC` **passes with the bug fully present**. Timezone
  assertions must run in a zone where the defect is observable, or they are a
  false green.

Never round-trip a date-only value through `toISOString()`. Prefer explicit
year/month/day parts, and for a bar timestamp pick a fixture where the UTC and
exchange dates actually differ (an NSE 09:15 IST bar is 03:45Z — same date, so it
cannot discriminate).

## 2. Survivorship bias in index universes

A universe built from **today's** index constituents and backtested over ten
years silently excludes every company that was delisted, merged or dropped —
i.e. most of the losers. The result is inflated and looks clean.

Resolve membership **as of each bar's date** from a point-in-time constituents
table that retains delisted names. That means the master table never deletes rows.

Reconstructing point-in-time membership from index-change announcements is the
usual route, and it floors out at whatever year the exchange's archive reaches.
State the floor rather than quietly starting the backtest there.

## 3. Corporate-action price breaks, and the cleaning rule that eats your data

An unadjusted series shows a 50% "fall" on a 1:2 split. Filters that discard
everything before the last implausible move look sensible and are dangerous: a
recent demerger can delete the entire window you actually need.

Two rules:

- **Prefer "keep the longest clean run" over "keep everything after the last
  defect."** It degrades gracefully whichever end the break lands on.
- A defect at index `i` means the move **into** `i` is bad, so `i` is the
  untrustworthy print and belongs to neither surviving segment. Keeping it as the
  first element of the later segment re-imports the break.

Before shipping any price-sanity filter, **measure where defects actually fall**
in real series. The premise "bad bars cluster at the start of history" is testable
in one pass, and recent corporate actions falsify it.

Bonus and split are **not transfers** — they re-allocate cost across a larger
quantity and retain the original acquisition date for holding-period purposes.

## 4. Broker statement format drift

The same statement, re-exported months apart, differs. Observed repeatedly:

- **Scheme and security names change.** "Kotak Emerging Equity Fund" becomes
  "Kotak Midcap Fund"; an index fund gains a "50" in its name. Identical units,
  NAV and amount on each row.
- **Dates differ by 1–3 days, non-uniformly.** That non-uniformity means it is
  *order date vs allotment date* — a genuine semantic difference, not the
  timezone bug in §1. Whichever export you ingest sets the lot's acquisition
  date, which **moves the STCG/LTCG boundary** for anything held near 12 months.

Decide which date the store holds, and enforce it **in the parser**. If the rule
lives in "which file someone happened to upload", the answer changes per upload.

Detection rules that survive:

- **Detect format by header-row signature, not filename.** Filenames are a
  convention; the header is the contract.
- **Scan for the header row rather than assuming an index.** Statements carry a
  variable number of preamble rows.
- Legacy `.xls` from RTA portals is **OLE2** (magic `d0cf11e0`), not zip-based
  OOXML. A reader that only handles OOXML fails on real files.

## 5. Cross-source duplicate transactions

The same purchase arrives from a broker feed and again from the RTA/CAS
statement, with **different precision** — units at 2dp from one, 3dp from the
other; amounts differing by rupees. An exact-match dedupe key cannot see them,
and the store silently doubles cost basis. Everything downstream is then wrong:
invested total, P&L, return %, XIRR, and every FIFO lot match.

Rules that worked:

- Match on **(instrument, side, date ± tolerance, quantity ± tolerance)**, and
  make the quantity tolerance **absolute, not a percentage**. A percentage bound
  scales with trade size: 0.5% of a 10,000-unit purchase is 50 units, which
  merges genuinely different trades.
- Keep the key **price-free**. Prices legitimately differ between sources.
- **Never dedupe on amount alone** — a second SIP instalment in the same month
  has a near-identical amount and must survive.
- Round **before** comparing against a tolerance. `14.045 - 14.04` is
  `0.005000000000000782` in binary float, so a pair sitting exactly on a 0.005
  tolerance fails a bare `<=` by 7.8e-16.
- Reconcile per instrument against a holdings statement and expect a ratio of
  **1.000**. A ratio of exactly 2.000 is a duplicate; 1.1–1.9 usually means one
  source covers only part of the position. Aggregate the statement per instrument
  first — a fund held in two folios reads as a spurious multiple otherwise.

## 6. Mutual fund scheme-name matching

Matching schemes by **token overlap** merges distinct funds. "Direct" vs
"Regular" and "Growth" vs "IDCW" are different schemes with different NAVs, and
merging them corrupts FIFO lots irreversibly.

What works is a **total parse**: consume every token of the name into exactly one
slot — identity, plan, or option — and **fail the match if any token fits no
slot**. A failed parse is an unresolved record, which is recoverable; a wrong
match is not.

Specifics that matter:

- "Fund" and "Scheme" are **boundary words**, not deletable noise.
- Words like *growth*, *dividend* and *bonus* appear inside real scheme names
  ("Axis Growth Opportunities Fund", "SBI Dividend Yield Fund"), so they cannot
  be treated as option markers wherever they appear.
- A repeated option ("Direct Growth Plan Growth Option") is **one** option, not a
  conflict.
- Handle AMC renames with an **explicit, sourced allow-list**. Fuzzy or
  edit-distance matching reintroduces exactly the false-merge class this design
  eliminates.
- Require **uniqueness**: zero candidates means unknown, more than one means
  ambiguous, and both must reject rather than pick.
- A **declared but non-matching** AMC is disqualifying evidence, not missing
  evidence.

## 7. Parser health: "produced something" is not success

A parser over a repeating record format can return 3 records from a 312-row file
and report success, if the caller only throws on a *completely* empty parse.

Compute a **coverage ratio** — candidate rows detected against records emitted —
and surface a shortfall as a warning. Keep it a warning, not a throw, when the
denominator is a heuristic that must never reject a good input.

Two corollaries:

- A record count jumping 3 → 301 proves rows were *read*, not read *correctly*.
  The binding check is an **arithmetic identity the data must satisfy**
  (`units × price == amount`), which a transposed column mapping fails.
- Make sure the coverage **denominator** is right. A ratio whose denominator is
  also broken under-reports the very failure it exists to catch.

## 8. Money precision

Use **integer paise** for monetary arithmetic; float drift on threshold and cess
boundaries silently corrupts a tax figure.

- `Math.round` is **half-up toward +∞**, so it is asymmetric for negatives:
  `Math.round(-2.5)` is `-2`. A debit and its matching credit then fail to net to
  zero. If you need symmetry, use `sign(v) * round(abs(v))` and normalise `-0`.
- Comparing values at **different precisions**: never equate two roundings. Use
  `|a − b| <= tolerance`, because two roundings of nearby values can straddle a
  boundary.
- When one field is derived from others, **derive it** rather than rounding it
  independently, so identities like `gain == consideration − cost` cannot drift.

## 9. Sanity gates on ingested data

A fetch succeeding is not the data being current — a third-party mirror serving
years-old data is the normal failure, not the exotic one.

- Gate a write on a **plausibility floor** (refuse a constituents list of 450
  when ~500 is expected).
- Before a bulk re-derivation, **diff the would-be result for duplicates against
  the current store and abort on any increase.** In an append-then-invert
  pipeline, a change applied twice cannot be inverted.
- Repair only records carrying a **provable defect signature**, never "everything
  re-derivable."

## Scope

Informational engineering guidance. For charge computation see
[indian-equity-charges](../indian-equity-charges/SKILL.md); for gain taxation see
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).
