# Primary sources for intraday-risk-sizing

All read on 2026-11-26. Each entry says what the skill takes from it. Nothing here gives a
current lot size, freeze quantity or tick for a named security; those come from the exchange
files at order time.

## NSE circulars

| Reference | Date | Used for |
|---|---|---|
| [NSE/CMTR/62174](https://nsearchives.nseindia.com/content/circulars/CMTR62174.pdf) | 24 May 2024 | Price-linked tick size in the cash segment from 10 Jun 2024; reviewed monthly on the last trading day's close; after a split, bonus, dividend or rights issue the old tick stays until the next review; the applicable tick is in the security files (`NSE_CM_security_ddmmyyyy.csv.gz`) |
| [NSE/CMTR/67133](https://nsearchives.nseindia.com/content/circulars/CMTR67133.pdf) | 13 Mar 2025 | Tick tiers from 15 Apr 2025: ₹0.01 below ₹250, ₹0.05 from ₹250 to ₹1,000, ₹0.10 above ₹1,000 up to ₹5,000, and wider ticks at higher prices; monthly review; tick in the security files |
| [NSE/FAOP/67134](https://nsearchives.nseindia.com/content/circulars/FAOP67134.pdf) | 13 Mar 2025 | Stock futures use the underlying's cash tick; stock options stayed at ₹0.05 then; tick in the F&O contract files |
| [NSE/FAOP/70382](https://nsearchives.nseindia.com/content/circulars/FAOP70382.pdf) | 23 Sep 2025 | Stock options tick ₹0.05 to ₹0.01 for underlying below ₹250 from 3 Nov 2025; monthly review |
| [NSE/FAOP/49118](https://archives.nseindia.com/content/circulars/FAOP49118.pdf) | 31 Jul 2021 | Section A: an order above the freeze quantity is frozen and automatically rejected; stock freeze is the lesser of 1% of the market-wide position limit and a notional of about ₹2.5 crore, rounded to lots; revised monthly and on corporate-action ex-dates |
| [NSE/FAOP/65435](https://nsearchives.nseindia.com/content/circulars/FAOP65435.pdf) | 5 Dec 2024 | `qtyfreeze.csv` and `fo_mktlots.csv` disseminated from 9 Dec 2024 on the equity-derivatives contract-information page |
| [NSE/FAOP/61157](https://nsearchives.nseindia.com/content/circulars/FAOP61157.pdf) | 15 Mar 2024 | Earlier discontinuation of those two reports; the MII contract file `NSE_FO_contract_ddmmyyyy.csv.gz` also carries quantity freeze and market lot |
| [NSE/FAOP/70616](https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf) | 3 Oct 2025 | Nifty 50 lot 75 to 65 (and Nifty Bank, Financial Services, Mid Select) from 28 Oct 2025 EOD; existing weekly and monthly contracts keep the old lot until their December 2025 expiries; the lot lives in the contract file |

The December 2024 and March 2024 circulars disagree on whether the two separate reports
exist. Treat the contract file as the source and check what NSE publishes on the day.

## SEBI

- Circular SEBI/HO/MRD/TPD-1/P/CIR/2024/132, 1 Oct 2024, para 5.4 (contract size for index
  derivatives): [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/oct-2024/1727786261636.pdf).
- Master Circular for Stock Exchanges and Clearing Corporations, Chapter 5, Exchange Traded
  Derivatives (December 2024 edition), clauses 1.1.4.3 and 3.1.6.2: exchanges review the lot
  size once in every 6 months on the average closing price of the last month, with at least
  2 weeks' advance notice; a higher revised lot applies to new contracts only; the lot size is
  the same across exchanges for one underlying:
  [PDF](https://www.sebi.gov.in/sebi_data/commondocs/dec-2024/RE_Chapter%205%20-%20Exchange%20Traded%20Derivatives%20FINAL_1_p.pdf).
  A later master circular may have replaced this edition; check before citing a clause number.

## Broker (Kite Connect v3 docs)

- Quotes: https://kite.trade/docs/connect/v3/market-quotes/ . `/quote` carries `timestamp`
  ("The exchange timestamp of the quote packet") and `last_trade_time` (null or string, "Last
  trade timestamp"); `/quote/ohlc` and `/quote/ltp` carry no time field. The documented
  instruments dump columns are `instrument_token`, `exchange_token`, `tradingsymbol`, `name`,
  `last_price`, `expiry`, `strike`, `tick_size` ("Value of a single price tick", float64),
  `lot_size` ("Quantity of a single lot", int64), `instrument_type`, `segment` and `exchange`;
  none is a freeze quantity.
- Margins: https://kite.trade/docs/connect/v3/margins/ . `/margins/orders` "calculates margins
  for each order considering the existing positions and open orders"; the example response
  shows `span`, `exposure`, `option_premium`, `additional`, `bo`, `cash`, `var`, `pnl` and
  `leverage`.

## Not read or not found

- The current NSE consolidated F&O circular that sets the index freeze-quantity methodology.
  A search-result summary named NSE/FAOP/67775 (30 Apr 2025); that circular was not read and
  the URL tried returned 404. The skill therefore cites only NSE/FAOP/49118 for the rule. Index freeze
  quantities are not sourced here, so the skill says only to read them from NSE's file.
- The NSE equity-derivatives contract-information page and the all-reports pages, which render
  only in a browser. The file names above come from circulars, not from the live page.
