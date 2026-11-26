# Weekly and monthly expiry weekday history (NSE and BSE)

Purpose: the dated table behind [SKILL.md](../SKILL.md) §8. Look up the expiry weekday by (exchange, index, contract type, expiry date); the transition is keyed on **contract expiry date**, not trade date. Verified against NSE and BSE circulars as of 2026-11-11. Re-check the current circular before relying on a date after that.

| Effective for | Change | Source |
|---|---|---|
| from 4 Sep 2023 | BANKNIFTY weekly Thursday → Wednesday; first Wednesday expiry 6 Sep 2023 | NSE/FAOP/57540 |
| from 20 Nov 2024 | One weekly benchmark index per exchange | see [nse-options-mechanics](../../nse-options-mechanics/SKILL.md) |
| contracts expiring after 3 Jan 2025 | SENSEX weekly Friday → Tuesday; monthly last Friday → last Tuesday | BSE 20241128-70 |
| from EOD 1 Jan 2025 | BANKNIFTY (last Wed), FINNIFTY (last Tue), MIDCPNIFTY (last Mon), NIFTYNXT50 (last Fri) monthly → last Thursday; NIFTY unchanged on Thursday | NSE/FAOP/65336 |
| proposed 4 Apr 2025 | Move to Monday. **Deferred on 27 Mar 2025 and never applied** | NSE/FAOP/66938, NSE/FAOP/67338 |
| contracts expiring on or after 1 Sep 2025 | NSE: all equity derivatives on Tuesday, monthly on last Tuesday; first Tuesday weekly 2 Sep 2025 | SEBI/HO/MRD/TPD-1/P/CIR/2025/76 (26 May 2025); NSE/FAOP/68589, 68747 (<https://nsearchives.nseindia.in/content/circulars/FAOP68747.pdf>) |
| contracts expiring after 1 Sep 2025 | BSE: SENSEX weekly Tuesday → Thursday; monthly → last Thursday | BSE 20250617-11, 20250623-59 |

## Reading the table

- In mid-2025, Thursday and Tuesday NIFTY contracts were listed side by side; pick the weekday by each contract's expiry date.
- The Monday move proposed for 4 Apr 2025 was deferred on 27 Mar 2025 and never applied. Code written during March 2025 may still carry that schedule.
- A holiday on the scheduled weekday shifts the expiry to the previous trading day (SKILL.md §7). A Monday expiry is valid only as such a shift.
