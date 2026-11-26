---
name: itr-filing-schedules
description: Choosing the Indian ITR form (ITR-1/2/3/4) and getting its schedules right — Schedule CG, 112A, OS, VI-A, FSI, TR, FA, CYLA/BFLA/CFL, AMT/AMTC, AL, TI/TTI — with cross-schedule reconciliation identities, foreign tax credit (Rule 128/Rule 76, Form 67/Form 44, Rule 115 FX rate), TDS de-duplication across 26AS and AIS, advance tax and §234C, §288A/§288B rounding, due dates, and ITR JSON emit pitfalls. Use when building or reviewing ITR preparation, form-suggestion or JSON-export code, deciding between ITR-1, ITR-2 and ITR-3, rounding tax payable, merging Form 26AS and AIS, reconciling AIS/26AS/portal figures, or when one loss or credit appears in several schedules and must agree, even if the user never says "schedule".
license: MIT
compatibility: Applies to resident-individual returns on the Indian e-filing portal. Form, schedule and rule facts verified 2026-11-11 for AY 2026-27 and tax year 2026-27. Not tax advice; rates and thresholds are deliberately left to the capital-gains skill and the statute.
metadata:
  author: hariharanvisves
  version: "1.2"
  verified: "2026-11-11"
  jurisdiction: India
---

# ITR Filing Schedules

Defect classes in ITR preparation code that produce a plausible return and are
found only by checking identities between schedules. Rates, thresholds,
holding periods and set-off rules live in [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md); charges in
[indian-equity-charges](../indian-equity-charges/SKILL.md). This skill covers
**structure**: which form, which schedule, what must agree. Each section gives
the rule, why it matters, and a **Detector** to run against code.

## Core rules

1. **Derive the form from facts**, not last year's form: any STCG, foreign asset, carried loss or business income rules out ITR-1 ([section 1](#1-pick-the-form-from-the-facts-not-from-the-users-last-year)).
2. **Every figure has one owning schedule**; CYLA, BFLA, CFL, TI and TTI read CG and OS outputs ([section 2](#2-schedule-map)).
3. **Assert cross-schedule identities** on the final emitted document, not the builder ([section 3](#3-cross-schedule-reconciliation-identities)).
4. **Set-off order is CYLA, then BFLA, then CFL**; a long-term loss never nets against short-term gain ([section 4](#4-capital-gains-ordering-inside-the-schedules)).
5. **FX rate is the SBI TT buying rate** at the last day of the month before the event; foreign tax credit is the lower of foreign tax and Indian tax. **Form 67 becomes Form 44** from tax year 2026-27 ([section 5](#5-foreign-income-and-tax-credit)).
6. **§288A/§288B rounding:** drop the paise first, then round to the nearest ₹10, only at total income and final tax ([section 6](#6-rounding-288a-and-288b-are-the-same-rule)).
7. **One TDS credit per (section, date, amount)**; a TAN-less 26AS stub is not a second credit ([section 7](#7-tds-de-duplication-across-26as-ais-and-the-portal)).
8. **§234C:** a shortfall from income arising after an instalment date is excused if the tax is paid in the remaining instalments ([section 8](#8-advance-tax-and-the-instalment-schedule)).
9. **Convert units once, at the emitter**; a missing value is a validation error, never `0` ([section 9](#9-json-emit-boundary-units-and-schema-per-year)).
10. **JSON keys keep 1961 literals** whatever the year; translate section numbers only in labels ([law version](#law-version-caveat-read-first)).

## Law-version caveat: read first

The Income-tax Act 2025 is in force from 1 April 2026 with renumbered sections;
the CBDT ITR JSON schema **keeps the 1961 literals in field names and
enumerations** (regime code, relief-section codes, special-rate section codes)
regardless of year. Translate section numbers only in human-facing labels, never
in JSON keys. Never translate by memory; verify against the CBDT concordance
utility and the schema for the year. The full 1961-to-2025 table (§111A to §196,
§288A/§288B to §516, Rule 128 to Rule 76, and the rest) is in
[references/section-concordance.md](references/section-concordance.md); read it
when labelling a section.

Years: **AY 2026-27** is the return for FY 2025-26 (1961 Act); **tax year
2026-27** is FY 2026-27 (2025 Act). A financial year (FY) runs 1 April–31 March.
Rule 76 and Form 44 apply from tax year 2026-27; returns for AY 2026-27 and
earlier still use Rule 128 and Form 67.

## 1. Pick the form from the facts, not from the user's last year

**Rule.** Derive the form from income and asset facts, and surface the blocker
that forced it.

| Fact | Consequence |
|---|---|
| Business or profession income, including F&O (non-speculative) or intraday (speculative) business income | ITR-3 (or ITR-4 only if the presumptive scheme applies and nothing else blocks it) |
| Any STCG, any capital gain other than §112A, or §112A LTCG above ₹1,25,000 | Not ITR-1 or ITR-4; ITR-2 at minimum |
| §112A LTCG of ₹1,25,000 or less, and no other capital gain | ITR-1/ITR-4 still allowed (a form limit, kept separate from the exemption constant) |
| Foreign asset, foreign income, or signing authority abroad | ITR-2 or ITR-3 (Schedule FA/FSI/TR); never ITR-1 |
| Brought-forward loss, or a loss to carry forward | Not ITR-1 or ITR-4 |
| Director in a company, or unlisted equity held at any time in the year | Not ITR-1 or ITR-4 |
| Salary, up to two house properties, interest only, within ITR-1 limits | ITR-1 |

ITR-1/ITR-4 total-income ceiling is 50 lakh, excluding §112A LTCG within the
form's ₹1,25,000 limit (AY 2026-27 portal instructions); eligibility should be evaluated at **record**
level (an eligible-looking filer holding one foreign lot or one carried loss is
not eligible). Surface prerequisites (Form 67, or Form 44 from tax year 2026-27, for an FTC claim) too. F&O and
intraday income, ITR-3 and tax audit: [fno-tax-and-charges](../fno-tax-and-charges/SKILL.md).

**Why.** A form lacking a schedule drops data silently or gets the return treated
as defective.

**Detector.** List every input the form-suggestion function branches on; each
row above must be one. Fixtures with only (a) one foreign holding, (b) one carried
loss, (c) F&O turnover, (d) a ₹1 STCG must each reject ITR-1 and name the
reason; (e) only a small §112A LTCG must not.

## 2. Schedule map

**Rule.** Every figure has one owning schedule; others read it.

- CG: gains by asset class, cost, sale, exemptions. Feeds CYLA, BFLA, TI.
- 112A: lot- or total-level detail of the specially taxed listed-equity gain. Feeds CG.
- OS: interest, dividend, winnings. Feeds TI.
- VI-A: deductions, an input to total income.
- FSI / TR: income outside India and tax paid there / relief claimed. TR feeds tax payable.
- FA: foreign assets, disclosure only.
- CYLA / BFLA / CFL: current-year set-off / brought-forward set-off / carry-forward.
- AMT / AMTC: alternate minimum tax and its credit.
- AL: assets and liabilities, required when total income exceeds 1 crore
  (AY 2026-27 ITR-2 utility; raised from 50 lakh).
- TI / TTI: total income / total tax and refund.

Schedule CG and the portal's capital-gains tables must be built from the **same
netted records** as the tax engine (after exemptions, deemed gains, transfer
expenses and substituted cost); two code paths drift. Chapter VI-A (Part C)
deduction keys must reach the engine with their caps. A pass-through map that
silently drops an unknown key loses the deduction, so reject unknown keys instead.

**Why.** A figure computed in two schedules by two code paths drifts, and the
portal either rejects the mismatch or accepts it.

**Detector.** For each emitted field, grep where it is assigned; more than one
site outside the owner is a defect. Confirm `cyla|bfla|cfl|ti|tti` functions take
CG/OS outputs as arguments rather than re-reading raw transactions.

## 3. Cross-schedule reconciliation identities

**Rule.** The same loss or credit appears in 2–3 schedules; assert they agree,
at the emit boundary, in the final document.

Identities to assert (all on emitted values, in one unit):

1. Sum of CG line gains by bucket == the bucket totals CYLA starts from.
2. CYLA + BFLA set-off + CFL carry-forward == loss available (none created or
   destroyed); CFL == loss unabsorbed after CYLA and BFLA.
3. Total of §112A-schedule rows == the corresponding CG line.
4. TR claimed credit == sum over FSI country rows of the allowed credit; never
   more than Indian tax on that income.
5. TI == sum of heads after set-off, less Chapter VI-A deductions.
6. TTI tax payable == tax on TI + surcharge + cess − relief/credit − TDS − TCS
   − advance tax − self-assessment tax, with refund = −(that) when negative.
7. TDS total in TTI == sum of the TDS credit rows after de-duplication (section 7).
8. Portal CG quarterly-accrual table row totals equal the matching BFLA items,
   including §112A gains covered by the exemption.
9. Foreign dividend appears in OS and the **same rupee amount** in FSI.

Items 8 and 9 and the measured double-count of brought-forward losses are in
[references/portal-notes.md](references/portal-notes.md); read it when matching
the portal's quarterly table. Add the identity test in the same change as any new
schedule.

```python
def reconcile(doc):
    bad = []
    cg = doc["CG"]["loss_available"]
    if doc["CYLA"]["setoff"] + doc["BFLA"]["setoff"] + doc["CFL"]["carry"] != cg:
        bad.append("loss created or destroyed across CYLA/BFLA/CFL")
    fsi = sum(r["allowed_credit"] for r in doc["FSI"]["countries"])
    if doc["TR"]["claimed"] != fsi:
        bad.append("TR credit != sum of FSI allowed credit")
    return bad
```

**Why.** Each schedule can be individually correct and the document wrong. A
loss counted in both CYLA and CFL, or a credit in both FSI and TR, only
shows when you add across.

**Detector.** Run `reconcile(doc)` over every golden fixture and over the final
emitted JSON. Prove it fires by perturbing one schedule by one unit.

## 4. Capital-gains ordering inside the schedules

**Rule.** The set-off order, the long-/short-term asymmetry and the annual §112A
exemption are owned by [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md) (its "Correct computation order"). In
schedule terms: CYLA first, then BFLA, then CFL. Never net a long-term loss
against short-term gain.

**Why.** The wrong order lowers tax in the draft and is reversed on assessment.

Defects seen in practice when the schedule writer needs the classifier, the
rebate or the surcharge cap (one shared residency predicate, one implementation
of each classification rule, both realised and unrealised holding-period paths
changed together): [references/classification-defects.md](references/classification-defects.md).
Read it before wiring those into Schedule CG.

**Detector.** Grep set-off code for any path where an `ltcl`/long-term loss
variable is subtracted from a short-term bucket. Fixture: STCG = 100, LTCL = 50,
LTCG = 0; expect STCG unchanged and 50 carried forward.

## 5. Foreign income and tax credit

**Rule.**

- Capital-gain conversion (**Rule 115**; Rule 206 of the 2026 Rules) uses the SBI
  telegraphic-transfer buying rate on the last day of the month **preceding** the
  month of transfer; tax-credit conversion (**Rule 128(5)**; Rule 76(7)) uses the
  same rate on the last day of the month preceding the month the foreign **tax was
  paid or deducted**. Keep the rate table per financial year with a source; a stale
  table silently mis-converts.
- **Form 67** (Form 44 from tax year 2026-27) must be filed within 12 months
  after the end of the financial year of the income, with the return itself filed
  under §139(1) or §139(4); for an updated return, by the date that return is filed.
  Filing it before the return is safe practice, not a legal precondition; never
  filing it is the usual failure.
- A US broker's **Form 1042-S** and similar withholding statements are the
  evidence for the tax paid; match the withheld amount, not the gross.
- In FSI, relief = min(tax paid abroad, Indian tax on that income), computed
  separately for each source of income per country. Leaving the
  Indian-tax column at 0 **silently zeroes the credit with no validation error**;
  compute it as the marginal-rate tax on the foreign income.
- Part B-TTI's foreign-asset question defaults to No even with Schedule FA filled;
  a false No is a black-money-law exposure. Warn loudly.
- What goes into Schedule FA, RSU and US-stock cost, LRS/TCS:
  [foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md).

**Why.** A different rate moves income and credit; a missing Form 67/44 voids the claim.

**Detector.** Grep the converter for how it picks a rate (a hardcoded
`usdInr`, today's rate, or the transaction date's rate are three different
defects). Check that the emit path warns on a TR claim with no Form 67/44
acknowledgement recorded and tracks its due date. Verify the cap with a fixture
where foreign tax exceeds Indian tax.

## 6. Rounding: §288A and §288B are the same rule

**Rule.** §288A (total income) and §288B (amount payable, refund) have the same text, and
the 2025 Act merges them into §516: **ignore the paise** (truncate toward zero to
the rupee), then round to the nearest ten, a last digit of 5 or more going up.
Neither rounds 50 paise up first: ₹1,234.60 is ₹1,230, while a round-to-rupee
first step gives ₹1,240. One shared helper is correct; a tax-side helper that
rounds the paise is non-statutory. Apply statutory rounding at
total income and final tax **only**, never in intermediate schedules; marginal
relief, surcharge and rebate must use the same rounded base as the tax they
adjust (a sub-ten drift appears at the rebate cliff otherwise).

```python
from decimal import Decimal, ROUND_DOWN

def round_288(amount):
    rupees = int(Decimal(str(amount)).to_integral_value(ROUND_DOWN))  # paise dropped toward zero
    tens, last = divmod(abs(rupees), 10)
    tens += last >= 5
    return (tens * 10) if rupees >= 0 else -(tens * 10)

round_288("1234.60")   # 1230: 1234 -> last digit 4 rounds down
round(1234.60)         # 1235 first, then to ten gives 1240: the wrong order
```

`Math.round` rounds halves toward +infinity, so signed pairs may not net to zero;
derive totals (gain = consideration - cost) from rounded parts.

**Why.** A ten-rupee drift in TI or tax payable is a portal mismatch or a wrong
demand, and it hides in every fixture that does not land on a boundary.

**Detector.** Grep `Math.round|toFixed|round(` in tax paths; each hit must sit at
the final TI or TTI step. Confirm one helper serves both and has tests for
positive, negative, last-digit-5 and x4.50-paise inputs (negative rounding and the
paise case are commonly untested).

## 7. TDS de-duplication across 26AS, AIS and the portal

**Rule.** The same deduction can appear in several sources. A Form 26AS row
without a TAN (a stub) and a TAN-bearing row for the same deduction are one
credit, not two. Key credits on (section, deduction date, amount), **not** on the
TAN, so the stub matches its real row; keep the TAN-bearing row and flag the
TAN-less one as a probable duplicate rather than adding it.

AIS is a broader information record than 26AS; the two legitimately differ
(AIS carries items that carry no TDS). 26AS is the TDS credit authority; AIS
informs income reporting. The portal's pre-filled view may lag either. Never
overwrite broker capital-gains figures with AIS: see
[indian-broker-statement-formats](../indian-broker-statement-formats/SKILL.md) section 17.

```python
def dedupe_credits(rows):
    kept = {}
    for r in rows:                       # r: section, date, amount, tan
        key = (r["section"], r["date"], r["amount"])
        if key not in kept or (r["tan"] and not kept[key]["tan"]):
            kept[key] = r                # prefer the TAN-bearing row
    return list(kept.values())

# two salary rows of 1,20,000, same section and date, one with a TAN: claim 1,20,000, not 2,40,000
```

The measured double-count (a real 26AS plus the stub from an AIS upload) and the
duplicated capital-gain rows from broker summary plus per-lot sheets are in
[references/portal-notes.md](references/portal-notes.md).

**Why.** Double-counted TDS inflates the refund and the portal rejects or later
recovers it.

**Detector.** Group the credit list by (amount, date) and look for groups where
one row has a TAN and one does not. Compare the sum of credits to the 26AS total
for the same TAN set.

## 8. Advance tax and the instalment schedule

**Rule.** Cumulative targets are 15%, 45%, 75% and 100% of the year's tax by
15 June, 15 September, 15 December and 15 March (§211; §408 of the 2025 Act).
Presumptive (§44AD/§44ADA) filers pay the whole by 15 March. Interest is on the
shortfall against the **cumulative** target. A shortfall caused by capital gains,
dividends, winnings or first-year business income arising **after** an instalment
date is excused (the §234C proviso; §425(4)) if the tax on it is paid in the
remaining instalments, so the quarterly accrual
split of capital gains and dividends must be tracked and is also entered in the
portal's quarterly accrual table. The §112A exemption is annual, applied to the
year's total, not per instalment. Late-filing interest (§234A; §423) is charged
on tax net of advance tax, TDS/TCS, §89/§90/§91 relief and MAT/AMT credit only;
self-assessment tax is not in that list and must not be netted into that base.

**Why.** Each of these changes the interest figure; one wrong and the return
shows interest not owed, or omits interest that is.

**Detector.** Fixture with all gains in the last quarter: earlier instalments
must show no shortfall.

## 9. JSON emit boundary: units and schema per year

**Rule.** The portal schema wants rupees as integers in most fields. If the
engine is paise-integer internally, convert exactly once, at the emitter, and
test the **emitted document**, not the builder.

- Check unit at the boundary: a 100x error passes every builder-level test.
- The schema, enumerations and required fields change every year (AY, then tax
  year); pin the schema version in the emitter and fail loudly on an unknown year.
- Do not default a missing field to 0 on emit; a missing value must be a
  validation error, since a zero reads as a statement.
- Assert each new section against a committed, value-free shape fixture taken
  from a portal-accepted JSON (shapes only, never values).
- Portal quirks (prefill supersedes an earlier AIS PDF, unpaid tax payable yields
  a demand, Schedule 112A has two modes) and the measured 100x defect:
  [references/portal-notes.md](references/portal-notes.md).

**Why.** Unit and default-zero errors survive every builder test and reach the
filed return.

**Detector.** Pick one emitted field (a TDS total), derive it independently in
rupees from the raw 26AS rows, and compare. Grep the emitter for `/ 100` and
`* 100`; more than one conversion site on a path is a double conversion.

## 10. Staleness of the rule data itself

**Rule.** Every rate, threshold and slab carries an as-of date and source.

**Why.** Limits move with each Finance Act and form release; an undated constant
cannot be re-verified and silently applies to the wrong year.

**Detector.** List constants lacking an adjacent date or source.

## 11. Filing window: due date, belated and revised returns

**Rule.** The due date (§263(1)(c); §139(1) in 1961 numbering) depends on the assessee:

| Assessee | Due date |
|---|---|
| Others (salary, capital gains, no business head) | 31 July |
| Business or profession, no audit (ITR-3/ITR-4; partners of non-audited firms) | 31 August |
| Audit case | 31 October |
| Transfer-pricing report case | 30 November |

The clock keys on whether the return has a **business head** (presumptive, books, or
F&O, even at a loss), not on the form alone. Late fee, §234A interest and the
`ItrFilingDueDate` field all read it. Check CBDT extensions before fixing a date;
Circular 07/2026 reportedly moved the AY 2026-27 audit-case date to 21 Nov 2026
(unverified).

A belated return (§263(4); §139(4)) cannot select the old regime and carries no
loss forward; a revised return has a 12-month window and a fee after 9 months. The
regime rules, fee amounts and the fail-closed filing-section rule are in
[references/filing-window.md](references/filing-window.md); read it when emitting a
late or revised return.

**Why.** A wrong clock mis-states late fee and interest, and a belated return
silently forfeits the old regime and the loss carry-forward.

**Detector.** Fixture: ITR-3 with F&O loss only and no audit is a 31 August case.

## Verifying an implementation

Run each Detector above as a test. The minimum fixture set:

- `reconcile(doc)` over every golden fixture and the final emitted JSON, plus one
  schedule perturbed by one unit to prove it fires.
- Form choice: fixtures (a)–(d) from section 1 reject ITR-1 and name the blocker; (e) does not.
- Set-off: STCG = 100, LTCL = 50, LTCG = 0 leaves STCG at 100 and carries 50.
- Rounding: ₹1,234.60 gives ₹1,230; add negative and last-digit-5 cases.
- TDS: a TAN-less stub plus its TAN-bearing row yield one credit.
- FTC: foreign tax above Indian tax caps the credit; the Indian-tax column is never 0.
- Advance tax: all gains in the last quarter show no earlier shortfall.
- Filing window: due-date clock keyed on business head; belated return cannot select the old regime; unmapped filing section raises.
- Units: one emitted total re-derived in rupees from raw rows matches.

## Scope

Return structure for resident individuals on the e-filing portal. Informational
only; **not tax advice**. Rates and charges: the skills linked at the top. Also
not here: F&O and intraday business income
([fno-tax-and-charges](../fno-tax-and-charges/SKILL.md)); buybacks, bonus, splits,
demergers, dividends ([corporate-action-taxation](../corporate-action-taxation/SKILL.md));
US stocks, RSUs, LRS/TCS ([foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md)).
