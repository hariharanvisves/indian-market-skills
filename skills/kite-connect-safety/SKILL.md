---
name: kite-connect-safety
description: Safety rules for integrating Zerodha Kite Connect (kiteconnect, pykiteconnect, Kite MCP) — login and SHA-256 checksum flow, 6 AM token expiry, server-side-only credentials, authorization (not just authentication), order-value ceilings, intent-derived idempotency keys, the UNKNOWN order outcome after a timeout, stale-quote policy, static IP, live-path hard-disable, position-aware rebalancing (holdings plus T1) and MCP hygiene. Use when writing or reviewing Kite login, request_token / access_token handling, a place_order wrapper with retries, rebalance or automation code on Zerodha, or any route that touches a Kite token, even if the user only asks for a quick order script. Owns the general broker-API safety principles; for SEBI algo rules or Upstox, Dhan, Angel One, Breeze or Fyers use indian-broker-api-safety.
license: MIT
compatibility: Written against Kite Connect v3 (https://kite.trade/docs/connect/v3/); the principles apply to any Indian broker REST API.
metadata:
  author: hariharanvisves
  version: "1.3"
  verified: "2026-11-11"
  jurisdiction: India
---

# Kite Connect Safety

Defects here move real money or leak the highest-value secret in the system. Each item
gives the rule, why, and a detector you can run. API facts cite the Kite Connect v3 docs as
read on 2026-10-04; anything marked "verify" was not confirmed, so check
https://kite.trade/docs/connect/v3/ before relying on it. Other brokers and SEBI retail-algo
rules: [indian-broker-api-safety](../indian-broker-api-safety/SKILL.md).

## Core rules

1. The checksum is SHA-256 of `api_key + request_token + api_secret`, computed on the
   server (§1).
2. The `access_token` expires at 6 AM next day: expiry is a normal state, and a `403` with
   `TokenException` means re-login, not retry (§2).
3. `api_secret`, `request_token` and `access_token` never reach the browser, logs or errors (§3).
4. Authenticate, authorize the owner, then rate limit; an unset owner setting means 403 (§5).
5. The live path stays hard-disabled (409) until the owner authorises it (§7).
6. A local order-value ceiling exists from day one and fails closed (§8a).
7. Derive the idempotency key from the order's intent, not the click, and claim it
   atomically before sending (§8b).
8. A timeout after send is `unknown`, not `rejected`: no retry, no auto-cancel, suspend
   automation, reconcile by `tag` or order id (§8c, §8d).
9. API orders need a whitelisted static IP from 2026-04-01; reads and WebSocket work
   from any IP (§8h).
10. Holdings = settled + `t1_quantity`; a holdings read failure places nothing (§9).
11. A risk-check PASS covers only the exact order it was computed for; any edit voids it, and a
    BLOCK is final (§8i).

Worked sketches for rules 6 to 8 and 11 are in section 8.

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

**Detector.** A test that feeds a `now` of 05:59 IST and 06:01 IST and asserts the expiry
moves by a day. Grep for retry loops around calls that can raise `TokenException`.

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
locally and name the ceiling. A missing, NaN, zero or negative value, or a
non-finite ceiling, also rejects. Raising it is step-up. Detector: place an order
over the cap, and one valued NaN; the broker client must not be called.

**8b. Intent-derived idempotency key.** Derive the key from the order's intent —
`(account, instrument, side, qty, type, price, trigger, product, pad-session)` —
not from the click. Two presses of an unchanged pad replay one key and return
the original order. Kite's `tag` field is optional, alphanumeric, max 20 chars
(orders docs); use it to carry the key's short form so the order can be found
again. Store the exact tag sent in the order record and reconcile by that stored value,
never by deriving it again; other brokers' tag lengths are in
[indian-broker-api-safety](../indian-broker-api-safety/SKILL.md) §8. Claim the key with an
atomic insert-if-absent (a unique-key insert) of a `pending` record **before** sending, so
two concurrent presses cannot both send. A stored result, `rejected` included, is replayed
for the same key: retrying a rejected order takes a new intent (a new pad session gives a
new key). Detector: submit the same intent twice, also from two threads at once; exactly
one broker call.

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

```python
def intent_key(a):        # a: account, instrument, side, qty, otype, price, trigger, product, pad_session
    raw = "|".join(str(x) for x in (a.account, a.instrument, a.side, a.qty, a.otype,
                                    a.price, a.trigger, a.product, a.pad_session))
    return hashlib.sha256(raw.encode()).hexdigest()

def check_ceiling(order_value, ceiling):                 # 8a: fail closed
    try:                                                 # ceiling = min(ABS_CAP, PCT * equity)
        ok = math.isfinite(order_value) and math.isfinite(ceiling) and 0 < order_value <= ceiling
    except TypeError:                                    # None or not a number
        ok = False
    if not ok:                                           # NaN, <= 0, over the cap, inf ceiling
        raise LocalReject(f"order value {order_value!r} not within ceiling {ceiling!r}")

def place_once(store, broker, a, order_value, ceiling):
    key = intent_key(a)
    tag = key[:20]                                       # 8b: Kite tag, alphanumeric, max 20
    if store.suspended(a.account):
        raise Suspended(a.account)                       # 8d: an earlier unknown is unresolved
    check_ceiling(order_value, ceiling)
    if not store.claim(key, Result("pending", tag=tag)): # atomic insert-if-absent, before send
        prior = store.get(key)
        if prior.status == "pending":                    # in flight, or a crash after send
            return Result("unknown", tag=prior.tag)      # reconcile; never send again
        return prior                                     # placed, rejected or unknown: replay
    try:
        result = Result("placed", tag=tag, order_id=broker.place(a, tag=tag))
    except BrokerRejected as e:                          # explicit rejection from the broker
        result = Result("rejected", tag=tag, reason=str(e))
    except Exception:                                    # 8c: anything else, the request may have left
        result = Result("unknown", tag=tag)
        store.update(key, result)                        # record first, then suspend
        store.suspend(a.account)                         # no retry, no auto-cancel
        return result
    store.update(key, result)
    return result

def reconcile(broker_orders, record):                    # 8d: by the stored tag, never a fuzzy tuple
    hits = [o for o in broker_orders if o.tag == record.tag]
    return hits[0] if len(hits) == 1 else None           # 0 or several: a human decides
```

Wrong: `except TimeoutError: return place_order(...)` sends a second live order when the first
reached the exchange. Right: the second call returns `unknown` with automation suspended,
and `reconcile` finds the order by the tag stored in the record. A `pending` record left
by a crash between send and update also reads as `unknown`; on startup, suspend the
account of every `pending` record and reconcile it.

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

**8i. Risk verdict bound to the exact order.** A risk check that approves "an order" and
a sender that sends "the order" can drift apart: the user edits the quantity after the PASS and the
edited order goes out unchecked. Fingerprint the order (instrument, exchange, side, qty, order
type, price, trigger, product, validity) and store each verdict under `(session, fingerprint)`.
The executor sends only when a `PASS` exists for the fingerprint of the order in hand, in the
current session. Any edit changes the fingerprint, so the old PASS no longer applies and the check
runs again. A `BLOCK` is final for that fingerprint: asking again returns the stored BLOCK, and
only a changed order or an explicit step-up override can proceed. This gate decides *whether* an
order may go; the idempotency key (§8b) decides whether it already went. Keep both, as the key
omits the verdict and the fingerprint omits the pad session. Detector: get a PASS, raise `qty` by
one, then send; the broker client must not be called. Also: re-run a BLOCKed order unchanged; it
stays blocked.

```python
def fingerprint(o):       # o: instrument, exchange, side, qty, otype, price, trigger, product, validity
    raw = "|".join(str(x) for x in (o.instrument, o.exchange, o.side, o.qty, o.otype,
                                    o.price, o.trigger, o.product, o.validity))
    return hashlib.sha256(raw.encode()).hexdigest()

def send_checked(verdicts, session, broker, o):
    if verdicts.get((session, fingerprint(o))) != "PASS":   # missing, BLOCK or edited order
        raise LocalReject("no PASS for this exact order in this session")
    return broker.place(o)
```

## 9. Position-aware rebalance planner

**Rule.** Diff targets against actual holdings and emit BUY / SELL / HOLD /
IGNORE rows (IGNORE: held but not managed by the app).
- Holdings quantity = settled + **T1** (`t1_quantity`; unsettled same-day shares count
  as owned), else a re-run double-buys.
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

**Why.** A planner that misses T1 buys again on a same-day re-run, and an account-wide
sweep liquidates holdings the app never bought.

Plan-and-approve execution, owned-quantity bookkeeping, input validation and test traps:
[references/rebalance-planner.md](references/rebalance-planner.md). The rebalance function
only plans; one executor is the sole caller of `placeOrder`, behind the §7 gate.

**Detector.** Fixture with an ETF in holdings and not in the managed set: it must come out
`IGNORE`. Run the planner twice: the second run is all HOLD. Make the holdings call throw:
nothing is placed.

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
- The hosted Kite MCP (`mcp.kite.trade`) is read-only: login via Kite, no credential
  sharing with the AI tool, and no order tools ("excludes potentially destructive
  trading operations", zerodha/kite-mcp-server README). Config is read at client
  startup. It is distinct from your own SDK-based order code.
- A **self-hosted** Kite MCP exposes order-placement tools to whatever model is
  attached. Treat that as a live path: do not enable it unattended, and prefer
  read-only tool subsets.
- Do not expose portfolio tools through MCP if ownership checks live only in
  HTTP handlers — direct service calls bypass them.
- NSE's own MCP servers are read-only market data with non-commercial terms:
  [nse-official-mcp](../nse-official-mcp/SKILL.md).

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
