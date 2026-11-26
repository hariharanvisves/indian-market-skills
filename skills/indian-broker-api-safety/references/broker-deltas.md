# Per-broker API deltas: auth flow, rate limits, not-final statuses, sandbox

Purpose: the full comparison behind section 8 of [SKILL.md](../SKILL.md). Token expiry and
tag limits stay in SKILL.md; this file holds the rest. Each cell comes from the broker's own
docs or support pages, read 2026-11-11. Broker limits change without notice; re-check before
hard-coding.

Contents: [Auth flow](#auth-flow) · [Order rate limits](#order-rate-limits) ·
[Not-yet-final statuses](#not-yet-final-statuses) · [Sandbox](#sandbox) · [More traps](#more-traps)

## Auth flow

| Broker | Auth flow | Token expiry source |
|---|---|---|
| Zerodha Kite | `request_token` plus SHA-256 checksum, see the [kite skill](../../kite-connect-safety/SKILL.md) §1 | kite.trade/docs/connect/v3/user |
| Upstox | OAuth 2.0 authorization code; also a TOTP+PIN token endpoint for individual apps and a notifier-approval flow | upstox.com/developer/api-documentation/get-token |
| Dhan | Token generated on Dhan Web; a TOTP endpoint; or API key consent in 3 steps (key and secret valid 12 months) | dhanhq.co/docs/v2/authentication |
| Angel One | `loginByPassword` with client code, PIN and TOTP, returning a JWT; publisher login also exists | smartapi.angelone.in/docs, User and FAQ |
| ICICI Breeze | Browser login gives `API_Session`; `CustomerDetails` returns `session_token`; requests are signed with SHA-256 of timestamp, JSON and secret; generated manually each day | icicidirect.com FAQ "What is a session key" |
| Fyers | Auth code; `appIdHash` = SHA-256 of `app_id:app_secret`; returns an access and a refresh token; refresh-token lifetime unverified | fyers.in/api-docs, validate-auth-code |

## Order rate limits

| Broker | Order rate limit |
|---|---|
| Zerodha Kite | kite skill §8g |
| Upstox | Unregistered: 10/s; registered: 50/s; 500/min, 2000/30 min, combined over place, modify, cancel, multi and GTT |
| Dhan | 10/s, 250/min, 1000/h, 7000/day; 25 modifications per order |
| Angel One | `placeOrder`, `modifyOrder`, `cancelOrder`: each 9/s, 500/min, 1000/h |
| ICICI Breeze | 100 calls/min, 5000/day; 10 orders/s combined over place, modify, cancel and square-off |
| Fyers | From 16 Oct 2026, Standard plan (no Prime subscription): transaction APIs 10/s, 200/min, 100000/day, data APIs 5/s, 50/min, 5000/day; Prime: 10/s, 500/min, 500000/day for both ([notice](https://fyers.in/notice-board/changes-to-fyers-api-rate-limits-and-usage)); place, modify and cancel stay within 10/s |

## Not-yet-final statuses

Map every one of these to `PENDING` (or `UNKNOWN` where marked), never `REJECTED`.

| Broker | Statuses |
|---|---|
| Zerodha Kite | `PUT ORDER REQ RECEIVED`, `VALIDATION PENDING`, `OPEN PENDING`, `MODIFY VALIDATION PENDING`, `MODIFY PENDING`, `TRIGGER PENDING`, `CANCEL PENDING`, `AMO REQ RECEIVED` |
| Upstox | `put order req received`, `validation pending`, `open pending`, `trigger pending`, `modify pending`, `modify validation pending`, `cancel pending`, `after market order req received`, `not cancelled`, `not modified` |
| Dhan | `TRANSIT` ("did not reach the exchange server"), `PENDING` |
| Angel One | `open pending`, `trigger pending`, `modify pending`, `after market order req received`, `modify after market order req received` |
| ICICI Breeze | `Requested`, `Queued`; meaning of `Ordered` and `Freezed` unverified, so map them to `UNKNOWN` |
| Fyers | `4` Transit, `6` Pending; async place returns `id_fyers`, not an order ID |

## Sandbox

| Broker | Sandbox |
|---|---|
| Zerodha Kite | None documented |
| Upstox | Yes, sandbox apps and tokens |
| Dhan | Yes, closed environment, not paper trading (dhan.co support) |
| Angel One | None documented |
| ICICI Breeze | None documented |
| Fyers | None documented |

## More traps

- Upstox Place Order only works from 5:30 AM to 12:00 AM IST (`UDAPI100074`).
- Fyers blocks the user for the rest of the day after the per-minute limit is exceeded more
  than 3 times in a day.
- Breeze covers NSE only and routes unregistered algos through a single API key.
- Dhan's order book carries an `algoId` field.
