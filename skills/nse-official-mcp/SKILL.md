---
name: nse-official-mcp
description: Using NSE's official MCP servers (mcp.nseindia.in) correctly — the two cash-market servers nse-bhavcopy (end-of-day history, indices, breadth, corporate actions) and cm-market (1–3 minute delayed live quotes, movers, indices), their 36 read-only tools, no-auth streamable-HTTP setup, the non-commercial and no-AI-training terms, unadjusted split/bonus prices, 3-month history chunks, holiday date snapping, stale-outside-hours data, empty-result-as-failure, index-name and series conventions, and the absence of any F&O, options-chain or open-interest server. Use when connecting Claude Code or another agent to the NSE MCP, writing code or prompts that call its tools, deciding whether its data may feed an app, backtest or model, or when an NSE MCP figure disagrees with bhavcopy, a broker or Yahoo.
license: MIT
compatibility: NSE-hosted MCP servers at mcp.nseindia.in (serverInfo nse-bhavcopy-redis-mcp 1.0.0 and cm-market-mcp 1.0.0). Tool lists, server instructions and the landing page at https://www.nseindia.in/nse-mcp were read on 2026-11-26; NSE changes them without notice, so re-run tools/list before relying on a tool name.
metadata:
  author: hariharanvisves
  version: "1.0"
  verified: "2026-11-26"
  jurisdiction: India
---

# NSE Official MCP Servers

NSE publishes two Model Context Protocol servers for its **cash market**. They are
free, need no account or API key, and are read-only. Its landing page is
https://www.nseindia.in/nse-mcp (https://mcp.nseindia.in/ redirects there).

The model defaults this skill corrects:

- assuming the history prices are split- and bonus-adjusted (they are not);
- assuming there is an F&O, option-chain or open-interest server (there is none);
- treating "free" as "free to build a product or train a model on" (the terms say no);
- treating an empty corporate-actions result as "no actions";
- trusting a live figure outside market hours.

## 1. The two servers

| Name to register | URL | serverInfo | Tools | Data |
|---|---|---|---|---|
| `nse-bhavcopy` | `https://mcp.nseindia.in/bhavcopy/cm/mcp` | `nse-bhavcopy-redis-mcp` 1.0.0 | 21 | End-of-day OHLCV from official bhavcopy files, 5-year window; indices, breadth, VIX, valuation, corporate actions |
| `cm-market` | `https://mcp.nseindia.in/cmmkt/mcp` | `cm-market-mcp` 1.0.0 | 15 | Live cash-market quotes, movers, indices; NSE states a 1–3 minute delay |

Register them in Claude Code (no auth), then restart the session so the tools load:

```sh
claude mcp add --transport http nse-bhavcopy https://mcp.nseindia.in/bhavcopy/cm/mcp
claude mcp add --transport http cm-market https://mcp.nseindia.in/cmmkt/mcp
```

The official site is `nseindia.com`, so the `.in` host needed proof of ownership. It
was checked on 2026-11-12: a DigiCert organisation-validated certificate with
`O=National Stock Exchange of India Ltd.`, NSE as whois registrant, and the same
Akamai edge as `nseindia.com`. NSE's own web pages also redirect from `.com` to
`.in` (see [nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md) §1).

**Scope.** The landing page lists only these two servers and describes them as "NSE
cash market data: prices, market breadth, top movers, SME stocks, bonds and corporate
actions." Neither server has a futures, options, option-chain, open-interest,
currency or commodity tool. `cm-market`'s `derivatives` index group is a group of
**indices**, not contracts. For F&O data use the F&O bhavcopy downloads. For F&O
mechanics see [nse-options-mechanics](../nse-options-mechanics/SKILL.md).

**Detector.** Code or a prompt that asks the NSE MCP for an option chain, OI, PCR or
futures basis.

## 2. Terms: research and learning, not products or training

Quoted from the landing page (2026-11-26):

- "NSE provides this data for information and learning. It is not meant for real-time
  trading, investment advice or commercial products."
- The MCP gives access to data "already available on the website of NSEIL, for
  informational purpose only and not using it for any commercial purposes."
- "Access to Data through the MCP shall not be construed as granting any license,
  right or permission to commercially exploit, train or fine-tune any AI systems,
  models, algorithms including but not limited to generative AI or third-party
  applications using such Data."
- NSEIL "does not warranty the accuracy, completeness, reliability or timeliness of
  the Data". Use is subject to NSEIL's Terms of Use, Disclaimer and Privacy Policy,
  which are linked from that page.

Both servers' `instructions` say the data is "for educational and research purposes
only" and is not investment advice. No rate limit or quota is published.

**Rule.** Use it as agent research data inside a session. Do not ship it as a
product's data feed, store it as an app's price history, put its output in test
fixtures or seeds, or use it to train or fine-tune a model, unless NSE grants a
licence. Read the full Terms of Use before building anything. This is engineering
guidance, not legal advice.

**Detector.** An app's provider layer, cron job or dataset builder that calls
`mcp.nseindia.in`.

## 3. Protocol behaviour

- Transport is streamable HTTP. `initialize` returns an `Mcp-Session-Id` header;
  send it on every later call. Protocol version `2025-06-18` is accepted.
- `tools/list` and `tools/call` replies are SSE-framed (`event: message`,
  `data: {json}`), even for one-shot calls. A `tools/call` result is JSON inside
  `content[0].text`, but `get_ltp_by_date` returns a bare number as text.
- The first `initialize` on each server returned HTTP 500 once and succeeded on
  retry. Retry transient 500s with backoff before treating the server as down.
- Tools carry no `readOnlyHint` annotation, though every tool is read-only.
- Neither `tools/list` paginates (no `nextCursor`).

## 4. Prices are not adjusted for splits or bonuses

The landing page says "Old prices are not adjusted for splits or bonus issues", and
the tool descriptions repeat it. Unadjusted outputs: `get_stock_history`,
`get_ltp_by_date`, `get_top_movers` (percent change from the raw previous close),
`compare_stocks` and `get_52_week_high_low`. Only `get_stock_vs_index` adjusts its
return for corporate actions, so do not adjust that figure again.

`get_corporate_actions(symbol, fromDate, toDate)` returns `exDate`, the raw `purpose`
text, `actionType` (`SPLIT`, `BONUS`, `DIVIDEND`, `OTHER`) and an `adjustmentFactor`.
Dividends carry factor 1.0, so prices are not dividend-adjusted either. Apply the
factor to prices before the ex-date, using the rules in
[nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).

**Why.** A 1:1 bonus reads as a 50% one-day crash in raw history. Momentum, drawdown
and 52-week figures across it are wrong.

**Detector.** A return, drawdown or moving average over `get_stock_history` output
with no corporate-action step; a stock that "fell 50%" on an ex-date.

## 5. Empty is a failure, not "nothing"

`get_corporate_actions` fetches from NSE's live site. Per its description, an `error`
field means the lookup failed, and a `warning` means the list may be incomplete.
NSE's bot protection can also return 401/403 or empty bodies under load.

**Rule.** Treat a missing, empty or error result as a failed call. Never read it as
"this stock had no corporate actions" or "no data for this date".

## 6. Dates, holidays and history chunks

- Dates are `yyyy-MM-dd` IST calendar dates with no timezone. `cm-market`
  freshness fields (`lastCrawled`, `updatedAt`) are UTC ISO-8601, while a quote's
  `latestTimestamp` is a naive IST-looking string. Do not compare the two without
  converting. For the IST-to-UTC trap see
  [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md).
- A non-trading date silently snaps to a trading day: `get_ltp_by_date` returns the
  previous trading day's close. Compare the returned date with the requested one
  (`get_index_snapshot` returns both `date` and `requested_date`). Never use the MCP
  to decide whether a date was a trading day; use
  [nse-trading-calendar](../nse-trading-calendar/SKILL.md).
- History comes in chunks: `get_stock_history` returns at most 3 months per call and
  `get_index_history` at most 12. Each returns `next_end_date`; loop on it until the
  start date is covered.
- `get_stock_history` rows carry `deliveryQty` 0 and `ch52WeekHigh`/`ch52WeekLow`
  0.0 (observed on 2026-11-26). Those fields are not populated, so do not use them.

## 7. Live data freshness (cm-market)

`cm-market`'s instructions say gainers and losers refresh every 5 minutes, price
watch and indices every minute, and that data is "Stale outside market hours"
(09:15–15:30 IST, Monday to Friday). The landing page states a 1–3 minute delay.

- Call `cm_get_data_status` (movers) or `cm_get_allstocks_status` (price watch)
  before trusting a live figure. Report the quote's timestamp with every number.
- Before the open, `open`, `high` and `low` are omitted. Do not read them as 0.
- It has no ticks and no order book, so it is not an execution or trading feed. For
  order paths see [kite-connect-safety](../kite-connect-safety/SKILL.md).

## 8. Names, series and symbols

- Index names differ between the servers. `nse-bhavcopy` uses long names (`Nifty 50`)
  and `cm-market` uses live short names (`NIFTY SMLCAP 100`). Map them explicitly.
- Index filters are substring matches: filtering `nifty 50` also returns `Nifty 500`.
  Pick the exact name from the result.
- Symbol lookups return ETFs (for example `NIFTYBEES`) alongside equities.
- `cm-market` splits listings by series: equities (`EQ`, `BE`, `BL`, `BT`, `IL`, `IQ`),
  SME (`SM`, `ST`), bonds and government securities, and call auction (`CA`, `CB`).
  Filter to the series you mean. For what each series implies see
  [nse-bhavcopy-corporate-actions](../nse-bhavcopy-corporate-actions/SKILL.md).
- `cm_get_live_market_data` takes `index` values `gainers` or `loosers` (NSE's
  spelling). `cm_get_live_gainers` and `cm_get_live_losers` return raw, unsorted
  data grouped by index; their descriptions point to `nse_get_market_movers`.
- Prices are rupee floats, not paise. Keep money as integer paise in your own code.

## 9. Do not treat it as a survivorship-free universe

The equity count is stated inconsistently: about 5,000 in the server's instructions
and "3,500+" on the landing page. Neither describes point-in-time index membership.
For a backtest universe use
[nse-universe-survivorship](../nse-universe-survivorship/SKILL.md).

## Verifying an implementation

- Run `tools/list` on both servers and diff the names against any tool your code
  calls. A renamed tool must fail loudly.
- A 1:1 bonus fixture over `get_stock_history`: the computed return across the
  ex-date must be about 0%, not −50%.
- A corporate-actions call that returns `error` must raise, not yield an empty list.
- A `get_ltp_by_date` call on a holiday must report that the returned date differs
  from the requested one.
- Grep app code, fixtures and seed data for `mcp.nseindia.in`. Any hit outside agent
  configuration is a terms question.

## Scope

Cash-market MCP servers only, as listed by NSE on 2026-11-26. Tool names,
descriptions and terms are NSE's and may change; re-read the landing page and
`tools/list` before depending on them. Not legal advice on NSE's terms, and not
investment advice.
