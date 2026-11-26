---
name: nse-options-mechanics
description: Mechanics of NSE equity and index options that US-derived code gets wrong — all options European-style (Black-Scholes applies; a tree is only for discrete dividends), IV solver non-convergence returns null, Greeks all-or-nothing, time to expiry as an IST expiry instant (not date subtraction or a hardcoded 15:30), settlement price by dated rule rather than the index at an instant, one ATM definition, r and q as dated config, multi-leg payoff, and lot sizes from the contract master. Use when computing option prices, implied volatility or Greeks for Nifty, Bank Nifty or stock options, building an option chain, payoff or strategy builder, backtesting an options strategy, or reviewing code that assumes American exercise, a binomial tree, a fixed expiry time or a fixed lot size, even if the user never mentions NSE rules.
license: MIT
compatibility: Covers NSE (India) equity and index options. Settlement and session timings change by exchange circular — verify current values before relying on them.
metadata:
  author: hariharanvisves
  version: "1.3"
  verified: "2026-11-11"
  jurisdiction: India
---

# NSE Options Mechanics

Options code ported from US markets makes assumptions that are wrong on NSE, and
they fail quietly: a plausible price with a wrong model behind it. The items below
are the ones that actually bite.

## Core rules

1. All NSE options, index and stock, are European. Use Black-Scholes-Merton; a tree is justified only by discrete dividends. [§1](#1-exercise-style-european-always)
2. IV non-convergence returns `null`, never the last iterate or 0. [§2](#2-implied-volatility-never-fabricate)
3. Compute Greeks only when every input exists; label the model or provider. [§3](#3-greeks-all-or-nothing-per-contract)
4. Time to expiry is `expiry instant − now` from a market calendar, not a date subtraction and not a hardcoded clock time. [§4](#4-time-to-expiry-an-instant-from-the-calendar-not-a-date-subtraction)
5. Settlement is derived from constituent or underlying prices by dated rule, not the index or price at an instant. [§5](#5-settlement-price-is-not-a-price-at-an-instant)
6. `r` and `q` are dated config, not constants. [§6](#6-r-and-q-are-config-versioned-by-effective-date)
7. Define ATM once: nearest the same-expiry future (else spot), ties to the lower strike. [§7](#7-define-atm-once)
8. Derive payoff from the legs; submit risk-reducing legs first. [§8](#8-multi-leg-payoff-derive-from-legs)
9. Lot size, strike interval and expiries come from the contract master for the trade date. [§10](#10-lot-sizes-and-contract-specs)

## 1. Exercise style: European, always

**Rule.** All NSE equity options, index *and* single stock, are European-style.
The exchange moved stock options to European for contracts expiring 2011-01-27
onward. There is no early exercise and no interim exercise.

**Why.** A binomial/tree model "for American-style stock options where early
exercise matters" implements a case that cannot occur, and it makes the same
option show **different Greeks depending on which pricer ran**.

- Black-Scholes-Merton is applicable throughout.
- If a tree model is introduced, the justification is **discrete dividends** on
  stock options, not exercise style. Say so explicitly; the distinction is what
  stops the next person reverting it.
- **Always label the model that produced a number.** Two pricers silently
  disagreeing is worse than one pricer being approximate.

**Detector.** Grep for `american`, `binomial`, `early_exercise` in pricing code.

## 2. Implied volatility: never fabricate

**Rule.** Newton-Raphson with a bisection fallback is the standard approach.
Non-convergence returns **null, never a guess**. The honest failure surface is a
UI that says *unavailable* for that strike.

**Why.** A fabricated IV propagates into every Greek and the error is invisible
downstream.

There is a real tension: applied literally, a null on every illiquid far-OTM
strike leaves a chain mostly blank, which users read as broken. If you
interpolate to fill it, the interpolated value must be **labelled as computed**
with the method named, never presented like a market-derived IV.

```python
def implied_vol(price, bs_price, vega, lo, hi, tol=1e-8, max_iter=100):
    if not bs_price(lo) <= price <= bs_price(hi):
        return None                       # outside the bracket: no solution
    sigma = 0.5 * (lo + hi)
    for _ in range(max_iter):
        diff = bs_price(sigma) - price
        if abs(diff) < tol:
            return sigma
        lo, hi = (lo, sigma) if diff > 0 else (sigma, hi)
        v = vega(sigma)
        nxt = sigma - diff / v if v > 1e-12 else None
        sigma = nxt if nxt is not None and lo < nxt < hi else 0.5 * (lo + hi)
    return None                           # never return the last iterate
```

**Detector.** Feed a price above `bs_price(hi)`; the result must be `None`.

## 3. Greeks: all-or-nothing per contract

**Rule.** Compute delta, gamma, theta, vega and rho **only when every input
exists**: spot, strike, time to expiry, risk-free rate, and a resolvable IV. A
missing input yields `null` and the UI shows unavailable.

**Why.** A default stand-in (IV 0, rate 0) yields a Greek that looks computed
and is not. Prefer **provider-supplied Greeks** where available and label them as
such: a provider's and your own will differ, and the user needs to know which they
are reading.

**Detector.** Grep for `iv or 0`, `rate = 0` and similar defaults in Greek code.

## 4. Time to expiry: an instant from the calendar, not a date subtraction

**Rule.** Resolve the **exchange expiry instant** (date and time, IST) for that
segment and date from a market calendar, then subtract `now`. Treat both the
expiry date *and* the expiry instant as **config**.

**Why.** Two errors, both common:

1. **A hardcoded clock time.** Expiry timing has changed. Following the Closing
   Auction Session's introduction, continuous trading in CAS-eligible stocks ends
   before the auction, and equity derivatives close later than the historical
   15:30: to 15:40 from 3 Aug 2026 (SEBI circular 16 Jan 2026), then from 7 Dec
   2026 to 15:45, except expiring index contracts on expiry day, which cease at
   15:30 (SEBI circular 15 Oct 2026; verified 2026-11-11). **Read the exact times
   from the current exchange circular**, not from any document, including this
   one.
2. **Calendar days from a naive date subtraction.** It mis-prices every
   short-dated contract, and the error grows as expiry approaches, exactly where
   it matters most. Expiry days moved by holidays:
   [nse-trading-calendar](../nse-trading-calendar/SKILL.md).

Worked example: an expiring index contract at 14:00 IST on expiry day, on a date
from 7 Dec 2026 (or before 3 Aug 2026), where the calendar lookup returned a 15:30
instant. Between 3 Aug and 6 Dec 2026 the lookup returns 15:40 instead.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def time_to_expiry(now: datetime, expiry_instant: datetime, year_seconds: float):
    if now.tzinfo is None or expiry_instant.tzinfo is None:
        raise ValueError("pass timezone-aware datetimes (IST)")
    secs = (expiry_instant - now).total_seconds()
    return secs / year_seconds if secs > 0 else None

# now = datetime(2026, 12, 8, 14, 0, tzinfo=IST); expiry = same date at 15:30, tzinfo=IST
# 15:30 - 14:00 = 5400 s; with a 365-day basis (31,536,000 s): T = 1.712e-4 years
# naive (expiry_date - today).days / 365 = 0 -> Black-Scholes divides by sqrt(0)
```

Keep the year basis consistent with the one your IV solver and Greeks use.

**Detector.** Test the last hour before expiry, where a naive day-count diverges
most. Grep for `.days / 365` and literal `15:30` / `15:40` / `15:45` in pricing code.

## 5. Settlement price is not a price at an instant

**Rule.** Derive final settlement from the dated rule below. Record it as config
with its source and the date range it applies to.

**Why.** Conflating the two puts every near-the-money contract on the **wrong side
of the ITM/OTM boundary**.

- **Index** final settlement is the index value computed from constituent
  prices, not the index sampled at an instant. Up to 6 Dec 2026 those prices are
  each constituent's closing price (from 3 Aug 2026, the CAS equilibrium price
  for F&O stocks); from 7 Dec 2026 they are each constituent's VWAP over the
  last 30 minutes of continuous trading.
- **Stock** derivatives: 3 Aug to 6 Dec 2026, volume-weighted average of the
  closing prices across exchanges; from 7 Dec 2026, VWAP of the underlying over
  the last 30 minutes of continuous trading across exchanges.

Source: SEBI circulars 16 Jan 2026 (para 4.9) and 15 Oct 2026 (para 4.9),
verified 2026-11-11; before 3 Aug 2026, index contracts settled on the index
value from the last-30-minute VWAP of its constituents, and stock contracts on the
VWAP of the underlying across exchanges (SEBI Master Circular 30 Dec 2024, Ch. 5
¶1.1.9, ¶3.1.2.7). The derivation is per segment and comes from the clearing corporation's rules.

**Detector.** Settle a near-the-money contract at expiry from the config for that
date range; ITM/OTM must flip when the last traded price and the settlement price
straddle the strike.

## 6. `r` and `q` are config, versioned by effective date

**Rule.** Neither the risk-free rate nor the dividend yield may be a hardcoded
constant. Version them by effective date, exactly like a charge schedule, and
record the source and the tenor-matching rule alongside the values.

**Why.** A backtest spanning several years with one fixed `r` **misprices every
option**. `q` is **required** for correct index option pricing.

**Detector.** Price one option on two dates either side of an `r` or `q` change;
the value used must follow the effective-date table.

## 7. Define ATM once

**Rule.** ATM is the strike closest to the **futures price of the same expiry**
where a future exists, else the spot, **ties broken to the lower strike**.
Offering spot as a user preference is reasonable; having three call sites each
pick their own is not.

**Why.** "Nearest strike" is ambiguous, and every consumer needs the same answer:
chain ITM/OTM shading, preset strike selection, and the moneyness label on Greeks.

**Detector.** Grep for "nearest strike" logic; more than one implementation is a
divergence waiting to happen.

## 8. Multi-leg payoff: derive from legs

**Rule.** Compute max profit, max loss, breakevens and the payoff curve **from the
leg set**, so a custom structure needs no special-casing. Unbounded outcomes
render as `Unlimited`, never a large number standing in for infinity.

Named strategies (straddle, strangle, iron condor, butterfly, the four vertical
spreads, …) are **presets over that engine, not separate implementations**: a
preset is a leg template plus a strike-selection rule and a lot multiple. Once
the user moves a leg it is simply a custom position, and the maths is identical.

**Two disclosures that matter for a real order:**

- Legs must submit in **risk-reducing order**: every long/protective leg before
  any short/risk-creating leg.
- Disclose **the max loss if only the risk-creating legs fill**, separately from
  the structure's designed max loss. That is the exposure carried *during*
  submission, and it is the number a partial fill leaves you holding.

**Detector.** Force a leg rejection at each position in turn and assert the
account is never left holding only risk-creating legs. Assert an unbounded leg
set reports `Unlimited`.

## 9. Two honesty rules

- **Probability metrics (POP, probability of touch) are model outputs, not
  forecasts.** Show them only with the model and assumptions stated (lognormal,
  IV as forward vol).
- **Open interest is never presented as directional.** Describe OI concentration
  and change; do not infer direction from it. Rising OI with rising price is not
  a signal, it is two facts.

## 10. Lot sizes and contract specs

**Rule.** Lot size, strike interval and available expiries are **per-instrument
config sourced from the exchange's contract master**, revised periodically. Never
assume or hardcode them, including a hand-maintained dated table in code: load the
contract master for the trade date instead.

**Why.** A stale lot size silently mis-sizes every order and every backtest
position. Weekly index expiries are also date-dependent: from 20 Nov 2024 each
exchange may offer weeklies on only one benchmark index (SEBI circular 1 Oct 2024,
para 5.5; verified 2026-11-11), so a chain built for an earlier date had weeklies
on more indices.

**Detector.** Grep for literal lot sizes and clock times (`15:30`, `15:40`, `15:45`); each
belongs in dated config.

## Verifying an options implementation

- **Match published references** for Black-Scholes prices and Greeks at known
  inputs, before trusting anything downstream.
- **Round-trip IV**: price → implied vol → price returns the input.
- **Assert non-convergence returns null** with a deliberately impossible input.
  A happy-path-only test cannot see a fabricated fallback.
- **Settle a near-the-money contract at expiry** from the settlement config (§5).
- **Price one option either side of an `r` or `q` change** (§6).
- **Test the expiry instant near the boundary** (§4).
- **Force a leg rejection at each position** in a multi-leg group (§8).
- **One ATM implementation** (§7); **no literal lot sizes or clock times** (§10).

## Scope

Informational and engineering guidance; **not investment advice**. Exchange
mechanics, timings and contract specs change by circular; verify against the
current NSE/clearing-corporation documents before relying on any specific value
here.

Transaction costs and tax on options: [fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).
The cash-segment table in [indian-equity-charges](../indian-equity-charges/SKILL.md)
does **not** transfer.
