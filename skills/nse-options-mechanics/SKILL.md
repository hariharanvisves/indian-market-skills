---
name: nse-options-mechanics
description: NSE equity and index options mechanics for correct pricing and Greeks — European-style exercise, Black-Scholes applicability, IV non-convergence handling, expiry-instant resolution, settlement price derivation, ATM definition, and multi-leg payoff. Use when computing option prices or Greeks, building an option chain or strategy builder, backtesting an options strategy, or reviewing code that assumes American-style exercise or a hardcoded expiry time.
license: MIT
compatibility: Covers NSE (India) equity and index options. Settlement and session timings change by exchange circular — verify current values before relying on them.
metadata:
  author: hariharanvisves
  version: "1.0"
  jurisdiction: India
---

# NSE Options Mechanics

Options code ported from US markets makes assumptions that are wrong on NSE, and
they fail quietly — a plausible price with a wrong model behind it. The items
below are the ones that actually bite.

## Exercise style: European, always

**All NSE equity options — index *and* single stock — are European-style.** The
exchange moved stock options to European for contracts expiring 2011-01-27 onward.
There is no early exercise and no interim exercise.

Consequences:

- **Black-Scholes-Merton is applicable throughout.** A binomial/tree model
  "for American-style stock options where early exercise matters" implements a
  case that cannot occur, and it makes the same option show **different Greeks
  depending on which pricer ran**.
- If a tree model is introduced, the justification is **discrete dividends** on
  stock options, not exercise style. Say so explicitly, because the distinction
  is what stops the next person reverting it.
- **Always label the model that produced a number.** Two pricers silently
  disagreeing is worse than one pricer being approximate.

## Implied volatility: never fabricate

Newton-Raphson with a bisection fallback is the standard approach.
**Non-convergence must return null, never a guess** — a fabricated IV propagates
into every Greek and the error is invisible downstream.

The honest failure surface is a UI that says *unavailable* for that strike.

There is a real tension here worth naming rather than resolving silently: applied
literally, a null on every illiquid far-OTM strike leaves a chain mostly blank,
which users read as broken. If you interpolate to fill it, the interpolated value
must be **labelled as computed** with the method named — never presented like a
market-derived IV.

## Greeks: all-or-nothing per contract

Compute delta, gamma, theta, vega and rho **only when every input exists**: spot,
strike, time to expiry, risk-free rate, and a resolvable IV. A missing input
yields `null` and the UI shows unavailable.

Prefer **provider-supplied Greeks** where available, and label them as such — a
provider's and your own will differ, and the user needs to know which they are
reading.

## Time to expiry: an instant from the calendar, not a date subtraction

Two errors, both common:

1. **A hardcoded clock time.** Expiry timing has changed. Following the Closing
   Auction Session's introduction, continuous trading in CAS-eligible stocks ends
   before the auction, and equity derivatives close later than the historical
   15:30. **Read the exact times from the current exchange circular**, not from
   any document — including this one.
2. **Calendar days from a naive date subtraction.** Time to expiry must resolve
   the **exchange expiry instant** for that segment and date from a market
   calendar. Naive subtraction mis-prices every short-dated contract, and the
   error grows as expiry approaches — exactly where it matters most.

Treat both the expiry date *and* the expiry instant as **config**, for the same
reason.

## Settlement price is not a price at an instant

Conflating the two puts every near-the-money contract on the **wrong side of the
ITM/OTM boundary**.

- **Index** final settlement is an **average of the underlying over a closing
  window** (historically the last 30 minutes).
- **Stock** derivatives settle against the **closing-auction equilibrium price**
  where CAS applies.

The derivation is per segment and comes from the clearing corporation's rules.
Record it as config with its source, and treat current CAS mechanics as
**unverified until read from the circular**.

## `r` and `q` are config, versioned by effective date

Neither the risk-free rate nor the dividend yield may be a hardcoded constant:

- A backtest spanning several years with one fixed `r` **misprices every option**.
- `q` is **required** for correct index option pricing.

Version them by effective date, exactly like a charge schedule, and record the
source and the tenor-matching rule alongside the values.

## Define ATM once

"Nearest strike" is ambiguous, and every consumer needs the same answer — chain
ITM/OTM shading, preset strike selection, and the moneyness label on Greeks.

A single definition that works: the strike closest to the **futures price of the
same expiry** where a future exists, else the spot, **ties broken to the lower
strike**. Offering spot as a user preference is reasonable; having three call
sites each pick their own is not.

## Multi-leg payoff: derive from legs

Compute max profit, max loss, breakevens and the payoff curve **from the leg set**,
so a custom structure needs no special-casing. Unbounded outcomes render as
`Unlimited` — never a large number standing in for infinity.

Named strategies (straddle, strangle, iron condor, butterfly, the four vertical
spreads, …) are **presets over that engine, not separate implementations**: a
preset is a leg template plus a strike-selection rule and a lot multiple. Once the
user moves a leg it is simply a custom position, and the maths is identical.

**Two disclosures that matter for a real order:**

- Legs must submit in **risk-reducing order** — every long/protective leg before
  any short/risk-creating leg.
- Disclose **the max loss if only the risk-creating legs fill**, separately from
  the structure's designed max loss. That is the exposure carried *during*
  submission, and it is the number a partial fill leaves you holding.

## Two honesty rules

- **Probability metrics (POP, probability of touch) are model outputs, not
  forecasts.** Show them only with the model and assumptions stated (lognormal,
  IV as forward vol).
- **Open interest is never presented as directional.** Describe OI concentration
  and change; do not infer direction from it. Rising OI with rising price is not
  a signal, it is two facts.

## Lot sizes and contract specs

Lot size, strike interval and available expiries are **per-instrument config
sourced from the exchange's contract master**, revised periodically. Never assume
or hardcode them — a stale lot size silently mis-sizes every order and every
backtest position.

## Verifying an options implementation

- **Match published references** for Black-Scholes prices and Greeks at known
  inputs. Do this before trusting anything downstream.
- **Round-trip IV**: price → implied vol → price should return the input.
- **Assert non-convergence returns null**, with a deliberately impossible input.
  A test that only checks the happy path cannot see a fabricated fallback.
- **Test the expiry instant near the boundary** — the last hour before expiry is
  where a naive day-count diverges most.
- **Force a leg rejection at each position in turn** in a multi-leg group, and
  assert the account is never left holding only risk-creating legs.
- **Check the ATM definition has exactly one implementation.** Grep for
  "nearest strike" logic; more than one is a divergence waiting to happen.

## Scope

Informational and engineering guidance; **not investment advice**. Exchange
mechanics, timings and contract specs change by circular — verify against the
current NSE/clearing-corporation documents before relying on any specific value
here.

For transaction costs on options (STT on premium vs intrinsic value, which
differs from the cash segment) see
[indian-equity-charges](../indian-equity-charges/SKILL.md) for the cash-segment
structure and then read the derivatives rates from the exchange directly — the
cash table does **not** transfer.
