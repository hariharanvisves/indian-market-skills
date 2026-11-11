---
name: corporate-action-taxation
description: Indian income-tax treatment of corporate actions for resident individuals holding listed shares — buybacks under three date-keyed regimes (§115QA company tax before 1 Oct 2024; deemed dividend at slab plus a capital loss to 31 Mar 2026; capital gains with a promoter additional tax from 1 Apr 2026), dividends (slab rate, tax year of declaration, ₹10,000 TDS threshold, no interest deduction from tax year 2026-27), bonus shares (nil cost, holding from allotment), splits and consolidations, rights entitlements, demergers (book-value cost split), mergers, dividend and bonus stripping, and 31-Jan-2018 grandfathering for bonus and split lots. Use when building lot or cost-basis logic for corporate actions, taxing a buyback, bonus, split, demerger, merger or rights issue, reviewing code that reuses price-adjustment factors as cost basis, or porting US stock-dividend or spin-off basis rules. Gives Income-tax Act 2025 sections with 1961 equivalents.
license: MIT
compatibility: Verified 2026-11-11 against the gazetted Income-tax Act 2025, the Finance Act 2026 (No. 4 of 2026) and the Union Budget memoranda for 2019, 2020, 2022, 2024, 2025 and 2026, for tax year 2026-27; re-verify before use, as rules change with each Finance Act.
metadata:
  author: hariharanvisves
  version: "1.0"
  verified: "2026-11-11"
  jurisdiction: India
---

# Corporate-Action Taxation

A corporate action changes two different things: the **price series**, which
return calculations need, and the **tax lots**, which cost basis and holding
period need. Code that derives one from the other is wrong, and the direction of
the error depends on the action. Price mechanics live in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).
Rates, the 12-month boundary, set-off and grandfathering arithmetic live in
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md). This skill
says which lot each action creates, at what cost, from what date, and how a
buyback or a dividend is taxed.

**Sections.** 2025-Act numbers come first, with 1961-Act numbers in brackets.
FY 2025-26 and earlier returns follow the 1961 Act, and ITR JSON fields still
carry 1961 numbers (the AY 2026-27 ITR-2 schema has `Dividend22f`,
`CapitalLossBuyBackShares` and `LossSec94of7Or94of8`). The 2025 text below is
checked against the gazetted Act (Act 30 of 2025). The bracketed numbers are
mapped by content, so check one against the 1961 text before you cite it in a
filing. Budget memoranda cited as "memo YYYY" are at
`https://www.indiabudget.gov.in/budget<YYYY-YY>/doc/memo.pdf`. The 2026 memo is
at [indiabudget.gov.in/doc/memo.pdf](https://www.indiabudget.gov.in/doc/memo.pdf).

## 1. Price adjustment is not cost-basis adjustment

| Action | Price series (returns) | Tax lots |
|---|---|---|
| Split / consolidation | scale pre-ex prices by the ratio | same lot: quantity rescaled, total cost and date unchanged |
| Bonus | scale pre-ex prices by `b/(a+b)` | original lot untouched; **new lot**, cost nil, dated at allotment |
| Rights | not adjusted by default | new lot at the subscription price, dated at allotment; original cost unchanged |
| Demerger | no constant factor | new lot in the resulting company with an apportioned cost and the parent's date; parent cost reduced by that amount |
| Merger | continuity across the symbol change | new-company lot with the same total cost and date |
| Dividend | optional total-return reinvestment | no change to any lot |
| Buyback | none | tendered shares leave the lot; taxed per §2 below |

**Rule.** Build cost basis from lot events. Never build it from a price factor.

**Why.** Scaling a lot by the bonus factor spreads the original cost over the
bonus shares and gives them the original purchase date. US code makes the same
mistake on purpose, because US law spreads basis across a stock dividend and
carries the holding period over. Indian law does neither.

**Worked example.** You buy 100 shares at ₹900 on 2024-05-02, so the cost is
₹90,000. A 1:1 bonus is allotted on 2025-09-15. On 2026-06-01 you sell 150 shares
at ₹520. FIFO applies to demat holdings under §67(7)(c) [§45(2A)], so the sale
takes the 100 originals first and then 50 bonus shares:

- Originals: proceeds ₹52,000, cost ₹90,000, so **LTCL ₹38,000** (held more than 12 months).
- Bonus: proceeds ₹26,000, cost nil, so **STCG ₹26,000** (held 8.5 months from allotment).
- The LTCL cannot offset the STCG, so ₹26,000 stays taxable at the STCG rate.
- Average-cost code gets 150 × ₹450 = ₹67,500 of cost, all dated 2024-05-02. It
  reports an LTCG of ₹10,500. That is the wrong head, the wrong amount and the
  wrong sign.

**Detector.** Cost-basis code that imports the adjustment factor. Look for
`cost *= factor` on a bonus, or a bonus lot with `buy_date = parent.buy_date`.

## 2. Buybacks: three regimes, keyed on the buyback date

| Buyback date | Shareholder's treatment | Source |
|---|---|---|
| before 1 Oct 2024 | Exempt [§10(34A)]. The company paid additional tax at 20% of distributed income [§115QA]. Listed companies were covered only from 5 Jul 2019. | memo 2019; memo 2024 |
| 1 Oct 2024 – 31 Mar 2026 | **Whole consideration** is a deemed dividend [§2(22)(f)], taxed at slab with no expense deduction. The cost of the tendered shares becomes a capital loss, because consideration is deemed nil [§46A]. That loss is STCL or LTCL by holding period. | memo 2024 |
| from 1 Apr 2026 (tax year 2026-27) | Capital gains: consideration minus cost (§69(1)). §2(40)(f) is omitted, so there is no dividend. | Finance Act 2026 §§35, 42; memo 2026 |

**Worked example (memo 2024).** You buy 100 shares at ₹40, so the cost is ₹4,000.
In 2024, 20 shares are bought back at ₹60. Under the 2024–26 regime:

- Deemed dividend: ₹1,200, taxed at slab.
- Capital loss: ₹800.
- You later sell 50 shares at ₹70, a gain of ₹1,500. After the loss, ₹700 is chargeable.

The same buyback on or after 1 Apr 2026 gives a capital gain of ₹400, classified
by holding period.

**Promoter additional tax** (§69(2)–(3), as substituted by Finance Act 2026 §42).
It applies only to a buyback under Companies Act §68 where the holder is a
promoter. For a listed company, "promoter" means a promoter under reg. 2(k) of the
SEBI Buy-Back Regulations 2018. The extra tax sits on top of the normal rate:

| Promoter | on §196 STCG | on §197/§198 LTCG |
|---|---|---|
| Not a domestic company (includes individuals) | +10% | +17.5% |
| Domestic company | +2% | +9.5% |

That additional tax carries a 12% surcharge (Finance Act 2026 §2(6)). The memo
puts the result at an effective 30% for promoters and 22% for promoter companies.

**Traps.**
- In 2024–26 the dividend is the **gross** consideration, not consideration minus
  cost. The two figures fall under different heads, so never net them. The loss
  offsets only capital gains, and it carries forward under the normal rules after
  the regime ends.
- For a grandfathered lot in 2024–26, the loss uses **actual cost**:
  `max(cost, min(fmv, 0)) = cost`. Code using `max(cost, fmv)` inflates the loss.
- Choose the regime from the buyback date. Do not use the sale date of the
  remaining shares, and do not use the FY of the return. Flag a tender that
  straddles a regime boundary.

## 3. Dividends

- **Slab rate.** A dividend is taxed at slab under "Income from other sources".
  This has applied since dividend distribution tax ended on 1 Apr 2020 (memo 2020).
  It is not §196/§198 income and gets no ₹1.25 lakh exemption. India has no
  "qualified dividend" rate.
- **Year.** A final dividend is income of the tax year in which it is
  **declared**. An interim dividend is income of the year in which it is
  unconditionally made available (§7(2) [§8]). Do not bucket on the record date
  or the credit date.
- **Deductions.**
  - Up to FY 2025-26, interest was the only deduction, capped at 20% of gross dividend [§57] (memo 2020).
  - From tax year 2026-27, **nothing** is deductible (§93(2) as substituted by Finance Act 2026 §44).
  - The §80M inter-corporate deduction is for companies, never for individuals.
- **TDS.** The rate is 10% (§393(1) Table Sl. 7 [§194]). An individual paid other
  than in cash has no TDS while that company's dividends for the tax year total
  at most **₹10,000** (§393(4) Table Sl. 10(f)). That threshold was ₹5,000 before
  1 Apr 2025 (memo 2025).
  - The threshold is per paying company per year. It is not per payment and not across companies.
  - TDS is a credit. Report the gross dividend, not the net credit.
- **Cost.** A dividend never reduces a lot's cost. Indian law has no
  return-of-capital basis reduction for a company dividend.

## 4. Bonus shares

- Cost is **nil** (§90(6)(d) [§55(2)(aa)]). The original lot keeps the amount
  actually paid (§90(6)(a)).
- The holding period runs from the **date of allotment** (§2(101)(c)(C)(IV)
  [§2(42A) Expl. 1]). That is not the ex-date, the record date or the original
  buy date. Store the allotment date. If you only have the record date, flag the
  lot, because a sale near the 12-month anniversary can flip STCG and LTCG.
- **Grandfathering.** It covers shares "acquired before 1 Feb 2018" (§90(7)
  [§55(2)(ac)]), and a bonus share is acquired on allotment:
  - Bonus allotted **before** 1 Feb 2018: stepped cost = `min(fmv, sale)`, because actual cost is 0.
  - Bonus allotted **on or after** 1 Feb 2018: nil cost and no step-up. The whole sale price is gain.
- The FMV is the **unadjusted** highest price on 31 Jan 2018 (§90(8)(b)(i)).
  Vendor histories that are back-adjusted for later bonuses or splits understate it.

## 5. Splits and consolidations

- **Cost.** It is derived from the shares the new shares came from (§90(9)(d)
  [§55(2)(b)(v)]). Total cost is unchanged and per-share cost scales by the ratio.
- **Holding period.** §2(101)(c) has no explicit carry-over entry for splits, and
  neither has the 1961 list. The original date is the reading that follows from
  the derived cost, but the statute does not state it. Carry the original date,
  and mark it as derived rather than restarting it at the split.
- **Pre-2018 lot split after 31 Jan 2018.** The quoted FMV is for the pre-split
  share. Divide it by the split ratio so the aggregate FMV is preserved. This is an
  interpretation: no CBDT clarification was found.
- **Compound actions.** A bonus and a split on one ex-date are two lot events.
  Apply each as the company's announcement states, not as one factor.

## 6. Rights issues and rights entitlements (RE)

Sources: §90(5)–(6) [§55(2)(aa)]; holding period §2(101)(c)(C)(II)–(III).

| Event | Cost | Holding period from |
|---|---|---|
| Subscribe on your own RE | amount paid to the company | allotment |
| Renounce or sell the RE | nil | date of offer, up to renunciation |
| Buy an RE, then subscribe | price paid for the RE plus amount paid to the company | allotment |
| Original shares | unchanged | unchanged |

- **RE sale rate.** An RE sale is almost always short term. An RE is not an
  equity share, so §196 [§111A] does not on its face apply. Whether it gets 20% or
  slab is unverified: no CBDT clarification was found. Route it to slab and flag
  it, following the fail-closed rule in indian-capital-gains-tax.
- **Detector.** Code that reduces the original lot's cost on a rights issue. That
  is demerger logic applied to the wrong action.

## 7. Demergers

- **Not a transfer.** It is not a transfer for the shareholder (§70(1)(k)
  [§47(vid)]). The share distribution is excluded from "dividend" (§2(40) long
  line (iv) [§2(22)(v)]).
- **Cost.** Resulting-company cost = `A × B / C` (§73 Table Sl. 14–15 and §73(2)(c) [§49(2C)–(2D)]):
  - A is the cost of the demerged-company shares.
  - B is the net book value of the assets transferred.
  - C is the net worth (paid-up capital plus general reserves) immediately before the demerger.
  - The parent's cost falls by the same amount. Take B/C from the company's
    published cost-apportionment figure, **never** from a price ratio.
- **Holding period.** It includes the period you held the demerged-company shares
  (§2(101)(c)(B)(III)). Apply the ratio lot by lot, and each lot keeps its own date.
- **Worked example.** You hold 10 parent shares bought 2020-07-01 for ₹10,000.
  There is a 1:1 demerger, and the published ratio is 30%. Resulting company: 10
  shares, cost ₹3,000, dated 2020-07-01. Parent: cost ₹7,000. A price split
  (parent ex-price ₹150, resulting company lists at ₹60, so 28.6%) gives ₹2,857,
  which is wrong.
- **Pre-2018 lots.** Grandfathering for resulting-company shares involves
  §90(8)(b)(iv). That is out of scope, so flag such lots.

## 8. Mergers and amalgamations

- **Not a transfer.** It is not a transfer when the consideration is shares of an
  amalgamated **Indian** company (§70(1)(f) [§47(vii)]).
- **Cost and date.** Cost is the cost of the old shares (§73 Table Sl. 2
  [§49(2)]). The holding period includes the old shares' period
  (§2(101)(c)(B)(II)).
- **Worked example.** You hold 100 shares of A, cost ₹50,000, bought 2019-03-01.
  The swap ratio is 3 B for 2 A, so you get 150 B at a total cost of ₹50,000
  (₹333.33 each), still dated 2019-03-01.
- **Cash for fractions.** This cash is not share consideration. Treat the fraction
  as sold for that cash, with apportioned cost. This is common practice: no CBDT
  clarification was found.
- **Foreign amalgamated company.** The exemption fails, and the swap is a taxable transfer.
- **Detector.** A new lot dated at the merger's effective date, or costed at the
  market value of the new shares.

## 9. Dividend and bonus stripping (§175 [§94])

- **Dividend stripping** (§175(8) [§94(7)]) needs three things:
  - you buy within 3 months before the record date;
  - you sell within 3 months after it (9 months for units);
  - the dividend is **exempt**.

  When all three hold, the loss is ignored up to the dividend. A resident
  individual's dividend is taxable, so for that holder this does not bite.
  indian-capital-gains-tax states the same condition.
- **Bonus stripping** (§175(9)–(10) [§94(8)]) has no exemption condition. It has
  applied to shares since AY 2023-24 (memo 2022). It needs three things:
  - you buy within 3 months before the record date;
  - you are allotted a bonus;
  - you sell any of the purchased shares within 9 months after the record date while still holding bonus shares.

  When all three hold, the loss is ignored, and that ignored loss becomes the cost
  of the bonus shares still held.
- **Worked example.** You buy 100 shares at ₹1,000 on 2026-06-01. A 1:1 bonus has
  record date 2026-07-15. You sell the 100 originals at ₹520 on 2026-09-01. The
  ₹48,000 loss is ignored. The 100 bonus shares cost ₹48,000 (₹480 each) instead
  of nil, and they stay dated at allotment.
- **Detector.** A wash-sale-style window, a disallowance with no deemed cost, or
  §94(7) applied to a taxable dividend.

## Verifying an implementation

- **Run the §1 bonus fixture.** Assert LTCL ₹38,000, STCG ₹26,000 and a bonus lot
  dated at allotment. Add a split control: the same lot, the same date and the
  same total cost. The pair fails if bonus and split share code.
- **Test the buyback dates** 2024-09-30, 2024-10-01, 2026-03-31 and 2026-04-01.
  Assert three distinct treatments.
- **Check the 2024–26 grandfathered buyback loss.** Assert it equals actual cost
  for a lot whose 31-Jan-2018 FMV exceeds that cost.
- **Check demerger totals.** Parent cost plus resulting-company cost equals the
  original cost to the rupee, and both lots keep the parent's date.
- **Test bonus stripping across the window.** Buy just inside and just outside
  3 calendar months before the record date. Count months as indian-capital-gains-tax does.
- **Test the dividend TDS threshold.** Two companies paying ₹6,000 each means no
  TDS from either. One company paying ₹6,000 twice means TDS applies.
- **Test a final dividend near year end.** Declare it 2026-03-28 and pay it
  2026-04-10. Assert it is FY 2025-26 income.

## Scope

Resident individuals holding NSE/BSE-listed shares as capital assets, not
stock-in-trade. Informational only; **not tax advice**. Surcharge on normal
rates and cess are out of scope here.

Not here:
- price adjustment ([nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md));
- STCG/LTCG rates and set-off ([indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md));
- mutual-fund IDCW and unit matching ([mf-scheme-matching](../mf-scheme-matching/SKILL.md));
- ITR schedule placement ([itr-filing-schedules](../itr-filing-schedules/SKILL.md));
- derivative contract adjustments ([fno-tax-and-charges](../fno-tax-and-charges/SKILL.md)).
