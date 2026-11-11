---
name: kite-connect-safety
description: Safety rules for integrating Zerodha Kite Connect (kiteconnect, pykiteconnect, Kite MCP) — login and checksum flow, daily token expiry, server-side-only credentials, authorization (not just authentication), order-value ceilings, intent-derived idempotency keys, the UNKNOWN order outcome, stale-quote policy, live-path hard-disable, position-aware rebalancing, and MCP hygiene. Use when writing or reviewing Kite login, request_token / access_token handling, order placement, rebalance or automation code on Zerodha, or any route that touches a Kite token.
license: MIT
compatibility: Written against Kite Connect v3 (https://kite.trade/docs/connect/v3/); the principles apply to any Indian broker REST API.
metadata:
  author: hariharanvisves
  version: "1.1"
  verified: "2026-11-11"
  jurisdiction: India
---

# Kite Connect Safety

Defects here move real money or leak the highest-value secret in the system.
Each item: the rule, why, and a detector you can run. API facts cite the Kite
Connect v3 docs as read on 2026-10-04; anything marked "verify" was not
confirmed — check https://kite.trade/docs/connect/v3/ before relying on it.
Other brokers and SEBI retail-algo rules: [indian-broker-api-safety](../indian-broker-api-safety/SKILL.md).

## 1. Login flow and checksum

**Rule.** Three steps: send the user to the Kite login page with your `api_key`;
Kite redirects to the redirect URL registered on the developer console with a
`request_token` query parameter; your **server** POSTs `request_token` and
`checksum` to get an `access_token`. Checksum = SHA-256 of
`api_key + request_token + api_secret` (hex), per the docs' user/login page.

**Why.** The `request_token` lives only a few minutes and must be exchanged
immediately. The `api_secret` is in the hash, so the exchange can only run where
the secret lives.

**Detector.** `grep -rn "createHash('sha256')\|sha256" src/` finds one checksum
function; a unit test with a fixed triple pins the digest. Confirm the redirect
URL registered on the console equals the one your server actually serves
(including port and path) — a mismatch looks like a hung login, not an error.

## 2. Daily token expiry is a normal state

**Rule.** The docs state the `access_token` expires at **6 AM the next day**
(regulatory requirement), earlier on logout or master-logout, or when the user
logs in to another Kite instance. A `403` with `TokenException` means the
session is gone: clear it and re-initiate login. Compute expiry in IST (UTC+5:30,
no DST, so 00:30 UTC is a constant).

**Why.** Treating expiry as an exception produces retries with a dead token and
alerts every morning. It is also a feature: automation must stop, not loop,
when the session lapses.

**Detector.** A test that feeds a `now` of 05:59 IST and 06:01 IST and asserts
the expiry moves by a day. Grep for retry loops around calls that can raise
`TokenException`.

## 3. Token exchange and storage: server-side only

**Rule.** The `api_secret`, `request_token` and `access_token` never reach the
browser, a log line, an error body, a URL you generate, an export or a backup
used for development. The browser holds your app session; the server holds the
broker session. Store credentials in env vars or a KMS-backed envelope, never as
plaintext in a database column.

**Why.** One leaked token is full account access until 6 AM. A route that
"connects" and returns the token to confirm success is the classic leak.

**Detector.**
- Seed a known sentinel credential, then assert the sentinel string appears in
  **no** response body across the whole route table. Name-independent, so a
  field rename cannot defeat it.
- Brand the credential type with a `toJSON()` that throws, so serialising one
  fails loudly.
- `grep -rnE "console\.(log|error)\(.*(token|secret)" src/` and check error
  handlers do not echo upstream request bodies.
- `grep -rn "access_token\|api_secret" <client bundle dir>` must be empty.

## 4. Capability must throw, never return empty

**Rule.** If the account's plan lacks a capability (the free personal tier does
not include live quotes, WebSocket streaming or historical candles — verify
current plan terms), the provider method **throws a typed capability error**.
It must not return `[]`, `0` or an empty order book.

**Why.** An empty book is a false claim about the market, not a degraded one. A
zero-filled quote renders like a live price.

**Detector.** For each provider method the plan cannot serve, a test asserts it
throws the capability error. `grep -rn "return \[\]\|return {}" src/*provider*`
should find no unsupported-capability path.

## 5. Authorization, not just authentication

**Rule.** Every broker route needs `authenticate → authorize owner → rate limit`.
When the app owns one brokerage account (single-owner model), compare the
authenticated user to a configured owner identity with exact, normalised
matching, and **fail closed** when the owner setting is unset (403, never
"allow"). Return a generic denial body.

**Why.** "Logged in" is not "owns this broker account". Any of N registered users
could read the owner's holdings or overwrite the shared access token.

**Detector.** Enumerate every route under the broker prefix; each must show the
owner middleware. Test with a second valid user and with the owner env var
unset — both must be 403.

## 6. Step-up re-auth before connecting a broker

**Rule.** Connecting, rotating or raising an order ceiling on a broker requires
a fresh step-up (e.g. TOTP) recorded on the **session**, not the user. Connecting
also notifies the user out of band.

**Why.** A stolen session cookie is exactly the attacker who connects their own
broker or lifts the ceiling. Recording step-up on the user lets a second session
inherit it.

**Detector.** Call the connect route with a session lacking step-up; expect a
refusal. Check the step-up flag column lives on the session table.

## 7. Live path hard-disabled until authorised

**Rule.** Non-dry-run execution returns a **409-style refusal** with a stable
code until the owner explicitly authorises it. The startup config refuses a
"live enabled" flag unless a live adapter is named and its credentials validate.
Remove the refusal only as a deliberate, recorded decision.

**Why.** A backtested strategy is not what a rebalance endpoint executes: risk
controls (stops, regime filters, rank exits) often exist only in the backtest
engine. Live money should not ride a path those controls never reached.

**Detector.** A behavioural check that boots the server with broker credentials
cleared and POSTs an execute request; expect 409. Coerce the dry-run flag
strictly — only boolean `false` or the string `"false"` disables it; `0`, `""`
and absent mean dry run.

## 8. Order safety

**8a. Default order-value ceiling.** A ceiling exists from account creation
(lesser of an absolute rupee cap and a percentage of equity). Above it, reject
locally and name the ceiling. Raising it is step-up. Detector: place an order
over the cap; the broker client must not be called.

**8b. Intent-derived idempotency key.** Derive the key from the order's intent —
`(account, instrument, side, qty, type, price, trigger, product, pad-session)` —
not from the click. Two presses of an unchanged pad replay one key and return
the original order. Kite's `tag` field is optional, alphanumeric, max 20 chars
(orders docs); use it to carry the key's short form so the order can be found
again. Detector: submit the same intent twice; exactly one broker call.

**8c. Three-state result.** `placed | rejected | unknown`. A timeout or a
5xx/network failure **after** the request left is `unknown`, not `rejected`. The
docs note that to know an order's true status you must scan order history or
fetch the order by `order_id`. Detector: make the client time out after the
request is sent; the result must be `unknown`, never `rejected`.

**8d. UNKNOWN is not failure.** On `unknown`: **no retry, no auto-cancel**,
suspend automation for that account until it resolves, and reconcile by
`tag`/order id. If only a `(instrument, side, qty, price, time)` tuple matches,
that is a *candidate* needing human acknowledgement; refuse to match when more
than one broker order fits. Detector: inject a timeout after send; assert zero
further placements and automation suspended.

**8e. Stale quote.** A stale quote **warns a human** (acknowledge, show last-tick
age) and **blocks a machine**. Blocking manual exits on thin stocks makes
illiquid positions un-exitable during fast moves. Detector: feed a quote older
than the threshold; a manual order asks for acknowledgement, an automated one
is refused.

**8f. Contract identity for F&O.** Show underlying, expiry, strike, option type
and lot size on confirmation, and check the lot-size multiple against `lot_size` in the
instrument dump. The dump has no freeze-quantity column; take freeze quantity
from the exchange's published file, never assume it. Detector: an F&O order
whose quantity is not a multiple of `lot_size` is rejected locally.

**8g. Rate limits.** Per the exceptions page: orders 10/second, 400/minute and
5000/day per user/API key; 25 modifications per order; quotes 1/second;
historical candles 3/second; other endpoints 10/second. Throttle client-side;
verify against the docs before hard-coding. Detector: burst 20 orders in one
second; the client must space them, not surface broker rate-limit errors.

**8h. Static IP.** From 2026-04-01 API order placement must come from a
whitelisted static IP (one primary, optionally one secondary; exchange rules
allow one change per calendar week). WebSocket data and read endpoints such as
orderbook and positions work from any IP
(https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip).
Detector: the deployed order path egresses from the registered IP; a dynamic
cloud or laptop address breaks it.

## 9. Position-aware rebalance planner

**Rule.** Diff targets against actual holdings and emit BUY / SELL / HOLD /
IGNORE rows (IGNORE: held but not managed by the app).
- Holdings quantity = settled + **T1** (unsettled same-day shares count as
  owned), else a re-run double-buys.
- A **managed** gate: exits only touch symbols the app itself bought. A real
  account holds ETFs, gold bonds and manual picks an account-wide "held but not
  in target, so sell" sweep would liquidate.
- A **holdings read failure throws**. No holdings view means no safe diff; the
  fallback "buy the whole basket" is the failure.
- Remove **unpriceable** symbols from the held map before diffing, so a quote
  failure cannot read as "exit this position".
- **SELL before BUY** for cash; if a SELL fails, stop — do not proceed to BUYs.
- Route exchange **per symbol** (NSE vs BSE). A hardcoded `NSE` errors on
  BSE-only holdings.
- Persist the real side; skip HOLD and IGNORE rows. Persist each order **before** placing
  the next so a crash cannot orphan live orders.

**Detector.** Fixture with an ETF in holdings and not in the managed set — it
must come out `IGNORE`. Run the planner twice — second run all HOLD. Make the
holdings call throw — nothing is placed.

## 10. Order records are an audit trail

**Rule.** A foreign key from the orders table to a user or scan uses
`ON DELETE SET NULL`, not `CASCADE`. A non-dry-run row records that money moved;
cascading it away destroys evidence. A NULL owner also fails safe on a sell
path (it matches no user's "ours to sell").

**Detector.** Assert the delete policy of **every** FK in a test, so a new FK
without a decision fails.

## 11. MCP hygiene

- A stdio MCP server's **stdout is the JSON-RPC channel**; diagnostics go to
  stderr. Detector: spawn it, send `initialize`, assert every stdout line
  parses as JSON.
- The hosted Kite MCP needs interactive OAuth per user; config is read at client
  startup. It is distinct from your own SDK-based order code.
- A **self-hosted** Kite MCP exposes order-placement tools to whatever model is
  attached. Treat that as a live path: do not enable it unattended, and prefer
  read-only tool subsets.
- Do not expose portfolio tools through MCP if ownership checks live only in
  HTTP handlers — direct service calls bypass them.

## 12. Terms of service

Do not assert that paper-trading or automation is permitted. Verify the broker's
terms and the exchange/SEBI retail-algo rules before enabling any automation;
the rules themselves: [indian-broker-api-safety](../indian-broker-api-safety/SKILL.md).

## Verifying an implementation

- One checksum function, pinned by a fixed-triple digest test (§1).
- Expiry test at 05:59 and 06:01 IST; no retry loop around `TokenException` (§2).
- A sentinel credential appears in no response body, log or client bundle (§3).
- Unsupported capabilities throw; none return `[]` or `0` (§4).
- Every broker route is 403 for a second valid user and for an unset owner (§5).
- Connect without step-up is refused; the flag lives on the session (§6).
- Execute with credentials cleared returns 409; dry run is the default (§7).
- Over-ceiling order, duplicate intent and post-send timeout each make the
  documented number of broker calls: zero, one, one (§8).
- Planner fixture: unmanaged ETF is IGNORE, second run is all HOLD, a holdings
  failure places nothing (§9).
- Every orders-table FK asserts `ON DELETE SET NULL` (§10).

## Scope

Kite Connect v3 integration safety: auth, tokens, orders, rebalancing, MCP.
Engineering guidance, not legal or investment advice. Companion skills:
[indian-equity-charges](../indian-equity-charges/SKILL.md),
[indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md).
