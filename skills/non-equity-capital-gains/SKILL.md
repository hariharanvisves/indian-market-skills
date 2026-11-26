---
name: non-equity-capital-gains
description: Indian capital gains tax for a resident individual or HUF on assets other than listed equity and equity mutual funds — land and buildings, gold and jewellery, unlisted shares, depreciable block assets. Covers the more-than-24-months holding test, 12.5% LTCG without indexation, the pre-23-Jul-2024 land and building option (20% with indexation, pay the lower), Cost Inflation Index and 1 April 2001 cost, stamp-duty-value substitution with its 110% band, and the exemptions §82 (old 54), §86 (old 54F), §85 (old 54EC) and the Capital Gains Account deposit. Use when computing or reviewing a property-sale, gold or unlisted-share gain, writing an indexation or stamp-duty-value function, building a house-purchase exemption or 54EC bond planner, or porting US cost-basis rules that have no indexation or reinvestment exemption. Gives Income-tax Act 2025 sections with 1961 equivalents.
license: MIT
compatibility: Verified 2026-11-26 against the gazetted Income-tax Act 2025 (§2(101), §72 to §91, §196, §197, §263; Act No. 30 of 2025) and checked against the enacted Finance Act 2026 (Act No. 4 of 2026), which does not amend §2(101), §72 to §91 or §196 to §198 (it substitutes the §263(1)(c) table and §263(5)). Tax year 2026-27 onward. Cost Inflation Index figures are not carried; load them from the CBDT notification. The Taxation and Other Laws (Amendment) Act 2026 (Act No. 21 of 2026) does not amend these sections. Re-verify before use, as rates change with each Finance Act.
metadata:
  author: hariharanvisves
  version: "1.1"
  verified: "2026-11-26"
  jurisdiction: India
---

# Non-Equity Capital Gains (Resident Individual)

Code ported from US law, or from the listed-equity rules, gets property and gold
wrong in four ways: the wrong holding period (24 months, not 12), indexation
applied to everything or to nothing, the stamp-duty value ignored, and house-purchase
exemptions measured on the wrong base. This skill covers the rules that
decide those four.

## Core rules

1. **Long term means more than 24 months** for land, buildings, gold, jewellery and unlisted shares. Exactly 24 months is short term ([section 1](#1-asset-classes-and-the-holding-period)).
2. **Long-term rate is 12.5% with no indexation** (§197). A short-term gain on these assets is taxed at slab rates; the §196 equity rate is not theirs ([section 2](#2-rates)).
3. **Land or building acquired before 2024-07-23, held by a resident individual or HUF: tax is the lower of** 12.5% without indexation and 20% with indexation. No other asset and no other holder gets the option ([section 2](#2-rates)).
4. **Indexed cost = cost x CII(transfer year) / CII(later of first year held and 2001-02).** Transfer expenses are never indexed ([section 3](#3-indexation-and-cost)).
5. **Asset held before 2001-04-01 (by you or, for a gift or inheritance, the previous owner): cost or fair market value on that date, at the taxpayer's option.** For land and buildings that value is capped at the stamp duty value of that date ([section 3](#3-indexation-and-cost)).
6. **Land or building sold below the stamp duty value: the stamp duty value is the sale price, unless it is within 110% of the actual price** ([section 4](#4-stamp-duty-value-replaces-the-sale-price)).
7. **A depreciable block asset has no holding period.** The excess over the block is always short term ([section 5](#5-depreciable-block-assets)).
8. **Old 54 (§82): house to house, measured on the gain.** Cost of the new house capped at ₹10 crore ([section 6.1](#61-82-old-54-residential-house-to-residential-house)).
9. **Old 54F (§86): other asset to house, measured on net consideration**, so the exemption is proportional ([section 6.2](#62-86-old-54f-other-long-term-asset-to-a-residential-house)).
10. **Old 54EC (§85): land or building only, any assessee, ₹50 lakh, six months, five-year lock-in.** No deposit route ([section 6.3](#63-85-old-54ec-specified-bonds)).
11. **Unspent gain goes to the notified deposit scheme before you file**, and by the due date at the latest ([section 6.4](#64-the-capital-gains-account-deposit)).
12. **Fail closed.** Unknown asset kind or a missing date raises; it never defaults to listed equity or to long term ([section 1](#1-asset-classes-and-the-holding-period)).

## 1. Asset classes and the holding period

| Asset | Long term when held | LTCG | STCG |
|---|---|---|---|
| Land, building | more than 24 months | 12.5%, §197 | slab |
| Physical gold, jewellery, other capital assets | more than 24 months | 12.5%, §197 | slab |
| Unlisted shares | more than 24 months | 12.5%, §197 | slab |
| Unlisted bond or debenture transferred on or after 2024-07-23 | never | none | slab, §76(2)(b) |
| Depreciable block asset | never | none | deemed short term, §74 |
| Listed equity, equity MF, debt funds, SGB, non-equity ETFs | not here | [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md) | |

**Rule.** §2(101)(a) makes an asset short term when held "not more than twenty-four
months"; §2(101)(b) shortens that to 12 months only for listed securities, UTI
units, equity-oriented fund units and zero-coupon bonds. Count calendar months with the
same strict `sale > buy + n months` predicate as listed equity
([indian-capital-gains-tax section 5](../indian-capital-gains-tax/SKILL.md#5-the-12-month-boundary)); only `n` changes to 24.
A gift, will or inheritance keeps the previous owner's cost and holding period
(§73 Table Sl. 1, §2(101)(c)(B)(I)).

**Why.** A 12-month threshold applied to a flat or a plot flips 12.5% into slab
rate, or the reverse: a lot held 18 months is long term for a listed share and short
term for a flat.

**Detector.** One shared `LONG_TERM_DAYS` or `12` constant used for every asset kind, or
a classifier whose default branch returns a long-term equity result.

Rates apply to a transfer from 2026-04-01 (tax year 2026-27 onward, §197). Transfers
before that date sat under the 1961 Act (§112 as amended by the Finance (No. 2)
Act 2024); the sketch below refuses them. For a transfer on or after 23 Jul 2024, 1961 §112(1)(a)
gave a resident individual or HUF 12.5%, or for land or building acquired before that
date the lower of that and the 20%-with-indexation tax (Finance (No. 2) Act 2024 s.30). For a
resident individual or HUF, LTCG is reduced by the amount by which other income
falls short of the basic exemption limit (§197(2)); surcharge and cess are out of scope.

## 2. Rates

- **Long term:** 12.5% on the gain, §197(1)(b). The annual exemption of listed equity
  does not apply ([indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md)).
- **Short term:** added to total income and taxed at slab rates. The special
  short-term rate belongs to STT-paid equity only (same skill).
- **Option, §197(3):** for a **resident individual or HUF** transferring a
  long-term **land or building acquired before 2024-07-23**, the tax is
  `A - E`, where `E = max(A - B, 0)` is the "excess income-tax" the Act says "shall be
  ignored". So the tax is `min(A, B)`, the **lower** of
  - A: 12.5% on the gain with no indexation, and
  - B: 20% on the gain with indexed cost of acquisition and indexed cost of improvement.
- Gold, jewellery, unlisted shares, any post-cutoff acquisition, and any
  non-resident or company get 12.5% with no indexation and no choice.

**Why.** Indexation was removed for everything except this one grandfathered
case. A property bought long ago with a low index ratio is cheaper at 12.5%; one
with a high ratio is cheaper at 20% indexed. Hard-coding either side overtaxes one
of the two.

The test is `acquired < CUTOFF`: an asset acquired on 2024-07-23 itself gets no
option. For a gift or inheritance the Act does not say which date is tested;
flag it, do not guess.

```python
from datetime import date
from decimal import Decimal as D
from dateutil.relativedelta import relativedelta

LONG_TERM_MONTHS = {"land": 24, "building": 24, "gold": 24, "jewellery": 24, "unlisted_shares": 24}
CUTOFF = date(2024, 7, 23)
ACT_2025_START = date(2026, 4, 1)

def full_value(consideration, sdv):
    if sdv is None:
        raise ValueError("stamp duty value required for land or building")
    return consideration if sdv <= consideration * D("1.10") else sdv

def ltcg_tax(kind, acquired, sold, consideration, cost, expenses=D(0), improvements=(),
             sdv=None, cii_sale=None, cii_base=None, *, holder_kind, is_resident):
    months = LONG_TERM_MONTHS.get(kind)
    if months is None or acquired is None or sold is None or holder_kind is None or is_resident is None:
        raise ValueError("unknown asset kind, missing date or missing holder")
    if sold < ACT_2025_START:
        raise ValueError("transfer before 2026-04-01: 1961 Act, not restated here")
    if sold <= acquired + relativedelta(months=months):
        raise ValueError("short term: slab rate, not this function")
    land = kind in ("land", "building")
    fv = full_value(consideration, sdv) if land else consideration
    flat = max(fv - cost - sum(a for a, _ in improvements) - expenses, D(0)) * D("0.125")
    if not (land and is_resident and holder_kind in ("individual", "huf") and acquired < CUTOFF):
        return flat, "12.5% no indexation"
    if cii_sale is None or cii_base is None or any(c is None for _, c in improvements):
        raise ValueError("CII required for the indexed option")
    idx_cost = cost * D(cii_sale) / D(cii_base)
    idx_impr = sum(a * D(cii_sale) / D(c) for a, c in improvements)
    indexed = max(fv - idx_cost - idx_impr - expenses, D(0)) * D("0.20")
    excess = max(flat - indexed, D(0))
    return flat - excess, ("20% indexed" if excess > 0 else "12.5% no indexation")
```

**Worked example.** Land acquired before 2024-07-23, ₹50,00,000 cost, sold in tax year
2026-27 for ₹1,50,00,000 at an equal stamp duty value, no improvements or expenses, by a
resident individual. The index values are **made up for illustration and are not
notified figures**. With `cii_base=10`, `cii_sale=20` (ratio 2.0): indexed cost
₹1,00,00,000, indexed gain ₹50,00,000, tax at 20% = ₹10,00,000, against ₹12,50,000
flat, so the indexed option wins. With `cii_base=10`, `cii_sale=12` (ratio 1.2):
indexed cost ₹60,00,000, gain ₹90,00,000, tax ₹18,00,000, so the flat 12.5%
(₹12,50,000) wins.

**Detector.** A fixed 20% or a fixed 12.5% on all property; indexation applied
to gold or shares; the option offered to a non-resident or a company; the option decided
per-year-bought without comparing both taxes.

## 3. Indexation and cost

- **Cost Inflation Index** is notified by CBDT for each tax year (§72(8)(a)). Load it from a
  dated table that cites the notification; this skill carries no figures. The 2026-27
  index is specified under §72(8)(a) by S.O. 3889(E) of 15 Jul 2026. Earlier years stay
  under the 1961 notifications (S.O. 1790(E) of 5 Jun 2017 and its amendments), which
  §536(2)(j) of the 2025 Act keeps in force.
  The year is the **financial year** (1 April to 31 March), so a January
  purchase belongs to the year that began the previous April.
- **Indexed cost of acquisition** = cost x CII(transfer year) / CII(first year held by
  the assessee, or 2001-02 if later) (§72(8)(b)).
- **Indexed cost of improvement** = cost x CII(transfer year) / CII(year of the
  improvement) (§72(8)(c)). Each improvement carries its own year.
- **Transfer expenses** are expenditure wholly and exclusively for the transfer
  (§72(1)(a)): brokerage and legal fees. Never indexed.
- **Not deductible:** interest already claimed under §22(1)(b) or Chapter VIII
  (§72(3)(a)). An improvement does not include spend already deducted under house
  property, business or other sources (§90(2)).
- **Assets held before 2001-04-01:** cost of acquisition is the actual cost or the fair market
  value on 2001-04-01, at the taxpayer's option (§90(9)(a)). Improvements count only
  from 2001-04-01 (§90(1)(b)(i)). The indexation base year is then 2001-02.
- **Gift, will, inheritance:** the previous owner's cost, plus the previous owner's improvements
  (§73 Table Sl. 1, §90(1)(b)(ii)). If the previous owner held the asset before
  2001-04-01, the option is the previous owner's cost or the fair market value on
  2001-04-01 (§90(9)(b)). If the previous owner's cost cannot be found, the cost is the
  fair market value on the date the previous owner acquired it (§90(11)).
- **Land and buildings:** the 2001-04-01 fair market value cannot exceed the stamp duty
  value on that date, where available. This cap applies to both §90(9)(a) and
  §90(9)(b) (§90(10)).
- **Indexation base year for a gift or inheritance:** the statute keys it to the first
  year the asset was held "by the assessee". Whether a previous owner's years count is
  not settled here; flag it rather than pick one.
- **Unlisted shares:** if the price is below fair market value (prescribed
  manner), that value replaces it, except for quoted shares (§79 (old 50CA)).

**Detector.** `year = date.year` for a CII lookup. A CII table with no
2001-02 base entry. An index applied to the expense term. A pre-2001 asset with
no cost-or-FMV option; a pre-2001 inherited plot costed from the heir's receipt date.

## 4. Stamp duty value replaces the sale price

For land or building (§78 (old 50C)): if the consideration is **less than the stamp
duty value**, the stamp duty value is deemed to be the full value of consideration.

- **Tolerance:** if the stamp duty value is **not more than 110% of the consideration**, the
  actual consideration stands (§78(1)(b)). Above 110% the **whole** stamp duty
  value is used, not just the excess: it is a cliff, not a band.
- **Agreement date:** if the agreement date and the registration date differ and any part of
  the consideration was received on or before the agreement date through a banking or online mode, the stamp duty value
  on the agreement date may be used (§78(1)(a)).
- **Dispute:** if the taxpayer claims the stamp duty value exceeds the fair market value, the officer may
  refer it to a Valuation Officer (§78(2)). If that value is higher than the stamp duty
  value, the stamp duty value stands (§78(3)).

**Worked example.** Consideration ₹1,00,00,000. Stamp duty value ₹1,08,00,000 is
within 110% (₹1,10,00,000), so the gain uses ₹1,00,00,000. Stamp duty value
₹1,12,00,000 is above it, so the gain uses ₹1,12,00,000. Exactly
₹1,10,00,000 still uses ₹1,00,00,000.

The buyer's side (the same difference taxed as income, and the buyer's cost
under §73 Table Sl. 17) is not covered here.

**Detector.** `max(consideration, sdv)` with no tolerance; `sdv - consideration`
taxed as an excess above 110%; `>=` instead of `<=` at the 110% edge; a missing
stamp duty value silently treated as zero.

## 5. Depreciable block assets

An asset in a block on which depreciation was allowed (§74 (old 50)) has **no
holding period**. In a tax year, if sale proceeds of block assets exceed
transfer expenses + opening written down value + cost of assets added in the year,
the excess is a **short-term** gain (§74(2)). If the block ceases to exist, cost is
opening written down value plus additions, and the result is short term, a gain or a
loss (§74(3)). There is no per-asset long-term path, no 12.5% rate and no indexation.

**Detector.** A holding-period check or a CII lookup on a block asset; a
per-asset gain on a depreciable asset instead of a block computation.

## 6. Exemptions

Each applies only to a **long-term** gain; a short-term gain on the same asset gets
none of them. §82 and §86 are open to an **individual or HUF** only. §85 is open to
**any assessee**. Which one fits:

| Original asset sold | Section | Who | Reinvest in | Measured on | Cap |
|---|---|---|---|---|---|
| Residential house | §82 (54) | individual, HUF | one house in India (two, once, if gain ≤ ₹2 crore) | the gain | ₹10 crore |
| Any other long-term asset | §86 (54F) | individual, HUF | one house in India | net consideration | ₹10 crore |
| Land or building | §85 (54EC) | any assessee | specified bonds | the gain | ₹50 lakh |

Not covered: agricultural land (§83, old 54B), compulsory acquisition of
industrial land (§84, old 54D), industrial shifting (§87, §88; old 54G, 54GA).

### 6.1 §82 (old 54): residential house to residential house

- **Original asset:** long-term residential house (or land appurtenant) whose income is
  house property.
- **New house:** bought one year before or two years after the transfer, or built within
  three years after.
- **Exemption** = `min(gain, cost of new house)`; the new house's cost counts only up to
  ₹10 crore (§82(7)). A gain above the cost is taxed.
- **Lock-in:** if the new house is sold within three years, its cost for that sale is reduced by
  the exempted gain (§82(1)(i), (ii)).
- **Two-house option (§82(5), (6)):** only when the gain is **not more than ₹2 crore**, and the
  taxpayer can use it **once**: not in the same tax year again, nor in any other.

### 6.2 §86 (old 54F): other long-term asset to a residential house

- **Original asset:** any long-term asset that is not a residential house: land,
  gold, unlisted shares, and also listed shares.
- **Net consideration** = full value of consideration minus transfer expenses (§86(10)).
- **Exemption** = gain x cost of new house / net consideration, or the whole gain when the
  cost of the new house is at least the net consideration (§86(1)). The new house's cost
  counts up to ₹10 crore (§86(8)).
- **New house:** bought one year before or two years after, or built within three years after.
- **Refused up front** (§86(5)) when the taxpayer, on the transfer date, owns more than one
  residential house other than the new one, or buys another house within one year, or
  constructs another within three years, **and** the income from that other house
  (not the one house owned on the transfer date) is chargeable as house property.
  Owning exactly one other house is allowed.
- **Withdrawn later** (§86(6)): buying another house within two years, or constructing
  one within three years, whose income is house property, charges the exempted gain as
  long-term gain in the year of that purchase or construction.
- **Lock-in:** selling the new house within three years charges the exempted gain as long-term
  gain that year (§86(7)).

```python
CAP_86 = D(10) * D(10**7)

def s86_exempt(*, original_is_house, long_term, gain, net_consideration, cost_new,
               other_houses_owned, other_house_bought_within_1y, other_house_built_within_3y,
               other_house_bought_in_year_2, other_house_income_is_house_property):
    inputs = (original_is_house, long_term, gain, net_consideration, cost_new, other_houses_owned,
              other_house_bought_within_1y, other_house_built_within_3y,
              other_house_bought_in_year_2, other_house_income_is_house_property)
    if any(x is None for x in inputs):
        raise ValueError("every input must be known")
    if original_is_house:
        raise ValueError("residential house: use section 82")
    if not long_term or gain <= 0:
        return D(0), D(0)
    if net_consideration <= 0:
        raise ValueError("net consideration must be positive")
    refused = (other_houses_owned > 1 or other_house_bought_within_1y
               or other_house_built_within_3y) and other_house_income_is_house_property
    if refused:
        return D(0), D(0)
    cost = min(cost_new, CAP_86)
    granted = gain if cost >= net_consideration else gain * cost / net_consideration
    withdrawn = granted if other_house_bought_in_year_2 and other_house_income_is_house_property else D(0)
    return granted, withdrawn
```

The sketch returns `(granted, withdrawn)`. `granted` is the exemption claimed on the return;
`withdrawn` is the amount charged in the later year of the §86(6) event.

**Worked example.** Net consideration ₹2,00,00,000, long-term gain ₹1,00,00,000,
new house ₹80,00,000: exempt = 1,00,00,000 x 80,00,000 / 2,00,00,000 =
**₹40,00,000**, so ₹60,00,000 stays taxable. Exempting the full ₹80,00,000 would be
the old-54 reading of the new house's cost, and it is wrong here. A new house
of ₹2,00,00,000 or more exempts the whole gain.

**Detector.** Exemption = `min(gain, cost_new)` on a non-house asset; net
consideration replaced by sale price (transfer expenses ignored); no one-other-house
test; a later second-house purchase never reversing the exemption; a missing
house-property-income input defaulting to false.

### 6.3 §85 (old 54EC): specified bonds

- **Original asset:** long-term **land or building** only. Not gold, not shares.
- **Invest within six months after the transfer** in a long-term specified asset: a bond
  redeemable after five years, issued on or after 2018-04-01, by NHAI or REC, or
  another bond the Central Government notifies (§85(6)). Notifications made under 1961
  §54EC continue under §536(2)(j); two found are HUDCO bonds issued on or after
  2025-04-01 (S.O. 1644(E)) and IREDA bonds issued on or after 2025-07-09 (S.O. 3060(E)).
  The full list was not read, so check the current notifications.
- **Limit ₹50 lakh**, from the gains of one or more original assets, in any tax year,
  or across the transfer year and the next one together (§85(2)).
- **Lock-in five years.** Transfer, conversion to money, or a loan or advance on the bond's
  security within five years makes the exempted gain long-term gain that year
  (§85(3), (4)).
- The same investment cannot also be claimed under the §123 deduction (old 80C) (§85(5)).
- **No deposit route.** Unlike §82 and §86, the six months is a hard stop; the due date of the
  return does not extend it, except after compulsory acquisition when the compensation
  arrives later (§89).

**Worked example.** Land transferred 2026-08-12, gain ₹80,00,000. ₹20,00,000 in REC
bonds on 2026-12-15 is within six months; ₹60,00,000 in NHAI bonds on 2027-03-01 is
outside it. Only ₹20,00,000 is exempt; ₹60,00,000 is taxable. Even with a timely
₹60,00,000, the exemption stops at ₹50,00,000.

**Detector.** A 54EC cap of `gain` with no ₹50 lakh limit; a deadline set to the
filing due date; the exemption offered on a gain from gold or shares.

### 6.4 The Capital Gains Account deposit

For §82, §86, §83 and §84, gain (or net consideration under §86) not used for the
new asset before you file the return must be deposited in a specified bank or
institution under the scheme the Central Government notifies. The deposit must be made **before the
return is filed and not later than the due date in §263(1)(c)**; proof goes with the return
(§82(2), §86(2)). The §263(1)(c) due dates (table substituted by Finance Act 2026 s.66(a))
are owned by [itr-filing-schedules](../itr-filing-schedules/SKILL.md). Filing late under
§263(4) does not move it. The deposited amount counts as the cost of the new asset
(§82(3), §86(3)).

For the deposit side the ₹10 crore ceiling applies too: gain above ₹10 crore is not
counted for the deposit under §82(8), and net consideration above ₹10 crore under §86(9).

If it is still unspent when the period ends, the unspent amount is charged in the tax
year in which that period expires, and can be withdrawn under the scheme. The period is
**three years** from the transfer for §82(4), §84(4) and §86(4), and **two years** for
§83(4). §86(4) charges only the part of the exemption that the unspent amount
supported. The scheme is the Capital Gains Accounts Scheme, 1988 (G.S.R. 724(E)) as amended
by the Second Amendment Scheme 2025 (S.O. 5293(E), 19 Nov 2025: electronic deposits and
statements, electronic closure from 2027-04-01), carried over by §536(2)(j). Its forms and
rules are not restated here.

**Detector.** Deposit date compared with the transfer date instead of the filing date;
the deposit accepted after the return is filed; a deposit counted for §85; one
three-year constant for §83.

## 7. Section map: Income-tax Act 2025 and the 1961 Act

Rows for §54 / §54EC / §54F, §111A / §112 / §112A and §49 are in
[itr-filing-schedules section-concordance](../itr-filing-schedules/references/section-concordance.md). Rows
that file lacks:

| 2025 Act | 1961 Act | Topic |
|---|---|---|
| §2(101) | §2(42A) | short-term and long-term asset, 24 or 12 months |
| §72 | §48 | computation, indexation |
| §74 | §50 | depreciable block |
| §76 | §50AA | specified mutual fund, market-linked and unlisted bonds |
| §78 | §50C | stamp duty value |
| §79 | §50CA | unlisted share below fair market value |
| §83, §84 | §54B, §54D | agricultural land, compulsory acquisition (not covered) |
| §89 | §54H | extension of time after compulsory acquisition |
| §90 | §55 | cost of acquisition and improvement; §90(9) is the 2001 option |
| §91 | §55A | reference to a Valuation Officer |
| §263 | §139 | return of income and due date |

The 1961 numbers still appear in ITR schedules and JSON field names; use them
there ([itr-filing-schedules](../itr-filing-schedules/SKILL.md)).

Sources: the Income-tax Act 2025 Gazette text (Act No. 30 of 2025) and the enacted
Finance Act 2026 (Act No. 4 of 2026). The Act amends §2, §69, §70 and other sections but
not §2(101), §72 to §91 or §196 to §198.

## Verifying an implementation

- **Boundary-test the 24 months:** sold on the anniversary (short term) and the day
  after (long term), including a 29 February window.
- **Test both sides of the option:** one property where indexed 20% is lower and one where
  flat 12.5% is lower, and assert the lower tax is returned each time.
- **Test the cutoff:** a property acquired 2024-07-22 gets the option; one acquired
  2024-07-23 does not. Test a non-resident, a company and a gold sale: no option.
- **Test the scope guard:** a transfer before 2026-04-01 must raise.
- **Test the 110% edge:** consideration ₹1,00,00,000 with stamp duty value
  ₹1,10,00,000 uses ₹1,00,00,000; ₹1,10,00,001 uses the stamp duty value.
- **Test §86 with an asymmetric case:** net consideration twice the new house's cost;
  assert half the gain is exempt, then a case with the new house above net
  consideration (whole gain).
- **Test the exemption limits:** a ₹60,00,000 §85 investment exempts at most
  ₹50,00,000; a six-month-plus-one-day investment exempts nothing; a second use of the
  two-house option is refused.
- **Test fail-closed paths:** unknown asset kind, `None` dates, a `None` holder or
  residence flag, a `None` house-property input and a missing stamp duty value must raise,
  never return zero tax.

## Scope

Resident-individual and HUF capital gains on the assets above. Informational only;
**not tax advice**. Surcharge, cess, the buyer's side of a property sale, TDS on
property and slump sales are out of scope. Cost Inflation Index figures must come
from the CBDT notification for each tax year.

Not here: listed equity and equity-fund rates, set-off, carry-forward, debt funds,
SGBs and non-equity ETFs ([indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md));
schedule and JSON mechanics ([itr-filing-schedules](../itr-filing-schedules/SKILL.md));
foreign shares, RSUs and LRS ([foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md));
buybacks, bonus, demerger cost splits ([corporate-action-taxation](../corporate-action-taxation/SKILL.md)).
