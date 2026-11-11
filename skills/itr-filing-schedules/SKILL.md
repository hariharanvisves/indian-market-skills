---
name: itr-filing-schedules
description: Choosing the Indian ITR form (ITR-1/2/3/4) and getting its schedules right — Schedule CG, 112A, OS, VI-A, FSI, TR, FA, CYLA/BFLA/CFL, AMT/AMTC, AL, TI/TTI — with cross-schedule reconciliation identities, foreign tax credit (Rule 128/Rule 76, Form 67/Form 44, Rule 115 FX rate), TDS de-duplication across 26AS and AIS, advance tax and §234C, §288A/§288B rounding, and ITR JSON emit pitfalls. Use when building or reviewing ITR preparation or JSON-export code, deciding between ITR-1, ITR-2 and ITR-3, reconciling AIS/26AS/portal figures, or when one loss or credit appears in several schedules and must agree.
license: MIT
compatibility: Applies to resident-individual returns on the Indian e-filing portal. Form, schedule and rule facts verified 2026-11-11 for AY 2026-27 and tax year 2026-27. Not tax advice; rates and thresholds are deliberately left to the capital-gains skill and the statute.
metadata:
  author: hariharanvisves
  version: "1.1"
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

## Law-version caveat — read first

The Income-tax Act 2025 is in force from 1 April 2026 with renumbered sections;
Chapter VI-A becomes Chapter VIII and "assessment year" becomes "tax year". The
CBDT ITR JSON schema **keeps the 1961 literals in field names and enumerations**
(regime code, relief-section codes, special-rate section codes) regardless of
year: translate section numbers only in human-facing labels, never in JSON keys.
Never translate by memory; verify against the CBDT concordance utility and the
schema for the year.

Years: **AY 2026-27** is the return for FY 2025-26 (1961 Act); **tax year
2026-27** is FY 2026-27 (2025 Act). A financial year (FY) runs 1 April–31 March.

The table below was checked against the gazetted Act text and the Income-tax
Rules 2026 on 2026-11-11; confirm sub-section-level mappings against the CBDT
concordance utility:

| 1961 | 2025 | | 1961 | 2025 |
|---|---|---|---|---|
| §111A | §196 | | §87A rebate | §156 |
| §112 | §197 | | §89 relief | §157 |
| §112A | §198 | | §80C/80CCC/80CCE | §123 |
| §115BB, §115BBH | §194 | | §80CCD | §124 |
| §115JC (AMT) | §206 | | §80D | §126 |
| §234A / B / C | §423 / §424 / §425 | | §54 / §54EC / §54F | §82 / §85 / §86 |
| §194S (VDA TDS) | §393 | | §49 (cost by acquisition mode) | §73(1) |
| §44AD/ADA/AE | §58 | | Rule 128 (FTC) | Rule 76 (2026 Rules) |
| §115BAC (new regime) | §202 | | Rule 115 (FX conversion) | Rule 206 (2026 Rules) |
| Form 67 (FTC statement) | Form 44 | | §288A / §288B (rounding) | §516 |

Rule 76 and Form 44 apply from tax year 2026-27; returns for AY 2026-27 and
earlier still use Rule 128 and Form 67. Guard each label key with a parity test;
a missing key renders `undefined`.

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
| Salary/one house/interest only, within ITR-1 limits | ITR-1 |

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
8. Portal CG quarterly-accrual table row totals equal the matching BFLA items
   (per project notes from a real portal filing): the long-term special-rate row
   equals the BFLA long-term item and **includes §112A gains covered by the
   exemption**, not only taxable gain. Negative quarterly cells are rejected, so
   fold a negative quarter into an adjacent one; only the sum is validated.
9. Foreign dividend appears in OS (added on top of the portal prefill, which
   knows nothing of foreign brokers) and the **same rupee amount** in FSI.

Measured defect: brought-forward losses were reported twice (CFL and BFLA) once
BFLA landed. Add the identity test in the same change as any new schedule.

**Why.** Each schedule can be individually correct and the document wrong. A
loss counted in both CYLA and CFL, or a credit in both FSI and TR, only
shows when you add across.

**Detector.** Write one function `reconcile(doc)` that returns a list of
violated identities, run it over every golden fixture and over the final emitted
JSON. Prove it fires by perturbing one schedule by one unit.

## 4. Capital-gains ordering inside the schedules

**Rule.** The set-off order, the long-/short-term asymmetry and the annual §112A
exemption are owned by [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md) (its "Correct computation order"). In
schedule terms: CYLA first, then BFLA, then CFL. Never net a long-term loss
against short-term gain.

**Why.** The wrong order lowers tax in the draft and is reversed on assessment.

Classification defects seen in practice (per project notes):

- Fail-closed classification, the SGB branch (exemption conditions, checked
  before any `gold|silver` name regex), zero §112A exemption for gold, foreign
  shares and non-equity ETFs, and the grandfathering formula are owned by
  the capital-gains skill. Keep **one** implementation of each, and have the
  schedule writer read it.
- Holding-period cutoffs differ by asset class (listed equity vs gold/foreign vs
  debt funds by purchase date), and all are counted in **calendar months**,
  not days (thresholds in the capital-gains skill). The same cutoff is often decided in a realized path
  and an unrealized path; change both or neither. A fix to one left gold/foreign
  under-stated in the realized path for 366-729 day holds.
- §112 and §112A rates may be equal yet are separate levers; never substitute.
- Rebate and surcharge: marginal relief must use the same rounded base as the
  tax; the 15% surcharge cap covers specified capital-gain and dividend income but
  **not** winnings or VDA income (which take the full band).

**Detector.** Grep set-off code for any path where an `ltcl`/long-term loss
variable is subtracted from a short-term bucket. Fixture: STCG = 100, LTCL = 50,
LTCG = 0 — expect STCG unchanged and 50 carried forward.

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

Measured defect: a real 26AS (TAN present) and the stub auto-created from an AIS
upload (no TAN) held the same salary credit; concatenation doubled the TDS and
turned a small genuine demand into a large false refund. Mirror defect: salary TDS present only in AIS and excluded from the AIS side
of a TDS reconciliation shows a false mismatch.

Similarly for capital-gain rows: broker P&L summary sheets and per-lot sheets
exported together count the same trades up to three times. A natural key that
includes sale date and amounts never matches an undated aggregate row against its
dated per-lot rows, so the duplicate check reports zero. Skip aggregate rows whose
quantity and consideration equal the per-lot sum.

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
- Real defect: a missing divide at one emit point produced a 100x capital-gain
  figure; builder-level tests pinned the builder's own scale and could not see it.
- Portal quirks (per project notes): prefill reads the live AIS at filing time and
  supersedes an earlier AIS PDF (including interest on a prior-year refund); if
  prefill exceeds your estimate, trust it. Filing with tax payable unpaid yields an
  intimation demand. Schedule 112A has a consolidated two-total mode for post-2018
  acquisitions and scrip rows for pre-2018 holdings. CYLA/BFLA/CFL are portal views.

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
- Units: one emitted total re-derived in rupees from raw rows matches.

## Scope

Return structure for resident individuals on the e-filing portal. Informational
only; **not tax advice**. Rates and charges: the skills linked at the top. Also
not here: F&O and intraday business income
([fno-tax-and-charges](../fno-tax-and-charges/SKILL.md)); buybacks, bonus, splits,
demergers, dividends ([corporate-action-taxation](../corporate-action-taxation/SKILL.md));
US stocks, RSUs, LRS/TCS ([foreign-equity-for-residents](../foreign-equity-for-residents/SKILL.md)).
