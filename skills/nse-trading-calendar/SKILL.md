---
name: nse-trading-calendar
description: Building a correct NSE/BSE trading and settlement calendar for backtests, T+1 settlement and derivatives expiry — where the official per-segment holiday list is published, late-declared closures, Muhurat and other special live sessions (budget-day weekend sessions, DR-site sessions), mock sessions that are not trading days, trading holidays vs settlement (clearing) holidays, expiry-day shift to the previous trading day, and the dated history of weekly-expiry weekdays. Use when generating trading days for an Indian backtest, computing a settlement date or an expiry date, deciding whether the market is open on a date, handling Diwali or a holiday in a date loop, or reviewing code that uses pandas business days, a US holiday calendar, a weekday filter, or missing bhavcopy files to decide trading days.
license: MIT
compatibility: NSE (India) cash, F&O, currency and commodity segments; BSE equity-derivatives expiry days. Holiday lists, sessions and expiry rules change by circular; dates verified against NSE, NSE Clearing and BSE sources as of 2026-11-11.
metadata:
  author: hariharanvisves
  version: "1.0"
  verified: "2026-11-11"
  jurisdiction: India
---

# NSE Trading Calendar

A trading calendar built from weekdays, from a US calendar or from the files
that happen to download is wrong on a handful of dates a year. Those dates are
the ones that matter: expiries, settlement, Diwali. Each entry below is
**rule**, **why**, **detector**.

Owners elsewhere: session timings, closing price and T+1 phase-in are in §21 of
[backtest-engine-correctness](../backtest-engine-correctness/SKILL.md). The
expiry instant and settlement price are in
[nse-options-mechanics](../nse-options-mechanics/SKILL.md). Bhavcopy file
formats are in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).

## 1. The calendar is dated config with a source

**Rule.** Store the calendar as data, one row per (segment, date, kind), with the
circular that created it:

```
segment  date        kind               source
CM       2026-01-15  trading_holiday    NSE/CMTR/72260 (2026-01-12)
CM       2026-02-19  clearing_holiday   NSE holiday-master type=clearing
CM       2026-11-08  special_session    NSE/CMTR/76941 (Muhurat)
```

A trading day is a weekday not marked as a holiday, **plus** every special live
session. Version the table and keep superseded rows: a backtest must be able to
say which list it ran against.

**Why.** `pd.bdate_range` / `BDay` treat every weekday as a trading day; NSE
closed on 16 weekdays in 2026. `USFederalHolidayCalendar` closes on Thanksgiving
and opens on Diwali. Third-party India calendars (`exchange_calendars`,
`pandas_market_calendars`) are hand-maintained copies that can lag a
late-declared closure (§2): diff them against the exchange before trusting them.

**Detector.** Compare your trading days for a full year with the exchange list
(§2). Assert zero differences, and assert 2026-11-08 (a Sunday) is a session.

## 2. Where the list comes from, and how it changes

**Rule.** Take holidays from the exchange, per segment:
- NSE publishes each year's list by circular. The 2026 capital-market list is
  NSE/CMTR/71775, dated 12 Dec 2025. The F&O list is NSE/FAOP/71777 of the same
  date.
- The holidays page `nseindia.com/resources/exchange-communication-holidays` is
  backed by `nseindia.com/api/holiday-master?type=trading` and `?type=clearing`.
  The API returns one list per segment key (`CM`, `FO`, `CD`, `COM`, `CBM`,
  `IRD`, `SLBS`, `MF` and others). It needs the cookie that the home page sets,
  even when the home page itself returns 403 (observed 2026-11-11).
- The list includes holidays that fall on a weekend (15 Feb 2026 Sunday,
  15 Aug 2026 Saturday). Do not count those as lost sessions.
- Re-fetch the list on a schedule. Never read it once a year.

**Why.** The list changes after publication, sometimes with three days' notice:
- **15 Jan 2026** (Maharashtra municipal elections) was not in the
  12 Dec 2025 list. NSE/CMTR/72260, dated 12 Jan 2026, added it "in partial
  modification" of that list. The commodity segment closed only its morning
  session (NSE/COM/72263).
- **22 Jan 2024** was declared a public holiday under s.25 of the Negotiable
  Instruments Act. NSE made it a trading holiday (NSE/CMTR/60338 and 60340, as
  cited in NCL/CMPT/60343). The special live session on **Saturday 20 Jan 2024**
  went ahead from the primary site only. NSE Clearing settled trades from both
  19 Jan and 20 Jan on 23 Jan 2024 (NCL/CMPT/60343).

**Detector.** Store the fetch timestamp with the list. Alert when a refetch adds
or removes a date. Re-run any backtest or schedule that spans that date.

## 3. Segments have different holidays

**Rule.** Key every lookup by segment. Never share one "market holiday" set
across segments.

**Why.** From the 2026 holiday master: equity cash (`CM`) and F&O (`FO`) list
the same 20 dates. Currency derivatives (`CD`) adds four more weekday closures:
19 Feb, 19 Mar, 1 Apr and 26 Aug 2026. The equity market trades on all four.
The commodity segment (`COM`) closes morning and evening sessions separately.
On 3 Mar 2026 (Holi) the morning session is closed and the evening session open.
On 1 Jan 2026 the morning session is open and the evening session closed.

**Detector.** Assert `CD` and `CM` holiday sets differ for 2026. One shared set
is the bug.

## 4. Trading holiday is not settlement holiday; T+1 uses the clearing list

**Rule.** Compute a T+1 settlement date as the next day on the **clearing**
calendar of NSE Clearing (holiday master `type=clearing`), not the next trading
day. A trading day can be a settlement holiday. In 2026, 19 Feb, 19 Mar, 1 Apr
and 26 Aug are equity trading days and clearing holidays. The weekend budget
sessions (§6) were too: NSE skipped the T0 session on both "due to settlement
holiday". Every 2026 weekday trading holiday is also on the clearing list.

Examples, derived from the 2026 clearing list:
- A trade on Wed 18 Feb 2026 settles on Fri 20 Feb, not Thu 19 Feb.
- A trade on Mon 30 Mar 2026 settles on Thu 2 Apr. 31 Mar is a full holiday
  and 1 Apr is a clearing holiday. Trades from 1 Apr also settle on 2 Apr, so
  one settlement date carries two trade dates.

**Why.** "T+1 = next trading day" gives the wrong pay-in date, margin-funding
interest and sell-before-delivery check. The error sits only around clearing
holidays, so tests on normal weeks pass.

**Detector.** Unit-test settlement dates for 18 Feb, 30 Mar and 1 Apr 2026
against the values above. Assert that the settlement function never takes a
trading calendar as input.

## 5. Muhurat trading: a dated, short, real session

**Rule.** Muhurat is a **special live trading session** on the Diwali
(Laxmi Pujan) holiday. Its date is in the December holiday circular. Its timings
come later, in a separate circular. Model it as a trading day with its own
session times, settlement and bhavcopy.

| Year | Date | Normal market | Source |
|---|---|---|---|
| 2025 | Tue 21 Oct | 13:45–14:45 (currency segment) | NSE/CD/70321 |
| 2026 | Sun 8 Nov | from 14:20; F&O to 15:40; CAS stocks continuous to 15:15, then auction | NSE/CMTR/76941, NSE/FAOP/76940 |

**Why.** Several defaults fail on this one date:
- **It is listed as a holiday.** 8 Nov 2026 is in the holiday master with an
  asterisk that marks Muhurat. "Weekdays minus holidays" drops it, and so does
  a weekend filter.
- **Trades settle.** The Muhurat circulars say the session's trades "shall
  result in settlement obligations". Trades from 8 Nov 2026 settle on
  9 Nov 2026 (NCL/CMPT/77037). For 2025, trades from both 20 Oct and 21 Oct
  settled on 23 Oct 2025 (NCL/CMPT/70411).
- **It is not an expiry day.** The NIFTY weekly contract due on Tue 21 Oct 2025
  expired on Mon 20 Oct 2025 (F&O bhavcopy), even though a session ran on 21 Oct.
- **It is short.** A bar of about an hour treated as a full day distorts daily
  volatility, volume averages and per-session annualisation. Flag the bar
  instead of dropping it.

**Detector.** Assert 2025-10-21 and 2026-11-08 are sessions with a `special`
flag. Assert neither appears in an expiry schedule.

## 6. Other special sessions, and mock sessions that are not sessions

**Rule.** Add each **live** weekend session by its circular. Never add **mock**
sessions.
- Budget day: Sat 1 Feb 2025 (NSE/CMTR/65729) and Sun 1 Feb 2026
  (NSE/CMTR/72349). Both ran full standard hours.
- DR-site sessions: Sat 2 Mar 2024 ran 09:15–10:00 from the primary site and
  11:30–12:30 from the disaster-recovery site (NSE/MSD/60677). That is two
  disjoint windows on one trading day.
- Mock sessions, for example Sat 25 Jul 2026 for the closing auction
  (NSE/CMTR/75401), are member tests of trading systems. They are not trading
  days.

**Why.** A weekend session breaks weekday-only arithmetic. A mock session added
by keyword search ("Saturday trading session") puts a non-day in the calendar.

**Detector.** Every weekend row needs a circular that announces a live trading
session. Reject rows sourced from a circular that says "mock".

## 7. Expiry day: scheduled weekday, shifted to the previous trading day

**Rule.** Compute an expiry date as follows. Take the scheduled weekday for that
contract and date range (§8). If that day is a trading holiday, use the
**previous** trading day. NSE's contract specifications (verified 2026-11-11)
say: "If the Tuesday is a trading holiday, then the expiry day is the previous
trading day." BSE says the same: "previous working day" (BSE notice
20241128-70).

Examples from NSE F&O bhavcopy:
- NIFTY monthly March 2026 expired on Mon 30 Mar 2026, because 31 Mar is
  Mahavir Jayanti.
- NIFTY weekly for Tue 10 Nov 2026 expired on Mon 9 Nov. The weekly for
  Tue 24 Nov 2026 expires on Mon 23 Nov.

**Why.** Two errors are common:
- **Shifting forward.** Rolling to the next trading day gives the wrong date
  and overstates time to expiry for every contract in the series.
- **Freezing the date at contract creation.** On 20 Oct 2025 the BANKNIFTY March
  2026 contract carried expiry 2026-03-31. The 2026 holiday list was published
  on 12 Dec 2025, and by 27 Mar 2026 the same contract expired on 2026-03-30.
  NSE's expiry-change annexures carry the note "Dates may be subject to change
  on account of any holiday declared". Recompute stored expiries when the holiday
  list changes, or read them from the current contract master.

The expiry **instant** (time of day) is a separate question; see
[nse-options-mechanics](../nse-options-mechanics/SKILL.md).

**Detector.** Generate expiries for 2025–2026 and diff them against the
`XpryDt` column of the UDiFF F&O bhavcopy. Include 2025-10-20 and 2026-03-30.

## 8. The expiry weekday has changed; it is a dated table

**Rule.** Look up the expiry weekday by (exchange, index, contract type, expiry
date). Never use a constant.

| Effective for | Change | Source |
|---|---|---|
| from 4 Sep 2023 | BANKNIFTY weekly Thursday → Wednesday; first Wednesday expiry 6 Sep 2023 | NSE/FAOP/57540 |
| from 20 Nov 2024 | One weekly benchmark index per exchange | see [nse-options-mechanics](../nse-options-mechanics/SKILL.md) |
| contracts expiring after 3 Jan 2025 | SENSEX weekly Friday → Tuesday; monthly last Friday → last Tuesday | BSE 20241128-70 |
| from EOD 1 Jan 2025 | BANKNIFTY (last Wed), FINNIFTY (last Tue), MIDCPNIFTY (last Mon), NIFTYNXT50 (last Fri) monthly → last Thursday; NIFTY unchanged on Thursday | NSE/FAOP/65336 |
| proposed 4 Apr 2025 | Move to Monday. **Deferred on 27 Mar 2025 and never applied** | NSE/FAOP/66938, NSE/FAOP/67338 |
| contracts expiring on or after 1 Sep 2025 | NSE: all equity derivatives on Tuesday, monthly on last Tuesday; first Tuesday weekly 2 Sep 2025 | SEBI/HO/MRD/TPD-1/P/CIR/2025/76 (26 May 2025); NSE/FAOP/68589, 68747 |
| contracts expiring after 1 Sep 2025 | BSE: SENSEX weekly Tuesday → Thursday; monthly → last Thursday | BSE 20250617-11, 20250623-59 |

**Why.** A backtest of NIFTY weeklies over 2024–2026 with "Tuesday" throughout
places every pre-September-2025 expiry two days early. Code written during
March 2025 may still carry the Monday schedule that never took effect. The
transition is set by **contract expiry date**, not trade date. In mid-2025,
Thursday and Tuesday contracts were listed side by side.

**Detector.** Assert the 2025-08-28 NIFTY expiry is a Thursday and the
2025-09-02 expiry is a Tuesday. Assert no NSE expiry falls on a Monday because of
the March 2025 proposal. A Monday expiry is valid only as a holiday shift (§7).

## 9. Session times and IST

**Rule.** Session boundaries are dated config, owned by §21 of
[backtest-engine-correctness](../backtest-engine-correctness/SKILL.md). The
familiar 09:00–09:08 pre-open and 09:15–15:30 market predate the 2026
closing-auction and pre-open changes. Store times per date and per special
session (§5, §6). Key the calendar by IST `date`, never by a midnight-UTC
`datetime`: the shift is in §1 of
[indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md).

## 10. Never infer holidays from missing bhavcopy days

**Rule.** File presence is not evidence of a session, and absence is not
evidence of a holiday. Cross-check every gap and every extra day against the
holiday list (§2).

**Why.** Observed on 2026-11-11:
- `sec_bhavdata_full_15012026.csv` (a holiday) returned HTTP 200 with the
  **14 Jan** file, byte-identical. `..._26012026.csv` served 23 Jan. A
  "200 means trading day" loop invents sessions and duplicates bars.
- The UDiFF file for the same holiday returned 404. A 404 also comes from a
  fetch failure or a format change (see
  [nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md)).
- A date index derived from the data inherits every defect above, even the
  union of all symbols' dates. Reconcile it with the calendar.

**Detector.** Assert the `DATE1` (or `TradDt`) inside each file equals the
requested date. Assert the set of loaded dates equals the calendar's trading
days for the range. Report both differences.

## Verifying an implementation

- **Year diff.** Generate 2026 trading days for `CM` and diff them against the
  holiday master. Expect weekdays minus 16 holidays, plus 1 Feb and 8 Nov.
- **Fixture dates.** Use a fixture set that covers every failure class:
  2024-01-20 (Saturday session), 2024-01-22 (late holiday), 2026-01-15 (holiday
  added 3 days ahead), 2026-02-19 (clearing holiday only), 2025-10-21 and
  2026-11-08 (Muhurat).
- **Settlement.** Test 2026-02-18 → 2026-02-20 and 2026-03-30 → 2026-04-02.
- **Expiry.** Diff generated expiries against `XpryDt` in the F&O bhavcopy
  across the September 2025 switch and each holiday shift.
- **Mutation test.** Swap in `pd.bdate_range`, a weekday filter, and
  next-day expiry shifting, one at a time. Each must fail the tests.
- **Provenance.** Fail the build on any calendar row without a source.

## Scope

Informational engineering guidance, not investment advice. Holiday lists,
special sessions and expiry rules are set by exchange and clearing circulars,
and they change at short notice. Fetch the current list from the exchange
before relying on any date here. BSE's own equity holiday list was not
verified for this skill: fetch it from bseindia.com instead of assuming it
matches NSE.
