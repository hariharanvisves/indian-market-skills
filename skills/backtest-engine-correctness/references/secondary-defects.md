# Secondary defect classes for SKILL.md §4, §5, §8, §9, §15, §17 and the result cache key

Purpose: full rule, why and detector for the lower-frequency defects. The decisions most often gotten wrong are in [SKILL.md](../SKILL.md).

## Contents

- §4 A −90% step that recovers next bar
- §5 The final mark is capped at the window end
- §8 Fetch window and calendar are not anchored on one symbol
- §9 Warm-up warnings are relative to what was asked
- §15 Aggregate across periods before clamping at zero
- §17 The benchmark is two inputs
- Result cache key

## 4. A −90% step that recovers next bar is an accounting bug

**Rule.** If equity (or a mark) falls ~90% and fully recovers on the next bar,
look in your valuation code before blaming data.
**Why.** No market event or bad print behaves that way. Chasing "bad data" first
cost a wrong fix that changed nothing.
**Detector.** Scan the equity curve for |step| > 50% followed by a step of
inverse sign within one bar.

## 5. The final mark is capped at the window end

**Rule.** The last valuation and any close-out price must not exceed the
requested end date, even if the data extends past it.
**Why.** Extra fetched bars silently extend the tail past the requested end.
**Detector.** Assert `lastEquityDate <= requestedEnd` with data deliberately
fetched past it.

## 8. Fetch window and calendar are not anchored on one symbol

**Rule.** The date index is the **union** of all symbols' dates; the fetch start
is derived from the requested start minus warm-up head-room, never a constant.
**Why.** Building the calendar from "the first symbol" made that symbol's listing
date the floor of the whole run. A hardcoded fetch start silently capped every
backtest years after the data begins.
**Detector.** Request a start before the first-sorted symbol lists; assert it is honoured.
Holidays and special sessions: [nse-trading-calendar](../../nse-trading-calendar/SKILL.md).

## 9. Warm-up warnings are relative to what was asked

**Rule.** Warn when simulated coverage of the *requested* window falls below a
threshold (e.g. 90%), and report the percentage, effective start date and how
much earlier to begin.
**Why.** A threshold measured against warm-up length (not the request) stayed
silent while a run lost a full year off the front (547 of 800 days).
**Detector.** Request a window shorter than the longest lookback; assert the
warning fires.

## 15. Aggregate across periods before clamping at zero

**Rule.** When a tax or loss-offset rule nets gains and losses within a year,
aggregate across sub-periods (eras) first, then clamp at nil.
**Why.** Clamping each era at zero discards a losing era and overstates tax.
Rates and eras: [indian-capital-gains-tax](../../indian-capital-gains-tax/SKILL.md).
**Detector.** Build one year with a gain era and a loss era; tax must equal tax
on the netted total, not on the gain era alone.

## 17. The benchmark is two inputs

**Rule.** Distinguish the **display curve** (benchmark line and its drawdown)
from the **regime driver** (the series a trend filter reads to change trades).
**Why.** Only the second changes trades and therefore every metric. If metrics
never receive the benchmark, alpha and beta do not exist in that engine; do not
assume otherwise. A run configured for one price source may still fetch its
benchmark from another unconditionally.
**Detector.** Swap the benchmark source with the filter off: metrics unchanged.
With the filter on: metrics may change. Grep what fetches the benchmark.

## Result cache key

 Key a stored result on the canonical request, the engine
version, a hash of the engine code and a hash of the **whole price manifest**.
A content hash of one file misses manifest fields such as an unadjusted-from
marker. Refuse to cache a run whose inputs have no content identity (live-fetched
provider prices), and store only if the key did not change during the run.
**Related defect.** A long-lived worker that loads prices once but re-reads
snapshot provenance per call serves old prices labelled with the new snapshot
hash after a data refresh.
