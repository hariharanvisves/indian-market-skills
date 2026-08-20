---
name: indian-capital-gains-tax
description: Indian capital gains taxation — Section 111A STCG and 112A LTCG rates, the 12-month boundary, the annual aggregate exemption, 31-Jan-2018 grandfathering, the loss set-off ordering and 8-year carry-forward. Use when computing or reviewing capital gains, classifying a trade as short or long term, building tax-loss harvesting logic, or adapting any US-authored tax code. Explicitly covers the rules that differ from US law — no wash-sale rule, no deduction against ordinary income.
license: MIT
compatibility: Rates verified 2026-08-20 for AY 2026-27; re-verify before use, as they change with each Finance Act.
metadata:
  author: hariharanvisves
  version: "1.0"
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

## The four rules that differ from US law

**1. There is no wash-sale rule.** No 30-day, 61-day, or any window disallows a
loss because you re-entered. You may sell at a loss and re-buy the same scrip the
same day. Porting a wash-sale check **suppresses legitimate loss harvesting** —
it withholds a real benefit to satisfy a constraint that does not exist.

The narrow Indian analogue is **§94(7) dividend stripping**: where a security is
bought within 3 months *before* a record date and sold within 3 months *after*
(9 months for units), the loss is disallowed **only up to the dividend received**.
That is a cap on the disallowance, not a blanket denial.

Separately, a same-day sell/re-buy may be re-characterised as **intraday**
(speculative business income) rather than a capital transaction. That is a
classification question, not a disallowance.

**2. No loss offsets ordinary income.** There is no equivalent of the US $3,000
deduction against salary. A capital loss offsets capital gains, or it waits.

**3. The set-off is asymmetric.**

| Loss | May offset |
|---|---|
| **STCL** | STCG **and** LTCG |
| **LTCL** | **LTCG only** — never STCG |

A long-term loss cannot shelter a short-term gain. This is the single most
consequential rule for harvesting logic, and pooling the two — as US code does —
silently wipes out STCG that is actually taxable.

**4. Carry-forward is 8 years and conditional.** Unabsorbed loss carries forward
**8 assessment years**, and **only if the return is filed by the §139(1) due
date**. A late return forfeits it entirely. STCL and LTCL carry forward
**separately** and keep their character permanently — an LTCL never becomes
available to STCG in a later year.

## Correct computation order

```
1. LTCL  -> LTCG only
2. STCL  -> STCG first, then any surviving LTCG
3. Apply the s.112A exemption to the LTCG that SURVIVES set-off
   (a loss cannot consume the exemption)
4. Carry forward the remainder, by bucket, for 8 AYs
```

There is no step where a loss reaches ordinary income, and no step where an LTCL
reaches STCG.

## The 12-month boundary

"More than 12 months." A position held **exactly 365 days is short term** — the
predicate is `days_held > 365`, not `>= 365`. Off by one flips 20% to 12.5%, a
7.5-point swing on the whole gain.

Write the test at 365 and 366. A mid-range fixture passes with either operator and
proves nothing.

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

Implementing only `max(actual_cost, fmv)` is the common error and it manufactures
losses on every such holding. If no 31-Jan-2018 fair market value is available,
return the lot untouched rather than guessing — and say so, rather than emitting a
figure that looks derived.

For reporting, keep the **stepped** cost and the **actual** cost in separate
fields. Indian ITR schedules require both so the step-up stays auditable.

## Crypto / VDA is a different regime entirely

Virtual digital assets are taxed under **§115BBH at a flat 30%**, with **no loss
set-off of any kind and no carry-forward**. Every offsetting, harvesting and
carry-forward concept above is inapplicable. A skill or script written for crypto
tax-loss harvesting has **no valid use** on Indian VDA holdings.

## Verifying an implementation

- **Boundary-test the holding period** at 365 and 366 days.
- **Test the exemption with two trades**, not one — a single-trade fixture passes
  with per-trade exemption logic that would understate tax by the trade count.
- **Test a sale spanning 2024-07-23** and assert the rate follows the sale date.
- **Test the financial-year boundary** (31 March / 1 April) — the FY is
  1 April–31 March, and the exemption is annual, so calendar-year bucketing puts a
  January sale in the wrong year.
- **Test the asymmetry with a discriminating case:** a large LTCL against a large
  STCG must leave the STCG fully taxable. Then add a control — an STCL against an
  LTCG **must** offset — so the test can actually fail rather than blanket-blocking.
- **If grandfathering is implemented**, test a pre-2018 lot whose price *fell*.
  That is the case where the naive form fabricates a loss and the correct nested
  form does not.

## Scope

Informational only; **not tax advice**. Rates and thresholds change with every
Finance Act — load them from a dated table with a single owner, verify against the
Income Tax Department or a current professional source, and state the assessment
year alongside any figure you display.

Transaction charges (STT, stamp duty, GST, DP) are not taxes on gains and do not
net against them — see
[indian-equity-charges](../indian-equity-charges/SKILL.md).
