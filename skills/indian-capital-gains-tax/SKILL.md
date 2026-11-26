---
name: indian-capital-gains-tax
description: Indian capital gains tax on listed equity and equity mutual funds — §111A STCG (20%) and §112A LTCG (12.5%) rates, the more-than-12-months boundary counted in calendar months, the annual ₹1.25 lakh 112A exemption, 31-Jan-2018 grandfathering, asymmetric STCL/LTCL set-off and 8-year carry-forward. Use when computing or reviewing STCG/LTCG, classifying a lot as short or long term, writing a holding-period or add_months function, building tax-loss harvesting, or porting US tax code (India has no wash-sale rule and no loss deduction against salary), even if the user only says "capital gains" or "tax harvesting". Also covers SGBs, debt funds, non-equity ETFs, ELSS, crypto/VDA and fail-closed classification.
license: MIT
compatibility: Rates verified 2026-11-11 against the Income-tax Act 2025 (§196, §198) and the Finance Act 2026, for AY 2026-27 and tax year 2026-27; re-verify before use, as they change with each Finance Act.
metadata:
  author: hariharanvisves
  version: "1.4"
  verified: "2026-11-11"
  jurisdiction: India
---

# Indian Capital Gains Tax

Most capital-gains code in circulation was written against US law. Ported to
India it produces confident wrong answers, because **four structural rules
differ**, not just the rates. This skill states those rules, the rates, and the
traps that route an asset into the wrong regime.

## Core rules

1. **Long term means more than 12 months in calendar months**, so exactly 12 months is
   short term: `sale > add_months(buy, 12)`, never a day count ([section 5](#5-the-12-month-boundary)).
2. **Listed equity, STT paid:** STCG **20%** (§111A), LTCG **12.5%** (§112A), annual
   exemption **₹1,25,000** on aggregate LTCG only. Key the rate to the **sale date** ([section 1](#1-rates-listed-equity-and-equity-oriented-mutual-funds-stt-paid)).
3. **No wash-sale rule.** A same-day sell and re-buy keeps the loss. Port §94(7) as a cap at the exempt dividend received, applied only when that dividend is exempt, never a re-entry window ([section 3](#3-the-four-rules-that-differ-from-us-law)).
4. **No capital loss reaches salary or any ordinary income.**
5. **Set-off is asymmetric:** STCL offsets STCG and LTCG; LTCL offsets LTCG only.
6. **Carry-forward is 8 years**, per bucket, and only if the return was filed by the due date.
7. **The exemption applies after set-off**, to the LTCG that survives ([section 4](#4-correct-computation-order)).
8. **Grandfathering is `max(cost, min(fmv_31_jan_2018, sale))`**, never `max(cost, fmv)` ([section 6](#6-section-112a-grandfathering-a-two-level-rule)).
9. **STT is never deductible** in a gain computation; brokerage is not barred.
10. **Unknown asset class routes to slab**, not §112A; VDA is a separate 30% regime ([sections 7](#7-asset-class-traps) and [8](#8-crypto--vda-is-a-different-regime-entirely)).

## 1. Rates: listed equity and equity-oriented mutual funds, STT paid

| | Holding period | Rate | Section |
|---|---|---|---|
| **STCG** | 12 months or less | **20%** | 111A |
| **LTCG** | more than 12 months | **12.5%** | 112A |

- **Annual exemption: ₹1,25,000** of *aggregate* LTCG per financial year. LTCG
  only. Not per trade, not per scrip.
- Both rates changed on **2024-07-23** (STCG 15%→20%, LTCG 10%→12.5%). Key the rate to the
  **sale date**. The ₹1,25,000 limit applies to the aggregate of LTCG before and after that date for the whole of FY 2024-25 (§112A proviso, Finance (No. 2) Act 2024 s.31); a series spanning that
  date cannot use one rate constant.
- Surcharge and cess apply on top and are out of scope here.

Other asset classes are **not** §112A and get **no ₹1.25L exemption**: debt mutual
funds are taxed at slab; gold, foreign shares and sovereign gold bond secondary
sales fall under §112, some with a 24-month threshold. Classify before you rate.

## 2. Section numbers and years: Income-tax Act 2025

The Income-tax Act 2025 replaced the 1961 Act from 1 April 2026 and renumbered
sections. The capital-gains group moved: **111A to 196, 112 to 197, 112A to 198**
(checked against the gazetted Act text). This skill uses
the 1961 numbers because most statements, schedules and ITR JSON field names
still carry them; check the field names of the schema you are emitting. Other
sections cited below are 1961-Act numbers: §94(7) is §175(8), §47(viic) is
§70(1)(x), §50AA is §76, §55(2)(ac) is §90(7) and §115BBH is §194(1) Table Sl. 4
of the 2025 Act (Gazette text, Act No. 30 of 2025).

Years: **financial year (FY)** means 1 April–31 March and is the period every
rule here works on. A return for FY 2025-26 is **AY 2026-27** (1961 Act); from
FY 2026-27 the 2025 Act calls the FY itself the **tax year** (tax year 2026-27).

## 3. The four rules that differ from US law

### 3.1 There is no wash-sale rule

No 30-day, 61-day, or any window disallows a loss because you re-entered. You may
sell at a loss and re-buy the same scrip the same day.

**Why.** A wash-sale check **suppresses legitimate loss harvesting**: it withholds
a real benefit to satisfy a constraint that does not exist.

The narrow Indian analogue is **§94(7) dividend stripping**: where a security is
bought within 3 months *before* a record date and sold within 3 months *after*
(9 months for units), **and the dividend or income on it is exempt**, the loss is
disallowed **only up to the dividend received**. A taxable dividend does not
trigger it. That is a cap on the disallowance, not a blanket denial. Implement it
*instead of* a wash-sale check, as a dividend-linked cap, never as a re-entry
window. Its sibling **§94(8) bonus stripping** (§175(9); bought within 3 months before the
record date, bonus allotted, original sold within 9 months while the bonus is
kept) ignores the loss on the original, and that ignored loss becomes the cost of the
retained bonus shares. The mechanics, plus dividend taxation and bonus cost basis,
are owned by [corporate-action-taxation](../corporate-action-taxation/SKILL.md).

Separately, a same-day sell/re-buy may be re-characterised as **intraday**
(speculative business income) rather than a capital transaction. That is a
classification question, not a disallowance; intraday and F&O as business income:
[fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).

**Detector.** Any re-entry window (`wash`, 30/61 days) in loss logic is ported US law.

### 3.2 No loss offsets ordinary income

There is no equivalent of the US $3,000 deduction against salary. A capital loss
offsets capital gains, or it waits. Porting the US deduction understates tax.

**Detector.** Any path from a capital-loss bucket to salary or total income.

### 3.3 The set-off is asymmetric

| Loss | May offset |
|---|---|
| **STCL** | STCG **and** LTCG |
| **LTCL** | **LTCG only**, never STCG |

**Why.** A long-term loss cannot shelter a short-term gain. This is the most
consequential rule for harvesting logic, and pooling the two, as US code does,
silently wipes out STCG that is actually taxable.

**Detector.** A pooled `net = stcg + ltcg - losses`, or any long-term loss
subtracted from a short-term bucket.

### 3.4 Carry-forward is 8 years and conditional

Unabsorbed loss carries forward for the **8 years** after the loss year (8
assessment years in 1961-Act terms), and **only if the return is filed by the
§139(1) due date**. A late return forfeits it entirely. STCL and LTCL carry
forward **separately** and keep their character permanently: an LTCL never
becomes available to STCG in a later year.

**Detector.** Carry-forward state must hold two buckets, each with its loss year,
and read an on-time-filing flag; one pooled bucket or no expiry is a defect.

## 4. Correct computation order

```
1. LTCL  -> LTCG only
2. STCL  -> STCG first, then any surviving LTCG
3. Apply the s.112A exemption to the LTCG that SURVIVES set-off
   (a loss cannot consume the exemption)
4. Carry forward the remainder, by bucket, for 8 years
```

There is no step where a loss reaches ordinary income, and no step where an LTCL
reaches STCG.

**Worked example.** Two lots held over two years, each with a ₹1,00,000 gain,
and separately ₹3,00,000 STCG against a ₹2,00,000 LTCL:

```python
def cg_tax(stcg, ltcg, stcl=0, ltcl=0, exemption=125_000):  # rates for sales on or after 2024-07-23
    ltcg_after = max(ltcg - ltcl, 0)
    ltcl_left = max(ltcl - ltcg, 0)              # LTCL never touches STCG
    stcg_after = max(stcg - stcl, 0)
    stcl_left = max(stcl - stcg, 0)
    stcl_carry = max(stcl_left - ltcg_after, 0)  # STCL left after STCG and LTCG
    ltcg_after = max(ltcg_after - stcl_left, 0)  # surplus STCL reaches LTCG
    taxable_ltcg = max(ltcg_after - exemption, 0)  # exemption after set-off
    return 0.20 * stcg_after + 0.125 * taxable_ltcg, ltcl_left, stcl_carry

cg_tax(0, 200_000)                   # (9375.0, 0, 0): (2,00,000 - 1,25,000) = 75,000 x 12.5%
cg_tax(300_000, 0, ltcl=200_000)     # (60000.0, 200000, 0): STCG fully taxable, LTCL carried forward
cg_tax(0, 30_000, stcl=50_000)       # (0.0, 0, 20000): STCL absorbed by LTCG, rest carried forward
```

A per-trade exemption would give ₹0 on the first call. Pooling the LTCL into
STCG would give ₹20,000 instead of ₹60,000 on the second.

**STT is not deductible** in computing capital gains: not as cost, not as a
transfer expense (§72(3)(b), §76(4) of the 2025 Act; proviso to §48 in 1961
numbering). A parser that subtracts STT from sale consideration, or adds it to
cost, understates tax. Brokerage is a different charge: the STT bar does not
reach it.

**Detector.** An STT term anywhere in a gain or cost expression.

## 5. The 12-month boundary

"More than 12 months", counted in **calendar months** (a month is a British-calendar
month under the General Clauses Act). A lot held **exactly 12 months is short
term**: bought 2025-01-10, sold 2026-01-10 is STCG; sold 2026-01-11 is LTCG. The
predicate is `sale_date > add_months(buy_date, 12)`, not `>=`, and not a day
count.

```python
from dateutil.relativedelta import relativedelta

def is_long_term(buy, sale):
    return sale > buy + relativedelta(months=12)

# bought 2023-03-01, sold 2024-03-01: 366 days, exactly 12 months -> short term
# days_held > 365 says long term here, the wrong answer
```

**Why.** `days_held > 365` is wrong whenever 29 February falls in the window.
Off by one flips 20% to 12.5%, a 7.5-point swing on the whole gain.

**Detector.** `365`, `366` or a day `timedelta` in holding-period code. A
mid-range fixture passes with either operator and proves nothing; test the
boundaries listed under Verifying.

## 6. Section 112A grandfathering: a two-level rule

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

**Worked example.** Bought at ₹100, FMV ₹200 on 31 Jan 2018, sold at ₹150. Cost is
`max(100, min(200, 150))` = **₹150**, so the gain is **zero**. It is not a ₹50
gain (actual cost) and not a ₹50 loss (FMV alone).

Implementing only `max(actual_cost, fmv)` is the common error and it manufactures
losses on every such holding. Grandfathering applies to §112A assets only, so
non-equity ETFs are excluded; units of an equity-oriented fund are covered, with the
31-Jan-2018 NAV as the fair market value (§90(7) of the 2025 Act). If no 31-Jan-2018 fair market value is available,
return the lot untouched rather than guessing, and say so, rather than emitting a
figure that looks derived.

For reporting, keep the **stepped** cost and the **actual** cost in separate
fields. Indian ITR schedules require both so the step-up stays auditable.

**Detector.** A `max(` over cost and the 31-Jan-2018 value with no inner `min(`
against sale consideration.

## 7. Asset-class traps

**Classify before you rate.** Each of these is a way the equity rules get
applied to something they do not cover.

**Fail closed.** An unrecognised asset (bond, REIT, InvIT, property, empty
string) routes to **slab**, not to §112A. Defaulting to equity hands an unknown
asset a 12.5% rate and the exemption; slab is the taxpayer-unfavourable, and
therefore safe, direction, and an unclassified row stays visible.
**Detector.** Read the classifier's default branch; it must return slab.

**Sovereign gold bonds.** Redemption at RBI maturity is exempt only for an individual who held from original issue till maturity (§70(1)(x) of the 2025 Act as substituted by the Finance Act 2026, from 1 April 2026; §47(viic) in 1961 numbering); earlier redemptions by any individual were exempt. A secondary-market buyer's redemption, or an early redemption, is taxable. Omit exempt redemptions upstream (no zero row) and fail loudly if one reaches the schedule writer. A market sale is a §112 gain with no §112A exemption, and an SGB fund is a mutual fund with no exemption. Check for an SGB before any gold-matching regex. Read [references/sgb-and-debt-funds.md](references/sgb-and-debt-funds.md) when classifying an SGB, its coupon base or tranche symbol.

**Debt mutual funds** (*specified mutual fund*, §76(5)(b) of the 2025 Act: more than 65% debt/money-market; §50AA in 1961 numbering, whose definition differed before 1 Apr 2026): units bought **on or after 1 April 2023** are taxed at slab whatever the holding period, while units bought before 1 Apr 2023 keep a long-term path; route on the **purchase** date. Read the same reference for the 1 April 2026 definition change and fund-of-funds ordering. An unknown MF sub-category must reject (fail closed), never default to equity.

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

## 8. Crypto / VDA is a different regime entirely

Virtual digital assets are taxed under **§115BBH at a flat 30%**, with **no loss
set-off of any kind and no carry-forward**. Every offsetting, harvesting and
carry-forward concept above is inapplicable. A skill or script written for crypto
tax-loss harvesting has **no valid use** on Indian VDA holdings.

## Verifying an implementation

- **Boundary-test the holding period** on the 12-month anniversary and the day
  after, including a window that spans 29 February.
- **Test the exemption with two trades**, not one: a single-trade fixture passes
  with per-trade exemption logic that would understate tax by the trade count.
- **Test a sale spanning 2024-07-23** and assert the rate follows the sale date.
- **Test the financial-year boundary** (31 March / 1 April): the FY is
  1 April–31 March, and the exemption is annual, so calendar-year bucketing puts a
  January sale in the wrong year.
- **Test the asymmetry with a discriminating case:** a large LTCL against a large
  STCG must leave the STCG fully taxable. Then add a control (an STCL against an
  LTCG **must** offset) so the test can actually fail rather than blanket-blocking.
- **Test a same-day sell and re-buy at a loss** and assert the loss survives.
- **If grandfathering is implemented**, test a pre-2018 lot whose price *fell*.
  That is the case where the naive form fabricates a loss and the correct nested
  form does not.

## Scope

Resident-individual capital gains on the asset classes above. Informational only;
**not tax advice**. Rates change with every Finance Act: load them from a dated,
single-owner table, verify against the Income Tax Department, and state the AY or
tax year beside any figure you display.

Not here: F&O and intraday ([fno-tax-and-charges](../fno-tax-and-charges/SKILL.md));
buybacks, splits, demergers ([corporate-action-taxation](../corporate-action-taxation/SKILL.md));
US stocks, LRS/TCS, Schedule FA ([foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md));
ITR forms and schedules ([itr-filing-schedules](../itr-filing-schedules/SKILL.md));
transaction charge rates ([indian-equity-charges](../indian-equity-charges/SKILL.md));
STT never nets against a gain (see "STT is not deductible" in section 4).
