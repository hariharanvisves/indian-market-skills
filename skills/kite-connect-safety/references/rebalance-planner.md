# Rebalance planner: plan and approve, owned quantity, test traps

Purpose: planner details behind section 9 of [SKILL.md](../SKILL.md). The BUY / SELL / HOLD /
IGNORE rules and the T1 holdings rule stay in SKILL.md.

## Two-phase plan and approve

The rebalance function only **plans**. Executing with `dryRun: false` requires an approved
plan id, and one executor function is the sole caller of `placeOrder`. This sits behind the
live-path gate (section 7 of SKILL.md).

## Owned quantity

Take it from the app's own order ledger as BUY minus SELL filled quantity over
**final-status** rows only, per exchange.

## Input validation

Validate an empty or invalid universe or symbol list before the exchange lookup, so the
route returns 4xx, not 500.

## Test trap

A mutant that drops the final-status filter survives when the fixture's non-final row has
NULL `filled_quantity`, because SQL `SUM` ignores NULL. Use a non-final row with a partial
fill.

## Detector fixtures

- An ETF in holdings and not in the managed set must come out `IGNORE`.
- Run the planner twice: the second run is all HOLD.
- Make the holdings call throw: nothing is placed.
