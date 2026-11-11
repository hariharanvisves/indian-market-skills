---
name: indian-equity-valuation
description: India-specific adjustments for DCF and comparable-company valuation of listed Indian equities — corporate tax regime inputs, risk-free rate source, beta and ERP currency consistency, Ind AS 116 EBITDA comparability, consolidated vs standalone, reporting lag and point-in-time data, promoter pledge, dividend taxation, and which sectors need a different model. Use when building or reviewing a DCF, WACC or cost-of-equity input, a peer-multiple (EV/EBITDA, P/E) table, a dividend discount model or a valuation screen for NSE/BSE companies.
license: MIT
compatibility: Applies to NSE/BSE-listed non-financial companies. Method-agnostic; covers only the India deltas to standard DCF and comps practice.
metadata:
  author: hariharanvisves
  version: "1.1"
  verified: "2026-11-11"
  jurisdiction: India
---

# Indian Equity Valuation — India Deltas

This is not a full DCF or comps method. It lists what changes when the subject
is a listed Indian company. Facts were checked on 2026-10-04 against the cited
primary source; where a figure was not confirmed it says "verify".

Each item: rule, why, detector.

## 1. Tax-rate input is a regime choice, not one number

**Rule.** Pick the company's actual regime and state it. Section numbers below
follow the Income-tax Act, 2025 (in force from 1 Apr 2026); the 1961 Act numbers
are in brackets. CBDT ITR JSON field names may still carry 1961 numbering —
verify per schema.

| Regime | Rate | Notes (source: Finance Bill 2026 memo, indiabudget.gov.in) |
|---|---|---|
| §200 (old 115BAA) | 22% + 10% surcharge + 4% cess = **25.168%** | Opt-in; forgoes most deductions and incentives |
| §201 (old 115BAB) | 15% base, **17.16%** effective | **Closed to new units** — manufacturing had to commence by 31-03-2024 |
| Non-opting domestic company | 25% if turnover in the reference year is ≤ ₹400 cr, else 30%; surcharge 7% (>₹1 cr–10 cr), 12% (>₹10 cr); cess 4% | Reference year was 2024-25 in the 2026 source read; verify for the year you model |
| MAT (§206, old 115JB) | **14%** from tax year 2026-27 (was 15%) | Under the old regime MAT is a final tax with no new credit; credit set-off applies only under the new regime, capped at 25% of liability |

**Why.** A flat 25% or 30% misstates NOPAT by several points, and the opt-in
regime changes whether past MAT credit is usable at all.

**Detector.** The model has an explicit `taxRegime` input; terminal-year tax is
the statutory rate for that regime, not the historical effective rate (which is
distorted by deferred tax and one-offs). Grep for a bare `0.25` / `0.30` tax
constant.

## 2. Risk-free rate: a dated FBIL figure, never memory

**Rule.** Use the 10-year G-Sec yield from the FBIL benchmark (FBIL, not RBI or
CCIL), published on Mumbai business days around 19:00 IST. Record the **as-of
date and the benchmark security** — the benchmark rotates (6.48% GS 2035 from
6 Oct 2025 per FBIL's methodology notice). Never type a risk-free number from
recall.

**Why.** A 50 bp error in rf moves a long-duration valuation by double-digit
percent, and a stale number is invisible in the output.

**Detector.** The rf input carries `{value, asOfDate, source}`; a valuation
older than a few days vs its rf date is flagged.

## 3. Beta and equity risk premium

**Rule.**
- Beta against a stated Indian index (Nifty 50 or Nifty 500; prefer the
  **total-return** series) with a stated window and frequency (e.g. 5y weekly).
  Adjust (Blume or sector re-levered) only if you say so.
- ERP is a judgement. State its source and currency.
- **Currency consistency:** an INR rf plus an INR ERP, or a USD rf plus a USD
  ERP and then an inflation-differential adjustment to convert. Never add a USD
  ERP to an INR rf without that adjustment, and never discount INR cash flows at
  a USD cost of capital.

**Why.** Mixed-currency discount rates are the most common silent India DCF
error; the output looks reasonable and is wrong by the inflation differential.

**Detector.** Every rate input is tagged with a currency; a validator rejects
cash flows and discount rate in different currencies.

## 4. Terminal growth

**Rule.** Terminal growth is capped at the long-run **nominal** growth you
believe for the Indian economy — a judgement, so state it and its basis; do not
present it as a statistic. It must also sit below the discount rate with a
comfortable spread, and the terminal reinvestment rate must be consistent with
it (`g = reinvestment × ROIC`).

**Why.** Terminal value is often most of EV, and explodes as g nears the
discount rate.

**Detector.** Terminal value share of EV is reported; above ~75% is flagged for
sensitivity. Run a table of ±100 bp on g and on WACC.

## 5. Ind AS and the 116 lease effect

**Rule.** Ind AS applies to **all** listed non-SME companies (the ₹250 cr
net-worth test is for unlisted companies). Banks, NBFCs and insurers follow
separate roadmaps. Ind AS 116 applies to periods from 1 Apr 2019: lessee
depreciation and interest replace rent, so **EBITDA rises** versus pre-2019 (an
inference from the standard's mechanics).

For EV/EBITDA, either use **post-116 EBITDA with lease liabilities in net debt
for every company and period**, or strip lease effects consistently. Never mix
pre- and post-2019 periods, or lease-heavy and lease-light peers on different
bases.

**Detector.** Each multiple row states its lease treatment; a time series of
EV/EBITDA crossing FY2019-20 is broken at the boundary or restated.

## 6. Consolidated vs standalone

**Rule.** Value on **consolidated** statements. Use standalone only for a pure
holding-company or sum-of-the-parts analysis, and then apply an explicit
holding-company discount to listed-subsidiary stakes. Minority interest and
associates must be in the EV-to-equity bridge.

**Why.** Standalone omits subsidiaries, so mixed bases mismatch EV and EBITDA.

**Detector.** Numerator (market cap + net debt + minorities) and denominator
(EBITDA) come from the same basis; mixing standalone EBITDA with consolidated
net debt is the common slip.

## 7. Fiscal year, reporting lag, point-in-time

**Rule.** FY ends **31 March**. LODR Reg 33(3)(a) allows **45 days** after
quarter end for quarterly results and Reg 33(3)(d) **60 days** for annual
(SEBI LODR, 2015). So Q4 data can be unavailable until late May; label periods
FY, not calendar year.

Build TTM from quarterly results: `TTM = last FY + current YTD − prior-year YTD`.
In a **backtest**, a figure is usable only from its **disclosure date**, not its
period end; and restated numbers must not overwrite what was knowable then.

**Why.** Joining on period end trades on results not yet published: look-ahead.

**Detector.** Each fundamental row carries `periodEnd` and `disclosedAt`; a
backtest join uses `disclosedAt <= decisionDate`. Test: a quarter ending 31 Dec
must not be visible on 15 Jan.

## 8. Promoter pledge as a risk input

**Rule.** Pledge creation, invocation and release are disclosed under SEBI SAST
Reg 31 (31(1) creation; 31(2) invocation/release) to the exchanges and the
company. Carry pledged % of promoter holding as a risk flag or cost-of-capital
adjustment you state — it is a forced-selling risk, not a cash-flow item.

**Detector.** Source the latest quarterly shareholding-pattern disclosure and
date it; do not use a pledge figure from a stale snapshot.

## 9. Dividends and the dividend discount model

**Rule.** Dividend Distribution Tax was abolished for dividends after
31-03-2020; dividends are taxed in the **shareholder's** hands. TDS applies at
10% above a **₹10,000** per-year threshold from 1 Apr 2025 (was ₹5,000), under
§393 of the 2025 Act (FB 2025 memo). A DDM for a taxable holder should discount
**post-tax** dividends at the holder's slab rate; for an institution, the
treatment differs — state which.

**Why.** The holder now pays the tax; a pre-tax DDM overstates value to them.

**Detector.** The DDM names the holder type and tax treatment; no pre-2020
"dividend after DDT" assumption survives.

## 10. Sectors that need a different model

**Rule.** Do not run an FCFF DCF or EV/EBITDA on **banks, NBFCs or insurers**.
Debt is their raw material and "free cash flow" is undefined. Use P/B vs RoE
(justified P/B = (RoE − g)/(Ke − g)), residual income, or embedded value for
insurers. A screen that mixes them with industrials is wrong by construction.

**Detector.** A sector filter excludes financials from EV-based multiples
before any statistics are computed.

## 11. Related-party transactions and governance

**Rule.** Read the related-party note. Promoter-group loans, inter-corporate
deposits, and purchases from promoter entities can shift margin and cash. Adjust
or at least flag; do not silently normalise.

**Why.** Related-party terms need not be arm's length, so margins built on them
may not persist.

**Detector.** The model lists each related-party item as adjusted or flagged;
an empty list for a group with material related-party flows is a gap.

## 12. Peer set

**Rule.** Peers are **listed Indian companies** on the same accounting basis
(Ind AS, consolidated, same lease treatment), similar business mix, size and
growth. Foreign peers need a country-risk and tax adjustment you state. Report
**median and range** with the count, and drop a peer only with a written reason.

**Why.** A mean over a few mismatched peers is one outlier's number.

**Detector.** Fewer than ~5 peers → say so; do not print a mean as if it were
a market consensus.

## 13. Output is research, not a recommendation

A valuation is an internal estimate with stated assumptions. Do not label it as
a buy/sell/target-price recommendation to others: giving investment advice or
publishing research for consideration can fall under the SEBI Investment
Advisers or Research Analysts regulations. Whether a given use is in scope is a
legal question — take counsel; this skill is not legal advice.

## Verifying an implementation

- No bare `0.25` / `0.30` tax constant; `taxRegime` is an explicit input (§1).
- rf, ERP and every cash flow carry `{value, asOfDate, source, currency}`; a
  currency mismatch is rejected (§2, §3).
- Terminal value share of EV is reported, with ±100 bp tables on g and WACC (§4).
- Each multiple states its lease treatment and statement basis (§5, §6).
- A quarter ending 31 Dec is not visible on 15 Jan in a backtest join (§7).
- Financials are excluded from EV-based multiples before statistics run (§10).

## Scope

India deltas to DCF, comps and DDM for NSE/BSE-listed companies; not a full
valuation method. Informational engineering guidance. For tax on gains see
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md); for data
hazards see [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md).
