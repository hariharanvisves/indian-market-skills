# Unverified claims

These claims appear in the skills, or were left out of them, because no primary
source could be reached on the review date. Each one is open for a contributor
to confirm or correct with a primary source. See the sourcing rule in
[CONTRIBUTING.md](../CONTRIBUTING.md).

Last reviewed: 2026-11-11.

## Tax

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `indian-capital-gains-tax` | "Month" means a British-calendar month (General Clauses Act §3(35)) | Confirmed only through secondary search results | General Clauses Act 1897 text (indiacode.nic.in) |
| `indian-capital-gains-tax` | Whether the 2024-07-23 exemption change applies to the whole of FY 2024-25 | Unresolved | Finance (No. 2) Act 2024 text |
| `indian-capital-gains-tax` | 2025 Act equivalent of 1961 §115BBH (§55(2)(ac) is §90(7), per `corporate-action-taxation`) | Not located | Income-tax Act 2025 gazette |
| `indian-capital-gains-tax` | Wording of the 15% surcharge cap | Not re-verified | Finance Act 2026, First Schedule |
| `itr-filing-schedules` | §234A interest on self-assessment tax | The statute's deduction list leaves it out, matching the skill. The Supreme Court ruling in *Prannoy Roy* may differ. | Statute + judgment text |
| `itr-filing-schedules` | FSI: Indian tax "at the marginal rate" | The rule does not say marginal or average | Rule 206 (2025 Rules) / Rule 128 |
| `itr-filing-schedules` | Form 67 / Form 44 deadline | Rule 128(9) says within 12 months of year-end. The portal page still says by the §139(1) date. | Rule 128(9); incometax.gov.in |

## Corporate actions

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `corporate-action-taxation` | Holding period of split shares runs from the original acquisition date | The statute is silent. The skill marks this as a derived reading. | CBDT clarification or case law |
| `corporate-action-taxation` | 31-Jan-2018 FMV divided by the ratio for later splits | Derived, not stated in the statute | CBDT FAQ on §112A grandfathering |
| `corporate-action-taxation` | Rate on sale of a rights entitlement (routed to slab) | Flagged in the skill | Statute / CBDT |
| `corporate-action-taxation` | Cash paid for fractional merger shares is a transfer | Derived | Statute / case law |
| `corporate-action-taxation` | Bracketed 1961 section numbers | Matched by content only. India Code and incometaxindia.gov.in were unreachable. | indiacode.nic.in |

## Foreign equity

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `foreign-equity-for-residents` | ₹10 lakh penalty under Black Money Act §43 | Primary text blocked | Black Money Act 2015 (indiacode.nic.in) |
| `foreign-equity-for-residents` | 20% LRS TCS rate under the 1961 Act for FY 2025-26 | Not confirmed from the statute | Finance Act 2025, §206C(1G) |
| `foreign-equity-for-residents` | Exchange rate for Schedule FA peak and closing values | Secondary sources only | ITR-2 instructions for the year |
| `foreign-equity-for-residents` | Whether cost is converted at the purchase month under Rule 206 | Rule 206 names only the sale month. The skill makes this an explicit setting. | Rule 206 (2026 Rules); CBDT clarification |
| `foreign-equity-for-residents` | Whether the 2026 small-taxpayer foreign-asset disclosure scheme is notified | Unknown | CBDT notifications |

## F&O

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `fno-tax-and-charges` | Base for the SEBI fee and stamp duty on options (premium) | Brokers bill both on premium. Not checked against SEBI's fee regulation or the Indian Stamp Act. | SEBI (Stock Brokers) fee regulation; Indian Stamp Act schedule |
| `fno-tax-and-charges` | ICAI Guidance Note para 5.11(b)(ii) on options premium in turnover | Ambiguous. The skill shows both readings and makes the choice an explicit setting. | ICAI Guidance Note on Tax Audit (icai.org copy) |
| `fno-tax-and-charges` | Whether ICAI turnover also sets the turnover for §58 (old §44AD) presumptive tax | Unresolved | Statute + CBDT clarification |
| `fno-tax-and-charges` | 1961 section numbers §36(1)(xv), §37(1), §70, §71 | Not re-read against the 1961 text | Income-tax Act 1961 (indiacode.nic.in) |

## Charges and valuation

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `indian-equity-charges` | Effective date 2026-03-01 for NSE cash transaction charge 0.00307% (circular NSE/FA/73061) | The rate is confirmed by two brokers' schedules. The circular PDF was not reachable. | nseindia.com circulars |
| `indian-equity-charges` | Whether NSE's 0.00307% includes the IPFT charge (₹0.01/crore), and whether IPFT enters the GST base | Unknown | NSE circular; zerodha.com/charges footnotes |
| `indian-equity-charges` | Dates of the F&O STT revisions (2024 and Budget 2026) | Not independently sourced | Finance (No. 2) Act 2024, Finance Act 2026 |
| `indian-equity-valuation` | MAT at 14% from tax year 2026-27, and MAT as a final tax under the old regime | Secondary sources only. The Finance Bill 2026 memo returned HTTP 403. | Finance Act 2026 text |
| `indian-equity-valuation` | Income-tax Act 2025 section numbers §200, §201, §206 | Consistent with commentary. The enacted text was not checked. | Income-tax Act 2025 (indiacode.nic.in) |
| `indian-equity-valuation` | Base for the 25% cap on MAT credit (tax liability vs tax on total income) | Sources differ | Statute text |
| `indian-equity-valuation` | FBIL publishes benchmarks at about 19:00 IST | Newsletter PDF unreadable | fbil.org.in |
| `indian-equity-valuation` | Reference year for the ₹400 crore turnover test for non-opting companies | Unknown | Finance Act text |

## Broker APIs

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `kite-connect-safety` | Orders above 10 per second need a registered strategy, and sharing a static IP is limited to family | Forum posts only. Not added to the skill. | SEBI retail-algo circular (4 Feb 2025); exchange implementation standards |
| `kite-connect-safety` | Hosted Kite MCP OAuth behaviour and free-tier capabilities | Marked "verify" in the skill | kite.trade docs |
| `indian-broker-api-safety` | Maximum length of ICICI Breeze `user_remark`, and what the `Ordered` and `Freezed` statuses mean | Not documented. The adapter maps both statuses to UNKNOWN. | api.icicidirect.com docs |
| `indian-broker-api-safety` | Fyers refresh-token lifetime | Not documented | fyers.in/api-docs |
| `indian-broker-api-safety` | Sandboxes for Kite, Angel One, Breeze and Fyers | None found in their docs | Each broker's developer docs |

## Backtests and options

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `backtest-engine-correctness` | F&O ban exit threshold of 80% of MWPL | Not in the 29 May 2025 SEBI circular. Flagged in the skill. | NSE F&O ban FAQ / circular |
| `backtest-engine-correctness` | T+0 settlement dates and durations of market-wide halts | Cited from 2026-10-04, not re-fetched | SEBI / NSE circulars |
| `backtest-engine-correctness` | CAS applicability and ±3% band after the Oct 2026 amendment | The amended text omits these paragraphs. The skill treats them as unchanged. | SEBI circular 15 Oct 2026, full text |
| `nse-options-mechanics` | Weekly expiry weekday (Tuesday / Thursday) by exchange and date | Not confirmed from a primary source | NSE / BSE circulars |
| `nse-options-mechanics` | Derivative settlement rule before 3 Aug 2026 | Not re-verified | NSE Clearing circulars |

## Data and statements

| Skill | Claim | Status | Primary source to check |
|---|---|---|---|
| `indian-capital-gains-tax` | Bonus shares start a new holding period at the bonus allotment date (1961 Act §2(42A) Expl. 1) and how the 2025 Act carries this | Secondary sources only. The claim was removed from `indian-market-data-pitfalls`. | Income-tax Act 2025 text |
| `nse-bhavcopy-corporate-actions` | `BL` / `IL` series meaning "same security under trading restriction" (BL is the block-deal series) | Unconfirmed | NSE series code list |
| `nse-bhavcopy-corporate-actions` | NSE circular 62424 as the UDiFF switch notice | Confirmed only by a search snippet. The behaviour is confirmed: 5 Jul 2024 legacy file served, 8 Jul 2024 returns 404. | nseindia.com all-reports notice |
| `mf-scheme-matching` | IDCW rename effective 1 Apr 2021 | Search snippet of a SEBI FAQ | SEBI circular SEBI/HO/IMD/DF3/CIR/P/2020/194 |
| `indian-broker-statement-formats` | Zerodha `-E` suffix, Console sheet names, Groww has no SIP column, CAMS JSON `dtTrxnResult`, CAMS and INDmoney `.xls` being OLE2, ITD `aced0005` wrapper, AIS categories | Observed on real files. These are not publicly documented. | A current statement file from each source |
