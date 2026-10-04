---
name: itr-filing-schedules
description: Choosing the right Indian ITR form (ITR-1/2/3) and getting the schedules right — CG, 112A, OS, VI-A, FSI, TR, FA, CYLA/BFLA/CFL, AMT/AMTC, AL, TI/TTI — including cross-schedule reconciliation identities, foreign income and tax credit (Rule 115, Rule 128, Form 67), TDS de-duplication, advance tax, rounding, and JSON emit pitfalls. Use when building or reviewing ITR preparation or JSON-export code, reconciling AIS/26AS/portal figures, or when the same loss or credit appears in more than one schedule and must agree.
license: MIT
compatibility: Applies to resident-individual returns on the Indian e-filing portal. Not tax advice; rates and thresholds are deliberately left to the capital-gains skill and the statute.
metadata:
  author: hariharanvisves
  version: "1.0"
  jurisdiction: India
---

# ITR Filing Schedules

Defect classes in ITR preparation code that produce a plausible return and are
found only by checking identities between schedules. Rates and exemption
amounts live in `indian-capital-gains-tax`; charges in `indian-equity-charges`.
This skill covers **structure**: which form, which schedule, what must agree.

## Law-version caveat — read first

The Income-tax Act 2025 is in force from 1 April 2026 with renumbered sections;
Chapter VI-A becomes Chapter VIII and "assessment year" becomes "tax year". The
CBDT ITR JSON schema **keeps the 1961 literals in field names and enumerations**
(regime code, relief-section codes, special-rate section codes) regardless of
year: translate section numbers only in human-facing labels, never in JSON keys.
Never translate by memory; verify against the CBDT concordance utility and the
schema for the year.

The Finance Bill 2026 memo confirms the individual regime is §202 and
§111A/§112/§112A become §196/§197/§198. The rest is **per project notes, verify
against the CBDT concordance utility**:

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

Form 67 keeps its number. Guard each label key with a parity test; a missing key renders `undefined`.

## 1. Pick the form from the facts, not from the user's last year

**Rule.** Derive the form from income and asset facts, and surface the blocker
that forced it.

| Fact | Consequence |
|---|---|
| Business or profession income, including F&O or intraday treated as non-speculative/speculative business | ITR-3 (or ITR-4 only if presumptive scheme applies and nothing else blocks it) |
| Capital gains of any kind | Not ITR-1; ITR-2 at minimum |
| Foreign asset, foreign income, or signing authority abroad | ITR-2 or ITR-3 (Schedule FA/FSI/TR); never ITR-1 |
| Brought-forward loss to carry or set off | Not ITR-1 |
| Salary/one house/interest only, within ITR-1 limits | ITR-1 |

ITR-1/ITR-4 total-income ceiling is 50 lakh (per project notes, verify against the
form instructions); eligibility should be evaluated at **record**
level (an eligible-looking filer holding one foreign lot or one carried loss is
not eligible). Surface prerequisites (Form 67 before an FTC claim) too.

**Why.** A form lacking a schedule drops data silently or gets the return treated
as defective.

**Detector.** List every input the form-suggestion function branches on; each
row above must be one. Fixtures with only (a) one foreign holding, (b) one carried
loss, (c) F&O turnover must each reject ITR-1 and name the reason.

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
- AL: assets and liabilities, required when total income exceeds 50 lakh (per
  project notes, verify against the form instructions; not the 1 crore surcharge band).
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

**Rule.** Set-off order follows the statute: current-year losses first, with a
long-term capital loss set off **only** against long-term capital gain; a
short-term capital loss may set off against short- or long-term gain. Then
brought-forward losses, then carry-forward. Never net a long-term loss against short-term gain.

**Why.** The wrong order lowers tax in the draft and is reversed on assessment.
The §112A exemption is **annual**, applied once to the year's long-term
gain on listed equity, not per instalment, per broker or per lot.

Classification defects seen in practice (per project notes):

- Non-equity ETFs and debt funds treated as equity inherit the equity rate and
  exemption. Classification must **fail closed**: unknown or unrecognised asset
  goes to the taxpayer-unfavourable slab path, never to the equity path.
- Gold, foreign shares and non-equity ETFs are outside §112A: exemption **zero**;
  they must not spend the shared pool.
- Sovereign-gold-bond maturity redemption is exempt and must be omitted upstream;
  a secondary-market sale is taxable. Check the SGB branch **before** any
  `gold|silver` name regex, since SGB names contain "Gold".
- Holding-period cutoffs differ by asset class (listed equity vs gold/foreign vs
  debt funds by purchase date). Per project notes some use **calendar months**
  (24 months), not day counts. The same cutoff is often decided in a realized path
  and an unrealized path; change both or neither. A fix to one left gold/foreign
  under-stated in the realized path for 366-729 day holds.
- Grandfathering (acquired before 31 Jan 2018): cost = max(actual cost,
  min(31 Jan 2018 fair value, sale consideration)). Both operators matter: dropping
  the inner `min` fabricates a loss when price later fell below that fair value.
  Keep **one** implementation; schedule 112A carries two cost columns (stepped and
  actual) so the step-up is auditable.
- §112 and §112A rates may be equal yet are separate levers; never substitute.
- Rebate and surcharge: marginal relief must use the same rounded base as the
  tax; the 15% surcharge cap covers specified capital-gain and dividend income but
  **not** winnings or VDA income (which take the full band).

**Detector.** Grep set-off code for any path where an `ltcl`/long-term loss
variable is subtracted from a short-term bucket. Fixture: STCG = 100, LTCL = 50,
LTCG = 0 — expect STCG unchanged and 50 carried forward.

## 5. Foreign income and tax credit

**Rule.**

- Per project notes, verify against statute: capital-gain conversion (**Rule 115**)
  uses the SBI telegraphic-transfer buying rate on the last day of the month
  **preceding** the transaction month; tax-credit conversion (**Rule 128**) uses the
  same rate on the last day of the month preceding the month the income accrued or
  tax was deducted. Keep the rate table per financial year with a source; a stale
  table silently mis-converts.
- **Form 67** must be filed **before** the credit is claimed in the return;
  claiming first is the usual failure.
- A US broker's **Form 1042-S** and similar withholding statements are the
  evidence for the tax paid; match the withheld amount, not the gross.
- In FSI, relief = min(tax paid abroad, Indian tax on that income). Leaving the
  Indian-tax column at 0 **silently zeroes the credit with no validation error**;
  compute it as the marginal-rate tax on the foreign income.
- Part B-TTI's foreign-asset question defaults to No even with Schedule FA filled;
  a false No is a black-money-law exposure. Warn loudly.
- Credit is capped at the lower of foreign tax paid and Indian tax on that
  income, computed per country and per head.

**Why.** A different rate moves income and credit; a missing Form 67 voids the claim.

**Detector.** Grep the converter for how it picks a rate (a hardcoded
`usdInr`, today's rate, or the transaction date's rate are three different
defects). Check that the emit path refuses a TR claim when no Form 67
acknowledgement field is present. Verify the cap with a fixture where foreign
tax exceeds Indian tax.

## 6. Rounding: §288A and §288B are different rules

Both end at the nearest ten rupees but differ in the first step. Per project
notes, verify against the statute text (2025 Act numbers differ):

- §288A (total income): the paise part is **dropped** (floor to the rupee), then
  round to the nearest ten.
- §288B (tax, interest, refund): round to the nearest rupee (50 paise and above
  up), then round to the nearest ten.

They are separate rules, not a duplicated helper to merge: replacing the floor
with a round makes the income helper non-statutory. Apply statutory rounding at
total income and final tax **only**, never in intermediate schedules; marginal
relief, surcharge and rebate must use the same rounded base as the tax they
adjust (a sub-ten drift appears at the rebate cliff otherwise).

`Math.round` rounds halves toward +infinity, so signed pairs may not net to zero;
derive totals (gain = consideration - cost) from rounded parts.

**Detector.** Grep `Math.round|toFixed|round(` in tax paths; each hit must sit at
the final TI or TTI step. Confirm two distinct helpers exist and have a test each
for positive, negative and exact-half inputs (negative rounding and the tax-side
helper are commonly untested).

## 7. TDS de-duplication across 26AS, AIS and the portal

**Rule.** The same deduction can appear in several sources. A Form 26AS row
without a TAN (a stub) and a TAN-bearing row for the same deduction are one
credit, not two. Key credits on (deductor TAN, section, deduction date, amount);
treat a TAN-less row as a probable duplicate and flag it rather than adding it.

AIS is a broader information record than 26AS; the two legitimately differ
(AIS carries items that carry no TDS). 26AS is the TDS credit authority; AIS
informs income reporting. The portal's pre-filled view may lag either.

Measured defect: a real 26AS (TAN present) and the stub auto-created from an AIS
upload (no TAN) held the same salary credit; concatenation doubled the TDS and
turned a small genuine demand into a large false refund. The dedupe key
must **omit the TAN** so the stub matches the real row, and keep the TAN-bearing
row. Mirror defect: salary TDS present only in AIS and excluded from the AIS side
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
15 June, 15 September, 15 December and 15 March (per project notes, verify against
the statute). Interest is on the shortfall against the **cumulative** target. Tax
on gains, dividends and presumptive income that arise **after** an instalment date
is excluded from earlier instalments (the §234C proviso), so the quarterly accrual
split of capital gains and dividends must be tracked and is also entered in the
portal's quarterly accrual table. The §112A exemption is annual, applied to the
year's total, not per instalment. Late-filing interest (§234A) is charged
on tax net of advance tax and TDS/TCS only; self-assessment tax paid early must
not be netted into that base.

**Detector.** Fixture with all gains in the last quarter: earlier instalments
must show no shortfall.

## 9. JSON emit boundary: units and schema per year

**Rule.** The portal schema wants rupees as integers in most fields. If the
engine is paise-integer internally, convert exactly once, at the emitter, and
test the **emitted document**, not the builder.

- Check unit at the boundary: a 100x error passes every builder-level test.
- The schema, enumerations and required fields change per assessment year; pin
  the schema version in the emitter and fail loudly on an unknown year.
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

**Detector.** Pick one emitted field (a TDS total), derive it independently in
rupees from the raw 26AS rows, and compare. Grep the emitter for `/ 100` and
`* 100`; more than one conversion site on a path is a double conversion.

## 10. Staleness of the rule data itself

**Rule.** Every rate, threshold and slab carries an as-of date and source.
**Detector.** List constants lacking an adjacent date or source.
