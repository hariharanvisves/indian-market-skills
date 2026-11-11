---
name: indian-market-data-pitfalls
description: Index of failure modes in Indian market and broker data — IST-to-UTC date shifts (toISOString one day early), survivorship bias in Nifty universes, split/bonus price cliffs, statement drift, cross-source duplicates, scheme-name merges, parser coverage, paise precision. Use when ingesting NSE bhavcopy, Zerodha/Groww statements, CAS/CAMS files or AMFI NAV history, building a backtest universe, or debugging wrong holdings, dates shifted by a day, duplicate transactions or an implausible return. Links to the skill owning each detail.
license: MIT
compatibility: Applies to NSE/BSE market data and Indian broker/RTA statement formats.
metadata:
  author: hariharanvisves
  version: "1.1"
  jurisdiction: India
  verified: "2026-11-11"
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
  tax rate (see [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md)).
- A test suite pinned to `TZ=UTC` **passes with the bug fully present**. Timezone
  assertions must run in a zone where the defect is observable, or they are a
  false green.

Never round-trip a date-only value through `toISOString()`. Prefer explicit
year/month/day parts, and for a bar timestamp pick a fixture where the UTC and
exchange dates actually differ (an NSE 09:15 IST bar is 03:45Z — same date, so it
cannot discriminate).

Detector: run date tests with `TZ=Asia/Kolkata` and assert a date-only input
comes back as the same calendar date.

## 2. Survivorship bias in index universes

A universe built from **today's** index constituents and backtested over ten
years silently excludes every company that was delisted, merged or dropped —
i.e. most of the losers. The result is inflated and looks clean.

Resolve membership **as of each bar's date** from a point-in-time constituents
table that retains delisted names; the master table never deletes rows. State the
earliest date the membership data reaches rather than quietly starting the
backtest there. Reconstruction, the ever-member union and its limits, and ticker
renames are in
[nse-universe-survivorship](../nse-universe-survivorship/SKILL.md).

Detector: the earliest membership date is a field on every backtest result.

## 3. Corporate-action price breaks, and the cleaning rule that eats your data

An unadjusted series shows a 50% "fall" on a 1:2 split or a 1:1 bonus. A bonus of
`a:b` (a new shares for every b held) multiplies the price by `b / (a + b)`, so a
3:2 bonus is a 60% fall and a 4:5 bonus a 44% fall: most corporate actions trip a
40% one-day filter. Filters that discard
everything before the last implausible move look sensible and are dangerous: a
recent demerger can delete the entire window you actually need.

Two rules:

- **Prefer "keep the longest clean run" over "keep everything after the last
  defect."** It degrades gracefully whichever end the break lands on.
- A defect at index `i` means the move **into** `i` is bad, so `i` is the
  untrustworthy print and belongs to neither surviving segment. Keeping it as the
  first element of the later segment re-imports the break.

Detector: before shipping any price-sanity filter, **measure where defects
actually fall** in real series. The premise "bad bars cluster at the start of history" is testable
in one pass, and recent corporate actions falsify it.

Bonus and split are **not transfers**. For their cost and acquisition-date
treatment see [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md); do
not assume the two behave alike. Parsing and adjustment rules are in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).

## 4. Broker statement format drift

The same statement, re-exported months apart, differs: scheme and security names
change with identical units, NAV and amount, and dates shift by 1-3 days,
non-uniformly. The non-uniformity marks it as order date vs allotment date, a
semantic difference and not the timezone bug in §1. It moves the STCG/LTCG
boundary for anything held near 12 months, so decide which date the store holds
and enforce it **in the parser**, not by "which file was uploaded".

Detector: a uniform offset between two exports is §1; a non-uniform one is drift.

Detect formats by header-row signature (section 1), scan for the header row
(section 2) and handle legacy OLE2 `.xls` (sections 1 and 16) as in
[indian-broker-statement-formats](../indian-broker-statement-formats/SKILL.md);
the drift itself is its section 6.

## 5. Cross-source duplicate transactions

The same purchase arrives from a broker feed and again from the RTA/CAS
statement, with **different precision** (units at 2dp vs 3dp, amounts differing by
rupees). An exact-match key cannot see them, and the store silently doubles cost
basis, so invested total, P&L, XIRR and every FIFO lot match are wrong.

Dedupe on a **price-free** key with **absolute** (not percentage) quantity and
date tolerances, never on amount alone (a second SIP instalment must survive), and
reconcile per instrument against a holdings statement. The rules and tolerances
are owned by [mf-scheme-matching](../mf-scheme-matching/SKILL.md) section 8; float
boundary handling is in §8 below.

## 6. Mutual fund scheme-name matching

Matching schemes by **token overlap** merges distinct funds ("Direct" vs
"Regular", "Growth" vs "IDCW" have different NAVs), and merging corrupts FIFO lots
irreversibly. Parse every token into exactly one slot and fail the match on any
leftover; a failed parse is an unresolved record, which is recoverable. Rules,
rename allow-lists and uniqueness requirements are in
[mf-scheme-matching](../mf-scheme-matching/SKILL.md).

Detector: Direct and Regular plans of one scheme must stay unmatched.

## 7. Parser health: "produced something" is not success

A parser over a repeating record format can return 3 records from a 312-row file
and report success if the caller only throws on a *completely* empty parse. Track
a coverage ratio (candidate rows vs records emitted) as a warning, and check an
arithmetic identity (`units x price == amount`), since a rising count proves rows
were read, not read correctly. Details are in
[indian-broker-statement-formats](../indian-broker-statement-formats/SKILL.md)
sections 12 and 13.

## 8. Money precision

Use **integer paise** for monetary arithmetic; float drift on threshold and cess
boundaries silently corrupts a tax figure.

- `Math.round` is **half-up toward +∞**, so it is asymmetric for negatives:
  `Math.round(-2.5)` is `-2`. A debit and its matching credit then fail to net to
  zero. If you need symmetry, use `sign(v) * round(abs(v))` and normalise `-0`.
- Comparing values at **different precisions**: never equate two roundings. Use
  `|a − b| <= tolerance`, because two roundings of nearby values can straddle a
  boundary. Round the **difference** to a few decimals (or add an epsilon) before
  the `<=`: `14.045 - 14.04` is `0.005000000000000782` in binary float, so a pair
  sitting exactly on a 0.005 tolerance fails a bare `<=` by 7.8e-16.
- When one field is derived from others, **derive it** rather than rounding it
  independently, so identities like `gain == consideration − cost` cannot drift.

Detector: a debit and its matching credit net to exactly zero, and a pair sitting
exactly on the tolerance passes.

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

## Verifying an implementation

- Date tests run under `TZ=Asia/Kolkata` on a fixture whose UTC and IST dates
  differ (§1).
- A price filter given a defect near the **end** of a series keeps the longest
  clean run, with the defect bar in neither segment (§3).
- Importing one holding from broker and RTA leaves units equal to the holdings
  statement (§5).
- A real file passes the coverage ratio and the amount identity (§7).
- A short constituents list or a stale mirror is refused before any write (§9).

## Scope

Informational engineering guidance for NSE/BSE market data and Indian broker and
RTA statements. For charge computation see [indian-equity-charges](../indian-equity-charges/SKILL.md);
for gain taxation see
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).
