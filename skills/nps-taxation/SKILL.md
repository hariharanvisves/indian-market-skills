---
name: nps-taxation
description: Income tax on the National Pension System (NPS) for a resident individual, salaried or self-employed. Which deductions survive in the new default regime (only the employer contribution, §124(1)-(2); not the own contribution or the extra ₹50,000), the 14% vs 10% employer limit on basic plus DA by regime and employer type, the ₹1.5 lakh and ₹50,000 own-contribution limits, the ₹7.5 lakh aggregate employer cap and its perquisite, exit lump sum excluded only if it does not exceed 60% of the corpus (PFRDA's new 80% option is not matched, so read it as taxable), partial withdrawal to 25% of an employee's own contributions, annuity at slab, plus Tier II, UPS and NPS Vatsalya. Income-tax Act 2025 sections with 1961 equivalents. Use when building or reviewing an NPS deduction, salary-tax or retirement-planning calculator, a Form 16 or ITR NPS line, or when asked about 80CCD(1), 80CCD(1B), 80CCD(2), 10(12A), 10(12B), NPS withdrawal tax, the 80% lump sum or the employer NPS cap.
license: MIT
compatibility: Checked 2026-11-26 against the Gazette text of the Income-tax Act 2025 (Act No. 30 of 2025; §§7, 16, 17, 29, 122, 123, 124, 202, Schedules II, III, XV), the Finance Bill 2026 as introduced, and the PFRDA Exits and Withdrawals Regulations as amended 16 Dec 2025. Checked against the enacted Finance Act 2026 (Act No. 4 of 2026), which does not amend §124, §17, Schedule II or Schedule XV; its §7, §29 and §202 amendments and its Schedule III insertions (Sl. 38A-38D) do not touch the NPS limits; re-verify before use.
metadata:
  author: hariharanvisves
  version: "1.0"
  verified: "2026-11-26"
  jurisdiction: India
---

# NPS Taxation (resident individual)

Most NPS tax code and advice describes the old regime: own contributions
deductible, employer cap 10%, and a 60% tax-free exit. The traps now are:
the default regime keeps only the employer deduction (own contributions were
already barred there), the employer limit depends on the regime (14% in the new
regime has applied since FY 2024-25), and, new from 16 December 2025, PFRDA lets
non-government subscribers take 80% as lump sum while the tax text still tests
the payment against 60%.

## Core rules

1. **New (default) regime allows only the employer contribution deduction**, §124(1)-(2). No deduction for own contributions, not §123 and not the extra ₹50,000 ([section 4](#4-the-regime-gate)).
2. **Employer limit is a percentage of basic plus DA:** 14% for Central or State Government employers, 10% for every other employer under the old regime, and 14% for every employer under the new regime ([section 3](#3-employer-contribution-section-1241-2)).
3. **Own contribution (old regime):** 10% of salary for an employee, 20% of gross total income for others, inside the shared ₹1,50,000 limit ([section 2](#2-own-contribution-sections-123-and-1243)).
4. **The extra ₹50,000 is for money not already claimed under the ₹1,50,000 limit**, and is old-regime only ([section 2](#2-own-contribution-sections-123-and-1243)).
5. **Employer contributions above ₹7,50,000 a year, summed across PF, NPS and superannuation, are a perquisite**, with the accretion on the excess ([section 5](#5-aggregate-employer-cap-75-lakh)).
6. **Exit lump sum: Schedule II Sl. 6(b) requires the payment not to exceed 60% of the total corpus.** Above 60% the fail-closed figure is the whole lump sum; excess-only is the alternative reading. Never print an 80% payout as tax-free ([section 6](#6-exit-lump-sum-schedule-ii-sl-6)).
7. **Partial withdrawal is exempt up to 25% of the subscriber's own contributions**, not of the corpus, for an employee or a minor's parent or guardian ([section 7](#7-partial-withdrawal-schedule-iii-sl-4)).
8. **Annuity income is taxable when received; buying the annuity is not income** ([section 8](#8-annuity-and-death)).
9. **Unknown regime or employer type must raise**, never default to a deduction ([section 10](#10-code-sketch)).

## 1. Years and sections

The Income-tax Act 2025 applies from 1 April 2026 (**tax year** 2026-27 onward).
FY 2025-26 returns (AY 2026-27) stay under the 1961 Act. The 1961 numbers below
are the ones ITR forms and Form 16 still show.

| Topic | 2025 Act | 1961 Act |
|---|---|---|
| Employer contribution deduction | §124(1)-(2) | §80CCD(2) |
| Extra ₹50,000 | §124(3) | §80CCD(1B) |
| Own contribution within ₹1.5 lakh | §123 with Schedule XV 1(y) | §80CCD(1) with §80CCE |
| Employer contribution is salary | §16(k), §7(1)(c) | §17(1)(viii) |
| Employer's own deduction, up to 14% | §29(1)(b) | §36(1)(iva) |
| ₹7.5 lakh aggregate perquisite | §17(1)(h), (i) | §17(2)(vii), (viia) |
| Exit lump sum exempt | Schedule II Sl. 6 | §10(12A) |
| Partial withdrawal exempt | Schedule III Sl. 4 | §10(12B) |
| Closure and annuity taxed | §124(6), (9) | §80CCD(3) onward |
| New regime gate | §202(2)(a)(xii) | §115BAC |
| Tier II tax saver (Central Government employees) | Schedule XV 1(w) | §80C(2) |

The 2025 column was read in the Gazette text; the 1961 column is the matching
1961 provision and was not re-read. Check the 1961 text for FY 2025-26 or earlier.
The enacted Finance Act 2026 (Act No. 4 of 2026) does not amend §124, Schedule II,
Schedule XV or §17, and its §7, §29 and §202 amendments do not touch the NPS limits.

## 2. Own contribution: sections 123 and 124(3)

**Rule (old regime only).** Two separate pools:

- **§123 with Schedule XV 1(y).** Own NPS contribution up to **10% of salary** for
  an employee of the Central Government or any other employer, or **20% of gross
  total income** for anyone else (self-employed, professional). It shares the
  **₹1,50,000** ceiling with PPF, EPF, life premia and every other Schedule XV item.
- **§124(3).** A further **₹50,000** for any individual, in addition. It is allowed
  only for an amount **not** claimed under §123 (§124(5), (10)).

**Salary** means basic plus dearness allowance where the terms of employment
provide for it; every other allowance and perquisite is excluded (§124(13)(b)).
Total Chapter VIII deductions cannot exceed gross total income (§122(2)).

**Why.** The ₹50,000 is a second pool, not a second claim on the same rupee. An
engine that adds ₹1,50,000 and ₹50,000 regardless of what else fills the first
pool overstates the deduction, and one that stops at ₹1,50,000 understates it.

**Worked example.** Old regime, private employee, basic plus DA ₹10,00,000, own
contribution ₹1,50,000, nothing else under §123: §123 allows 10% = ₹1,00,000,
and the remaining ₹50,000 goes to §124(3). Total own-contribution deduction is
₹1,50,000. If the same employee already uses the full ₹1,50,000 on EPF and
PPF, the NPS rupees go entirely to §124(3) and only ₹50,000 is allowed.

**Detector.** A deduction for own contributions with no regime test; `min(x, 150000) + 50000` with no
`own - already_claimed` term; a salary base that includes HRA or special allowance.

## 3. Employer contribution: section 124(1)-(2)

**Rule.** The employer's contribution to the NPS account is deductible up to a
share of salary (basic plus DA):

| Regime | Employer is the Central or a State Government | Any other employer |
|---|---|---|
| Old | 14% (§124(1)(a)) | 10% (§124(1)(b)) |
| New (default, §202(1)) | 14% | 14% (§124(2)) |

The contribution is part of salary income (§16(k), §7(1)(c)) and the deduction
removes it, up to the limit. The employee need not contribute. An amount above the
limit stays taxable. Only the Central Government or a State Government is named in
§124(1)(a); read a public-sector company, bank or statutory body as "other" and say so.
The employer's own business deduction (§29(1)(b), up to 14%) is a different limit
and never caps the employee's.

**Why.** Reading 10% as the cap in every regime undercounts deductions in the new
regime, which is the default for most salaried people from tax year 2026-27.

**Worked example.** Basic plus DA ₹10,00,000, employer contribution ₹1,30,000,
private company. Old regime: ₹1,00,000 deductible, ₹30,000 taxable. New regime:
14% = ₹1,40,000, so the full ₹1,30,000 is deductible. A Central Government employee
gets the full ₹1,30,000 in both regimes.

**Detector.** One `0.10` constant for non-government employers with no regime branch;
a cap on gross salary or CTC rather than basic plus DA.

## 4. The regime gate

**Rule.** Under §202(1) the income is computed without any Chapter VIII deduction
**other than §124(1), §124(2), §125(2) and §146** (§202(2)(a)(xii)). So in the new
regime: employer contribution yes; §123 (own contribution), §124(3) and §124(4)
(the ₹50,000 and a minor's account) no. §202(2)(a)(i) names only
Schedule III Sl. 5, 6, 7, 8, 11 and 17; the NPS exit exclusion (Schedule II Sl. 6)
and the partial-withdrawal exclusion (Schedule III Sl. 4) are not named, so both
apply in both regimes.

The new regime is the default each tax year unless the option in §202(4) is
exercised. A person with business or professional income who opts out can
withdraw only once (§202(4)(a)), so do not model a free yearly switch for the
self-employed. ITR and Form 16 mechanics: [itr-filing-schedules](../itr-filing-schedules/SKILL.md).

**Detector.** A deduction table that is keyed by section but not by regime.

## 5. Aggregate employer cap: ₹7.5 lakh

**Rule.** The employer's contributions in a tax year to a recognised provident
fund, to the NPS under §124(1), and to an approved superannuation fund are added.
The amount above **₹7,50,000** is a perquisite (§17(1)(h)), and so is the annual
accretion (interest, dividend or similar) on that excess, computed as prescribed
(§17(1)(i)). It applies in both regimes and counts employer money only.

**Why.** It is a separate test from the 14% or 10% deduction limit. A contribution
can be inside §124(1) and still push the three-fund total over ₹7,50,000. Netting
the two tests hides the perquisite.

**Worked example.** PF ₹4,00,000, NPS ₹3,50,000 and superannuation ₹1,00,000 total
₹8,50,000. ₹1,00,000 is a perquisite, plus the accretion on that ₹1,00,000.

**Detector.** No sum across the three funds anywhere in payroll or Form 16 logic;
employee contributions added to the ₹7,50,000 total.

## 6. Exit lump sum: Schedule II Sl. 6

**Rule.** Schedule II Sl. 6 excludes a payment from the NPS Trust only when two
conditions in column C hold (§10(12A) in 1961 numbering). Verbatim from the Gazette text:

> (a) Such payment is on closure of account of the assessee or on his opting out of
> the pension scheme referred to in section 124; and
> (b) the said payment does not exceed 60% of the total amount payable at the time of
> such closure or his opting out of the scheme.

The test is against the **whole corpus**, not the lump sum. The 1961 words "to the
extent it does not exceed" are gone: Sl. 6(b) is a condition, and other rows of the same
Schedule, such as Sl. 8(d), still say "to the extent". On a literal reading a payment
above 60% fails (b) and gets no exclusion, and §124(6) then deems "the whole of the
amount" received on closure to be income of that year.

PFRDA now lets non-government subscribers (All Citizen, Corporate) take **up to 80%**
as lump sum, effective 16 December 2025 (Regulations, Schedule I Table 2), and a corpus up to
₹8 lakh may be taken entirely as lump sum. Government-sector lump sum stays at 60%.
Full tables: [references/pfrda-exit-rules.md](references/pfrda-exit-rules.md).

| Case | Lump sum as share of corpus | Fail-closed (strict) taxable | Alternative (excess only) |
|---|---|---|---|
| Government sector, normal exit | up to 60% | nil | nil |
| Non-government, normal exit, 80% option | up to 80% | the whole lump sum | 20% of corpus |
| Any sector, small corpus taken 100% | 100% | the whole lump sum | 40% of corpus |
| Fixed-amount option, up to ₹6 lakh on a ₹8 to ₹12 lakh corpus | 50% to 75%, computed per case | nil at or below 60% (corpus ₹10 lakh or more); otherwise as above | excess over 60% |
| Premature exit | up to 20% | nil | nil |

**Fail-closed rule.** If the lump sum is more than 60% of the corpus, treat the
**whole lump sum as taxable at slab in the tax year received**, and show the
excess-only figure as the alternative reading. Say which one you printed. No
amendment to Sl. 6 appears in the Gazette text or the enacted Finance Act 2026
(Act No. 4 of 2026), and no CBDT notification matching the PFRDA change was found. Other points stay open:

- whether §124(6) reaches only amounts "in respect of which a deduction has been
  allowed" plus accruals, since the Act does not say how a mixed corpus is split;
- whether systematic lump-sum withdrawal or unit redemption instalments are tested
  against 60% when received.

**Why.** Regulators and tax law are separate sources, and the tax text lost its
"to the extent" wording. Copying PFRDA's 80% into the exemption, or assuming 60% of an
80% payout is exempt, is the likeliest error after the 2025 amendment.

**Worked example.** Non-government subscriber, corpus ₹50 lakh, takes ₹40 lakh lump
sum (80%) and buys a ₹10 lakh annuity. ₹40 lakh is above the 60% cap of ₹30 lakh.
Strict reading: all ₹40 lakh taxable. Excess-only reading: ₹10 lakh taxable. The
₹10 lakh annuity purchase is not income. A ₹30 lakh lump sum (60%) is tax-free
under both readings.

**Detector.** `0.8`/`0.6` times the lump sum instead of the corpus; a lump-sum
limit read from PFRDA tables feeding the exemption; an output of "exempt" for a
payment above 60% with no stated reading.

## 7. Partial withdrawal: Schedule III Sl. 4

**Rule.** Schedule III Sl. 4 applies to "(i) any employee; or (ii) an assessee, being
the guardian or parent of a [minor]". Its condition is a partial withdrawal under PFRDA
terms, with the exclusion not exceeding **25% of the contributions made by him**
(§10(12B) in 1961 numbering). Employer contributions and returns are not in the base.
PFRDA regulation 8(1) states the same 25% of own contributions, subject to purposes
and frequency.

**Eligibility is fail-closed.** The Act text names employees and a minor's parent or
guardian. A self-employed or All-Citizen subscriber who is not an employee is not
named, so treat the withdrawal as not excluded unless the reader confirms the
reading, and say so.

**Worked example (employee).** Own contributions ₹8,00,000, employer contributions
₹4,00,000, corpus ₹20,00,000. The base is ₹8,00,000, so ₹2,00,000 is the limit, not
25% of ₹20,00,000 or of ₹12,00,000.

**Detector.** `0.25 * corpus` or `0.25 * (own + employer)`; the exclusion applied
without an employee or parent-of-minor test.

## 8. Annuity and death

**Rule.** Pension from an annuity bought on closure is taxable in the year received,
at the person's normal rates (§124(6)(b)). An amount used to buy an annuity in the
same tax year is not treated as received (§124(9)). Amounts received by a nominee on
the subscriber's death are not the nominee's income (§124(7)); the same holds for a
parent or guardian after a minor's death (§124(8)).

**Why.** Taxing the purchase and then the pension counts the same money twice.

**Detector.** Annuity purchase price added to taxable income; annuity pension
excluded.

## 9. Tier II, UPS and NPS Vatsalya

- **Tier II.** No deduction, except a Central Government employee's tax-saver
  Tier II with a fixed period of at least 3 years, which sits inside the ₹1,50,000
  of §123 (Schedule XV 1(w)). The Act has no Tier II exit exclusion; the tax treatment of Tier II gains is unverified, so do not output a figure.
- **Unified Pension Scheme.** A UPS subscriber's lump sum at superannuation or
  voluntary retirement is excluded when it does not exceed 60% of the individual corpus (Schedule II
  Sl. 15(b), worded like Sl. 6(b), so the same cap-or-cliff question applies); the "lump sum amount" of the UPS notification is excluded (Sl. 16); a
  transfer to the pool corpus is not income (§124(12)).
- **Minor's account.** §124(4) allows the parent or guardian a deduction for a
  deposit into a minor's NPS account inside the same ₹50,000 as §124(3), old regime
  only. Partial withdrawal by the parent or guardian from a minor's account is excluded up to 25% of
  contributions (Schedule III Sl. 4). The Act says "the said pension scheme notified by
  the Central Government" and does not use the name "NPS Vatsalya"; the notification
  naming it was not read, so cite the Act sections and mark the mapping unverified.

## 10. Code sketch

The deduction by regime and the exit split, the two rules most often wrong:

```python
GOVT, OTHER, SELF = "central_or_state_govt", "other_employer", "self_employed"

def _rupees(*vals):
    if any(type(v) is not int or v < 0 for v in vals):
        raise ValueError("whole non-negative rupees only")

def nps_deductions(regime, who, salary, gti, own, employer, other_80c=0):
    """salary = basic + DA only. NPS deductions in whole rupees for the tax year."""
    if regime not in ("old", "new") or who not in (GOVT, OTHER, SELF):
        raise ValueError("unknown regime or employer type")
    _rupees(salary, gti, own, employer, other_80c)
    if who == SELF and employer:
        raise ValueError("self-employed has no employer contribution")
    emp_pct = 14 if regime == "new" or who == GOVT else 10          # s.124(1)-(2)
    d = {"employer": min(employer, salary * emp_pct // 100), "own_123": 0, "extra_50k": 0}
    if regime == "old":                                              # new: s.202(2)(a)(xii)
        cap = gti * 20 // 100 if who == SELF else salary * 10 // 100  # Sch XV 1(y)
        d["own_123"] = max(0, min(own, cap, 150_000 - other_80c))
        d["extra_50k"] = min(50_000, own - d["own_123"])             # s.124(3), (5)
    d["total"] = min(sum(d.values()), gti)                           # s.122(2)
    return d

def exit_lump_sum_taxable(total_corpus, lump_sum, annuity_bought=0, strict=True):
    """Sch II Sl.6(b): 'payment does not exceed 60% of the total amount payable'.
    strict: above 60% the whole lump sum is taxed. strict=False: only the excess."""
    _rupees(total_corpus, lump_sum, annuity_bought)
    if lump_sum + annuity_bought > total_corpus:
        raise ValueError("payout exceeds corpus")
    cap = total_corpus * 60 // 100
    if lump_sum <= cap:
        return 0
    return lump_sum if strict else lump_sum - cap

nps_deductions("new", OTHER, 1_000_000, 1_000_000, 150_000, 130_000)
# {'employer': 130000, 'own_123': 0, 'extra_50k': 0, 'total': 130000}
nps_deductions("old", OTHER, 1_000_000, 1_000_000, 150_000, 130_000)
# {'employer': 100000, 'own_123': 100000, 'extra_50k': 50000, 'total': 250000}
exit_lump_sum_taxable(50_00_000, 40_00_000, 10_00_000)               # 4000000
exit_lump_sum_taxable(50_00_000, 40_00_000, 10_00_000, strict=False)  # 1000000
```

The `extra` line gives the ₹50,000 pool the rupees the §123 pool cannot take, and
`total` is capped at gross total income (§122(2)) for the NPS items only; other
Chapter VIII deductions also count against it. `exit_lump_sum_taxable` defaults to
the fail-closed reading in section 6; `strict=False` gives the excess-only
alternative. Neither is a settled figure.

## Verifying an implementation

- **Run the same salary through both regimes** and assert own contributions drop
  to zero in the new regime while the employer deduction stays.
- **Test a private and a Central Government employer in the old regime**, so the
  10% and 14% branches both run; then repeat in the new regime and assert both give 14%.
- **Fill the ₹1,50,000 with other Schedule XV items**, then add NPS. The NPS
  rupees must flow to the ₹50,000 pool only.
- **Test a salary with HRA or special allowance** and assert it does not change the
  cap.
- **Test an exit with an 80% lump sum** and assert it is not reported as exempt (strict:
  whole lump sum taxable; excess-only: 20% of corpus); then a lump sum of exactly 60%
  (nil under both); then a 100% lump sum on a small corpus.
- **Test a deduction total above gross total income** and assert it is capped.
- **Pass negative and fractional rupee inputs**; they must raise.
- **Test the three-fund total** at exactly ₹7,50,000 (no perquisite) and one rupee
  above.
- **Pass an unknown regime and an unknown employer type**; both must raise.

## Scope

Resident-individual income tax on NPS contributions, employer contributions and
exits for tax year 2026-27 onward, with 1961 equivalents. Informational only; **not
tax advice**. Re-verify limits against each Finance Act.

Not here: ITR forms, Schedule VI-A and advance tax ([itr-filing-schedules](../itr-filing-schedules/SKILL.md));
capital gains on units and other assets ([indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md)).
Also out: non-residents, the Agniveer Corpus Fund (§125), the employer's company tax
and PFRDA operational procedure beyond the lump-sum limits above.
