---
name: foreign-equity-for-residents
description: Indian tax and reporting rules for a resident individual holding foreign (mainly US) shares, bought through LRS platforms (INDmoney, Vested and similar) or received as employer RSUs, ESPP or ESOPs. Covers ROR vs RNOR gating, the USD 250,000 LRS limit and TCS on remittances with its credit, the 24-month holding period and rate for shares not listed in India, SBI TT buying-rate conversion (Rule 115 / Rule 206), RSU and ESPP perquisite and cost basis, US dividend withholding at the India-US treaty rate with foreign tax credit, Schedule FA on a calendar year with peak and closing values, Black Money Act penalties, and US estate-tax exposure. Use when computing or reviewing gains, cost basis, exchange rates, TCS or Schedule FA for US stocks, RSUs, ESPP, W-8BEN, Form 1042-S or Form 67, or when code treats US stocks like NSE-listed equity.
license: MIT
compatibility: Rules verified 2026-11-11 against the Income-tax Act 2025, Finance Act 2026, Income-tax Rules 2026 and the AY 2026-27 ITR-2. Covers FY 2025-26 (1961 Act) and tax year 2026-27 onward (2025 Act). Not tax advice; re-verify each Finance Act.
metadata:
  author: hariharanvisves
  version: "1.0"
  jurisdiction: India
  verified: "2026-11-11"
---

# Foreign Equity for Resident Individuals

To an Indian resident, a US share is a different asset from an NSE share. Its
holding period, rate, exemption, exchange-rate rule and disclosure all differ.
Code that reuses the listed-equity path gets each one wrong, and the output still
looks plausible. Indian-asset rates and set-off are owned by
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md). Schedule and
Form 67 / Rule 128 mechanics are owned by
[itr-filing-schedules](../itr-filing-schedules/SKILL.md). This skill states only
the **foreign-asset delta**.

## Law version: pick the Act from the year

FY 2025-26 (AY 2026-27) income falls under the **1961 Act and 1962 Rules**. From
tax year 2026-27, the **Income-tax Act 2025** and the **Income-tax Rules 2026**
(Notification 22/2026, G.S.R. 198(E)) apply. Each 2025 number below was checked
against the Gazette text of the Act and of the Rules. The bracketed 1961 numbers
are standard concordance; confirm them with the CBDT concordance before you use
one as a label.

| Topic | 2025 Act / 2026 Rules | 1961 Act / 1962 Rules |
|---|---|---|
| RNOR, scope of income | §6(13), §5(1)(c) | §6(6), §5(1)(c) proviso |
| Short-term capital asset | §2(101) | §2(42A) |
| LTCG on other assets | §197 | §112 |
| ESOP/RSU perquisite | §17(1)(d), value §17(4)(h) | §17(2)(vi) |
| Cost = FMV taxed as perquisite | §73(1) Table Sl. 4 | §49(2AA) |
| TCS on LRS | §394(1) Table Sl. 7 | §206C(1G)(a) |
| Exchange rate for income | Rule 206 | Rule 115 |
| Foreign tax credit | Rule 76, **Form No. 44** | Rule 128, Form 67 |

The 2026 Rules number the FTC statement **Form No. 44** (Rule 76(10)(a)). Code
keyed on "Form 67" needs a year switch.

## 1. Residential status gates everything

**Rule.** Only a resident and ordinarily resident (ROR) individual is taxed on
worldwide income and fills Schedule FA. An RNOR is taxed on income that accrues
outside India only when it comes from a business controlled in India or a
profession set up in India (§5(1)(c), §6(13)). Income received in India is taxed
either way. The ITR-2 manual says Schedule FA "need not be filled up if you are
Not Ordinarily Resident or a Non-Resident"
([e-filing](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/file-itr-2-online/itr-2-UM)).

**Why.** Returning employees are often RNOR for a year or two. If code taxes their
US dividends, or forces Schedule FA, it overstates what they owe. A single
`resident` flag cannot tell ROR from RNOR.

**Detector.** The residency field needs three values: ROR, RNOR and NR. The
foreign-income branches and the FA branch must each test for ROR, not for "resident".

## 2. LRS limit and TCS on the remittance

**Rule.**
- Under LRS a resident individual may remit **USD 2,50,000 per financial year
  (April–March)**, all permitted purposes combined
  ([RBI FAQ](https://www.rbi.org.in/commonman/english/Scripts/FAQs.aspx?Id=1834);
  [Master Direction](https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10192)).
  This is a FEMA cap in USD, not a tax threshold.
- The authorised dealer collects TCS on LRS remittances above **₹10 lakh**. For
  purposes other than education or medical treatment, investment included, the
  rate is **20% of the excess** (§394(1) Table Sl. 7(b)). Finance Act 2026 §85(e)
  cut only the education and medical rate, from 5% to 2%, from 1 Apr 2026.
- For FY 2025-26, Finance Act 2025 §72 raised the §206C(1G) threshold from ₹7 lakh
  to ₹10 lakh ([incometaxindia.gov.in](https://www.incometaxindia.gov.in/w/section-72-94)).
  The 1961-text 20% rate is unverified here; check §206C(1G) for that year.
- TCS is **tax paid on your behalf**, not a fee (§390(5)). Claim it as a credit in
  the return. An employee can also ask the employer to count it against salary TDS
  (§392(4)(a)(v) [§192(2B)]).

**Why.** Ledgers show TCS as a deduction from the remittance, so importers add it
to cost or book it as an expense, and the credit is lost.

**Example.** ₹25,00,000 remitted for US shares in tax year 2026-27, with no other
LRS use. TCS = 20% × (25,00,000 − 10,00,000) = **₹3,00,000**, all of it creditable.
The share cost is what was bought in USD.

**Detector.** Grep the cost-basis builder for `tcs`: any arithmetic on it there is
a defect. The TCS total should appear only in the tax-credit rows.

## 3. Foreign shares are not listed equity in India

**Rule.** Under §2(101)(b)(i), "listed" means listed on a **recognised stock
exchange in India**, so a NASDAQ or NYSE share counts as unlisted.
- It is long term only when held **more than 24 months**. A share held for 24
  months or less is short term (§2(101)(a) [§2(42A)]).
- LTCG is taxed at **12.5% without indexation** (§197(1)(b) [§112]). STCG is taxed
  at slab rates. These are the rates after 23 Jul 2024; the rate owner is
  [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).
- §196 and §198 [§111A, §112A] do **not** apply, because they need an STT-paid
  share listed in India. So there is no 20% STCG rate, no ₹1.25 lakh exemption and
  no 31-Jan-2018 grandfathering. US-listed ETFs and fractional shares are the same.

**Why.** Most code defaults to "equity, 12 months, 12.5%, ₹1.25L exempt". On a
foreign share held 13 to 24 months, that turns slab-rate tax into zero.

**Example.** 10 shares bought at $100 on 15 Jan 2024 and sold at $180 on
20 Jul 2025, held 18 months. Assume rates of ₹83.00 at cost and ₹85.50 at sale
(illustrative, not SBI rates). Cost ₹83,000, sale ₹1,53,900, gain **₹70,900 STCG at
slab**. At 30% plus 4% cess the tax is ₹22,121. The listed-equity path calls it
LTCG inside the exemption and gives ₹0.

**Detector.** The 12-or-24-month predicate must key on "listed on an Indian
exchange", for example an `IN` ISIN plus an NSE or BSE symbol. It must never key on
"equity", and it must fail closed to 24. Test at exactly 24 months and 24 months
plus one day, counting calendar months, not 730 days.

## 4. Currency conversion: SBI TT buying rate, month before

**Rule.** Rule 206 [Rule 115] converts foreign-currency income at the **SBI
telegraphic transfer buying rate** (TTBR, defined in Rule 207(3)(b)) on a
specified date:

| Income | Specified date |
|---|---|
| Capital gains | Last day of the month **before** the month of transfer (Rule 206 Table Sl. 6) |
| Dividends | Last day of the month before the month the dividend is declared, distributed or paid (Sl. 5) |
| Salary | Last day of the month before the month salary is due or paid (Sl. 1) |
| Foreign tax, for credit | Last day of the month before the month the tax was paid or deducted (Rule 76(7)(b)) |

So a sale on 10 Apr 2026 uses the TTBR for **31 Mar 2026**. Never use the
10 April rate or an RBI reference rate.

**The cost side is unsettled.** The capital-gains row names only the month of
transfer. One reading converts the USD gain at that single rate. The other
converts cost at the month-end before purchase and the sale at the month-end
before sale. Neither the Rule nor any CBDT text found here decides between them.
Make the reading an explicit, documented setting, apply it to every lot, and never
mix the two in one return.

**Rule 115A does not apply.** §72(6) and Rule 52 [§48 first proviso, Rule 115A]
cover only **non-residents** selling shares of an **Indian** company.

**Why.** Trade-date spot, today's rate and a hard-coded `USD_INR` are each wrong.

**Detector.** Grep `usdInr|USD_INR|fx_rate|exchangeRate`. All conversion must go
through one function of (income type, event date) that returns the prior
month-end TTBR from a dated, sourced table and raises if the rate is missing.

## 5. RSU, ESPP and ESOP

**Rule.** Shares from an employer plan are a salary **perquisite** on allotment.
- The perquisite is the FMV on the exercise or allotment date, less the amount you
  paid (§17(1)(d), §17(4)(h) [§17(2)(vi)]). For an RSU you pay nothing, so the
  whole FMV at vest is salary.
- The **cost of acquisition is the FMV taken for the perquisite** (§73(1) Table
  Sl. 4 [§49(2AA)]). The holding period runs from the **date of allotment or
  transfer** (§2(101)(c)(C)(V)), not from the grant date.
- **ESPP:** the discount is the perquisite. With FMV $100 and purchase price $85,
  the $15 discount is salary and the cost is **$100**, not $85.
- **FMV for a share not listed in India** is a merchant banker's value under
  Rule 15(6)(d) [Rule 3(8)(iii)]. A US exchange is not a "recognised stock
  exchange" (§2(92)). Take the **INR perquisite value from Form 16 or the
  payslip** as the source of truth. Never recompute it.
- **Indian-listed employer vs foreign parent.** Shares of an NSE- or BSE-listed
  employer sold there with STT follow
  [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md). Shares of a
  foreign parent follow section 3 and belong in Schedule FA.

**Example.** 100 RSUs vest on 10 Jun 2025 at $150. Form 16 shows a perquisite of
₹12,78,000, so the cost is ₹12,780 per share. A sale on 5 Mar 2026 is short term.
The gain is the sale value less ₹12,780 per share, not the whole proceeds.

**Why.** A zero cost, or the ESPP price used as cost, taxes salary income a second
time as capital gain. Counting from the grant date makes a lot long term too early.

**Detector.** Fixture: an RSU lot sold at its vest FMV must show a gain of about
zero, apart from currency movement. A sell-to-cover sale at vest must appear as its
own short-term row.

## 6. US dividends: treaty rate and foreign tax credit

**Rule.**
- The US withholds **30%** on a non-resident alien's dividends, or the treaty rate
  with a **W-8BEN** on file
  ([IRS](https://www.irs.gov/individuals/international-taxpayers/federal-income-tax-withholding-and-reporting-on-other-kinds-of-us-source-income-paid-to-nonresident-aliens)).
  For an individual, India–US DTAA Article 10(2)(b) caps it at **25%**; the 15%
  rate needs a company holding 10% or more of the voting stock
  ([treaty](https://www.irs.gov/pub/irs-trty/india.pdf)).
- File a **W-8BEN** with the broker before the dividend is paid, so the 25% rate
  is withheld at source instead of 30%.
- In India the dividend is slab-taxed as "Other sources" (Schedule OS), and the
  same rupee amount goes in Schedule FSI. The credit is the
  **lower of** the foreign tax and the Indian tax on that income. Foreign tax above
  the treaty rate **is ignored** (Rule 76(7)(a)), so recover any excess from the
  IRS instead.
- File the FTC statement (Form 67, or Form No. 44 from tax year 2026-27) before
  claiming the credit. For the deadline and the FSI/TR mechanics, see
  [itr-filing-schedules](../itr-filing-schedules/SKILL.md) section 5.
- The same IRS page says a non-resident alien's capital gains are "not usually
  taxable". A US sale usually leaves no foreign tax to credit.

**Example.** A $1,000 dividend at an illustrative ₹85 is ₹85,000. With 25%
withheld ($250 = ₹21,250) and Indian tax of ₹26,520 (30% + cess), the credit is
₹21,250 and ₹5,270 is payable. Without a W-8BEN, $300 is withheld, but the credit
stays ₹21,250.

**Detector.** Credit = min(withheld, treaty-rate tax, Indian tax). A fixture with
30% withholding must still cap the credit at 25%.

## 7. Schedule FA: calendar year, peak and closing value

**Rule.**
- An ROR reports every foreign asset held **at any time in the calendar year
  ending 31 December**, not the April–March year. For AY 2026-27 that is the year
  ending 31 Dec 2025
  ([ITR-2](https://www.incometaxindia.gov.in/documents/d/guest/itr-2-2026-eng-pdf)).
- Table A3 (foreign equity) asks for the acquisition date and initial value, the
  **peak value during the period** and the **closing value**. It also asks for the
  gross amount paid or credited and the gross sale proceeds. Table A2 holds the
  broker or custodial account. Peak needs daily or per-transaction history.
- Converting closing value at the 31 Dec TTBR and peak at the peak-date TTBR is
  secondary-source practice, unverified; check the ITR-2 instructions.
- **Penalty.** Black Money Act §43: ₹10 lakh for an undisclosed or wrongly
  disclosed foreign asset (unverified at primary source; check
  [§43](https://www.incometaxindia.gov.in/w/section-43-114)). Finance (No. 2) Act
  2024 §156 switched off §42/§43 where assets other than immovable property total
  **≤ ₹20 lakh**, from 1 Oct 2024
  ([Gazette](https://egazette.gov.in/WriteReadData/2024/255676.pdf)). Finance Act
  2026 §160 extends that carve-out to prosecution (§49, §50).
- That relief removes the **penalty, not the duty to report**: the form has no de
  minimis. Finance Act 2026 Chapter IV also creates a Foreign Assets of Small
  Taxpayers Disclosure Scheme, 2026, starting on a notified date; check its status.

**Why.** If FA is built from the FY capital-gains ledger, it misses calendar-year
holdings. That is the incomplete disclosure the penalty is aimed at.

**Detector.** Build FA from holdings history filtered to 1 Jan–31 Dec. Fixture for
the CY 2025 FA: a lot sold in Feb 2025 is in FA, though its gain falls in FY
2024-25. A lot bought in Feb 2026 is not, though it falls in FY 2025-26. The TTI
foreign-asset question must read Yes whenever FA has a row.

## 8. US estate-tax exposure (risk note)

For a non-resident non-citizen, US-company shares are US-situated property,
wherever they are held. Form 706-NA is due if US-situated assets exceed **$60,000**
at death
([IRS](https://www.irs.gov/individuals/international-taxpayers/some-nonresidents-with-us-assets-must-file-estate-tax-returns)).
India has no estate-tax treaty with the US
([IRS list](https://www.irs.gov/businesses/small-businesses-self-employed/estate-gift-tax-treaties-international)).
Flag the exposure when US holdings pass $60,000. Ways to reduce it are out of scope.

## Verifying an implementation

- **Holding period:** foreign shares held 13, 24 and 25 months classify as short,
  short and long. No foreign row touches the §112A exemption pool.
- **Exchange rate:** a sale on the 1st uses the previous month-end TTBR; a missing
  rate raises an error.
- **TCS:** ₹25 lakh for investment gives ₹3 lakh of credit and no cost change.
- **RSU and ESPP:** a sale at vest FMV gains about zero; ESPP cost is the FMV.
- **Credit:** 30% withholding without a W-8BEN is capped at 25% and at Indian tax.
- **FA:** calendar-year window, peak ≥ closing, and no rows for RNOR or NR.
- **Year switch:** FY 2025-26 emits 1961 numbers and Form 67. Tax year 2026-27
  emits 2025 numbers and Form No. 44.

## Scope

Informational only; **not tax advice**. Covers resident individuals holding foreign
listed shares or employer-plan shares.

**Non-residents are a different regime and are not covered.** An NRI is taxed only
on income that is Indian-source or received in India (§5(2)), so foreign shares
generally sit outside Indian tax and Schedule FA. TDS on payments to them is the
payer's duty under §393(2) Table Sl. 17 [§195]. Treaty relief needs a tax residency
certificate (§159(8) [§90(4)]). Also out of scope: US filing (1040-NR), foreign
mutual funds, valuing unlisted foreign equity, and gifts or inheritance of foreign
shares.
