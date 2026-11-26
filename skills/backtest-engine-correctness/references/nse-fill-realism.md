# NSE fill realism: dated rules behind SKILL.md §20–§23

Purpose: the price-band, halt, settlement, trade-for-trade and F&O ban detail that decides whether a backtest fill could have happened on NSE. Apply by **trade date**: pick the rule in force for each date in the backtest. The closing-price regime (§21) stays in [SKILL.md](../SKILL.md) because every close-based backtest needs it.

## Contents

- Price bands and circuit locks (§20)
- Halts, settlement cycle and pre-open (§21, remainder)
- Trade-for-trade series and GSM (§22)
- F&O ban, ASM and GSM surveillance (§23)

## Price bands and circuit locks (§20)

**Rule.** A bar whose open, high, low and close all sit at one price limit (no two-way trading) cannot fill a buy at the upper limit or a sell at the lower limit. Skip or defer the order; do not fill at the limit.

**Facts.**
- Price bands of 2/5/10/20% apply to non-F&O stocks and are revised periodically.
- F&O stocks have no cash-market band, only a 10% dummy order-entry filter that NSE relaxes near the limit.
- Stock-futures bands flex 10% to 15% to 20% (triggers at 9.90% and 14.90% of base).
- Source: NSE FAQ on price band / operating range flex; NSE/FAOP/63405 and NSE/FAOP/64995 (verified 2026-11-11).

**Detector.** Count fills on bars where high == low == a band limit; expect zero.

## Halts, settlement cycle and pre-open (§21, remainder)

The closing-price regime by date is in SKILL.md §21. The rest:

- **Market-wide halts.** A 10/15/20% move in whichever of Sensex or Nifty 50 breaches first halts trading. 10%: before 13:00, 45 min halt plus 15 min pre-open; 13:00 to 14:30, 15 min plus 15 min pre-open; at or after 14:30, no halt. 15%: before 13:00, 1 h 45 min; 13:00 to 14:00, 45 min; on or after 14:00, rest of day. 20%: any time, rest of day. Treat an intraday fill across a halt as unfillable. Source: NSE circuit-breakers page, https://www.nseindia.in/products-services/equity-market-circuit-breakers (verified 2026-11-26).
- **T+1 settlement** applies to all equities from 27 Jan 2023. It was phased in by stock before that, so verify the cycle per stock for 2022 dates.
- **Optional T+0** is beta: live from 28 Mar 2024 (NSE T+0 page). It reached the top 500 in monthly batches of 100 from the bottom: 31 Jan 2025, 28 Feb 2025, 28 Mar 2025, 30 Apr 2025 and 30 May 2025 (complete). Source: NSE T+0 FAQ, updated 30 Apr 2025, https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Trading_in_T+0_Security_0.pdf (verified 2026-11-26).
- **Pre-open order collection** was 9:00–9:08 before 7 Sep 2026. From that date it is 9:00–9:05 (limit and market) and 9:05–9:10 (limit only), with continuous trading from 9:15. Source: SEBI circulars dated 16 Jan 2026 and 15 Oct 2026 (verified 2026-11-11).
- **Oct 2026 amendment.** The SEBI circular of 15 Oct 2026 does not restate its applicability and band paragraphs in the amended text. Treat F&O-only and the ±3% band as unchanged until the text is read (open item in `docs/unverified-claims.md`).

**Detector.** A fill timed inside a halt window, or a settlement date computed with the wrong cycle for the trade date.

## Trade-for-trade series and GSM (§22)

**Rule.** BE and BZ series settle trade-for-trade (gross, every trade deliverable). Do not model intraday netting there. Stage II–IV GSM names are trade-for-trade as well, and Stage III–IV trade only once a week (first trading day of the week).

**Why.** Netting a same-day buy and sell there models a trade that settles gross. Source: NSE series legend; NSE GSM FAQ (verified 2026-11-11).

**Detector.** On a BE/BZ or GSM Stage II–IV name, a same-day buy and sell must book two deliverable trades. A Stage III–IV fill on any day other than the week's first trading day is impossible.

## F&O ban, ASM and GSM surveillance (§23)

| Item | Rule |
|---|---|
| F&O ban entry | Futures-equivalent open interest exceeds 95% of MWPL |
| MWPL | Lower of 15% of free float and 65× average daily delivery value (floor 10% of free float), recalculated quarterly. Both apply from 1 Oct 2025; before that, MWPL was 20% of free float on plain open interest |
| Ban exit | Normal trading resumes when open interest is at or below 80% of the market-wide position limit. Source: SEBI Master Circular annexure 1.3.2.1.4.6, https://www.sebi.gov.in/sebi_data/commondocs/may-2026/Annexure-%20B_p.pdf. Futures-equivalent delta: call N(d1), put N(d1)-1, future 1 (NSE/SURV/71090) |
| Long-term ASM, F&O stocks | F&O margin at least 50% at Stage I rising to 100%; MWPL cut to 75% / 50% from Stage II / III; no fresh contracts at Stage IV |
| Long-term ASM, cash | Cash margin 100% from Stage I; Stage IV gross settlement with a 5% band |
| GSM Stage I | 100% margin, band of 5% or less |

Source: SEBI circular 29 May 2025 (paras 5.2, 6); NSE ASM and GSM FAQs (verified 2026-11-11).

**Why.** Ban, margin and band rules decide whether a position could be opened and at what cost. Ignoring them fills trades that never existed.

**Detector.** A derivatives backtest that opens positions in a banned name, or a cash backtest that ignores a 5% band on a GSM name, is unfillable as modelled.
