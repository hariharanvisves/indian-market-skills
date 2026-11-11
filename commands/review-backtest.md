---
description: "Review a backtest for look-ahead, survivorship, cost and metric errors on Indian markets"
argument-hint: "[path or git range — defaults to the current diff]"
---

Dispatch the `indian-market-skills:backtest-reviewer` subagent to review $ARGUMENTS. If no target is given, review the uncommitted diff, or the last commit if the tree is clean.

Relay its findings exactly as it reports them, most severe first. Do not apply fixes unless the user asks.
