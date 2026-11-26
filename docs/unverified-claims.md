# Unverified claims

These claims appear in the skills, or were left out of them, because no primary
source could be reached on the review date. Each one is open for a contributor
to confirm or correct with a primary source. See the sourcing rule in
[CONTRIBUTING.md](../CONTRIBUTING.md).

Last reviewed: 2026-11-26.

Each row has a GitHub issue labelled
[`unverified-claim`](https://github.com/hariharanvisves/indian-market-skills/issues?q=label%3Aunverified-claim).
When you resolve one, remove its row here and close the issue.

## Tax

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `indian-capital-gains-tax` | "Month" means a British-calendar month (General Clauses Act §3(35)) | Confirmed only through secondary search results | General Clauses Act 1897 text (indiacode.nic.in) |
| `itr-filing-schedules` | Whether CBDT Circular 2/2015 (no §234A interest on self-assessment tax paid before the due date) carries over to §423 of the 2025 Act | §423(4)(d) does not list self-assessment tax; the circular was read on a mirror (itatonline); no 2025-Act FAQ read | CBDT FAQ on §§423-426 |
| `itr-filing-schedules` | How Indian tax on treaty-country foreign income is computed for the credit (Rule 76(7)(a) says "tax payable under the Act on such income" without a method) | No CBDT method found; §160(3)(c) average rate applies only to non-treaty countries | CBDT FAQ or ITR-2 instructions on Schedule FSI |
| `nps-taxation` | Schedule II Sl. 6(b) (and Sl. 15(b) for UPS) "the said payment does not exceed 60% of the total amount payable": a cap (only the excess taxable) or a condition (whole lump sum taxable under §124(6)) | The 1961 "to the extent" wording is absent while Sl. 8(d) keeps it; the skill defaults to the whole lump sum taxable and shows excess-only as the alternative | Schedule II Sl. 6 and Sl. 15 and §124(6) as enacted; any CBDT notification or circular on the PFRDA 2025 amendment |
| `nps-taxation` | Who qualifies for the Schedule III Sl. 4 partial-withdrawal exclusion | Column C names "any employee" and a parent or guardian of a minor; the skill treats a non-employee subscriber as not exempt unless confirmed | Schedule III Sl. 4 as enacted; CBDT clarification |
| `nps-taxation` | How §124(6) splits a corpus that mixes deducted and non-deducted contributions | The Act does not say; the skill treats the lump sum (or excess) and the annuity as taxable | §124(6) as enacted; CBDT clarification |
| `nps-taxation` | Tax on systematic lump-sum withdrawal and unit-redemption instalments and on Tier II withdrawal gains; the new-regime 14% employer limit applying from FY 2024-25 | Act text silent on the first two; the FY 2024-25 date is from the 1961 position, not read | CBDT notification or circular; Finance (No. 2) Act 2024 text |
| `nps-taxation` | NPS Vatsalya is the pension scheme notified for §124(4) and Schedule III Sl. 4(ii) | The Act never names Vatsalya; notification not read | Central Government notification under §124; PFRDA Vatsalya scheme documents |
| `nps-taxation` | 1961 equivalents: 80CCD(1), (1B), (2); 10(12A), 10(12B); 17(1)(viii); 17(2)(vii), (viia); 36(1)(iva); 115BAC | Mapped from the 1961 Act, not re-read | Income-tax Act 1961 as amended to 31 Mar 2026 (indiacode.nic.in) |
| `nps-taxation` | A public-sector company, bank or statutory body is an "other employer" (10% old-regime limit) | Reading of §124(1)(a), which names only the Central or a State Government | CBDT circular; Form 16 and ITR instructions |
| `non-equity-capital-gains` | Cost Inflation Index values (2001-02 = 100 through 2026-27) | Not carried in the skill; incometaxindia.gov.in returned HTTP 403 to automated fetch, so no notification was read | CBDT CII notifications under §72(8)(a) (and old §48 Explanation) |
| `non-equity-capital-gains` | Rate and the 20%-with-indexation option for land or building transfers from 23 Jul 2024 to 31 Mar 2026 under 1961 §112 | Not restated; the skill states §197(3) of the 2025 Act only and its sketch refuses transfers before 1 Apr 2026 | Finance (No. 2) Act 2024 text |
| `non-equity-capital-gains` | Indexed-option edge cases: an indexed result below zero gives nil tax; whether the §82/§85/§86 exemption is measured on the unindexed or the indexed gain | §197(3) is silent; the sketch returns nil for a negative indexed result | §197(3) with a CBDT clarification or the Finance (No. 2) Act 2024 memorandum |
| `non-equity-capital-gains` | Indexation base year and the "acquired before 23 Jul 2024" test for gifted or inherited property | §72(8)(b) "first year in which the asset was held by the assessee" and §197(3) "acquired before"; the skill says to flag, not pick | Statute plus CBDT or judicial guidance |
| `non-equity-capital-gains` | Capital Gains Accounts Scheme mechanics and the notified list of §85 (old 54EC) bonds | Act text read (§82(2), §85(6), §263(1)(c)); scheme and bond notifications not fetched | CBDT scheme notification; notified bond list |
| `nps-taxation` | The new-regime gate is still numbered §202(2)(a)(xii) after Finance Act 2026 s.56 omitted sub-clause (iii) | s.56 gives no renumbering instruction; the consolidated §202 was not read | Consolidated Income-tax Act 2025 text (incometaxindia.gov.in) |

## Corporate actions

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `corporate-action-taxation` | Holding period of split shares runs from the original acquisition date | §2(101)(c)(A)–(C) of Act 30 of 2025, Rule 6 of the Income-tax Rules 2026 and 1961 §2(42A) Expl. 1 list no split or consolidation entry; the skill's reading is derived | CBDT clarification or case law (none found) |
| `corporate-action-taxation` | 31-Jan-2018 FMV divided by the ratio for later splits | Derived, not stated in the statute | CBDT FAQ on §112A grandfathering |
| `corporate-action-taxation` | Whether a rights-entitlement sale is chargeable to STT and so outside §196 | §196 needs an equity share or unit and an STT-chargeable sale; an RE is neither share nor unit on its face; slab is the textual default; no CBDT clarification found | Statute / CBDT |
| `corporate-action-taxation` | Cash paid for fractional merger shares is a transfer | §70(1)(f) [§47(vii)] exempts only transfers for allotted shares, so cash for a fraction falls outside it by text; no CBDT or case-law authority found | Statute / case law |
| `corporate-action-taxation` | A listed buyback announced on or before 5 Jul 2019 is taxed to the holder as capital gains under §46A, with no §10(34A) exemption | Inferred from the §115QA proviso and the 2019 omission of "(not being listed…)" from §10(34A); no CBDT statement found | CBDT circular; Finance (No. 2) Act 2019 as enacted |

## Foreign equity

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `foreign-equity-for-residents` | Whether cost is converted at the purchase month under Rule 206 | Rule 206 names only the sale month. The skill makes this an explicit setting. | Rule 206 (2026 Rules); CBDT clarification Rule 206: https://www.incometaxindia.gov.in/w/rule-206-1 |
| `foreign-equity-for-residents` | Fallback rate when the Rule 206 specified date has no SBI TTBR | Rule 206 is silent; Rule 207(1) allows "the last such published rate" only for TDS under Rule 207(2), so applying it to Rule 206 is by analogy | Rule 206 / Rule 207 (Income-tax Rules 2026); CBDT clarification |
| `foreign-equity-for-residents` | The ₹10 lakh LRS TCS threshold is aggregated by PAN across all authorised dealers | §206C(1G) and Act 2025 §394 Table Sl. 7 aggregate the amounts remitted "by a buyer in a financial year"; neither names PAN or banks | CBDT Circular 10/2023 or an AD/CBDT FAQ |

## F&O

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `fno-tax-and-charges` | Which reading of ICAI Guidance Note para 5.11(b)(ii) applies (net profit not separately included, or premium replacing the difference) | Paragraph text verified in the Revised 2026 note; the ambiguity is in the note itself | ICAI clarification |
| `fno-tax-and-charges` | Whether ICAI turnover also sets the turnover for §58 (old §44AD) presumptive tax | ICAI GN 5.11 limits its method to §44AB; §58(2) does not define F&O turnover; no CBDT clarification found | Statute + CBDT clarification |
| `fno-tax-and-charges` | 1961 section number §70 (same-head set-off) | §36(1)(xv), §37(1) and §71 confirmed from the CBDT ITR-3 form and instructions; §70 not found in a portal document | Income-tax Act 1961 text |

## Charges and valuation

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `indian-equity-charges` | Whether the IPFT charge (₹0.01/crore, included in NSE's 0.00307% per NSE/FA/73061) enters the GST base | Unknown | NSE circular; zerodha.com/charges footnotes |

## Broker APIs

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `kite-connect-safety` | Hosted Kite MCP free-tier capabilities | Read-only and no order tools are confirmed (mcp.kite.trade page, kite-mcp-server README). Free-tier data capabilities are not. | kite.trade docs |
| `indian-broker-api-safety` | Maximum length of ICICI Breeze `user_remark`, and what the `Ordered` and `Freezed` statuses mean | Not documented. The adapter maps both statuses to UNKNOWN. | api.icicidirect.com docs |
| `indian-broker-api-safety` | Fyers refresh-token lifetime | Not documented | fyers.in/api-docs |
| `indian-broker-api-safety` | Sandboxes for Kite, Angel One, Breeze and Fyers | None found in their docs | Each broker's developer docs |
| `indian-broker-api-safety` | Dhan has no documented logout or token-revocation call | Dhan's docs list generate, renew and a 24-hour expiry only | docs.dhanhq.co/api/v2/authentication |
| `indian-broker-api-safety` | What the SEBI/NSE kill switch blocks, and whether exits still go through | Not read; the entry-limit rule is stated as a client engineering rule | SEBI circular 4 Feb 2025 ¶5.IV(a)(iii) and NSE/INVG/67858 §J.3, read in full |

## Backtests and options

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `nse-options-mechanics` | Window of the stock-derivative VWAP before 3 Aug 2026 | SEBI Master Circular Ch. 5 ¶3.1.2.7 says only "VWAP from the cash segment across all exchanges"; the window is not stated | NSE Clearing circular or bye-laws on the stock-derivative final settlement price |
| `nse-trading-calendar` | NSE regular-session timings (pre-open, normal market, closing session) | Not read; the session-hours rule says to cite them only from NSE | NSE trading-timings page and the current NSE market-timings circular |
| `nse-trading-calendar` | Broker MIS intraday square-off times | Left out on purpose; brokers publish their own | Each broker's published square-off page (Zerodha, Upstox, Dhan, Angel One) |
| `backtest-engine-correctness` | Stop order types (SL / SL-M) NSE and brokers accept for algo orders, and how a stop-market gap fills | Not read; the gap-through-stop rule is engineering only | NSE order-type and algo FAQ, and each broker's order-type docs |

## Data and statements

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `nse-bhavcopy-corporate-actions` | `www.nseindia.com` page and `/api/...` paths 301-redirect to `www.nseindia.in`; `.com` homepage 403 to scripted clients | Observed 2026-11-26 only. No NSE announcement found. `nsearchives.nseindia.com` not redirected. | NSE notice or circular on the host change |
| `nse-bhavcopy-corporate-actions` | Yahoo chart API `meta.chartPreviousClose` is not the previous session close for ranges longer than 1d | Observed 2026-11-26 on RELIANCE.NS only. The API is unofficial and undocumented. | None exists; re-observe before relying on it |
| `nse-bhavcopy-corporate-actions` | Whether any `IL` series rows appear after 1 Jul 2018 | NSE/CMTR/37880 discontinued the series; NSE's inter-institutional page still mentions IL, undated | NSE legend of series page (renders only in a browser) |
| `indian-broker-statement-formats` | Zerodha `-E` suffix, Console sheet names, Groww has no SIP column, CAMS JSON `dtTrxnResult`, CAMS and INDmoney `.xls` being OLE2, ITD `aced0005` wrapper, AIS categories | Observed on real files. These are not publicly documented. | A current statement file from each source |
