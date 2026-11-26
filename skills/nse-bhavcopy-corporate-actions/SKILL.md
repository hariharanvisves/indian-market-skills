---
name: nse-bhavcopy-corporate-actions
description: Building an adjusted NSE price history from bhavcopy (legacy cm*bhav.csv, sec_bhavdata_full, CM-UDiFF) and the NSE corporate-actions API — which file format and host covers which dates, EQ vs BE/BZ series filtering, column-layout traps, parsing split/bonus/dividend subject text, adjustment factors, banded post-action price walks, and caching Yahoo .NS fetches. Use when ingesting NSE bhavcopy, a bhavcopy downloader stops getting files after July 2024, adjusting prices for splits and bonuses, parsing corporate-action subjects, debugging a price cliff or one-day 50% drop on a split date, delivery quantity of 0, a missing symbol history, or fetching Yahoo Finance prices for .NS tickers, even if the user never says "bhavcopy". Tax on bonus or split is corporate-action-taxation.
license: MIT
compatibility: Applies to NSE cash-market bhavcopy files and the NSE corporate-actions API. Format dates apply to NSE only.
metadata:
  author: hariharanvisves
  version: "1.2"
  jurisdiction: India
  verified: "2026-11-11"
---

# NSE Bhavcopy and Corporate Actions

Turns NSE bhavcopy files and corporate-action records into a price history whose
returns are right. Most defects here are silent: a wrong format date, a wrong
column, a wrong factor or a one-bar assumption each give plausible-looking prices.

Goes deeper than §1 and §3 of [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md)
(date shift, the "longest clean run" price-sanity rule). Read that first. Universe
and rename defects are in
[nse-universe-survivorship](../nse-universe-survivorship/SKILL.md).

Host paths and layouts below were observed to work. NSE changes them without
notice; re-probe before depending on one.

## Core rules

1. Legacy `cm*bhav.csv` ended 5 Jul 2024; CM-UDiFF replaces it from 8 Jul 2024. Check for it, or the pipeline stops without an error. [§1](#1-formats-hosts-and-the-delivery-data-floor)
2. Delivery quantity does not exist before 30 Sep 2019 and is absent from UDiFF. Emit unavailable fields **empty, never 0**. [§1](#1-formats-hosts-and-the-delivery-data-floor)
3. Prices use `SERIES == EQ`; liveness uses a wider same-ISIN series set. Do not merge the two filters. [§2](#2-prices-are-eq-only-identity-is-a-different-wider-set)
4. Read the header before any positional read; the symbol is not always column 1 and `PREVCLOSE` moves between layouts. [§3](#3-column-layout-the-symbol-is-not-column-1)
5. Parse `Re.` as well as `Rs.`; a bonus-plus-split subject is **two** price events. [§5](#5-corporate-actions-api)
6. Adjust strictly before the ex-date (`date < exDate`). A split from Rs.10 to Rs.2 is factor 0.2 (new over old), not 5. [§6](#6-adjustment-rules)
7. Ordinary dividends stay raw and rights are not adjusted by default. Mergers and demergers get no invented factor. [§6](#6-adjustment-rules)
8. A correct factor can still show as a multi-session walk in a banded stock; do not assume one-bar rebasing. [§7](#7-banded-rebasing-an-action-can-take-several-sessions-to-show)
9. The bhavcopy path needs its own price sanitiser or a split books as a fabricated crash. [§8](#8-price-sanity-guard-on-the-bhavcopy-path)

## 1. Formats, hosts and the delivery-data floor

| Format | Range | Notes |
|---|---|---|
| `content/historical/EQUITIES/<YYYY>/<MON>/cm<DDMONYYYY>bhav.csv.zip` | served back to 1995; last file 5 Jul 2024 (legacy) | OHLC, volume, turnover, prev close; `TOTALTRADES` and `ISIN` columns from about late 2011 (absent in Jan 2011 files) |
| `products/content/sec_bhavdata_full_<DDMMYYYY>.csv` | 30 Sep 2019+, still published | adds average price and delivery quantity/percent; no ISIN column |
| `content/cm/BhavCopy_NSE_CM_0_0_0_<YYYYMMDD>_F_0000.csv.zip` (CM-UDiFF common bhavcopy) | from 8 Jul 2024 | replaces the legacy file (NSE circular 62424, 12 Jun 2024); has ISIN, no average price, no delivery data |

Source for the UDiFF date: NSE all-reports page. Legacy bhavcopy was discontinued
on 8 Jul 2024. A pipeline hard-wired to the legacy name stops getting files on that
date without an error unless it checks.

Rules:
- Fetch archives from `nsearchives.nseindia.com`. The API host moved: `www.nseindia.com`
  `/api/...` paths 301-redirect to `www.nseindia.in` (observed 2026-11-26). Keep the host
  in one constant and make a stalled export fail loudly. Read
  [references/nse-hosts-and-api-access.md](references/nse-hosts-and-api-access.md)
  when a fetch returns 403, a redirect or nothing.
- Delivery quantity **does not exist before 30 Sep 2019** (a 2019-09-27 request
  404s, 2019-09-30 serves) and is absent from UDiFF, so after 8 Jul 2024 it comes
  only from `sec_bhavdata_full`. Trade count is absent before about late 2011.
  Emit unavailable fields **empty, never 0**, so a real zero-delivery session and an
  unavailable field do not look alike.
- Likewise leave `AvgPrice` empty for layouts that lack it. A synthetic
  `(high+low)/2` is indistinguishable from the exchange's figure downstream.
- A missing file can come back as an HTML body: HTTP 404 on `nsearchives`, HTTP 200
  on `niftyindices.com`. Verify `PK`/CSV header bytes, not the status.

Detector: assert each date range parsed yields the expected column set; fail if a
trading day returns zero rows.

## 2. Prices are EQ only; identity is a different, wider set

Rule: for **prices**, keep `SERIES == EQ`. The same symbol also appears as BE, BL,
GS and others on the same day, and mixing series double-counts a day.

Rule: for "is this listing still alive" (termination dates, rename windows), use a
**wider** set. Measured over the ISIN-bearing years by checking whether the same
symbol's other-series row carries the same ISIN as its EQ listing: BE, BZ, BL, IL,
SM and ST are the same security under a trading restriction. Of 151+ series codes,
the N-series, Y/Z/W series, GS, GB, MF and the like carried different ISINs, so
they are different instruments.

Why: BE and BZ are trade-for-trade segments (NSE series legend). A
symbol moved into one is the same listing under surveillance, not a delisting.
Dropping those series from the liveness test fabricates a termination date at the
migration. One symbol was measured as ending 252 days early with 68 sessions
discarded, which opened a window admitting a different issuer that then co-traded
with it. SME symbols moving `SM -> ST` did the same until ST was added; 167 symbols
carried a wrong first/last day and 13 "predecessors" were still trading.

Do not harmonise the two filters. One answers "what is the price", the other "is it
alive". Enumerate every series code in your corpus rather than assuming the list.

Detector: for each symbol, compare last EQ session to last session in any identity
series; a gap of months is the signature of a series migration.

## 3. Column layout: the symbol is not column 1

Rule: read the header before any positional read.

Why: an exported file named `daily_prices` keyed on symbol, with header
`Date,Symbol,...`, has the **date** first. Two sessions in one hour got it wrong:
`grep -c '^SYMBOL,'` returned 0 on a symbol with thousands of rows, and
`cut -f1 | sort -u | wc -l` reported 4,194 "symbols", which is the count of distinct
dates. The dangerous case is a consistent wrong answer on both sides of a diff.

Rules:
- Read the header before any positional command. Assert it in the producer and in
  the check, not in a comment.
- Append new columns, never insert, so positional readers stay valid.
- A zero from grep on a symbol that must exist is a probe failure far more often
  than a data failure.
- Anchor one side of any comparison on an independently known quantity (a manifest
  symbol count), so a wrong column cannot agree with itself.
- `sec_bhavdata_full` has a leading space after each comma (`ZOMATO, EQ`); legacy and
  UDiFF files do not. `grep '^ZOMATO,EQ,'` silently finds nothing.
- The legacy layout carries `PREVCLOSE` at 0-based index 7, while `sec_bhavdata_full`
  has `PREV_CLOSE` at index 3. Reading index 3 of a legacy row returns `HIGH`, which
  once produced hundreds of consecutive daily "splits" per symbol. Guard the
  **extraction**, not just the comparison.

Detector: compare a distinct-symbol count against a manifest count. A count equal
to the number of distinct dates means the date column was read.

## 4. Snapshot identity: content hash, not row count

Every published figure is a function of the price export, yet results rarely record
which export. Two exports can share a row count.

Rules:
- Identity is a SHA-256 of the content. Rows, symbols, date range and byte size are
  corroboration so a mismatch is diagnosable.
- Compute the digest in the single write pass; a direct write that bypasses the
  hashing emitter produces a manifest that does not describe the file. Write the
  manifest only after the stream flushes.
- Track the manifest (small) and ignore the data (large): a fresh clone then
  carries the identity of the export results were validated against, and a rebuilt
  file that disagrees is detectable.
- Missing manifest yields the literal `"unknown"`, never `""` or a made-up hash.
  Unrecorded build inputs are `null`, never `0`.
- Never hash the large file on a hot path; verify on demand.

Detector: edit one price without changing the row count and require the identity
to move.

## 5. Corporate-actions API

`nseindia.com/api/corporates-corporateActions?index=equities&from_date=DD-MM-YYYY&to_date=DD-MM-YYYY`
needs `index=equities`; access notes are in
[references/nse-hosts-and-api-access.md](references/nse-hosts-and-api-access.md).
The `subject` field is free text; every trap was found by reading unparsed rows,
which took price-affecting unparsed rows from 27 to 1. The three that change a
price factor follow. Traps 3-6, 8 and 9 (debentures, multiple dividends, separators,
ambiguous forms, two-tranche rights, ETFs) are in
[references/corporate-action-subject-traps.md](references/corporate-action-subject-traps.md):
read it when writing or fixing a subject parser.

1. **`Re` versus `Rs`.** NSE writes the singular for one rupee (`To Re.1/-`).
   Requiring `Rs` left every split-to-Re.1 unparsed, including large well-known
   ones.
2. **Compound actions.** `Bonus 1:1 And Face Value Split From Rs.2/- To Re.1/-` is
   **two** price events on one ex-date. Typing it as SPLIT alone understates the
   adjustment by 2x. Emit a compound type carrying both ratios.
7. **Split ratio orientation.** In one corpus every split ratio was `a>b` (`10:2`),
   so a bare `a/b` gives 5.0 where the price factor is 0.2. A fixture using `1:2`,
   the orientation that never occurs, cannot catch it.

Detector: print a coverage ratio each run (dividend rows with a parsed amount,
price-affecting rows with a parsed ratio) and warn below a floor, so a wording
change cannot zero a field silently.

## 6. Adjustment rules

- Split and bonus adjust prices **strictly before** the ex-date (`<`, not `<=`); the
  ex-date bar already trades adjusted. A 09:15 bar on the ex-date counts as on it.
  Compare dates, not timestamps. Volume scales inversely.
- Keep full precision. Re-rounding to tick size makes a 1:10 split accumulate drift.
- A 1-for-2 split (one share becomes two) is factor 0.5. A face-value split Rs.10
  to Rs.2 is 2/10 = 0.2 (new over old). Bonus 5:7 is 7/12.
- **Rights are not adjusted by default.** They are only partly a price event
  (discounted, requires subscription), and a naive share-count ratio overstates it.
- **Dividends stay raw.** Ordinary dividends leave the price series untouched; a
  material dividend may adjust derivatives, stored rather than derived.
- A malformed ex-date must raise, not skip: that is the "missed split".
- Mergers and demergers have no constant factor. Do not invent one.
- An action is filed under the ticker in force on its ex-date. If you fold renames,
  fold the action's symbol too, or the action is dropped while its target is
  queried.

Worked example: a 5:1 split (Rs.10 to Rs.2, factor 0.2) with raw closes 2273 the
day before the ex-date and 454 on it. The compound subject from §5 combines two
factors by multiplying them: a 1:1 bonus is 1/2 and Rs.2 to Re.1 is 1/2, so 0.25.
Typed as SPLIT alone it would apply 0.5, the 2x understatement.

```python
def adjust(bars, ex_date, factor):
    # bars: [(date, close, volume)] ; compare dates, not timestamps
    return [(d, c * factor, v / factor) if d < ex_date else (d, c, v)
            for d, c, v in bars]

# 2273 * 0.2 = 454.6 vs raw 454 on the ex-date: adjusted series is flat
assert abs(2273 * 0.2 - 454) < 1
combined = (1 / 2) * (1 / 2)   # bonus 1:1 x split Rs.2 -> Re.1 = 0.25
```

Whether bhavcopy prices are unadjusted for corporate actions: NSE publishes no
statement that settles it. **Verify empirically on a known split date**: pick a
symbol with a documented split, compare the close the day before and the day of, and
require a cliff of about the split ratio. One such check (a 5:1 split, raw close
2273 to 454, a 0.2 cliff) is how the pipeline's adjustment is proven.

Detector for that check: compare only **consecutive trading days** (cap the gap at
about 5). A partially harvested cache leaves a seam, and comparing across it reports
years of drift as one move. Mutation-test it: blank the adjusted column and
require failure; invert the factor and require failure.

## 7. Banded rebasing: an action can take several sessions to show

Rule: do not assume a corporate action re-bases the raw price in one bar. A 5:7
bonus (factor 0.5833) on one small-cap walked raw close 163.00 to 93.50 over ten
sessions, five of them locked (`Open == High == Low == Close`), each move pinned at
about -4.97% to -5.00%. The action, ratio and factor were all correct; the check's
one-bar assumption was wrong.

Detect the signature (several locked bars at the band, cumulative move reconciling
to the factor within tolerance), not a market rule. Several-session falls with zero
locked bars are crashes, not band walks. Read
[references/banded-rebasing.md](references/banded-rebasing.md) before writing or
loosening a continuity gate.

## 8. Price-sanity guard on the bhavcopy path

Rule: the bhavcopy path needs its own sanitiser.

Why: a bhavcopy loader without a sanitiser serves the raw split cliff. A hedge ETF held
across a 1:100 split booked a fabricated total loss (-99%). Yahoo was protected only
by accident because its sanitiser discards the pre-split scale.

Apply the rules in §3 of
[indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md) (longest
clean run; the defect bar belongs to neither segment). One recent-demerger series lost 1,823 bars to the
"cut before the last defect" rule.

Do not retry a market-wide derivation of splits from the next day's previous-close.
It failed three ways: it was noise-dominated (12,062 breaks over 1,776 sessions,
mostly cache gaps where "yesterday" was a week old); the field sits at a different
index in the legacy layout (§3); and the one symbol it was built for split on the layout
changeover day.

Detector: load a symbol across a known split through the bhavcopy path and fail
on any one-bar move near the split ratio.

## 9. Fetching Yahoo prices for NSE tickers

- Cache at the fetch layer, not by threading a cache object through callers; one
  change fixes every call site.
- Key on `resolvedTicker|period1|interval`. Resolved ticker means `RELIANCE` and
  `RELIANCE.NS` share an entry while `.NS` and `.BO` never do. Period and interval
  belong in the key because a 2018-start or weekly series is a different dataset;
  reusing one for a 2015-start daily request silently corrupts every metric.
- Cache the in-flight promise so concurrent callers share one request.
- **Never cache failures.** Caching a rejection turns one transient rate limit into a
  TTL-long outage for that symbol; evict on reject.
- Bound with a TTL (daily bars go stale in a long-lived server).
- Skip any per-symbol politeness delay on a cache hit, or most of the runtime
  remains. In one measurement a cold run took 23.3s and a warm one 3.5s with
  byte-identical output.
- Yahoo's chart API is unofficial and undocumented. Observed 2026-11-26 on
  `RELIANCE.NS` with `interval=1d`: `meta.chartPreviousClose` was the close before
  the range start for `range=1mo` and equalled the first returned bar's close for
  `5d` and `1y`; `meta.previousClose` was absent. It is not the previous session's
  close beyond `1d`. Compute the daily change from the last two bar closes, and
  verify against raw bar closes, not another endpoint of the same app.
- Yahoo serves nothing for retired NSE tickers (see
  [nse-universe-survivorship](../nse-universe-survivorship/SKILL.md) §9); this
  cache does not change that.

Detector: stub the network; assert two keys differing only by exchange, period or
interval do not collide, and a rejected fetch is retried on the next call.

## Verifying an implementation

- Each format's date range yields its expected column set; a trading day with
  zero rows fails; unavailable delivery and `AvgPrice` are empty, not 0 (§1).
- Prices use `EQ` only; liveness uses the same-listing series set (§2).
- Editing one price without changing the row count moves the content hash (§4).
- The corporate-action parser prints its coverage ratio, and fixtures include
  `Re.1`, a bonus-plus-split compound, `Bonus Deb`, a two-dividend subject and a
  `10:2` split (§5).
- Adjustment uses `date < exDate`; a known split shows a raw cliff of about the
  ratio and a flat adjusted series across consecutive trading days; blanking the
  adjusted column or inverting the factor fails the check (§6).
- Each banded-walk gate has its own synthetic fixture and mutation (§7).
- Yahoo cache keys differing by exchange, period or interval do not collide, and a
  rejected fetch is retried (§9).

## Scope

NSE cash-segment prices and corporate actions. Universe membership and renames
are in [nse-universe-survivorship](../nse-universe-survivorship/SKILL.md); tax
treatment of bonus and split is in
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).

Informational engineering guidance. Verify any date, URL or layout against NSE's
own pages before depending on it; the bhavcopy-unadjusted behaviour in particular
is empirical, not documented.
