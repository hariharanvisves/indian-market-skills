---
name: backtest-engine-correctness
description: Checklist of 24 defect classes that make an equity backtest look plausible and be wrong — look-ahead marking, null-close valuation, CAGR with years = points/252, hardcoded sqrt(252) Sharpe, phantom round-trips on rebalance, fee-after-sizing, NaN metrics, regime filters that act only on rebalance dates, engine versioning and result-cache keys, and NSE fill realism (circuit-locked bars, closing auction from 3 Aug 2026, trade-for-trade series, F&O ban). Use when writing, reviewing or auditing a backtester or equity-curve code, when CAGR, Sharpe or drawdown looks too good, too bad or pinned at 99.99%, when trade count or win rate looks off, or before quoting any backtest result for Indian equities, even if the user only asks for a quick sanity check.
license: MIT
compatibility: Engine-agnostic. NSE rules are dated; each section says which regime applies to which backtest dates.
metadata:
  author: hariharanvisves
  version: "1.2"
  verified: "2026-11-11"
  jurisdiction: India
---

# Backtest Engine Correctness

Every defect below produced a plausible number, passed its tests and survived review.
Each entry is a **rule**, a **why** and a **detector**. Figures marked "measured on
NSE data" came from real runs; re-measure before relying on them.

## Core rules

A model that reads only this block should avoid the worst mistakes. Rule numbers
(§1–§24) are stable and cited by other skills.

1. Fill a bar-*i* signal at bar *i+1*'s open, never at bar *i*'s close. [§1](#1-signal-on-bar-i-fills-on-bar-i1)
2. Value a position with the last real close **at or before** the date; skip null and zero closes. [§2](#2-mark-to-market-backward-never-forward), [§3](#3-a-null-or-zero-close-must-never-be-multiplied)
3. `years = (last − first date) / 365.25`, never `points / 252`; annualise Sharpe, Sortino and vol by observed periods per year, not `sqrt(252)`. [§6](#6-years-comes-from-elapsed-time-not-point-count), [§7](#7-annualise-by-actual-periods-per-year)
4. Book an exit only for names absent from the next basket; resize retained ones. [§10](#10-no-phantom-round-trips)
5. Size against the all-in cost, and charge by side, base and **trade date**. [§11](#11-size-against-the-all-in-cost-retained-positions-charge-nothing), [§12](#12-charges-are-side-specific-base-specific-and-dated)
6. No metric may be NaN or Infinity; skip the pair, never substitute 0; Sharpe is null on a short window. [§13](#13-no-metric-may-be-non-finite-skip-the-pair-never-substitute-0), [§14](#14-sharpe-is-null-under-a-minimum-window)
7. Quote a regime-filter result only with its rebalance frequency. [§16](#16-a-regime-filter-only-acts-on-rebalance-dates)
8. Keep `simulate()` pure, version the engine on economic change, key caches on the whole price manifest. [§18](#18-simulate-is-pure-io-sits-outside), [§19](#19-version-the-engine-bump-only-when-the-economic-result-changes)
9. NSE fills depend on the date: closing-price regime changed on 3 Aug 2026 and again on 7 Dec 2026, circuit-locked bars cannot fill, trade-for-trade and F&O-ban names have their own rules. [§20–§23](#f-nse-fill-realism)
10. A survivorship-biased or half-adjusted price history fails before any rule here matters. [§24](#24-survivorship-and-corporate-actions)

## A. Valuation and time

### 1. Signal on bar *i* fills on bar *i+1*

**Rule.** A signal computed from bar *i*'s close fills at bar *i+1*'s open (or
later). Never at bar *i*'s close.
**Why.** The close is unknowable until the bar ends; filling there is the single
largest source of fake edge.
**Detector.** Tamper bar *i*'s close and every later bar (set to a huge value),
re-run, and compare only the **fills** dated at or before *i*; they must not
change. Do not compare selections: a selection at *i* may legitimately use close
*i*, but a fill at *i* may use only bar *i*'s open or earlier. Perturbing from
*i+1* would miss a fill at bar *i*'s own close.

```python
def test_no_lookahead(run, bars, i):
    base = run(bars)
    huge = {"open": 1e9, "high": 1e9, "low": 1e9, "close": 1e9}
    tampered = {s: b[:i] + [{**b[i], "close": 1e9}] + [huge] * (len(b) - i - 1)
                for s, b in bars.items()}
    assert fills_through(run(tampered), i) == fills_through(base, i)  # fills with bar <= i
```

An engine that fills at bar *i*'s close fails this test; one that fills at bar
*i+1*'s open passes.

### 2. Mark to market backward, never forward

**Rule.** To value a position on date *d*, use the last real close **at or
before** *d*. Never the first bar on or after *d*.
**Why.** "First bar on or after" is a one-line `findIndex(q => q.date >= d)`. On
a symbol with a gap it returns a bar months in the future, leaking future prices
into a historical valuation, a ranking and a fill. Measured on NSE data: 347
symbols carried an internal gap over 60 days, while the obvious test universe
(an index of large caps) had none at its rebalance dates, so the bug was
invisible there and inflated CAGR by 5.39pt (while understating drawdown by
3.57pt) on a gap-heavy universe.
**Detector.** Grep every date lookup in the engine (valuation, selection,
stop/target, hedge entry). Require one shared helper returning exact-date index
or -1, with each caller choosing its own fallback. A fix applied to one call site
and not the rest is the usual state; count raw usages and pin the count.

Wrong versus right, with §3 folded in:

```python
# wrong: the first bar on or after d can be months ahead on a gappy symbol
close = next(c for dt, c in bars if dt >= d)

# right: last real close at or before d, skipping null/zero
def mark(dates, closes, d):
    i = bisect.bisect_right(dates, d) - 1
    while i >= 0 and not closes[i]:
        i -= 1
    return closes[i] if i >= 0 else None
```

### 3. A null or zero close must never be multiplied

**Rule.** Skip null/zero closes and walk backward to the last real one, in
valuation **and** in both exit paths.
**Why.** `quantity * null` is `0`. NSE occasionally holds special Saturday
sessions that some vendors emit with `close: null` for every symbol; a healthy
book marked to ~0 for one bar pinned max drawdown at 99.99% over 25 years and
turned a +25% CAGR into -97%. In an exit path it books a sale at 0 and a
fabricated 100% loss.
**Detector.** Feed a series with one null-close bar; assert equity never drops
more than a plausible day move, and no trade has exit price 0.

### 4. A −90% step that recovers next bar is an accounting bug

**Rule.** Equity or a mark that falls ~90% and fully recovers on the next bar is a valuation bug, not bad data. Detail: [reference](references/secondary-defects.md#4-a-90-step-that-recovers-next-bar-is-an-accounting-bug).

### 5. The final mark is capped at the window end

**Rule.** The last valuation and any close-out price must not exceed the requested end date. Detail: [reference](references/secondary-defects.md#5-the-final-mark-is-capped-at-the-window-end).

### 6. `years` comes from elapsed time, not point count

**Rule.** `years = (lastDate − firstDate) / 365.25 days`. Never
`points / 252`.
**Why.** An equity curve with one point per rebalance, divided by 252, turns a
decade of monthly rebalancing (120 points) into 0.48 years. `years` is then about
21× too small, the CAGR exponent `1/years` about 21× too large, and CAGR is
**inflated**, not deflated. CAGR, Calmar and Sortino all divide by it. The error
grows with run length, so short smoke tests never show it.
**Detector.** Run monthly vs daily rebalancing over the same span; `years` must
be identical.

Worked example: a curve that doubles over 10 years, sampled monthly (120 points).

```python
total = 2.0
years_wrong = 120 / 252                         # 0.476
cagr_wrong = total ** (1 / years_wrong) - 1     # 2**2.1 - 1  = 328.7%
years = (last_date - first_date).days / 365.25  # 10.0
cagr = total ** (1 / years) - 1                 # 2**0.1 - 1  = 7.18%
```

### 7. Annualise by actual periods per year

**Rule.** Sharpe, Sortino and annualised volatility scale by
`sqrt(periodsPerYear)` computed from the observed spacing, not a hardcoded
`sqrt(252)` applied to per-rebalance returns.
**Why.** At a 21-day rebalance, hardcoded 252 inflates all three by
`sqrt(252/12) = sqrt(21) ≈ 4.6×` in theory. Measured on NSE data, the inflation was
larger: 93% vs 16.87% annualised vol on identical performance, about 5.5×.
**Detector.** Resample the same equity path daily and monthly; annualised vol
must agree to within sampling error. Mutate the constant and watch it fail.

Compute `periods_per_year = len(returns) / years` using the `years` from §6; a
21-day rebalance gives about 12, so scale by `sqrt(12)`.

### 8. Fetch window and calendar are not anchored on one symbol

**Rule.** The date index is the **union** of all symbols' dates; the fetch start is the requested start minus warm-up head-room, never a constant. Detail: [reference](references/secondary-defects.md#8-fetch-window-and-calendar-are-not-anchored-on-one-symbol).

### 9. Warm-up warnings are relative to what was asked

**Rule.** Warn when simulated coverage of the *requested* window falls below a threshold (e.g. 90%), reporting the percentage, effective start and how much earlier to begin. Detail: [reference](references/secondary-defects.md#9-warm-up-warnings-are-relative-to-what-was-asked).

## B. Trades and costs

### 10. No phantom round-trips

**Rule.** Book an exit only for symbols absent from the next basket. A retained
position is resized, keeping its original entry price and date.
**Why.** Liquidating the whole book and re-buying the same names at the same
price books one ~0% closed trade per holding per rebalance. Money never moves,
so equity is right and no equity test can catch it. Measured A/B: trades 276 →
93, win rate 62 → 55.9, risk/reward 1.14 → 3.02, **CAGR byte-identical**.
Win rate, payoff and trade counts use **realised disposals** only; an open
position at the end is neither a win nor a loss.
**Detector.** A/B any trade-ledger edit: trade-count metrics move, CAGR and total
return must be byte-identical. An unpriceable pick must count as a departure, or
its trade stays open forever.

Worked example: holding {A, B, C}, next basket {B, C, D}.

```python
exits  = held - next_basket          # {A}: the only closed trade
resize = held & next_basket          # {B, C}: keep entry price and date
buys   = next_basket - held          # {D}
# wrong: sell all three, rebuy B, C, D -> 3 closed trades, 2 of them ~0% "wins"
```

### 11. Size against the all-in cost; retained positions charge nothing

**Rule.** `qty = floor(budget / (fill × (1 + cost)))`, not `floor(budget / price)`
with a fee added after. Resizing a retained position charges nothing. The
end-of-run close-out charges nothing (the curve marks to market and never
liquidated). Slippage and commission are separate knobs: slippage changes the
affordable quantity, commission only reduces cash.
**Why.** Fee-after-sizing overdraws the allocation into negative cash. Flat
per-scrip charges come off the budget before dividing; see
[indian-equity-charges](../indian-equity-charges/SKILL.md) §2 item 5.
**Detector.** Assert spend ≤ budget at absurd costs (1000 bps stays finite and
non-negative). **Invariant:** a zero-friction run must reproduce the frictionless
numbers byte-for-byte, and trade count must be unchanged by costs (costs move
money, not structure).

### 12. Charges are side-specific, base-specific and dated

**Rule.** STT, exchange charge, stamp duty and the rest apply to different bases
on different sides, and rates change by date. Apply the schedule in force on the
**trade date**.
**Why.** One blended bps figure overstates some eras and understates others; a
backtest spanning a rate change is wrong in both halves.
**Detector.** Run one buy and one sell across a known rate change; assert the
itemised charge differs by era. Schedule and bases:
[indian-equity-charges](../indian-equity-charges/SKILL.md).

## C. Metrics

### 13. No metric may be non-finite; skip the pair, never substitute 0

**Rule.** If a period return is NaN or Infinity (a zero equity **value**, not a
flat curve), skip that pair and warn. Do not substitute 0.
**Why.** `0/0 − 1` is NaN, which `JSON.stringify` renders as `null`, so a client
reads "volatility not measurable" for corrupt input. A substituted 0% return
understates volatility while claiming the period was measured. A flat curve is
fine and must report `annualisedStd: 0`.
**Detector.** Call the metrics function with a hand-built curve containing a zero
value; assert every output is finite.

### 14. Sharpe is null under a minimum window

**Rule.** Return `null` (not a number) when there are too few periods or too
short a span to estimate it; say why.
**Why.** A ratio from a handful of returns is noise that reads as a measurement.
**Detector.** Run a 3-month window; assert `sharpe === null`.

### 15. Aggregate across periods before clamping at zero

**Rule.** When a tax or loss-offset rule nets gains and losses within a year, aggregate across eras first, then clamp at nil. Detail: [reference](references/secondary-defects.md#15-aggregate-across-periods-before-clamping-at-zero).

## D. Regime filters and benchmarks

### 16. A regime filter only acts on rebalance dates

**Rule.** Never quote a regime-filter result without its rebalance frequency.
**Why.** Measured on NSE data: at monthly rebalancing, an `exit_all` filter moved
drawdown by under 1.8pt while CAGR spanned 5–42%, because the March 2020 fall
lay entirely between two monthly dates. The same filter at weekly rebalancing cut
drawdown to −12.09%. A "half the portfolio" action concentrates into the
highest-momentum names and can make drawdown worse; a filter helps only when
paired with an uncorrelated asset.
**Detector.** Run the filter at weekly and monthly frequency on a window with a
crash between month-ends; compare drawdown.

### 17. The benchmark is two inputs

**Rule.** Distinguish the **display curve** from the **regime driver** (the series a trend filter reads); only the second changes trades and metrics. Detail: [reference](references/secondary-defects.md#17-the-benchmark-is-two-inputs).

## E. Engine hygiene

### 18. `simulate()` is pure; I/O sits outside

**Rule.** The simulation takes data in and returns a result. Fetching, caching
and persistence are the caller's.
**Why.** An impure core cannot be reproduced from its report, and a function
named `generate*`/`run*` that quietly writes is a destructive getter.
**Detector.** Run the core twice with the same inputs and network disabled;
results must be byte-identical.

### 19. Version the engine; bump only when the economic result changes

**Rule.** Bump the engine version when a change alters the metrics a stored
configuration would produce. Do not bump for derived reporting over an unchanged
ledger. Quarantine rows from older versions rather than mixing them.
**Why.** A fix that changes results on one population only (gap-heavy symbols)
looks like a no-op on the test universe and gets shipped as a tidy-up. A
volatility-estimator change is a bump even though a pure scale factor would
cancel: [momentum-factor-research](../momentum-factor-research/SKILL.md) §2.
**Detector.** Characterise the input shape the bug needs, count rows with that
shape, and re-measure there before deciding "no delta".

**Result cache key.** Key a stored result on the canonical request, the engine
version, a hash of the engine code and a hash of the **whole price manifest**.
Refuse to cache a run whose inputs have no content identity. Detail and the
stale-provenance defect: [reference](references/secondary-defects.md#result-cache-key).

## F. NSE fill realism

Apply by **trade date**: pick the rule in force for each date in the backtest.
Read [references/nse-fill-realism.md](references/nse-fill-realism.md) for price-band
figures, halts, the settlement cycle, pre-open windows, GSM/ASM stages and the F&O
ban thresholds. It also holds the sources and verification dates.

### 20. Circuit-locked bars are unfillable

**Rule.** If a bar's open, high, low and close sit at one price limit (no
two-way trading), a buy at the upper limit or a sell at the lower limit cannot
fill. Skip or defer, do not fill at the limit.
**Why.** Non-F&O stocks have 2/5/10/20% bands, revised periodically; F&O stocks
have none in the cash market. Band detail and sources are in the reference.
**Detector.** Count fills on bars where high == low == a band limit; expect zero.

### 21. Market halts, settlement and closing-price regime

**Rule.** A close-based backtest must say which closing-price method applies on
each date. Market-wide halts, the T+1 and T+0 dates and the pre-open windows are
in the reference; treat an intraday fill across a halt as unfillable.
- **Before 3 Aug 2026**, close = VWAP of the last 30 minutes for all stocks.
- **From 3 Aug 2026**, F&O stocks close from a Closing Auction Session
  (15:15–15:35; reference VWAP 15:00–15:15, ±3% band, matching 15:30–15:35) and
  continuous trading for them ends at 15:15. Non-F&O stocks keep the 30-minute
  VWAP close with trading to 15:30.
- **From 7 Dec 2026** (SEBI circular 15 Oct 2026), the auction is 15:30–15:40 with
  reference VWAP of the last 15 minutes of continuous trading (15:15–15:30), so
  continuous trading for F&O stocks runs to 15:30. The circular's applicability
  and band paragraphs are not restated in its amended text: treat F&O-only and
  ±3% as unchanged until read.

Source: SEBI circulars dated 16 Jan 2026 and 15 Oct 2026 (verified 2026-11-11).
Expiry-day derivative settlement prices changed on the same dates: see
[nse-options-mechanics](../nse-options-mechanics/SKILL.md).
**Why.** "The close" is a different print under each regime, and an intraday
fill across a halt never traded.
**Detector.** A backtest filling "at the close" after 3 Aug 2026 on an F&O stock
is filling at an auction price; confirm the data source records that print.

### 22. Trade-for-trade series are not intraday-netted

**Rule.** BE and BZ series settle trade-for-trade (gross, every trade
deliverable); do not model intraday netting there. Stage II–IV GSM names are
trade-for-trade too, and Stage III–IV trade only once a week (first trading day
of the week).
**Detector.** On a BE/BZ or GSM Stage II–IV name, a same-day buy and sell must
book two deliverable trades. Sources are in the reference.

### 23. F&O ban and surveillance lists

**Rule.** A stock enters the F&O ban when futures-equivalent open interest
exceeds 95% of MWPL (MWPL rule from 1 Oct 2025; before that date MWPL was 20% of
free float on plain open interest; trading resumes at 80% of MWPL or below per SEBI Master
Circular annexure 1.3.2.1.4.6). ASM and GSM stages
change margin, band and contract availability.
**Why.** Ban, margin and band rules decide whether a position could be opened
and at what cost; ignoring them fills trades that never existed.
**Detector.** A derivatives backtest that opens positions in a banned name, or a
cash backtest that ignores a 5% band on a GSM name, is unfillable as modelled.

### 24. Survivorship and corporate actions

A backtest that does not hold delisted names, or that mixes adjusted and
unadjusted prices, fails before any engine rule matters. See
[nse-universe-survivorship](../nse-universe-survivorship/SKILL.md),
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md) and
[indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md).

## Verifying an implementation

- **Look-ahead first:** the perturbation test (§1) and a gap / null-close
  fixture (§2, §3). They catch the largest fake edge.
- **Time and scale:** `years` and annualised vol agree across daily and monthly
  rebalancing of one path (§6, §7).
- **Ledger A/B:** a trade-ledger change moves trade counts and leaves CAGR
  byte-identical (§10).
- **Costs:** a zero-friction run reproduces frictionless numbers byte-for-byte;
  trade count is unchanged by costs (§11).
- **Metrics:** every output is finite on a curve with a zero value (§13).
- **Prove each guard:** remove it, watch the specific test fail, restore it; a
  mutant killed by the wrong assertion is untested. Build fixtures that can
  express the defect (a low-volatility series cannot show variance drag). Assert
  the resolved count of any list-taking call, not its exit status.

## Scope

Engine mechanics and NSE fill realism for equity backtests. Charge rates:
[indian-equity-charges](../indian-equity-charges/SKILL.md). Tax on gains:
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md). Factor method:
[momentum-factor-research](../momentum-factor-research/SKILL.md). Option pricing:
[nse-options-mechanics](../nse-options-mechanics/SKILL.md).

Engineering guidance, not investment advice. Rates and market rules cited above
carry a verification date; confirm against the primary source before relying on
them for a date after it.
