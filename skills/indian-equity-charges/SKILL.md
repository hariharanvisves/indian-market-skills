---
name: indian-equity-charges
description: Itemised transaction charges for Indian equity trades — STT, exchange transaction charge, SEBI turnover fee, stamp duty, brokerage, GST and DP charges, with the correct base and buy/sell side for each. Use when computing or reviewing trade costs, building a brokerage calculator, modelling backtest friction, reconciling against a contract note, or when a rupee charge figure is asserted in code or a test. Covers the NSE/BSE cash segment (delivery and intraday).
license: MIT
compatibility: Rates verified 2026-08-20 against broker charge schedules; re-verify before relying on them, as they change with the Union Budget and exchange circulars.
metadata:
  author: hariharanvisves
  version: "1.0"
  jurisdiction: India
---

# Indian Equity Transaction Charges

A blended "cost in basis points" figure cannot express Indian equity charges,
because the charges differ **by side**, sit on **different bases**, and one of
them does not scale with trade value at all. This skill holds the structure.

## Charges, by side and base — equity **delivery**, cash segment

| Charge | Rate | Side | Base |
|---|---|---|---|
| STT | 0.1% | **both** | turnover |
| Exchange transaction charge (NSE) | 0.00307% | both | turnover |
| Exchange transaction charge (BSE) | varies by scrip group | both | turnover |
| SEBI turnover fee | ₹10 per crore (0.0001%) | both | turnover |
| Stamp duty | 0.015% (₹1,500/crore) | **buy only** | turnover |
| Brokerage | ₹0 at discount brokers for delivery | — | — |
| GST | 18% | both | **brokerage + SEBI fee + transaction charge** |
| DP charge | ~₹20 per scrip (varies by broker) | **sell only** | **flat, per scrip** |

## Equity **intraday** differs on three lines

| Charge | Intraday |
|---|---|
| STT | **0.025%, sell side only** |
| Stamp duty | **0.003%** (₹300/crore), buy side |
| Brokerage | typically 0.03% or ₹20/order, whichever is lower |
| DP charge | **none** |

Using the delivery table for an intraday trade overstates STT fourfold on the buy
leg and understates nothing — a silent, one-directional error.

## Five things implementations get wrong

**1. GST's base is not turnover.** GST is 18% of
`brokerage + SEBI fee + transaction charge` only. STT and stamp duty sit
**outside** the GST base — they are taxes, not services. Applying GST to the
whole charge stack overstates cost; applying it to turnover overstates it by
orders of magnitude.

**2. Stamp duty is buy-side only; DP charge is sell-side only.** A symmetric
charge function is wrong in both directions, and it is why a round trip costs
different amounts in each leg at identical turnover.

**3. The DP charge does not scale.** It is per scrip per day, not per share and
not per rupee. On a small position it can exceed every other charge combined —
which is what makes a high-turnover, small-allocation strategy look viable under
a bps model and unviable under this one. In a position-sizing calculation it must
be **subtracted from the budget before** dividing by per-share cost, never folded
into a rate.

**4. STT rounds to the nearest rupee.** It is not carried at sub-rupee precision.
Rounding once at the end of a summed stack gives a different answer from rounding
STT at its own step. Round where the broker rounds.

**5. Sizing against an all-in cost is circular — solve it, don't approximate.**
Charges depend on turnover; turnover depends on quantity. Compute quantity
against the charge-inclusive per-share cost:

```
qty = floor((budget - flat_charges) / (fill_price * (1 + proportional_rate)))
```

Computing quantity first and subtracting charges after can overdraw the
allocation into negative cash.

## Composition order

GST reads a subtotal, so order matters:

```
turnover   = qty * fill_price
stt        = round(turnover * STT_RATE)          # to nearest rupee
txn        = turnover * EXCHANGE_RATE            # NSE != BSE
sebi       = turnover * 0.000001                 # Rs 10 per crore
stamp      = is_buy  ? turnover * STAMP_RATE : 0
brokerage  = per broker and product
gst        = 0.18 * (brokerage + sebi + txn)
dp         = is_sell ? DP_PER_SCRIP : 0
total      = stt + txn + sebi + stamp + brokerage + gst + dp
```

## Verifying an implementation

A charge model is a money path, so a plausible-range assertion is not a test.

- **Reconcile one real contract note**, line item by line item, to the rupee.
  This is the only check that catches a wrong *base* — a unit test written from
  the same wrong assumption as the code passes.
- **Assert the buy/sell asymmetry directly.** Same turnover, both sides, must
  produce *different* totals. A round-trip total alone passes with stamp duty
  wrongly applied to both legs.
- **Pin the GST base.** Change the STT rate and assert GST does not move. If it
  does, the base is wrong.
- **Test a tiny trade.** If the DP charge is modelled as a rate, a ₹500 sell will
  under-charge; if modelled flat, it will dominate. Both are informative.
- **Report gross and net side by side** wherever a cost drag is shown. A drag
  figure that stays flat when charges are toggled means the charges never reached
  the calculation.

## Keeping the rates honest

**Every rate above is a moving target.** STT changed on 2024-10-01, and NSE's
transaction charge changed with a 2026-03-01 circular. Two rules:

- **Load rates from a dated, single-owner table**, never inline them at a call
  site. A backtest spanning a rate change needs the rate keyed to the trade date,
  or every historical result is priced at today's rates.
- **Verify against a broker's published charge list, not a blog or a search
  summary.** While writing this skill, two secondary sources gave the NSE cash
  transaction charge as 0.00297% — a stale figure. Two brokers' live schedules
  agreed on 0.00307%. Prefer a source that has to be correct because it bills
  people.

State the rate's as-of date wherever a computed charge is displayed. An unverified
rate presented as fact is worse than a missing one, because it looks right.

## Scope

Cash segment (delivery and intraday) only. **Futures and options have different
rates, different sides, and for options a base of premium or intrinsic value
rather than turnover** — do not reuse this table for derivatives.

These are **transaction charges**, not tax on gains. STT reduces proceeds; it
never nets against a capital gain. For gain taxation see
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).

Informational only; not tax or investment advice.
