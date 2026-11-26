---
name: indian-equity-charges
description: Itemised transaction charges for Indian equity cash-segment trades (delivery and intraday on NSE/BSE) — STT, exchange transaction charge, SEBI turnover fee, stamp duty, brokerage, GST and DP charge, each with its correct base and buy/sell side. Use when computing or reviewing trade costs, writing a charges or brokerage calculator, using a flat bps or round-trip cost in a backtest, sizing a position after costs, reconciling a Zerodha or Groww contract note that is off by a few rupees, or when a rupee charge figure is asserted in code or a test, even if the user never says "STT". Not for F&O charges (fno-tax-and-charges) or tax on gains (indian-capital-gains-tax).
license: MIT
compatibility: Rates verified 2026-11-11 against Zerodha and Groww published charge schedules; re-verify before relying on them, as they change with the Union Budget and exchange circulars.
metadata:
  author: hariharanvisves
  version: "1.3"
  verified: "2026-11-11"
  jurisdiction: India
---

# Indian Equity Transaction Charges

A blended "cost in basis points" cannot express Indian equity charges: they differ
**by side**, sit on **different bases**, and one (the DP charge) does not scale with
trade value. This skill holds that structure and prevents silent, one-directional
cost errors.

## Core rules

1. GST is 18% of `brokerage + SEBI fee + transaction charge` only. STT and stamp duty are outside it. [§2](#2-five-things-implementations-get-wrong)
2. Stamp duty is **buy side only**; the DP charge is **sell side only**. Never write a symmetric charge function. [§2](#2-five-things-implementations-get-wrong)
3. Delivery STT is 0.1% on **both** sides; intraday STT is 0.025% on the **sell** side only. [§1](#1-charges-by-side-and-base--equity-delivery-cash-segment)
4. The DP charge is flat per scrip per day, never a rate. Subtract it from the budget before sizing. [§2](#2-five-things-implementations-get-wrong)
5. STT rounds to the nearest rupee at its own step, not at the end of the stack. [§2](#2-five-things-implementations-get-wrong)
6. Size against the charge-inclusive per-share cost; do not size first and subtract after. [§2](#2-five-things-implementations-get-wrong)
7. Load rates from a dated single-owner table keyed to trade date, and show the as-of date. [§5](#5-keeping-the-rates-honest)
8. Futures and options use different rates, sides and bases: see [fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).

## 1. Charges, by side and base — equity **delivery**, cash segment

| Charge | Rate | Side | Base |
|---|---|---|---|
| STT | 0.1% | **both** | turnover |
| Exchange transaction charge (NSE) | 0.00307% | both | turnover |
| Exchange transaction charge (BSE) | varies by scrip group (0.00375% for groups A/B at Zerodha) | both | turnover |
| SEBI turnover fee | ₹10 per crore (0.0001%) | both | turnover |
| Stamp duty | 0.015% (₹1,500/crore) | **buy only** | turnover |
| Brokerage | ₹0 at discount brokers for delivery | — | — |
| GST | 18% | both | **brokerage + SEBI fee + transaction charge** |
| DP charge | varies by broker: ₹15.34 at Zerodha (includes its own GST); ₹3.5 + ₹16.5 plus 18% GST at Groww | **sell only** | **flat, per scrip** |

NSE rates are from NSE/FA/73061 (27 Feb 2026), effective 1 Mar 2026 (<https://nsearchives.nseindia.in/content/circulars/FA73061.pdf>): per ₹ crore per side, including ₹0.01 IPFT, cash 307 (0.00307%), futures 183 (0.00183%), options 3,553 on premium (0.03553%). Whether IPFT sits inside the GST base is not confirmed. The difference is 18% of ₹0.01 per crore, about ₹0.002 per crore.

### Intraday differs on three lines

| Charge | Intraday |
|---|---|
| STT | **0.025%, sell side only** |
| Stamp duty | **0.003%** (₹300/crore), buy side |
| Brokerage | typically 0.03% or ₹20/order, whichever is lower |
| DP charge | **none** |

Using the delivery table for an intraday trade charges STT on the buy leg that
does not exist, overstates sell-leg STT fourfold and buy-side stamp duty fivefold,
and adds a DP charge that intraday does not carry.

## 2. Five things implementations get wrong

**1. GST's base is not turnover.** GST is 18% of
`brokerage + SEBI fee + transaction charge` only. STT and stamp duty are taxes,
not services, so they sit **outside** the base. Applying GST to the whole stack
overstates cost; applying it to turnover overstates it by orders of magnitude.

**2. Stamp duty is buy-side only; DP charge is sell-side only.** A symmetric
charge function is wrong in both directions, and it is why the two legs of a round
trip cost different amounts at identical turnover.

**3. The DP charge does not scale.** It is per scrip per day, not per share and
not per rupee. On a small position it can exceed every other charge combined,
which is what makes a high-turnover, small-allocation strategy look viable under a
bps model and unviable under this one. In sizing, **subtract it from the budget
before** dividing by per-share cost; never fold it into a rate.

**4. STT rounds to the nearest rupee.** Rounding once at the end of a summed stack
gives a different answer from rounding STT at its own step. Round where the broker
rounds.

**5. Sizing against an all-in cost is circular: solve it.** Charges depend on
turnover and turnover depends on quantity, so compute quantity against the
charge-inclusive per-share cost:

```
qty = floor((budget - flat_charges) / (fill_price * (1 + proportional_rate)))
```

Quantity-first sizing, with charges subtracted afterwards, can overdraw the
allocation into negative cash.

## 3. Composition order

GST reads a subtotal, so order matters:

```
turnover   = qty * fill_price
stt        = round_half_up(turnover * STT_RATE)  # nearest rupee, .50 rounds up; intraday: sell side only
txn        = turnover * EXCHANGE_RATE            # NSE != BSE
sebi       = turnover * 0.000001                 # Rs 10 per crore
stamp      = is_buy  ? turnover * STAMP_RATE : 0  # STAMP_RATE differs for intraday
brokerage  = per broker and product
gst        = 0.18 * (brokerage + sebi + txn)
dp         = (is_sell && is_delivery) ? DP_PER_SCRIP : 0  # broker's all-in figure; its GST is not in the gst line above
total      = stt + txn + sebi + stamp + brokerage + gst + dp
```

### Worked example: ₹1,00,000 NSE delivery buy, then sell

Illustrative turnover per leg, brokerage ₹0, Zerodha DP figure. Arithmetic from the
table above:

| Line | Buy | Sell |
|---|---|---|
| STT 0.1% | 100.00 | 100.00 |
| Transaction 0.00307% | 3.07 | 3.07 |
| SEBI ₹10/crore | 0.10 | 0.10 |
| Stamp 0.015% | 15.00 | 0 |
| GST 18% × (0 + 0.10 + 3.07) | 0.57 | 0.57 |
| DP charge | 0 | 15.34 |
| **Total** | **118.74** | **119.08** |

Wrong versions: GST on turnover gives ₹18,000; GST on the whole stack
(`0.18 * (100 + 3.07 + 0.10 + 15)`) gives about ₹21.27 on the buy leg instead of
₹0.57. A symmetric function that charges stamp on both legs makes the sell total
134.08 instead of 119.08.

## 4. Verifying an implementation

A charge model is a money path, so a plausible-range assertion is not a test.

- **Reconcile one real contract note**, line item by line item, to the rupee.
  This is the only check that catches a wrong *base*: a unit test written from
  the same wrong assumption as the code passes.
- **Assert the buy/sell asymmetry directly.** Same turnover, both sides, must
  produce *different* totals. A round-trip total alone passes with stamp duty
  wrongly applied to both legs.
- **Pin the GST base.** Change the STT rate and assert GST does not move. If it
  does, the base is wrong.
- **Pin STT rounding.** Pick a turnover whose STT ends in exactly ₹0.50 and
  assert it rounds up to the next rupee (half-up, not Python's half-even
  `round`), as a whole-rupee line rounded at its own step.

```python
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

- **Size at absurd costs.** Assert `qty * fill_price + charges <= budget` with
  the DP charge larger than one share's price; quantity-first sizing fails it.
- **Test a tiny trade.** If the DP charge is modelled as a rate, a ₹500 sell will
  under-charge; if modelled flat, it will dominate. Both are informative.
- **Report gross and net side by side** wherever a cost drag is shown. A drag
  figure that stays flat when charges are toggled means the charges never reached
  the calculation.

## 5. Keeping the rates honest

**Every rate above is a moving target.** Cash-equity STT (0.1% / 0.025%) was not
touched by the F&O STT revisions of 1 Oct 2024 (NSE/FATAX/63809) and 1 Apr 2026 (NSE/FATAX/73524), but NSE's cash
transaction charge changed with a 2026-03-01 circular. Two rules:

- **Load rates from a dated, single-owner table**, never inline them at a call
  site. A backtest spanning a rate change needs the rate keyed to the trade date,
  or every historical result is priced at today's rates.
- **Verify against a broker's published charge list, not a blog or a search
  summary.** While writing this skill, two secondary sources gave the NSE cash
  transaction charge as 0.00297%, a stale figure. Two brokers' live schedules
  agreed on 0.00307%. Prefer a source that has to be correct because it bills
  people.

State the rate's as-of date wherever a computed charge is displayed. An unverified
rate presented as fact is worse than a missing one, because it looks right.

## Scope

Cash segment (delivery and intraday) only. **Futures and options have different
rates, different sides, and for options a base of premium or intrinsic value
rather than turnover**: do not reuse this table for derivatives. F&O charges
and tax: [fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).

These are **transaction charges**, not tax on gains. STT reduces proceeds; it
never nets against a capital gain. For gain taxation see
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).

Informational only; not tax or investment advice.
