---
name: mf-scheme-matching
description: Rules for matching Indian mutual-fund scheme names across CAS, CAMS, KFintech, Groww and AMFI data without silently merging different funds — total-parse matching, plan and option slots (Direct/Regular, Growth/IDCW), rename aliases, AMFI NAVAll.txt lookup by ISIN, folio-aware FIFO grouping, and price-free cross-source dedupe. Use when importing mutual-fund transactions from more than one source, writing a scheme resolver or fuzzy name matcher, fixing duplicate or merged holdings, or changing anything that feeds FIFO lots or realised capital gains.
license: MIT
compatibility: Applies to AMFI, CAMS, KFintech and broker-app scheme naming conventions as of the SEBI 2021 IDCW rename.
metadata:
  author: hariharanvisves
  version: "1.1"
  jurisdiction: India
  verified: "2026-11-11"
---

# Mutual-Fund Scheme Matching

One wrong merge puts two funds into one FIFO queue: lots are consumed from the
wrong fund and realised gains are wrong, with nothing erroring. One wrong split
leaves a fund visible as "unresolved". **Every failure must fall toward
unresolved, never toward a merge.** Format facts for the source files are in
[indian-broker-statement-formats](../indian-broker-statement-formats/SKILL.md).

## 1. Parse totally; do not compare token bags

**Rule.** Walk the name's tokens left to right and require that **every** token
lands in exactly one slot: `identity`, `plan` (direct | regular | not stated), or
`option` (growth | idcw payout | idcw reinvestment | bonus | not stated). A token
fitting no slot fails the whole parse, and a failed parse is unresolved. Two
names match only if all three slots are equal, identity as an ordered exact
string.

**Why.** Every bag-of-tokens or subset approach lets a token that carries
identity vanish from the comparison, and a vanished token can only cause a false
accept. In the project this came from, six review rounds produced six distinct
silent merges, each introduced by the fix for the previous one.

**Tell.** Matching code with `Set`, `includes`, overlap ratios, "strip noise",
or "first matching word wins". Delete it.

## 2. No fuzzy, Jaccard, edit-distance or token-subset matching

**Rule.** Do not "generalise" the resolver into a similarity score.
Equivalence between two different spellings comes only from an explicit,
sourced allow-list (section 5), never from closeness.

**Why.** "Flexi Cap" vs "Focused" differ by one word; "Direct" vs "Regular"
differ by one token and by a different expense ratio and NAV. Similarity cannot
tell a rename from a different fund.

**Tell.** A threshold constant (0.45, 0.8) in a name matcher.

## 3. `option: null` is not Growth

**Rule.** A name that never states an option has `option = null` (the "not
stated" value of section 1). Default it only
by a **per-scheme** table with a cited source, never globally. Compare null to
null; never null to growth.

**Why.** Defaulting globally merges a Growth holding into its IDCW sibling and
corrupts the lots. Likewise a name that is silent on plan must not match a
Direct name.

**Tell.** `option ?? 'growth'` anywhere outside a per-scheme table.

## 4. Widen the vocabulary, never the rule

**Rule.** When a real name fails, add what a token **means** (a new alias, a new
abbreviation) and keep the equality rule unchanged. Each addition needs an
anti-over-merge test proving two genuinely different funds stay distinct;
Direct vs Regular is the standard probe.

**Vocabulary to handle explicitly:**
- Abbreviations: `DG` (direct growth), `RG` (regular growth), `DP` (direct
  plan), `Dir`, `Reg`, `Gr`.
- Custody suffix such as `(Non-Demat)`.
- Rename annotations `(formerly ...)` / `(erstwhile ...)`: strip the annotation
  **before** tokenizing, so the old name is not parsed as part of the identity.
- A repeated identical option ("Direct Growth Plan Growth Option") is one
  option, not a conflict. A second, different option, or two plans, fails the
  parse.
- Option words are not deletable noise: "Growth Opportunities Fund" and
  "Dividend Yield Fund" contain option words inside the scheme's own name. Treat
  `fund` / `scheme` as identity boundaries and read the option only from the
  tail.

**Why.** A loosened rule applies to every name; a vocabulary entry applies only
to the token it defines.

**Tell.** A fix that edits the comparison function instead of a vocabulary table.

## 5. Renames and dividend-to-IDCW: explicit and sourced

**Rule.** Hold scheme renames as an allow-list of name groups, each with a
source. AMC renames (house name changes) are **flagged for review, never
matched**. SEBI's rename of Dividend options to IDCW (1 Apr 2021) is a vocabulary map
you add deliberately; do not let the matcher treat the two words as equal by
default.

**Why.** An unresolved old-name row is visible and recoverable. A wrong graft is
silent.

**Tell.** A resolver that returns a match for names no source says are the same
fund.

## 6. Dropped AMC prefix: last-resort suffix match, narrowly

**Rule.** RTA exports state the fund house in its own column and omit it from the
scheme name. Allow a prefix-dropped match only when all hold: the shorter name
is an **ordered suffix** of the longer; plan and option are exactly equal; the
hit is **unique** (0 = unknown, more than 1 = ambiguous; both reject); and only
the *stored* name may be the longer one. A declared AMC that does not match is
disqualifying evidence, not missing evidence.

**Why.** Each relaxed condition admits a same-suffix fund of another house, and
that merge is silent.

**Tell.** Two stored funds both satisfying the suffix test: the row must stay
unresolved.

## 7. Prefer the ISIN; pick AMFI schemes by ISIN

**Rule.** When a source carries the ISIN (CAS scheme headers do), key on it and
treat name matching as the fallback. The AMFI `NAVAll.txt` file
(`portal.amfiindia.com/spages/NAVAll.txt`; the `www.amfiindia.com` URL redirects) is
semicolon-delimited. Checked 2026-11-11, the header has 8 columns:

```
Scheme Code ; ISIN Div Payout/ ISIN Growth ; ISIN Div Reinvestment ; Scheme Name ; Plan ; Option ; Net Asset Value ; Date
```

Older copies had 6 columns, without `Plan` and `Option`. Missing ISINs are `-`;
`Plan` and `Option` are empty on matured schemes; dates are `dd-Mon-yyyy`.
Section headers (category lines, AMC name lines) and blank lines are
interleaved with data rows; skip anything that does not split into the header's
column count. Select the row by **ISIN**, matched against **both** ISIN columns;
selecting by name text re-introduces everything above.

**Why.** A scheme code is one plan/option, and the ISIN is the stable per-option
identifier across sources. `Option` is spelled many ways (`IDCW`, `Growth Option`,
`Payout of Income Distribution cum capital withdrawal option`), so do not match on
it. Read the column order from the file header on every download.

**Tell.** An NAV looked up by a name search returning a Regular-plan NAV for a
Direct holding.

## 8. Cross-source dedupe: price-free, precision-tolerant, month-bucketed

**Rule.** The same purchase arrives from the RTA and from the broker app. Key
the duplicate check on `asset class | resolved symbol | side | date | units`,
**without price**.

- **Price-free:** NAV differs between sources by stamp duty and rounding, units
  do not. A price-including hash can never dedupe across sources.
  Never dedupe on amount alone: a second SIP instalment has a near-identical amount.
- **Precision-tolerant:** broker apps often report units to 2 decimals and RTAs
  to 3. Compare `|a - b| <= tolerance` as an **absolute** unit bound (guard the float
  boundary as in
  [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md) §8), never
  `round2(a) === round2(b)` (sources that round `x.xx5` down disagree with
  half-up rounding) and never a percentage (a percentage scales with trade size).
- **Date-tolerant:** the same transaction can differ by a few days between order
  and allotment; bucket by month and accept a small day tolerance, but keep it
  small: two genuine SIP instalments sit a month apart.
- **Different sources only:** require the two `source` values to differ;
  identical-source rows are real repeats.
- Resolve names to the stored canonical symbol **before** the dedupe, or the key
  never matches.

**Tell.** Units of a fund double after importing a second statement.
Reconcile per fund against a holdings statement: expect a ratio of **1.000**;
exactly 2.000 is a duplicate; 1.1-1.9 usually means one source covers only part of
the position. Aggregate the statement per fund first (a fund in two folios reads as
a spurious multiple), and a switch pair is not a duplicate.

## 9. Folio belongs in the FIFO grouping key

**Rule.** Group lots by `(fund identity, folio)`, not by fund alone, wherever
the source carries a folio. Merge folios only for display aggregates.

**Why.** Two folios of one fund hold different lot ages and costs; a switch or
redemption consumes from the folio it was placed in. Pooling them changes which
lots are sold, so changes the realised gain and the holding period.

**Tell.** A fund with two folios whose realised STCG/LTCG split disagrees with
the RTA's own statement.

## 10. Re-import gate: realised gains unchanged to the rupee

**Rule.** After importing a second statement covering history already held,
recompute the realised capital gains for the financial year. They must be
**identical to the rupee** to the figure before the import. Any change means a
duplicate slipped past the key or a lot was mis-grouped.

**Why.** Duplicate or merged rows do not crash; they alter FIFO consumption and
the tax figure. This is the one end-to-end check that sees both defects.

**Tell.** Total units rise while cash flow is unchanged. Run the gate on real
files before declaring an importer done; unit tests pin the key, not the
outcome.

## 11. Verifying an implementation

- **Anti-over-merge cases per slot:** Direct vs Regular; Growth vs IDCW
  Payout vs IDCW Reinvestment; "X Fund" vs "X Focused Fund"; a name with the
  AMC prefix dropped that fits two stored funds.
- **A discriminating dedupe fixture:** two records at 2dp vs 3dp units that
  differ by exactly the tolerance and by slightly more; a fixture with equal
  inputs cannot fail an inequality.
- **Mutation-check the guard:** weaken the matcher to a subset test and watch
  the anti-over-merge test fail, then restore.
- **Unresolved is a reported outcome:** return the list of unresolved names to
  the user; a silent skip is the same defect as a wrong merge.
- **Run the re-import gate on real files** (section 10) before calling an
  importer done.

## Scope

Scheme identity, NAV lookup, cross-source dedupe and FIFO grouping for Indian
mutual funds. Source file layouts are in
[indian-broker-statement-formats](../indian-broker-statement-formats/SKILL.md);
tax on the realised gains is in
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).

Naming conventions differ by AMC and change at SEBI re-categorisations. Use
synthetic names in tests, for example "Example Flexi Cap Fund - Direct Growth".
