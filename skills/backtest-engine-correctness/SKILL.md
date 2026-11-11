---
name: backtest-engine-correctness
description: Defect classes in equity backtest engines that produce plausible numbers and survive review — null-close valuation, look-ahead marking, wrong annualisation, phantom round-trips (an engine that sells and rebuys names it keeps at every rebalance), cost sizing, non-finite metrics, regime-filter blind spots, engine versioning, and NSE fill realism (circuit locks, closing auction, trade-for-trade series, F&O ban). Use when writing, reviewing or auditing a backtester, when a CAGR/Sharpe/drawdown figure looks too good or too bad, or before quoting any backtest result for Indian equities.
license: MIT
compatibility: Engine-agnostic. NSE rules are dated; each section says which regime applies to which backtest dates.
metadata:
  author: hariharanvisves
  version: "1.1"
  verified: "2026-11-11"
  jurisdiction: India
---

# Backtest Engine Correctness

Every defect below produced a plausible number, passed its tests, and survived
review. Each entry is: **rule**, **why**, **detector**. Figures marked "measured
on NSE data" came from real runs; re-measure before relying on them.

## A. Valuation and time

### 1. Signal on bar *i* fills on bar *i+1*

**Rule.** A signal computed from bar *i*'s close fills at bar *i+1*'s open (or
later). Never at bar *i*'s close.
**Why.** The close is unknowable until the bar ends; filling there is the single
largest source of fake edge.
**Detector.** Perturb bar *i+1* onward (set every later close to a huge value)
and re-run: selections and fills dated at or before *i* must not change. Any
change is look-ahead.

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

**Rule.** If equity (or a mark) falls ~90% and fully recovers on the next bar,
look in your valuation code before blaming data.
**Why.** No market event or bad print behaves that way. Chasing "bad data" first
cost a wrong fix that changed nothing.
**Detector.** Scan the equity curve for |step| > 50% followed by a step of
inverse sign within one bar.

### 5. The final mark is capped at the window end

**Rule.** The last valuation and any close-out price must not exceed the
requested end date, even if the data extends past it.
**Why.** Extra fetched bars silently extend the tail past the requested end.
**Detector.** Assert `lastEquityDate <= requestedEnd` with data deliberately
fetched past it.

### 6. `years` comes from elapsed time, not point count

**Rule.** `years = (lastDate − firstDate) / 365.25 days`. Never
`points / 252`.
**Why.** An equity curve with one point per rebalance, divided by 252, reported
a decade of monthly rebalancing as 2.0 years. CAGR, Calmar and Sortino all
divide by it; the error grows with run length so short smoke tests never show it.
**Detector.** Run monthly vs daily rebalancing over the same span; `years` must
be identical.

### 7. Annualise by actual periods per year

**Rule.** Sharpe, Sortino and annualised volatility scale by
`sqrt(periodsPerYear)` computed from the observed spacing, not a hardcoded
`sqrt(252)` applied to per-rebalance returns.
**Why.** At a 21-day rebalance, hardcoded 252 inflates all three by
`sqrt(252/12) = sqrt(21) ≈ 4.6×` in theory. Measured on NSE data, the inflation was
larger: 93% vs 16.87% annualised vol on identical performance, about 5.5×.
**Detector.** Resample the same equity path daily and monthly; annualised vol
must agree to within sampling error. Mutate the constant and watch it fail.

### 8. Fetch window and calendar are not anchored on one symbol

**Rule.** The date index is the **union** of all symbols' dates; the fetch start
is derived from the requested start minus warm-up head-room, never a constant.
**Why.** Building the calendar from "the first symbol" made that symbol's listing
date the floor of the whole run. A hardcoded fetch start silently capped every
backtest years after the data begins.
**Detector.** Request a start before the first-sorted symbol lists; assert it is honoured.
Holidays and special sessions: [nse-trading-calendar](../nse-trading-calendar/SKILL.md).

### 9. Warm-up warnings are relative to what was asked

**Rule.** Warn when simulated coverage of the *requested* window falls below a
threshold (e.g. 90%), and report the percentage, effective start date and how
much earlier to begin.
**Why.** A threshold measured against warm-up length (not the request) stayed
silent while a run lost a full year off the front (547 of 800 days).
**Detector.** Request a window shorter than the longest lookback; assert the
warning fires.

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

### 11. Size against the all-in cost; retained positions charge nothing

**Rule.** `qty = floor(budget / (fill × (1 + cost)))`, not `floor(budget / price)`
with a fee added after. Resizing a retained position charges nothing. The
end-of-run close-out charges nothing (the curve marks to market and never
liquidated). Slippage and commission are separate knobs: slippage changes the
affordable quantity, commission only reduces cash.
**Why.** Fee-after-sizing overdraws the allocation into negative cash. Flat
per-scrip charges come off the budget before dividing; see
[indian-equity-charges](../indian-equity-charges/SKILL.md) item 5.
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

**Rule.** When a tax or loss-offset rule nets gains and losses within a year,
aggregate across sub-periods (eras) first, then clamp at nil.
**Why.** Clamping each era at zero discards a losing era and overstates tax.
Rates and eras: [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).
**Detector.** Build one year with a gain era and a loss era; tax must equal tax
on the netted total, not on the gain era alone.

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

**Rule.** Distinguish the **display curve** (benchmark line and its drawdown)
from the **regime driver** (the series a trend filter reads to change trades).
**Why.** Only the second changes trades and therefore every metric. If metrics
never receive the benchmark, alpha and beta do not exist in that engine; do not
assume otherwise. A run configured for one price source may still fetch its
benchmark from another unconditionally.
**Detector.** Swap the benchmark source with the filter off: metrics unchanged.
With the filter on: metrics may change. Grep what fetches the benchmark.

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

## F. NSE fill realism

Apply by **trade date**: pick the rule in force for each date in the backtest.

### 20. Circuit-locked bars are unfillable

**Rule.** If a bar's open, high, low and close sit at one price limit (no
two-way trading), a buy at the upper limit or a sell at the lower limit cannot
fill. Skip or defer, do not fill at the limit.
**Why.** Price bands of 2/5/10/20% apply to non-F&O stocks and are revised
periodically. F&O stocks have no cash-market band, only a 10% dummy order-entry
filter that NSE relaxes near the limit; stock-futures bands flex 10% to 15% to 20%
(triggers at 9.90% and 14.90% of base). Source: NSE FAQ on price band / operating
range flex; NSE/FAOP/63405 and NSE/FAOP/64995 (verified 2026-11-11).
**Detector.** Count fills on bars where high == low == a band limit; expect zero.

### 21. Market halts, settlement and closing-price regime

**Rule.** A 10/15/20% Nifty 50 or Sensex move halts trading (length depends on
time of day; no halt for 10% after 14:30); treat intraday fills across a halt as
unfillable (NSE circuit-breakers page, verified 2026-10-04). T+1 settlement applies to all equities from 27 Jan 2023; it was phased in by
stock before that, so verify the cycle per stock for 2022 dates. Optional T+0 is beta (from 28 Mar 2024, top 500 from 31 Jan 2025). A
close-based backtest must say which closing-price method applies on each date:
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
Expiry-day derivative settlement prices changed on the same dates: see
[nse-options-mechanics](../nse-options-mechanics/SKILL.md).
Pre-open order collection was 9:00–9:08 before 7 Sep 2026; from that date it is
9:00–9:05 (limit and market), 9:05–9:10 (limit only), with continuous trading
from 9:15. Source: SEBI circulars dated 16 Jan 2026 and 15 Oct 2026 (verified
2026-11-11); NSE T+0 page (verified 2026-10-04).
**Why.** "The close" is a different print under each regime, and an intraday
fill across a halt never traded.
**Detector.** A backtest filling "at the close" after 3 Aug 2026 on an F&O stock
is filling at an auction price; confirm the data source records that print.

### 22. Trade-for-trade series are not intraday-netted

**Rule.** BE and BZ series settle trade-for-trade (gross, every trade
deliverable). Do not model intraday netting there. Stage II–IV GSM names are
trade-for-trade as well, and Stage III–IV trade only once a week (first trading
day of the week).
**Why.** Netting a same-day buy and sell there models a trade that settles
gross. Source: NSE series legend; NSE GSM FAQ (verified 2026-11-11).
**Detector.** On a BE/BZ or GSM Stage II–IV name, a same-day buy and sell must
book two deliverable trades; a Stage III–IV fill on any day other than the
week's first trading day is impossible.

### 23. F&O ban and surveillance lists

**Rule.** A stock enters the F&O ban when futures-equivalent open interest
exceeds 95% of MWPL. MWPL is the lower of 15% of free float and 65× average
daily delivery value (floor 10% of free float), recalculated quarterly; both
apply from 1 Oct 2025 (before: MWPL 20% of free float, plain open interest). The
exit threshold (80%) is from an older NSE page and **unconfirmed under the
futures-equivalent method: verify against the current NSE circular**. Long-term
ASM on F&O stocks: F&O margin at least 50% at Stage I rising to 100%, MWPL cut to
75% / 50% from Stage II / III, no fresh contracts at Stage IV; cash margin 100%
from Stage I, Stage IV gross settlement with a 5% band. GSM Stage I is 100%
margin with a band of 5% or less. Source: SEBI circular 29 May 2025 (paras 5.2,
6); NSE ASM and GSM FAQs (verified 2026-11-11).
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
