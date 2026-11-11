---
name: fno-tax-and-charges
description: Charges and income tax on Indian equity and index futures and options (F&O) for resident individuals. Charges - STT by side and base (futures on traded price, options on premium, exercised options on intrinsic value, paid by the buyer) with the Finance Act 2026 rates from 1 April 2026, exchange transaction charge on premium, SEBI fee, buy-side stamp duty. Tax - F&O as non-speculative business income, intraday equity as speculative, ITR-3, loss set-off and 8/4-year carry-forward, ICAI turnover for tax audit, §44AB thresholds, §44AD/§58 presumptive interplay, deductible expenses, Income-tax Act 2025 section numbers. Use when building an F&O brokerage, P&L or tax calculator, computing F&O or intraday tax, turnover or audit applicability, reconciling an F&O contract note, or when code applies STCG/LTCG, §111A/§112A or a notional-value STT to derivatives.
license: MIT
compatibility: Rates verified 2026-11-11 against NSE circular 02/2026, the Finance Act 2026 and Zerodha and Upstox charge schedules; sections against the gazetted Income-tax Act 2025; turnover against the ICAI Guidance Note on Tax Audit (Revised 2026). Re-verify before use, as rates change with each Finance Act and exchange circular.
metadata:
  author: hariharanvisves
  version: "1.0"
  verified: "2026-11-11"
  jurisdiction: India
---

# F&O Tax and Charges

A generic agent makes two errors on Indian derivatives. It prices option charges
on **notional value**, and it taxes F&O profit as **capital gains**. Both are
wrong. Option charges sit on premium, and F&O is **business income**. This skill
holds both structures. Cash-segment equity lives elsewhere (see Scope).

## 1. Charges by side and base: NSE equity and index F&O

| Charge | Futures | Options | Side | Base |
|---|---|---|---|---|
| STT on sale | **0.05%** | **0.15%** | **sell only** | futures: traded price × qty; options: **premium** × qty |
| STT on exercise | — | **0.15%** | **purchaser** (the long holder) | **intrinsic value** = settlement price − strike, × qty |
| Exchange transaction charge (NSE) | 0.00183% | 0.03553% | both | futures: turnover; options: **premium** |
| SEBI fee | ₹10 per crore | ₹10 per crore | both | turnover; options: premium turnover as brokers bill it (unverified against SEBI's regulation) |
| Stamp duty | 0.002% | 0.003% | **buy only** | buy-side turnover; options: premium turnover as brokers bill it (unverified against the Stamp Act) |
| GST | 18% | 18% | both | brokerage + SEBI fee + transaction charge |

Sources: STT rates from NSE circular 02/2026 (NSE/FATAX/73524, 31 Mar 2026),
which applies Finance Act 2026 §159 amending §98 of the Finance (No. 2) Act 2004.
STT bases and payer from NSE's equity-derivatives STT page. Transaction charges
from the Zerodha and Upstox schedules, effective 1 Mar 2026. Stamp duty from NSE's
investor levies page, in force since 1 Jul 2020. For GST's base, see
[indian-equity-charges](../indian-equity-charges/SKILL.md); some brokers also
add an NSE IPFT line inside it. BSE differs: Zerodha lists ₹0 on futures and
0.0325% of premium on options.

**STT is keyed to the trade date.** Three regimes, from the NSE circulars
02/2024 (NSE/FATAX/63809) and 02/2026:

| Trade date | Futures, sale | Option, sale (premium) | Option, exercised (intrinsic) |
|---|---|---|---|
| to 2024-09-30 | 0.0125% | 0.0625% | 0.125% |
| 2024-10-01 to 2026-03-31 | 0.02% | 0.1% | 0.125% |
| from 2026-04-01 | 0.05% | 0.15% | 0.15% |

NSE transaction charges were 0.00173% (futures) and 0.03503% (options premium)
up to 2026-02-28, per Upstox's dated schedule.

## 2. What implementations get wrong on charges

**2a. Option STT is on premium, not notional.** Sell 300 units at a premium of
₹50, strike 24,000. Premium turnover is ₹15,000, so STT is **₹22.50**. Charging
STT on notional (300 × 24,000 = ₹72,00,000) gives ₹10,800, which is 480 times
too much. The same error hits the exchange charge. **Detector:** the option
charge function reads `strike` or `underlying_price`.

**2b. Exercise STT is on intrinsic value, and the buyer pays it.** A long call,
strike 24,000, settles at 24,100 on 300 units. Intrinsic value is
100 × 300 = ₹30,000, so STT is **₹45**, charged to the **long** side. On
settlement price × qty you get ₹10,845. An OTM option expires with no exercise
STT. The short side pays no exercise STT. NSE's procedural note says "levied on
settlement price". Its definition says intrinsic value, so use the definition
and reconcile to a contract note.

**2c. Exercise and sale were priced differently until 2026-03-31.** Before
2024-10-01, letting an ITM option be exercised (0.125% of intrinsic) cost twice
the STT of selling it at the same value (0.0625% of premium). Since 2026-04-01
both rates are 0.15%, so an "exit before expiry" rule tuned to the old gap needs
re-checking. Key every rate by trade date: the futures rate rose 4×, from
0.0125% to 0.05%, across the two changes.

**2d. Futures are asymmetric too.** STT is sell only and stamp duty is buy only.
A symmetric per-leg cost passes a round-trip test and fails each leg.

```
turnover  = qty * (premium if option else price)
stt       = is_sell ? turnover * STT_SALE(kind, trade_date) : 0
txn       = turnover * TXN(exchange, kind, trade_date)
sebi      = turnover * 0.000001                  # Rs 10 per crore
stamp     = is_buy ? turnover * STAMP(kind) : 0
gst       = 0.18 * (brokerage + sebi + txn)
stt_exer  = long and itm_at_expiry ? qty * (settle - strike if call else strike - settle) * STT_EXERCISE(expiry_date) : 0
```

STT rounding and the GST base are cash-segment rules, owned by
[indian-equity-charges](../indian-equity-charges/SKILL.md).

## 3. Section numbers and years

The Income-tax Act 2025 is in force from 1 April 2026 (§1(3)). FY 2025-26
(AY 2026-27) and earlier fall under the 1961 Act; tax year 2026-27 onward under
the 2025 Act, the same date the STT rise took effect. 2025 numbers were matched
by content against the gazetted text. ITR JSON field names may keep 1961 numbers.

| Rule | 1961 Act | 2025 Act |
|---|---|---|
| Business income head | §28 | §26 |
| Speculation business is separate | §28 Expl. 2 | §26(3) |
| "Speculative transaction"; derivatives excluded | §43(5), proviso (d) | §66(31)(a), §66(33) |
| STT deductible against business income | §36(1)(xv) | §32(k) |
| General business expenses | §37(1) | §34(1) |
| Same-head and inter-head set-off | §70, §71 | §108, §109 |
| Business loss carry-forward, 8 years | §72 | §112 |
| Speculation loss: only vs speculation, 4 years | §73, §73(4) | §113 |
| Carry-forward needs a return by due date | §80 with §139(3) | §121 (return under §263(1)) |
| Presumptive business income | §44AD | §58 |
| Tax audit | §44AB | §63 |

The 1961 numbers for §36(1)(xv), §37(1), §70 and §71 were not re-read against
the 1961 text. The rest are quoted in the ICAI Guidance Note.

## 4. Classification: business income, not capital gains

| Activity | Nature | Return |
|---|---|---|
| Equity or index F&O on a recognised exchange | **non-speculative** business income | ITR-3 |
| Intraday equity, cash segment, no delivery | **speculative** business income | ITR-3 |
| Delivery equity | capital gains for an investor | see [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md) |

**Why.** A contract settled by difference rather than delivery is speculative
(§66(31)). A "specified derivative transaction" is carved out (§66(31)(a)). That
means exchange derivatives traded through a SEBI-registered broker, on a
time-stamped contract note carrying the client code and PAN (§66(33)). Intraday
equity is not a derivative, so it stays speculative.

**So §111A and §112A (§196, §198) do not apply.** There is no holding period and
no STCG/LTCG split. There is no 20% or 12.5% rate and no ₹1.25 lakh exemption.
F&O profit joins total income at slab rates. Paying STT on a futures sale does
not make it a §111A transaction. **Detector:** `holding_days`, `STCG`, `LTCG`,
`111A` or `112A` anywhere on an F&O code path.

Physical delivery of a stock derivative creates a share position. Classify that
position's later sale under the cash-segment rules.

Choosing between ITR-3 and ITR-4 is owned by
[itr-filing-schedules](../itr-filing-schedules/SKILL.md). The e-filing portal
puts presumptive income (§44AD) on ITR-4, so ITR-3 is the default for F&O.

## 5. Loss set-off and carry-forward

| Loss | Same year, may offset | Carried forward, may offset | Years |
|---|---|---|---|
| **F&O** (non-speculative business) | any head **except salary**, including capital gains and speculative profit | business income only, including speculative | **8** |
| **Intraday** (speculative) | **speculative profit only** | speculative profit only | **4** |
| Capital loss | capital gains only | capital gains only | 8 |

Sources: §108, §109(1)(a), §109(2), §112(2) and §113(1)–(3) of the 2025 Act;
ICAI Guidance Note para 62.6. Carry-forward requires a return filed by the due
date (§121). A late return forfeits the loss.

Three asymmetries US-trained code misses:

- **An F&O loss can absorb a capital gain in the same year, but a capital loss
  cannot absorb F&O profit** (§109(2)). F&O loss is not a capital loss. Netting
  it in the capital-loss bucket is wrong both ways.
- **An F&O loss can offset intraday profit, but an intraday loss cannot offset
  F&O profit** (GN para 62.6, §113(1)). A single "trading P&L" pool overstates
  the deduction.
- **No business loss reaches salary** (§109(1)(a)). There is no US-style
  $3,000 ordinary-income allowance, and no salary offset at all.

## 6. Turnover for tax audit: the ICAI method

Turnover is **not** contract value and **not** net P&L. The ICAI Guidance Note
on Tax Audit (Revised 2026), para 5.11(b), sets it "only and only for the
purpose of computing turnover for tax audit":

1. The total of favourable and unfavourable differences on squared-off trades,
   meaning the **sum of absolute** settled differences.
2. "Premium received on sale of options is also to be included in turnover.
   However, where the premium received is included for determining net profit
   for transactions, then such net profit should not be separately included."
3. Reverse-trade differences count; an open position counts in the year it is
   squared off; on delivery settlement, trade price minus settlement price counts.

Each trade is independent (para 5.11(a)): compute per trade, never after netting
per symbol or per day.

**Example.** A future gains ₹40,000 and another loses ₹25,000. A short option is
sold for ₹12,000 and bought back for ₹4,000 (+₹8,000). A long option bought for
₹10,000 is sold for ₹2,000 (−₹8,000). A short option sold for ₹6,000 expires
worthless (+₹6,000).

Net P&L is ₹21,000: **not turnover**. Absolute differences sum to **₹87,000**.
Rule 2 has two readings that commentators dispute; under the second, the ₹12,000
premium replaces that trade's ₹8,000 difference, giving ₹91,000. Both readings
forbid counting a premium **and** its own trade's difference. Make the reading an
explicit, documented setting. The note is written for 1961 §44AB; check for an
edition under 2025 §63 before citing its paragraph numbers.

**Audit thresholds (§63 Table Sl. 1; 1961 §44AB(a)).** Audit applies when
business turnover exceeds **₹1 crore**. The threshold is **₹10 crore** when cash
receipts **and** cash payments are each at most 5%. The cash test covers all
business receipts and payments, not just F&O.

## 7. Presumptive taxation (§44AD / §58)

§58(2) deems business profit at 6% of turnover received through banking channels
and 8% of the rest, or the actual profit if higher. It applies to an eligible
resident with turnover up to ₹2 crore, or ₹3 crore where cash receipts are at
most 5%. For F&O this is an **election with a five-year tail**, not a default.

- Under §58(4), no loss, allowance or deduction is allowed against presumptive
  income. A loss-making trader who elects it is taxed on a deemed profit.
- If you declare under §58 and then step out within five years, you are barred
  for the next five years (§58(7)). Books and an audit are also required if
  income exceeds the basic exemption limit (§58(8) with §63; 1961 §44AD(4),
  §44AB(e)).
- No audit is needed when profit is declared under §58(2) (§63(2)).
- The ICAI turnover method above is stated for §44AB only. Do not assume it is
  the turnover that §58 multiplies by 6%. Flag that choice for a professional.

**Detector.** Any code that applies 6% to F&O turnover without a user election
and a record of earlier years' choices.

## 8. Deductible expenses

On the business head, costs reduce income:

- STT (§32(k)). Under capital gains, STT is **not** deductible (§72(3)(b)).
- Brokerage, exchange charges, SEBI fee, stamp duty and GST on them.
- Anything spent wholly and exclusively for the trading business (§34(1)), such
  as data feeds, software, internet and advisory subscriptions. Capital items
  are claimed through depreciation, not as an expense.

**Detector.** A broker's tax P&L is often already net of charges; deducting the
charge statement again double-counts them. Reconcile gross, charges and net first.

## Verifying an implementation

- **Pin the option STT base.** Change the strike, hold the premium: STT must
  not move. If it does, the base is notional.
- **Test exercise both ways.** An ITM long at expiry pays 0.15% of intrinsic
  value; an OTM expiry and the short side pay nothing.
- **Boundary-test each rate change:** 2024-09-30/10-01 and 2026-03-31/04-01
  (STT), 2026-02-28/03-01 (NSE transaction charge).
- **Reconcile one real F&O contract note**, including an exercised expiry.
- **Turnover:** the five-trade example must give ₹87,000 (difference-only
  reading), not net P&L and not contract value.
- **Set-off, with a control:** an intraday loss against F&O profit must **not**
  offset, and an F&O loss against intraday profit **must**. Then confirm an F&O
  loss does not reach salary.
- **Grep the F&O path** for `111A`, `112A`, `STCG`, `LTCG` and `holding`.

## Scope

Resident individuals; NSE equity and index futures and options. **Out of scope:**
currency and commodity derivatives (commodities transaction tax, not STT), NRIs,
surcharge and cess, and advance tax.

- Cash-segment charges: [indian-equity-charges](../indian-equity-charges/SKILL.md)
- Capital gains on delivery equity: [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md)
- Expiry, settlement price and lot sizes: [nse-options-mechanics](../nse-options-mechanics/SKILL.md)
- ITR form choice and schedules BP, CYLA, BFLA and CFL: [itr-filing-schedules](../itr-filing-schedules/SKILL.md)

Informational only; **not tax advice**. Classification of a particular
taxpayer's activity, the turnover reading and the presumptive election need a
qualified professional. State the tax year and rate as-of date wherever a figure
is shown.
