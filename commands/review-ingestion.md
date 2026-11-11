---
description: "Review broker-statement, CAS and RTA parsers for false merges, duplicates and coverage gaps"
argument-hint: "[path or git range — defaults to the current diff]"
---

Dispatch the `indian-market-skills:statement-ingestion-reviewer` subagent to review $ARGUMENTS. If no target is given, review the uncommitted diff, or the last commit if the tree is clean.

Relay its findings exactly as it reports them, most severe first. Do not apply fixes unless the user asks.
