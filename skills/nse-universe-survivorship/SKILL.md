---
name: nse-universe-survivorship
description: Building survivorship-free NSE index universes — reconstructing point-in-time membership from index-change press releases, why an ever-member union is a weaker claim, press-release parser defects, constituent CSV sources, and deriving ticker renames without merging distinct companies. Use when backtesting over Nifty 50/100/200/500 or other NSE indices, using today's constituent list on past dates, ingesting NSE index-change releases or constituent CSVs (ind_nifty50list.csv), building a symbol rename map, handling delisted tickers, or when a backtest return looks too good against the index's own buy-and-hold, even if the user never says "survivorship". Prices and corporate actions are nse-bhavcopy-corporate-actions.
license: MIT
compatibility: Applies to NSE index data (nseindia.com, niftyindices.com) and NSE equity tickers. BSE needs a different, browser-driven route.
metadata:
  author: hariharanvisves
  version: "1.2"
  jurisdiction: India
  verified: "2026-11-11"
---

# NSE Universe Survivorship

Builds the set of stocks an index actually held on each date. Today's constituent
list on past dates inflates returns and a wider list inflates them more. The fixes:
point-in-time membership, honest labelling of weaker claims, and rename maps that
never merge distinct companies.

Goes deeper than §2 of [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md),
which states the basic bias. Read that first. Price-side defects (formats,
series, corporate actions) are in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).

Endpoint paths and field names below were observed to work; NSE changes them
without notice. Re-probe before relying on one.

## Core rules

1. Never apply today's constituents to past dates; a wider current list (Nifty 200) is worse than Nifty 50, not a mitigation. [§1](#1-todays-constituents-on-history-inflate-returns-and-a-wider-universe-is-worse)
2. Reconstruct membership by walking **backwards** from today's verified list, inverting each change event. [§2](#2-point-in-time-membership-reconstruct-backwards-from-todays-anchor)
3. Filter `content.field_type` case-insensitively (`NSE INDICES` became `NSE Indices` in May 2025). [§2](#2-point-in-time-membership-reconstruct-backwards-from-todays-anchor)
4. Zero warnings is not correctness: a deleted 1-for-1 swap is invisible. A build that warns is quarantined, not written. [§3](#3-zero-warnings-proves-no-unbalanced-gap-nothing-more)
5. An ever-member union is a weaker claim, and survivorship bias in reverse if backtested as the index. Label it. [§4](#4-an-ever-member-union-is-a-weaker-claim-not-point-in-time)
6. Parse press releases by layout; never take "the last all-caps token". [§5](#5-press-release-parser-defects)
7. Derive index-name patterns from the archive's distinct strings, not the modern spelling. [§6](#6-index-names-drift-factor-indices-sharing-the-number-are-different-indices)
8. Fetch each constituents CSV by its pinned filename and reject a body that starts with `<`. [§7](#7-constituent-lists-nse-csvs-strategy-indices-bse)
9. A rename fold is an identity claim: ISIN wins, compare issuers (first 7 characters) not full ISINs, no many-to-one folds. [§8](#8-ticker-renames-a-map-applied-to-prices-is-an-identity-claim)
10. Report the earliest covered date, and symbols requested versus used, on every result. [§2](#2-point-in-time-membership-reconstruct-backwards-from-todays-anchor), [§9](#9-absence-is-not-delisting-nothing-serves-retired-tickers)

## 1. Today's constituents on history inflate returns, and a wider universe is worse

Rule: never apply today's list to past dates.

Why: measured on one backtest set, strategies reported 19.5-29.0% CAGR against a
9.66% Nifty 50 buy-and-hold over the same 2018-2026 window, 9.8-19.3pt of
"alpha" where published Indian momentum research lands at 3-6pt. A wider
universe made it worse: Nifty 50 21.5%, Nifty 100 40.0%, Nifty 200 66.1% CAGR.
Broader indices hold smaller, more volatile names, so survivors are more extreme
winners and the failures are absent from the list entirely.

Detector: compare the strategy's CAGR with the index's own buy-and-hold CAGR over
the same window. An excess in the teens is the bias, not a finding. Never propose a
broader universe as a mitigation.

Scale caveat: with membership held fixed and only the price source varied
(survivor-only vs including delisted names), the effect was small at
concentrated selection (+0.3pt at top-10) and flipped sign at top-60 (-0.8pt).
The sign flip is the survivorship signature: forced to hold nearly everything,
the dataset missing its failures looks better. Do not generalise "small" from one
concentrated configuration.

## 2. Point-in-time membership: reconstruct backwards from today's anchor

Rule: walk back from today's verified list, inverting each change event. Never
walk forward from an assumed old list.

Why: forward walks compound gaps invisibly. A backward walk from a known-correct
anchor makes a missed circular show up as an impossible inversion ("included X
was not present to remove").

```python
def members_asof(anchor, events, date):
    # anchor: today's verified set; events: [(effective, included, excluded)]
    cur = set(anchor)
    for eff, inc, exc in sorted(events, key=lambda e: e[0], reverse=True):
        if eff <= date:
            break
        if not inc <= cur:
            raise ValueError(f"included {sorted(inc - cur)} was not present to remove")
        cur = (cur - inc) | exc
    return cur
```

A missed circular that unbalances an add/remove pair surfaces as the `ValueError`; a deleted 1-for-1 swap does not ([§3](#3-zero-warnings-proves-no-unbalanced-gap-nothing-more)).

Source: NSE's press-release CMS endpoint,
`GET https://www.nseindia.com/api/press-release-cms20?fromDate=DD-MM-YYYY&toDate=DD-MM-YYYY`
(earlier cookie-gated; a bare curl worked on 2026-11-11, so keep loading a nseindia.com page first only as a fallback; the `.com` host now redirects to `.in`, see [nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md) §1). Four traps:

1. Filter `content.field_type` **case-insensitively**. It is `"NSE INDICES"` in older
   records and `"NSE Indices"` from May 2025. An exact `===` drops every
   recent release and looks exactly like an archive that ended in May 2025.
2. Not the circulars endpoint. It is a different stream (about 1,100 records for
   early 2018 and zero index changes).
3. The `category` query parameter is accepted and ignored. Filter client-side or
   silently receive everything.
4. Index names drift (§6).

Archive floor: the NSE API floors out around 2015; `niftyindices.com/Press_Release`
serves `ind_prsDDMMYYYY.pdf` releases back to at least 2010. State the floor in
your output; backtests before it carry the full bias. A missing file on that host
returns HTTP 200 with an HTML body, so byte-verify the `%PDF` magic. There is no
index page to enumerate, so candidate business dates must be walked.

Detector: assert the earliest date your membership table covers, and surface it
as a field next to every backtest result.

## 3. "Zero warnings" proves no unbalanced gap, nothing more

Rule: a net-change-0 and per-snapshot-size check cannot see a deleted 1-for-1
swap.

Why: proven by mutation. Deleting one real review (one stock out, one in) and
rebuilding produced zero warnings and a silently wrong history: every earlier
snapshot held the wrong stock, count a perfect 50. In the same corpus an
inclusion/exclusion balance of 824/824 and full half-year coverage both held
while the reconstruction was still broken (556 warnings, 209 failed inversions).
Balanced counts prove no wholesale gap and say nothing about identity.

Detectors that earned their place:
- Review cadence. Nifty 50 is reviewed semi-annually, so a half-year with no
  event is a hole even when counts balance. Emit it as a **note, not a gate**, since
  a genuinely unchanged review also leaves a hole.
- Inversion failures, which catch broken add/remove pairs but not balanced swaps.
  The two checks are complementary.
- Mutation-test the validator itself: delete a known real event, require the
  build to complain, restore it.
- Rejected on evidence, so do not retry: exchange "date of listing" (a corporate
  action mints a new row, so a long-standing constituent reads as listed 2023) and
  next-50 pairing (only 29 of 50 exits re-enter the next tier).

A build that warns must **quarantine** its output rather than write it. Incomplete
point-in-time data is worse than none: it looks like the fix. Copy the previous
good file before any rebuild.

## 4. An ever-member union is a weaker claim, not point-in-time

Rule: if inversion cannot validate (large indices), a union of every symbol that
was ever a member is obtainable, but label it as such.

Why: an `included` entry proves membership from that date and an `excluded` entry
proves membership until that date. Both read forwards off the document, with no
inversion and no member count, so the warnings that block reconstruction do not
apply. Full accuracy on the weaker claim from data that cannot support the
stronger one.

What it is not: backtesting against the union as if it were the index on a given
date is survivorship bias in **reverse**. It includes companies that had not yet
joined and ones already removed. Carry a caveat field in the artifact, and assert
the caveat text survives. Measured size for Nifty 500: 500 current plus 542
former, of which 155 no longer trade.

Also state the floor: a company that joined and left entirely before the archive
begins is absent from the union.

Detector: count how many point-in-time files you actually have. In one corpus
exactly one index (Nifty 50) had true PIT membership; every other file was a
quarantined build or a union. If a "discovery universe" is a union, no result on
it can be validated as PIT at any date.

## 5. Press-release parser defects

Rule: a row parser that takes "the last all-caps token" is wrong for at least two
layouts. A trailing `Month D, YYYY` effective-date column yields the year as a
symbol, and G-Sec/SDL/bond releases sharing the channel yield a maturity year.
Name-only releases need exact match or an explicit alias, never fuzzy matching.
The same release served under two filenames must be deduped on content
`(effective, index, included, excluded)`. Read
[references/press-release-parser-defects.md](references/press-release-parser-defects.md)
for all six layouts when writing or debugging the parser.

Detector: enumerate every distinct symbol your parser ever emitted and reject
anything all-digit, a single character, or in the legal-suffix set. Abort the
write if the result contains any duplicate row; repair already-parsed events only
where the defect signature is provable, never "re-parse everything".

## 6. Index names drift; factor indices sharing the number are different indices

Rule: derive match patterns by enumerating the distinct index strings in the
archive, never from the modern spelling.

Why: Nifty 100 was published as "CNX 100 Index" until 2015, Next 50 as "CNX Nifty
Junior", Nifty 200 as "CNX 200 Index", Nifty 50 as "CNX Nifty" and later with an
"Index" suffix. Matching the modern form silently drops five years and still looks
like a clean build (one index fell from 44 events to 27).

Counter-risk: loosening a pattern to a bare number swallows `Nifty500 Value 50`,
`Nifty Smallcap 500` and similar. Also distinct: `CNX Midcap`/`CNX Smallcap`
(100-member predecessors) versus Midcap 150/Smallcap 250.

Detector: per-index event-count floor per naming era; a test that no factor
variant bleeds in; mutation by narrowing a pattern to its modern form.

Later floors are market facts, not gaps: midcap 150, smallcap 250 and
midsmallcap 400 date from about 2016, large-midcap 250 from 2018.

## 7. Constituent lists: NSE CSVs, strategy indices, BSE

NSE archive CSVs under `nsearchives.nseindia.com/content/indices/` work with a
browser User-Agent and no cookies, but filenames are **inconsistent per index**
(`ind_nifty50list.csv` versus `ind_nifty200Momentum30_list.csv`): pin each
explicitly, because a derived name returns an HTML error page. Strategy indices
and BSE need other routes; read
[references/constituent-lists-and-sources.md](references/constituent-lists-and-sources.md)
before fetching either.

Detector: reject a body that starts with `<`, and a list shorter than the index's
member count.

## 8. Ticker renames: a map applied to prices is an identity claim

Prices key on the symbol as it traded that day, so an unfolded rename truncates
history silently. But a wrong fold transplants one company's price history, and
its index membership, onto another. Eight of 95 Nifty 50 ever-members traded under
a different ticker in the window.

Two rules stay here. The other eight (ISIN reach, no chaining, date adjacency,
many-to-one folds, ambiguous successors, uniqueness, series set, regeneration) are
in [references/ticker-rename-rules.md](references/ticker-rename-rules.md): read it
when generating or reviewing a rename map.

**Rule 2. ISIN wins conflicts.** Where price continuity and ISIN disagree, the ISIN
is on the correct final ticker and continuity stopped at an intermediate hop.

**Rule 6. Compare issuers, not full ISINs.** An ISIN's first seven characters name
the issuer; characters 8-11 identify the security and the 12th is a check digit. A
re-denomination (face value change) keeps the issuer and changes the suffix:
`INE450D01013 -> INE450D01021` is one continuous listing. A full-string compare
rejected 17 of 149 same-issuer pairs. Refuse only when both are known, differ at
issuer level and are disjoint. Reject malformed identifiers (`IN0000000000`) rather
than truncating them, or every placeholder matches every other. Do not forget the
INF (fund) prefix.

```python
import re

ISIN_SHAPE = re.compile(r"IN[EF][0-9A-Z]{8}[0-9]")

def _issuer(isin):
    if not isinstance(isin, str) or not ISIN_SHAPE.fullmatch(isin):
        return None   # malformed or placeholder (IN0000000000): unknown
    if set(isin[3:11]) == {"0"}:
        return None
    return isin[:7]

def same_issuer(old_isin, new_isin):
    # True/False when both are valid; None when either is unknown (never a match)
    a, b = _issuer(old_isin), _issuer(new_isin)
    return None if a is None or b is None else a == b

same_issuer("INE450D01013", "INE450D01021")   # True: re-denomination, one listing
same_issuer("IN0000000000", "IN0000000000")   # None: placeholders never match
```

Detector: assert the confirmed set **by name**. A counts-only contract (`564
applied / 262 confirmed`) stays green when six confirmed renames leave and nine
unconfirmed arrive. Keep a monotonic floor of confirmed names and report losses by
name; a frozen digest goes red on every legitimate refresh and invites pasting the
new hash.

## 9. Absence is not delisting; nothing serves retired tickers

- The exchange equity master was partial in one measurement (2,397 symbols against
  2,707 trading in the same day's bhavcopy). "Absent from the master" does not
  mean delisted. Use presence in the latest bhavcopy.
- Yahoo serves nothing for a retired NSE ticker and short or wrong series for
  renamed ones. Pricing delisted names from Yahoo silently reintroduces the bias
  the membership work removed. Use exchange bhavcopy for history.
- Coverage at a historical start date is a market fact: 71.8% of Nifty 500 was
  tradeable on 2019-01-01 because the rest had not listed. Report symbols
  requested versus used so "359 symbols" does not read as healthy for a 500
  universe.

## 10. Suffix handling: `.NS.NS` makes an empty universe, not an error

Store bare symbols; apply the exchange suffix (`.NS`, `.BO`) in exactly one place,
idempotently. A double suffix (`RELIANCE.NS.NS`) returns "No data found" that every
caller catches and skips, so the failure mode is a silently empty universe.
`.BO` needs the ticker, not the scrip code (`500325.BO` fails), and throttles
harder than `.NS`; one failed `.BO` probe does not mean it is unsupported.

Detector: assert no universe file contains a suffix; assert universe size after
load equals size in the file.

## 11. Guards left on by default are modelling decisions

Rule: resolve any sampling limit against the real universe size once membership
is known, and report what was dropped.

Why: a symbol-count cap (30) applied to an 82-name union of point-in-time
snapshots discarded 63% of it and cost 4.6pt of CAGR, an order of magnitude
larger than the survivorship effect at the same configuration.

## Verifying an implementation

- Strategy CAGR is reported beside the index's own buy-and-hold for the same
  window (§1).
- Membership is built backwards from a verified current list, and its earliest
  covered date is a field on every result (§2).
- Deleting one real 1-for-1 review makes the build complain; a warning
  quarantines the output (§3).
- A union artifact carries a caveat field, and a test asserts the text (§4).
- The parser's emitted symbol set has no all-digit, single-character or
  legal-suffix entries; any duplicate row aborts the write (§5).
- Each index has an event-count floor per naming era, and no factor index bleeds
  in (§6).
- The rename map's confirmed set is asserted by name; many-to-one folds and
  ambiguous successors stay unapplied (§8).
- No universe file holds a suffix; size after load equals size in the file (§10).

## Scope

Index membership and ticker identity for NSE indices. Price formats and
corporate actions are in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).

Informational engineering guidance, not investment advice. Source URLs and field
names are observed behaviour, not a published contract.
