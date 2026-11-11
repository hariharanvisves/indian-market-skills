---
name: indian-capital-gains-tax
description: Indian capital gains tax on listed equity and equity mutual funds — §111A STCG and §112A LTCG rates, the more-than-12-months boundary in calendar months, the annual ₹1.25 lakh 112A exemption, 31-Jan-2018 grandfathering, asymmetric STCL/LTCL set-off and 8-year carry-forward. Use when computing or reviewing STCG/LTCG, classifying a lot as short or long term, building tax-loss harvesting, or porting US tax code (India has no wash-sale rule and no loss deduction against salary). Also covers SGBs, debt funds, non-equity ETFs, ELSS, crypto/VDA and fail-closed classification.
license: MIT
compatibility: Rates verified 2026-11-11 against the Income-tax Act 2025 (§196, §198) and the Finance Act 2026, for AY 2026-27 and tax year 2026-27; re-verify before use, as they change with each Finance Act.
metadata:
  author: hariharanvisves
  version: "1.2"
  verified: "2026-11-11"
  jurisdiction: India
---

# Indian Capital Gains Tax

Most capital-gains code in circulation was written against US law. Ported to
India it produces confident wrong answers, because **four structural rules
differ** — not just the rates. Those four are flagged below.

## Rates — listed equity and equity-oriented mutual funds, STT paid

| | Holding period | Rate | Section |
|---|---|---|---|
| **STCG** | 12 months or less | **20%** | 111A |
| **LTCG** | more than 12 months | **12.5%** | 112A |

- **Annual exemption: ₹1,25,000** of *aggregate* LTCG per financial year. LTCG
  only. Not per trade, not per scrip.
- Both rates changed on **2024-07-23** (STCG 15%→20%, LTCG 10%→12.5%, exemption
  ₹1,00,000→₹1,25,000). Key the rate to the **sale date**; a series spanning that
  date cannot use one constant.
- Surcharge and cess apply on top and are out of scope here.

Other asset classes are **not** §112A and get **no ₹1.25L exemption**: debt mutual
funds are taxed at slab; gold, foreign shares and sovereign gold bond secondary
sales fall under §112, some with a 24-month threshold. Classify before you rate.

## Section numbers and years: Income-tax Act 2025

The Income-tax Act 2025 replaced the 1961 Act from 1 April 2026 and renumbered
sections. The capital-gains group moved: **111A to 196, 112 to 197, 112A to 198**
(checked against the gazetted Act text). This skill uses
the 1961 numbers because most statements, schedules and ITR JSON field names
still carry them; check the field names of the schema you are emitting. Other
sections cited below are 1961-Act numbers: §94(7) is §175(8), §47(viic) is
§70(1)(x), §50AA is §76 and §55(2)(ac) is §90(7) of the 2025 Act; verify §115BBH
against statute for its 2025 equivalent.

Years: **financial year (FY)** means 1 April–31 March and is the period every
rule here works on. A return for FY 2025-26 is **AY 2026-27** (1961 Act); from
FY 2026-27 the 2025 Act calls the FY itself the **tax year** (tax year 2026-27).

## The four rules that differ from US law

**1. There is no wash-sale rule.** No 30-day, 61-day, or any window disallows a
loss because you re-entered. You may sell at a loss and re-buy the same scrip the
same day. Porting a wash-sale check **suppresses legitimate loss harvesting** —
it withholds a real benefit to satisfy a constraint that does not exist.

The narrow Indian analogue is **§94(7) dividend stripping**: where a security is
bought within 3 months *before* a record date and sold within 3 months *after*
(9 months for units), **and the dividend or income on it is exempt**, the loss is
disallowed **only up to the dividend received**. A taxable dividend does not
trigger it. That is a cap on the disallowance, not a blanket denial. Implement it
*instead of* a wash-sale check, as a dividend-linked cap, never as a re-entry
window. Its sibling **§94(8) bonus stripping** (§175(9); bought within 3 months before the
record date, bonus allotted, original sold within 9 months while the bonus is
kept) ignores the loss entirely. Dividend taxation and bonus cost basis:
[corporate-action-taxation](../corporate-action-taxation/SKILL.md).

Separately, a same-day sell/re-buy may be re-characterised as **intraday**
(speculative business income) rather than a capital transaction. That is a
classification question, not a disallowance; intraday and F&O as business income:
[fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).

**Detector.** Any re-entry window (`wash`, 30/61 days) in loss logic is ported US law.

**2. No loss offsets ordinary income.** There is no equivalent of the US $3,000
deduction against salary. A capital loss offsets capital gains, or it waits.
Porting the US deduction understates tax.
**Detector.** Any path from a capital-loss bucket to salary or total income.

**3. The set-off is asymmetric.**

| Loss | May offset |
|---|---|
| **STCL** | STCG **and** LTCG |
| **LTCL** | **LTCG only** — never STCG |

A long-term loss cannot shelter a short-term gain. This is the single most
consequential rule for harvesting logic, and pooling the two — as US code does —
silently wipes out STCG that is actually taxable.

**Detector.** A pooled `net = stcg + ltcg - losses`, or any long-term loss
subtracted from a short-term bucket.

**4. Carry-forward is 8 years and conditional.** Unabsorbed loss carries forward
for the **8 years** after the loss year (8 assessment years in 1961-Act terms),
and **only if the return is filed by the §139(1) due
date**. A late return forfeits it entirely. STCL and LTCL carry forward
**separately** and keep their character permanently — an LTCL never becomes
available to STCG in a later year.

**Detector.** Carry-forward state must hold two buckets, each with its loss year,
and read an on-time-filing flag; one pooled bucket or no expiry is a defect.

## Correct computation order

```
1. LTCL  -> LTCG only
2. STCL  -> STCG first, then any surviving LTCG
3. Apply the s.112A exemption to the LTCG that SURVIVES set-off
   (a loss cannot consume the exemption)
4. Carry forward the remainder, by bucket, for 8 years
```

There is no step where a loss reaches ordinary income, and no step where an LTCL
reaches STCG.

## The 12-month boundary

"More than 12 months", counted in **calendar months** (a month is a British-calendar
month under the General Clauses Act). A lot held **exactly 12 months is short
term**: bought 2025-01-10, sold 2026-01-10 is STCG; sold 2026-01-11 is LTCG. The
predicate is `sale_date > add_months(buy_date, 12)`, not `>=`, and not a day
count: `days_held > 365` is wrong whenever 29 February falls in the window
(bought 2023-03-01, sold 2024-03-01 is 366 days but exactly 12 months, so short
term). Off by one flips 20% to 12.5%, a 7.5-point swing on the whole gain.

**Detector.** `365`, `366` or a day `timedelta` in holding-period code. A
mid-range fixture passes with either operator and proves nothing; test the
boundaries listed under Verifying.

## Section 112A grandfathering — a two-level rule

For equity acquired **before 2018-02-01**:

```
cost = max(actual_cost, min(fmv_31_jan_2018, sale_consideration))
```

Read the nesting. It is a `max` against a `min`, not a substitution of the 2018
fair market value.

- The inner `min` is the **second proviso**. Without it, a stock that fell after
  2018 gets a cost basis above its sale price and the computation **fabricates a
  loss**.
- The outer `max` stops a pre-2018 fall from *reducing* a genuine cost.

Worked case: bought at ₹100, FMV ₹200 on 31 Jan 2018, sold at ₹150. Cost is
`max(100, min(200, 150))` = **₹150**, so the gain is **zero**. It is not a ₹50
gain (actual cost) and not a ₹50 loss (FMV alone).

Implementing only `max(actual_cost, fmv)` is the common error and it manufactures
losses on every such holding. Grandfathering applies to §112A assets only, so
non-equity ETFs are excluded. If no 31-Jan-2018 fair market value is available,
return the lot untouched rather than guessing — and say so, rather than emitting a
figure that looks derived.

For reporting, keep the **stepped** cost and the **actual** cost in separate
fields. Indian ITR schedules require both so the step-up stays auditable.

**Detector.** A `max(` over cost and the 31-Jan-2018 value with no inner `min(`
against sale consideration.

## Asset-class traps

**Classify before you rate.** Each of these is a way the equity rules get
applied to something they do not cover.

**Fail closed.** An unrecognised asset (bond, REIT, InvIT, property, empty
string) routes to **slab**, not to §112A. Defaulting to equity hands an unknown
asset a 12.5% rate and the exemption; slab is the taxpayer-unfavourable, and
therefore safe, direction, and an unclassified row stays visible.
**Detector.** Read the classifier's default branch; it must return slab.

**Sovereign gold bonds.**
- **Redemption at RBI maturity is exempt only if an individual held the bond
  from the date of original issue till maturity** (§70(1)(x) of the 2025 Act as
  substituted by the Finance Act 2026, from 1 April 2026; §47(viic) in 1961
  numbering). A secondary-market buyer's redemption, or an early redemption, is a
  taxable capital gain. Omit exempt redemptions from the capital-gains rows
  upstream; do not emit a zero row. Fail loudly if one reaches the schedule writer.
- A **market sale** before maturity is an ordinary §112 long-term gain (§197
  under the 2025 Act): no §112A exemption. Check for an SGB **before** any
  gold-matching regex, or "gold" in the name routes it wrongly.
- Match tranche symbols tightly (`SGB` plus six digits), not `^SGB`, which
  catches unrelated tickers. An SGB *fund* is a mutual fund with no exemption.
- The 2.5% coupon accrues on the tranche's **nominal issue price**, not on your
  cost. A secondary-market buyer's cost overstates it; an online-discount buyer's
  understates it. Hold nominal prices in a sourced table and render "issue price
  unknown" for an unlisted tranche rather than falling back to cost.

**Debt mutual funds** (a *specified mutual fund* under §50AA: more than 65% in
debt and money-market instruments). Units bought **on or after 1 April 2023** are taxed at
slab, always, whatever the holding period; there is no long-term bucket. Units
bought before that date keep a long-term path. Route on the **purchase** date,
not the sale date, and verify the current thresholds against statute before
coding either.

**Non-equity ETFs** (gold, silver, international) are under §112 (§197), not
§112A. So **no ₹1.25L exemption** and no §112A grandfathering. Keep them out of
the shared §112A exemption pool; spending the pool on them understates tax.
Verify the holding-period threshold per class.

**Foreign shares** (US-listed stocks, foreign-employer RSUs) get no §112A
treatment or exemption, as above. Their cost, FX conversion and disclosure: [foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md).

**ELSS.** The 3-year lock-in blocks redemption, so a harvesting plan cannot sell
a locked lot. Filter harvest candidates by lock-in, or the plan recommends sales
the platform will reject.

**Realised rows must be per lot.** Emit one row per sold lot with its own buy
date and gain type. A "MIXED" or multi-lot aggregate with a null purchase date
cannot be placed in a schedule, and hides lots that straddle the 12-month
boundary. If an aggregate reaches the writer, fail loudly rather than guess.

## Crypto / VDA is a different regime entirely

Virtual digital assets are taxed under **§115BBH at a flat 30%**, with **no loss
set-off of any kind and no carry-forward**. Every offsetting, harvesting and
carry-forward concept above is inapplicable. A skill or script written for crypto
tax-loss harvesting has **no valid use** on Indian VDA holdings.

## Verifying an implementation

- **Boundary-test the holding period** on the 12-month anniversary and the day
  after, including a window that spans 29 February.
- **Test the exemption with two trades**, not one — a single-trade fixture passes
  with per-trade exemption logic that would understate tax by the trade count.
- **Test a sale spanning 2024-07-23** and assert the rate follows the sale date.
- **Test the financial-year boundary** (31 March / 1 April) — the FY is
  1 April–31 March, and the exemption is annual, so calendar-year bucketing puts a
  January sale in the wrong year.
- **Test the asymmetry with a discriminating case:** a large LTCL against a large
  STCG must leave the STCG fully taxable. Then add a control — an STCL against an
  LTCG **must** offset — so the test can actually fail rather than blanket-blocking.
- **Test a same-day sell and re-buy at a loss** and assert the loss survives.
- **If grandfathering is implemented**, test a pre-2018 lot whose price *fell*.
  That is the case where the naive form fabricates a loss and the correct nested
  form does not.

## Scope

Resident-individual capital gains on the asset classes above. Informational only;
**not tax advice**. Rates change with every Finance Act — load them from a dated,
single-owner table, verify against the Income Tax Department, and state the AY or
tax year beside any figure you display.

Not here: F&O and intraday ([fno-tax-and-charges](../fno-tax-and-charges/SKILL.md));
buybacks, splits, demergers ([corporate-action-taxation](../corporate-action-taxation/SKILL.md));
US stocks, LRS/TCS, Schedule FA ([foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md));
ITR forms and schedules ([itr-filing-schedules](../itr-filing-schedules/SKILL.md));
transaction charges, which never net against a gain
([indian-equity-charges](../indian-equity-charges/SKILL.md)).
