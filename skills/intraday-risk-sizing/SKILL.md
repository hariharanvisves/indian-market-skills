---
name: intraday-risk-sizing
description: Engineering-correctness rules for sizing an Indian equity or F&O order from a stop - quantity as the minimum of independent caps (max loss at the stop, position value, available margin, per-order value ceiling, exchange freeze quantity) with the deciding cap reported and zero refused, sizing from the worse of the planned entry and a fresh quote, F&O quantity in whole lots rounded down, freeze-quantity split or refuse, stop and target rounded on the instrument's own tick size (stop away from entry, target toward it), intraday (MIS) margin from the broker's margin API instead of a fixed multiplier, and fail-closed handling of stale quotes, missing lot, tick or freeze data, NaN and wrong-side stops. Use when writing or reviewing position-sizing, risk-per-trade, lot-size, freeze-quantity or tick-rounding code, or an intraday order builder for NSE, even if the user only asks for a quick quantity calculator. Not trading advice and not signals.
license: MIT
compatibility: Facts read on 2026-11-26 from NSE circulars, the SEBI master circular on exchange-traded derivatives and the Kite Connect v3 docs. Lot size, freeze quantity and tick size change by exchange circular, so read them from the exchange files and never from this skill.
metadata:
  author: hariharanvisves
  version: "1.0"
  verified: "2026-11-26"
  jurisdiction: India
---

# Intraday Risk Sizing

An order sized from one number goes wrong in a quiet way. A risk-only quantity ignores the lot
size, the freeze quantity and the margin, so the exchange or broker rejects it. A quantity sized
from a flattering price risks more than the budget. This skill gives the arithmetic rules only;
it never says where to enter, where to stop or whether to trade.

## Core rules

1. Quantity is the minimum of independent caps. Report which cap decided it, and refuse when
   the result is 0 (§1).
2. Measure stop distance from the worse of the planned entry and a fresh quote: the higher for a
   buy, the lower for a sell (§2).
3. F&O quantity is a whole number of lots, rounded down, with the lot size read for that exact
   contract from the exchange file (§3).
4. Above the freeze quantity, split into slices or refuse. Slicing never raises the total
   (§4).
5. Round the stop away from entry and the target toward entry, on the instrument's own tick
   size read from the exchange master, never to 2 decimals (§5).
6. Margin comes from the broker's margin API at order time, not a fixed multiplier. A per-unit
   figure only pre-filters: the final quantity, and each slice, must pass a fresh margin
   check (§6).
7. Fail closed on a stale quote, missing lot, tick or freeze data, a non-finite input, an
   off-grid entry or a stop on the wrong side of the planned entry (§7).
8. These caps gate entries only. An exit or reducing order is capped at the open quantity and
   never refused because a sizing cap came out as 0 (§8).

Primary sources and the exact wording they carry:
[references/primary-sources.md](references/primary-sources.md).

## 1. Quantity is the minimum of independent caps

**Rule.** Compute each cap in units of the instrument, then take the minimum.

| Cap | Units it allows |
|---|---|
| Max loss at the stop | risk budget ÷ stop distance per unit (§2, §5) |
| Position-value cap | position-value cap ÷ reference price |
| Available cash or margin | available margin ÷ the broker's margin per unit, then a margin check on the final quantity (§6) |
| Per-order value ceiling | ceiling ÷ reference price; the ceiling itself is [kite-connect-safety](../kite-connect-safety/SKILL.md) §8a |
| Freeze quantity (F&O only) | the freeze quantity (§4) |

Round the minimum down: to a whole number of lots for F&O (§3), to a whole share otherwise.
Return the quantity and the name of the cap with the smallest raw value. Ties go to the first cap
in a fixed order, so the same inputs always name the same cap. If the quantity is 0, raise: do
not place a minimum order "so something goes out".

**Why.** Each cap protects a different thing, and the binding one changes with price,
volatility and the account's state. A sizer that returns only a number hides why the order is
small, so nobody notices when the risk cap stopped binding and a looser cap took over. The
reported cap also feeds the order record and the §8i verdict in
[kite-connect-safety](../kite-connect-safety/SKILL.md).

**Detector.** A table test where each cap is made the smallest in turn and the returned name is
that cap. A test where every cap allows less than one lot or share must raise. Grep for
`max(1,` or `or 1` near a quantity, which turns a refusal into an order.

## 2. Size from the worse price

**Rule.** The reference price is the less favourable of the planned entry and a fresh quote:
`max` for a buy, `min` for a sell. If the order carries its own limit price, that price is the
planned entry, because a limit buy can fill anywhere up to it. Stop distance is measured from the
reference price to the tick-rounded stop (§5). The position-value and ceiling caps divide by the
same reference price. The stop must also be on the loss side of the **planned** entry, not only of
the reference price: a buy planned at ₹1,200 with a fresh quote of ₹1,203.30 and a stop of ₹1,202
is refused, although the stop is below the reference price.

**Why.** A stop distance measured from a better price than the one you get is too small, so the
quantity is too big. The loss at the stop is then above the budget on the very first fill. A
quote that moved against the plan during the minutes before the order must shrink the order, not
be ignored.

**Detector.** Move the fresh quote above the planned entry for a buy, with everything else
fixed: the quantity must fall or stay the same, never rise. Mirror it for a sell. A stop between
the planned entry and a worse fresh quote must raise, for both sides.

Worked example (rupee figures are illustrative, not market data): a buy with planned entry
₹1,200.00, fresh quote ₹1,203.30, stop ₹1,196.46 and a tick of ₹0.10 (§5).

| Step | Value |
|---|---|
| Reference price | ₹1,203.30 (the higher) |
| Stop rounded away from entry | ₹1,196.40 |
| Stop distance | ₹6.90 |
| Risk cap, budget ₹2,000 | 289.86 units, so 289 |
| Position-value cap ₹4,00,000 | 332 units |
| Margin cap, ₹1,50,000 at ₹361.00 per unit | 415 units |
| Ceiling ₹5,00,000 | 415 units |

The quantity is 289 and the deciding cap is `risk`. The loss at the stop is 289 × ₹6.90 =
₹1,994.10, inside the ₹2,000 budget. Sized from the plan alone with a stop rounded to 2 decimals,
the risk cap reads 564 units and the position-value cap wins at 333 units. At the real fill and
the real stop that order loses 333 × ₹6.90 = ₹2,297.70, which is ₹297.70 over budget. The loss at the stop ignores gap-through, slippage and charges; a gap fills
at the gap price, not the stop ([backtest-engine-correctness](../backtest-engine-correctness/SKILL.md),
gap through a stop).

## 3. Lot size: whole lots, rounded down, per contract

**Rule.** An F&O quantity is a whole multiple of the lot size, rounded **down**. Read the lot
size from the exchange's current contract file for the exact contract (underlying and expiry),
or from the broker's instrument dump, which carries it per instrument (Kite: `lot_size`,
"Quantity of a single lot"). Never use a constant, and never round up to reach one lot: if the
quantity is under one lot, refuse.

**Why.** SEBI's master circular on exchange-traded derivatives has exchanges review lot sizes
once every 6 months, with at least 2 weeks' notice. NSE/FAOP/70616 (3 Oct 2025) cut the Nifty 50
lot from 75 to 65 from 28 Oct 2025 (EOD) while existing weekly and monthly contracts kept 75
until their December 2025 expiries, so two lot sizes were live for one underlying at once. A
table keyed by underlying is wrong during such a window, and a hardcoded lot is wrong after it.
Rounding up buys more risk than the cap allowed. The broker-side twin of this rule is the local
reject in [kite-connect-safety](../kite-connect-safety/SKILL.md) §8f.

**Detector.** Grep for numeric lot sizes (`lot = 75`, `LOT_SIZES = {`). A test passes a quantity
of 130 with lot 25 and expects 125; a quantity of 24 with lot 25 must raise. A lookup keyed by
underlying alone, with no expiry, is a defect.

## 4. Freeze quantity: split or refuse

**Rule.** The exchange rejects an order above the freeze quantity (NSE/FAOP/49118 section A:
orders "having quantity more than the respective freeze quantity limit ... shall be frozen and
automatically rejected"). Read the freeze quantity per underlying from the exchange file, never
a constant: stock freeze limits are revised monthly and on the ex-date of a corporate action;
read index freeze quantities from NSE's file too. The columns documented for Kite's instrument
dump (`instrument_token`, `exchange_token`, `tradingsymbol`, `name`, `last_price`, `expiry`,
`strike`, `tick_size`, `lot_size`, `instrument_type`, `segment`, `exchange`) include no freeze
quantity ([kite-connect-safety](../kite-connect-safety/SKILL.md) §8f), so a Kite integration still
needs NSE's file. When the sized quantity is above the freeze quantity, either refuse or split it:
- Each slice is at most the freeze quantity rounded down to a whole number of lots, and each is a
  whole number of lots. If that slice size is 0, refuse.
- The caps in §1 apply to the **total**. Slicing partitions an already-capped quantity; it is
  never a way past the per-order value ceiling.
- Every slice is its own order with its own order id. Each needs its own idempotency key
  (§8b) and its own PASS fingerprint (§8i) in
  [kite-connect-safety](../kite-connect-safety/SKILL.md), and each counts against the order
  rate limit ([indian-broker-api-safety](../indian-broker-api-safety/SKILL.md) §3). Slices 1
  and 2 of 1,800 / 1,800 / 400 have identical intent, so an intent-derived key collides and
  slice 2 replays slice 1. The key and the PASS fingerprint must include the slice index and
  the slice count; `split_for_freeze` returns `(index, total, qty)` for that reason.
- Refuse when the split needs more slices than `max_slices`, set from the orders-per-second
  threshold (10 per second, [indian-broker-api-safety](../indian-broker-api-safety/SKILL.md)
  §3). Do not burst past it.
- A slice that is rejected or `unknown` stops the remaining slices (§8d of
  [kite-connect-safety](../kite-connect-safety/SKILL.md)). An `unknown` slice must be
  reconciled before the protective stop is placed, and the stop covers the quantity that
  actually filled.

**Why.** An oversized order is rejected whole, so the position the stop was sized for never
opens, or a naive splitter sends dozens of orders and trips the rate limit mid-way. A
slice off the lot grid is a malformed F&O quantity (§3).

**Detector.** A quantity of 4,000 with lot 25 and freeze 1,800 (illustrative values) gives
slices 1,800, 1,800 and 400, summing to 4,000, each at most 1,800 and a multiple of 25, with
distinct `(index, total)` pairs. A freeze quantity below one lot, a float quantity or more slices
than `max_slices` must raise. Fault-inject a rejection on slice 2: slice 3 must not be sent.

## 5. Tick grid: round the stop away, the target toward entry

**Rule.** Use the instrument's own tick size, read from the exchange's per-security master (the
CM security file; the F&O contract file for derivatives; Kite's dump carries `tick_size` as a
float, so convert it with `Decimal(repr(x))`). Never round prices to 2 decimals. Round on the
grid in the direction that never understates risk or overstates reward:

| Side | Stop (away from entry) | Target (toward entry) |
|---|---|---|
| Buy | round down | round down |
| Sell | round up | round up |

After rounding, re-check that the stop is still on the loss side of entry and the target still
beyond it; otherwise refuse. The entry price you send must also sit on the grid; `size_order` refuses one that does not.

**Why.** NSE moved the cash segment to a tick that depends on the security's price: ₹0.01 for a
security below ₹250, and from 15 Apr 2025 ₹0.10 above ₹1,000 up to ₹5,000 (NSE/CMTR/67133). The
tick is reviewed every month, and corporate actions keep the old tick until the next review
(NSE/CMTR/62174). Stock futures follow the underlying's cash tick (NSE/FAOP/67134), while
options on stocks below ₹250 changed from ₹0.05 to ₹0.01 from 3 Nov 2025 (NSE/FAOP/70382). So one
stock can have different ticks in its cash, futures and options markets, and the same instrument
can change tick between months. A stop rounded to the nearest 2 decimals can land off the grid
or inside the entry side, which cuts the stop distance. A target rounded away from entry is a
price the market may never print.

**Detector.** Test a buy stop of ₹1,196.46 on tick ₹0.10: the result is ₹1,196.40, below the
raw stop. A sell stop of ₹1,203.54 gives ₹1,203.60. A buy target of ₹1,210.97 gives ₹1,210.90.
Grep for `round(` and `.quantize(Decimal("0.01"))` in price code. Cache the tick keyed by
`(instrument, date)`, never by symbol alone.

```python
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR

class SizingRefused(ValueError):
    """Every refusal is this type; the caller places nothing."""

def dec(name, x):                         # price, tick, budget: finite and > 0, never bool
    if isinstance(x, bool) or not isinstance(x, (Decimal, int, str, float)):
        raise SizingRefused(f"{name}: unsupported type {type(x).__name__}")
    try:
        d = Decimal(repr(x)) if isinstance(x, float) else Decimal(x)
    except InvalidOperation:
        raise SizingRefused(f"{name}: not a number: {x!r}")
    if not d.is_finite() or d <= 0:
        raise SizingRefused(f"{name}: must be finite and > 0, got {x!r}")
    return d

def whole(name, x):                       # lot size, freeze quantity: int > 0, never bool
    if isinstance(x, bool) or not isinstance(x, int) or x <= 0:
        raise SizingRefused(f"{name}: need a positive int from the exchange file, got {x!r}")
    return x

def check_side(side):
    if side not in ("BUY", "SELL"):
        raise SizingRefused(f"side must be BUY or SELL, got {side!r}")
    return side == "BUY"

def on_grid(price, tick, rounding):
    return (price / tick).to_integral_value(rounding=rounding) * tick

def round_stop(stop, entry, tick, side):  # away from entry: buy floors, sell ceils
    buy, stop, entry, tick = check_side(side), dec("stop", stop), dec("entry", entry), dec("tick", tick)
    if (stop >= entry) if buy else (stop <= entry):
        raise SizingRefused(f"stop {stop} is not on the loss side of entry {entry} for a {side}")
    out = on_grid(stop, tick, ROUND_FLOOR if buy else ROUND_CEILING)
    if out <= 0:
        raise SizingRefused(f"stop {stop} rounds to {out} on tick {tick}")
    return out

def round_target(target, entry, tick, side):  # toward entry: buy floors, sell ceils
    buy, target, entry, tick = check_side(side), dec("target", target), dec("entry", entry), dec("tick", tick)
    if (target <= entry) if buy else (target >= entry):
        raise SizingRefused(f"target {target} is not on the profit side of entry {entry} for a {side}")
    out = on_grid(target, tick, ROUND_FLOOR if buy else ROUND_CEILING)
    if (out <= entry) if buy else (out <= 0 or out >= entry):
        raise SizingRefused(f"target {target} rounds to {out}, no longer beyond entry {entry}")
    return out
```

## 6. Intraday (MIS) margin comes from the broker, at order time

**Rule.** Take the margin for the order from the broker's margin API or calculator when you
size it. Do not use a fixed leverage multiplier such as "5x for MIS". Kite's margin API
(`/margins/orders`, https://kite.trade/docs/connect/v3/margins/, read 2026-11-26) "calculates
margins for each order considering the existing positions and open orders" and returns `span`,
`exposure`, `option_premium`, `additional`, `cash`, `var` and a `leverage` value per order.
Derive margin per unit from a call for the actual order and use it only as a pre-filter, then
call again with the final quantity (and for each slice) and refuse if the required margin
exceeds the available margin. In the sketch that call is `margin_check(qty) -> bool`, required
for every order. Broker-specific API facts belong to
[indian-broker-api-safety](../indian-broker-api-safety/SKILL.md); it states no margin-API
facts today, so read the docs of the broker in use. Intraday square-off times are the broker's
own and come from its page ([nse-trading-calendar](../nse-trading-calendar/SKILL.md) §9).

**Why.** Margin depends on the instrument, the exchange's margin rules, the broker's policy and
the positions already held. Do not assume margin scales linearly with quantity: ask the broker's
margin endpoint for the actual quantity, because a per-unit figure from one call can be off at the
final size. A fixed multiplier is wrong the day any of them changes.

**Detector.** Grep for `leverage = `, `* 5`, `MIS_MULTIPLIER`. A test where the margin API
reports a requirement above the available margin for the final quantity must refuse, although the
per-unit pre-filter passed. A test
where the margin call fails must refuse, not fall back to a default multiplier.

## 7. Fail closed

**Rule.** Raise, and place nothing, on any of these:
- A quote older than a configured maximum age, or timestamped in the future. Kite's `/quote`
  response carries `timestamp` ("The exchange timestamp of the quote packet") and
  `last_trade_time` (nullable, "Last trade timestamp"); the `/quote/ohlc` and `/quote/ltp`
  responses carry no time field (https://kite.trade/docs/connect/v3/market-quotes/, read
  2026-11-26). Age the quote by `timestamp`. A thin stock can go minutes without a trade, so a
  stale `last_trade_time` alone is not a stale feed. Never size from an untimed price.
- A missing, zero or non-integer lot size, freeze quantity or tick size, for an instrument that
  needs it.
- A NaN, infinite, zero or negative price, budget, margin or ceiling. A non-number, a float
  that is not finite, a bool, and a naive (no timezone) datetime are also refused.
- A stop on the wrong side of the planned entry, or a stop or target that rounds onto or past
  entry (§5), and a planned entry that is off the tick grid.
- A quantity that rounds to 0 (§1).

The policy for who may override a stale quote is
[kite-connect-safety](../kite-connect-safety/SKILL.md) §8e: a person is warned and may
re-quote; a machine is blocked. The sizer has no `force` flag. A person's override is a new
price passed in, not a skipped check. Inject `now` so a replay is deterministic.

**Why.** Each of these turns arithmetic into a plausible-looking quantity: a NaN risk cap
compares false against everything, `min` can pick it up or skip it depending on order, and a
zero or negative margin per unit gives an infinite or negative cap. The cost of a wrong refusal is one missed order. The cost
of a wrong order is real money.

**Detector.** A parametrised test feeds each bad input above and asserts `SizingRefused` with a
broker client that fails the test if called, and the same for a stop between the planned entry
and a worse fresh quote. Include `Decimal("NaN")`, `float("nan")`,
`"inf"`, `True`, a naive datetime, `lot_size` or `freeze_qty` passed with `derivative=False`, a quote 10 seconds old against a 5-second limit, and a quote
from the future.

```python
def size_order(*, side, planned_entry, fresh_quote, quote_time, now, max_quote_age,
               stop, tick, risk_budget, max_position_value, available_margin,
               margin_per_unit, margin_check, order_value_ceiling,
               derivative=False, lot_size=None, freeze_qty=None, split_ok=False):
    buy = check_side(side)
    if not (isinstance(quote_time, datetime) and isinstance(now, datetime)
            and quote_time.utcoffset() is not None and now.utcoffset() is not None
            and isinstance(max_quote_age, timedelta)):
        raise SizingRefused("quote_time and now must be aware datetimes, max_quote_age a timedelta")
    age = now - quote_time
    if age < timedelta(0) or age > max_quote_age:
        raise SizingRefused(f"quote age {age} is outside 0..{max_quote_age}")
    if not derivative and (lot_size is not None or freeze_qty is not None):
        raise SizingRefused("lot_size or freeze_qty given with derivative=False")
    planned, fresh, tick = dec("planned_entry", planned_entry), dec("fresh_quote", fresh_quote), dec("tick", tick)
    if on_grid(planned, tick, ROUND_FLOOR) != planned:
        raise SizingRefused(f"planned entry {planned} is off the {tick} tick grid")
    stop = round_stop(stop, planned, tick, side)                # loss side of the planned entry
    ref = max(planned, fresh) if buy else min(planned, fresh)   # the worse price for this side
    caps = {                                                    # units each cap allows
        "risk": dec("risk_budget", risk_budget) / abs(ref - stop),
        "position_value": dec("max_position_value", max_position_value) / ref,
        "margin": dec("available_margin", available_margin) / dec("margin_per_unit", margin_per_unit),
        "order_value_ceiling": dec("order_value_ceiling", order_value_ceiling) / ref,
    }
    unit = 1
    if derivative:
        unit = whole("lot_size", lot_size)
        freeze = whole("freeze_qty", freeze_qty)
        if not split_ok:
            caps["freeze_quantity"] = Decimal(freeze)
    cap, raw = min(caps.items(), key=lambda kv: kv[1])          # ties: first in the dict
    qty = int(raw // unit) * unit
    if qty <= 0:
        raise SizingRefused(f"quantity 0: the {cap} cap allows {raw:.4f} units, one lot or unit is {unit}")
    try:
        ok = margin_check(qty)                                  # broker margin API for the final qty
    except Exception as exc:
        raise SizingRefused(f"margin check failed for {qty}: {exc!r}") from exc
    if ok is not True:
        raise SizingRefused(f"margin check refused {qty}")
    return qty, cap

def split_for_freeze(qty, lot_size, freeze_qty, max_slices):
    qty, lot, freeze = whole("qty", qty), whole("lot_size", lot_size), whole("freeze_qty", freeze_qty)
    biggest = freeze // lot * lot
    if biggest == 0 or qty % lot:
        raise SizingRefused(f"cannot split {qty} into lots of {lot} under freeze {freeze}")
    sizes = [biggest] * (qty // biggest) + ([qty % biggest] if qty % biggest else [])
    if max_slices is not None and len(sizes) > whole("max_slices", max_slices):
        raise SizingRefused(f"{len(sizes)} slices exceed max_slices {max_slices}")
    return [(i, len(sizes), q) for i, q in enumerate(sizes, 1)]  # index and total go into the key

def size_exit(requested_qty, open_qty, lot_size=None, freeze_qty=None):
    qty = min(whole("requested_qty", requested_qty), whole("open_qty", open_qty))
    if lot_size is None and freeze_qty is None:
        return [(1, 1, qty)]
    return split_for_freeze(qty, lot_size, freeze_qty, max_slices=None)  # paced, never refused for count
```

With `split_ok=False` the freeze quantity is one more cap, so the result is one order. With
`split_ok=True` the freeze cap is dropped and the caller passes the total to `split_for_freeze`,
then runs `margin_check` on each slice. `size_exit` has no price, risk or margin input, so a
stale quote or an exhausted budget cannot refuse it. The sketch is tested for lot rounding, freeze
split and refuse, tick direction for a buy and a sell, a fresh quote above plan, a stop between
plan and a worse quote, an off-grid entry, zero quantity, the margin re-check, exits, and NaN or
stale input.

## 8. These caps gate entries, not exits

**Rule.** Sizing runs on orders that open or increase a position. A closing or reducing order
is capped at the open quantity (`size_exit`) and is never refused because the risk budget or the
margin or position-value cap is 0, or because the quote is stale: entry-side limits never trap a
position ([indian-broker-api-safety](../indian-broker-api-safety/SKILL.md) §7). Above the freeze
quantity an exit is sliced like an entry, but a slice count over the entry limit never refuses
it. Check whether entries are still allowed on that date before sizing, using the session rule in
[nse-trading-calendar](../nse-trading-calendar/SKILL.md) §9, not a literal clock time. Algo
orders carry a limit price, or the broker's market-protection price for a market order (same
broker-safety §7), and the price used in §2 is that price. A re-sized quantity is a different
order, so its risk verdict is a new fingerprint
([kite-connect-safety](../kite-connect-safety/SKILL.md) §8i).

**Why.** The moment risk is exhausted is the moment a position most needs to be cut. A sizer
that returns 0 for an exit leaves the position open.

**Detector.** Exhaust the risk budget, then send an exit for the open quantity: it goes through.
Send an entry in the same state: it is refused. Send an exit larger than the position: capped
at the open quantity, never sent as a new entry.

## Verifying an implementation

- One cap per row of the §1 table, each made the smallest in turn, returns its own name (§1).
- A fresh quote above plan on a buy never raises the quantity; the sell case mirrors it (§2).
- F&O quantity is a multiple of the lot, rounded down; under one lot raises (§3).
- A quantity above the freeze quantity splits into lot-multiple slices summing to the total, or
  refuses; slices carry index and count for the key and PASS fingerprint; a rejected slice stops
  the rest (§4).
- The final quantity and each slice pass a fresh margin check (§6).
- Stop rounds away and target toward entry for both sides, on the instrument's tick (§5).
- No literal lot size, freeze quantity, tick size or leverage multiplier in the code (§3-§6).
- Every bad input in §7 raises with no broker call.
- An exit passes with the risk budget exhausted (§8).

## Scope

Arithmetic and failure handling for sizing one NSE equity or F&O order from a stop. It does not
choose entries, stops or targets, and it is engineering guidance, not trading or investment
advice. Order safety, ceilings and idempotency:
[kite-connect-safety](../kite-connect-safety/SKILL.md). SEBI algo rules and broker deltas:
[indian-broker-api-safety](../indian-broker-api-safety/SKILL.md). Session rules:
[nse-trading-calendar](../nse-trading-calendar/SKILL.md). Charges and tax on the trade:
[indian-equity-charges](../indian-equity-charges/SKILL.md),
[fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).
