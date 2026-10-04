---
name: momentum-factor-research
description: How to research and quote cross-sectional momentum on Indian equities without fooling yourself — the performance/volatility lookback ladder, volatility-estimator choice and why replacing it was rejected, parameter sensitivity (never quote CAGR without parameters and window), factor existence versus portfolio robustness, out-of-sample reversal of blend uplift, and safe evaluation of user-written factor formulas. Use when ranking stocks by momentum, designing or reviewing a factor formula, comparing a volatility estimator, or before quoting any momentum backtest figure.
license: MIT
compatibility: Daily NSE close data. Figures marked "measured on NSE data" are dated findings from one codebase; re-measure on yours.
metadata:
  author: hariharanvisves
  version: "1.0"
  jurisdiction: India
---

# Momentum Factor Research

Cross-sectional momentum is the best-supported factor on Indian equities and the
easiest to misreport. The failures below are about method, not about whether
momentum works. Engine defects live in
[backtest-engine-correctness](../backtest-engine-correctness/SKILL.md).

## 1. Lookback ladder

**Rule.** Define performance and volatility over a fixed ladder of trading-day
windows: 21, 63, 126, 189, 252 bars (about 1, 3, 6, 9 and 12 months). A "month"
is a bar count, set once, shared by every factor.
**Why.** A calendar-month window varies in bars and silently changes between a
signal and its denominator. A 12-month factor needs 253 bars, consumed from the
front of the requested range.
**Detector.** Grep for a month-to-bars conversion; two different conversions in
one codebase is the defect. Confirm the performance and volatility windows in a
ratio match unless the mismatch is deliberate and documented.

## 2. Volatility estimator is a contract

**Rule.** Pick one estimator and freeze it. A defensible baseline: zero-mean
root-mean-square of **simple** returns, denominator **n**, un-annualised:

```
r_i = C_i / C_(i-1) - 1
vol = sqrt( (1/n) * sum(r_i^2) )
```

Do not document it as a sample standard deviation, and do not mix it with an
annualised log-return estimator in one expression.
**Why.** The change from annualised log sample deviation to this form is not a
common scale factor. The scale alone cancels in inverse-vol weight
normalisation (identical to 5.6e-17), but the estimator changes shape: measured
on NSE data, inverse-vol weights moved by up to 0.205 percentage points, and a
stored ratio such as `6M performance / 6M volatility` changed score even though
its ranking was largely preserved. So an estimator change alters stored results
and is an engine-version bump.
**Detector.** Pin the estimator with assertions on `n` versus `n−1`,
annualisation, and simple versus log; mutate each and watch it fail.

## 3. Estimator replacement is second-order; the window is first-order

**Rule.** Replace a volatility estimator only on demonstrated improvement in the
**product decision** (the selected basket), not on estimator theory.
**Why.** When volatility is a ranking denominator, the test is basket
displacement. Measured on NSE data, 716 symbols, `6M performance / <variant>`,
top-30 basket: textbook log-return deviation at the matched window changed 1
name, Parkinson 4, downside deviation 4, MAD 6 (4 of 15 at top-15), RMS over a
fixed 1-year window 6. Rank correlation for an estimator swap was 0.997–0.999 at
every horizon from 21 to 252 bars. Changing the window moves the basket far more
than changing the estimator.
**Yang-Zhang was the worst of six** (out-of-sample predictive error 28.98 /
40.79 / 17.62% at 21 / 63 / 126 bars against 26.74 / 23.78 / 13.84% for RMS).
Cause: 10.39% of NSE bars have Open exactly equal to the previous Close (stale
opens on illiquid names), which corrupts every overnight-dependent estimator.
OHLC estimators also change the data contract (most pipelines carry only a
close).
**Detector.** Before accepting an estimator change, compute the top-N basket
under old and new on the full universe and report the count of changed names.

## 4. Defaults are load-bearing

**Rule.** Never quote a CAGR without its full parameter set and exact window.
**Why.** Measured on NSE data, one parameter varied at a time on a large-cap
universe over 2011–2016: lookbacks swung CAGR by 18.76pt (`[21,63]` 13.86% to
`[126,252]` 32.62%), rebalance frequency by 10.48pt, basket size by 6.19pt,
compounding by 5.38pt, a symbol limit by 5.24pt. That lookback margin shrank to
2.0pt in other windows, so a single-window figure is not typical. Moving only the
start date by 2.5 months changed one run from 21.32% to 13.80%. Longer lookbacks
also consume more warm-up, so variants simulate different periods; hold the
effective start fixed to compare them.
**Detector.** Any stored or quoted result lacking parameters, universe rule,
`simulatedFrom` and `simulatedTo` is uninterpretable. Never compare runs whose
effective start dates differ.

## 5. Factor existence is not portfolio robustness

**Rule.** Establish that a factor carries information **directly** — rank
information coefficient (IC) and its t-statistic against forward returns, before
building a portfolio. Treat "the signal exists" and "this construction earns it"
as separate claims with separate evidence.
**Why.** Measured on NSE data, 189 monthly dates, cross-sections of 262–354
names: medium-horizon performance and slope factors showed mean 6-month IC about
0.11 with t about 9 and a 76% hit rate, surviving removal of the two strongest
years. Yet portfolio returns were year-concentrated and the constructions built
on that signal failed validation (section 6). The cheap, high-information
measurement is one pass computing all factors, with no portfolio and no engine.
**Detector.** Ask for the IC table before the equity curve. Pre-register the
design and freeze the result file before interpreting it.

## 6. Out-of-sample reversal of a blend uplift

**Rule.** A combination that beats its best component in discovery must beat it
on a held-out window before it is promoted.
**Why.** Measured on NSE data, an additive blend of two slope factors beat its
best component by +6.40pt in discovery and lost by −5.23pt in validation: the
shorter component diluted the stronger one. Dividing momentum by volatility
improved Sharpe in discovery (+0.108) and worsened it out of sample (−0.176),
because volatility changes sign of its relationship to returns across regimes: a
regime-conditional variable used as a regime-invariant divisor.
**Detector.** Require a frozen discovery window and a later validation window
with the digest of each result recorded before analysis. Of 98 combinations, the
five that beat their best component by more than 3pt were all one family — a
cluster of one idea, not five findings.

## 7. User-written formula engines

If users write factor formulas (`6M Perf / 6M Vol`), the evaluator is a security
and correctness boundary.

1. **No `eval`, no `Function`.** Parse with a recursive-descent parser over a
   tokenizer. Detector: grep the evaluator for `eval(` and `new Function`.
2. **Dry-run parse.** Validate the whole formula against the grammar and the
   known factor names before any data is touched.
3. **Reject `A -- B`.** Two adjacent binary operators are a typo. Key the guard
   on **token type** (operator followed by operator), never on the character:
   a `-` after `(` is legitimate unary minus.
4. **Parenthesise negative substitutions.** Substitute `-10` as `(-10)`, so
   `a - (-10)` stays valid. Consequence: `a +- b` must throw while `a + -b`
   (unary minus after an operator) must evaluate. If your own tests assert both
   cannot hold, one encodes an untested belief; re-derive from the tokenizer.
5. **Explicit ÷0 policy.** Division by zero returns a defined result (skip the
   symbol, or null), never `Infinity` silently ranked first.
6. **Never run an unresolved formula.** If a factor name does not resolve, fail;
   never substitute 0 or an empty value and rank anyway.
7. **Test both unary-minus shapes** (`-x`, `a - -x`, `a * (-x)`) and assert error
   **text**, not merely that something throws.
8. **Async tests must actually run.** A synchronous harness passes any async
   assertion without running it; mutate an expected value to a false one and
   confirm it fails.

## Scope

Research method, not a strategy recommendation. Past measured findings come from
specific NSE universes and windows and are not forecasts.
