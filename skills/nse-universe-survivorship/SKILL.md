---
name: nse-universe-survivorship
description: Building survivorship-free NSE index universes — reconstructing point-in-time membership from index-change press releases, why an ever-member union is a weaker claim, press-release parser defects, and deriving ticker renames without merging distinct companies. Use when backtesting over Nifty 50/100/200/500 or other NSE indices, ingesting NSE index-change releases or constituent CSVs (ind_nifty50list.csv), building a symbol rename map, handling delisted tickers, or when a backtest return looks too good against the index's own buy-and-hold.
license: MIT
compatibility: Applies to NSE index data (nseindia.com, niftyindices.com) and NSE equity tickers. BSE needs a different, browser-driven route.
metadata:
  author: hariharanvisves
  version: "1.1"
  jurisdiction: India
  verified: "2026-11-11"
---

# NSE Universe Survivorship

Goes deeper than §2 of [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md),
which states the basic bias. Read that first. Price-side defects (formats,
series, corporate actions) are in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).

Endpoint paths and field names below were observed to work; NSE changes them
without notice. Re-probe before relying on one.

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

Source: NSE's press-release CMS endpoint,
`GET https://www.nseindia.com/api/press-release-cms20?fromDate=DD-MM-YYYY&toDate=DD-MM-YYYY`
(earlier cookie-gated; a bare curl worked on 2026-11-11, so keep loading a nseindia.com page first only as a fallback). Four traps:

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
layouts.

1. **Trailing token eats the Effective Date column.** Releases carrying a per-row
   date column print `Zuari Industries Limited  ZUARIAGRO  April 9, 2012`. The
   last `[A-Z0-9&-]{2,}` token is `2012`. This yields a wrong symbol rather than
   a failure, lands in both `included` and `excluded`, and loses the release's
   real changes. Strip a trailing `Month D, YYYY` first and reject all-digit
   tokens.
2. **G-Sec/SDL/bond releases share the channel.** They key on ISIN with a Maturity
   Date column and no Symbol column, so the parser scrapes a maturity year as a
   symbol. Screen fixed-income releases out in the shared parser, not in one
   caller: a caller reading PDFs off disk never sees the API summary that the
   other caller filtered on.
3. **Section nesting.** Releases nest a numbered prose heading (`1) Replacements
   on account of semi-annual review`), a lettered index heading (`a) Nifty 50`),
   then tables. Treating the numbered level as the index collapsed one release
   into five pseudo-indices. Use the lettered heading.
4. **Effective date placement.** It appears in the title (`w.e.f. April 02, 2018`)
   or the body (`shall become effective from March 27, 2020`), sometimes wrapped
   mid-date. Collapse whitespace first.
5. **Name-only releases.** Older releases list company names with no symbol
   column. "Last token of the row" returns `LTD`. Resolve names by **exact match
   or an explicit alias only**; fuzzy matching swaps Reliance Industries for
   Reliance Infrastructure.
6. **Same release, two hosts.** NSE CMS and niftyindices serve one document under
   different filenames with identical content. Dedupe on content
   `(effective, index, included, excluded)`, not filename; applying a change twice
   cannot be inverted.

Detector: enumerate every distinct symbol your parser ever emitted and reject
anything all-digit, a single character, or in the legal-suffix set. Repair
already-parsed events only where the defect signature is provable (an all-digit
symbol), never "re-parse everything", because re-parsing a de-duplicated sibling
refills it and doubles rows (88 duplicates against zero in one corpus). Abort the
write if the result contains any duplicate row.

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

- NSE archive CSVs under `nsearchives.nseindia.com/content/indices/` work with a
  browser User-Agent and no cookies, but filenames are **inconsistent per index**
  (`ind_nifty50list.csv` versus `ind_nifty200Momentum30_list.csv`). Pin each
  explicitly. A derived name returns an HTML error page; reject a body that starts
  with `<`.
- **Strategy/factor indices** (Alpha 50, Value 20, High Beta 50) are not in those
  CSVs (404 under every filename tried). Use the live-site market-data API after
  loading a page for cookies. Response data sat one level deeper than expected,
  the first row is the index itself, and some index names have two spellings where
  only one returns rows.
- Old third-party GitHub mirrors of constituents lists are years stale.
- **BSE has no plain-HTTP source.** It needs browser automation: constituents come
  from one host keyed on scrip code with no ticker, the scrip master from a second
  host, and the two block cross-origin reads. Join on scrip code. BSE sector
  indices are classifications (hundreds of names), not curated baskets. Some
  endpoints return only the top 30 for every index, which looks plausible and
  silently truncates.

Detector: reject a body that starts with `<`, and a list shorter than the index's
member count.

## 8. Ticker renames: a map applied to prices is an identity claim

Prices key on the symbol as it traded that day, so an unfolded rename truncates
history silently. But a wrong fold transplants one company's price history, and
its index membership, onto another. Eight of 95 Nifty 50 ever-members traded under
a different ticker in the window.

Rules, each measured:

1. **ISIN reach depends on which files you load.** The legacy bhavcopy carries ISIN
   from about late 2011 to 5 Jul 2024 and UDiFF carries it after; only
   `sec_bhavdata_full` has none (formats in
   [nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md) §1). A pipeline that
   switched to `sec_bhavdata_full` in 2019 loses ISIN for later renames. A rename is
   ISIN-derivable only if the old ticker traded in an ISIN-bearing window of the
   files you loaded.
2. **ISIN wins conflicts.** Where price continuity and ISIN disagree, the ISIN is on
   the correct final ticker and continuity stopped at an intermediate hop.
3. **Do not chain hops.** Chaining assumes every intermediate is in the map; one
   missing hop silently yields a stale ticker. Flatten at generation. A map where
   several sources share one ISIN and point to one target is a legitimately
   flattened chain, not a collision.
4. **Date adjacency is not evidence.** In any 20-session window the exchange lists
   dozens of unrelated IPOs, ETFs and rights entitlements (46 candidates for one
   symbol). Suffixed lines (`-RE`, `-BE`) are never successors.
5. **Reject many-to-one folds.** Two different old symbols claiming one target
   means at least one is wrong. Co-trading on the same session proves distinct
   issuers (one pair overlapped on 4,168 sessions). Measure co-trading using the
   same series filter as the generator, or you get false overlaps from rights
   lines.
6. **Compare issuers, not full ISINs.** An ISIN's first seven characters name the
   issuer; the last four the security. A re-denomination (face value change) keeps
   the issuer and changes the suffix: `INE450D01013 -> INE450D01021` is one
   continuous listing. A full-string compare rejected 17 of 149 same-issuer pairs.
   Refuse only when both are known, differ at issuer level and are disjoint.
   Reject malformed identifiers (`IN0000000000`) rather than truncating them, or
   every placeholder matches every other. Do not forget the INF (fund) prefix.
7. **Leave ambiguous unapplied.** More than one qualifying successor is a human
   decision from a source document. In one corpus 247 such cases were recorded and
   never applied.
8. **Uniqueness is not identity.** Promoting a candidate because it is the only
   survivor converts every killed rival into a confident rename with no evidence.
   Track a separate `identityConfirmed` flag; "applied" is not "confirmed".
9. **Series set for "is this listing alive".** Use the same-listing series
   ([nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md) §2). Dropping them fabricates a termination date and opens a false
   successor window.
10. **Regeneration is a semantic change.** A wider price corpus reduced candidate
    counts without raising identity certainty and promoted ambiguous entries to
    confident ones. Diff the confirmed set before adopting a regenerated map.

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
