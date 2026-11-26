---
name: indian-broker-api-safety
description: SEBI retail algo trading framework and per-broker API deltas for Indian broker APIs (Upstox, Dhan, Angel One SmartAPI, ICICI Breeze, Fyers, Zerodha Kite). Covers the 4 Feb 2025 SEBI circular and its phased dates to 1 Apr 2026, NSE implementation standards, the 10 orders-per-second threshold, exchange algo ID tagging, static IP whitelisting and weekly change limit, OAuth and 2FA, no open APIs, white-box vs black-box algos and Research Analyst registration, family-only algo sharing, kill switch, the ban on algo market orders, and per-broker token expiry, order tag limits, rate limits, pending or in-transit statuses and sandbox. Use when writing or reviewing an Indian algo trading bot, a multi-broker adapter or order-status mapper, order throttling, static IP or Lambda or cloud deployment for broker APIs, or when asked whether a retail algo needs registration, may be shared with friends, or may use market orders, even if SEBI is not mentioned. Kite-only code: kite-connect-safety.
license: MIT
compatibility: SEBI and NSE circulars and broker API docs as read on 2026-11-11. Broker limits change without notice; re-check each broker's docs before hard-coding.
metadata:
  author: hariharanvisves
  version: "1.3"
  jurisdiction: India
  verified: "2026-11-11"
---

# Indian Broker API Safety

The regulatory layer and per-broker deltas for retail API and algo trading in India. A
bot that works on one broker's constants (6 AM expiry, 20-character tags, a retry on
failure) breaks on the next, and a pre-framework flow is non-compliant. General order-safety
rules live in [kite-connect-safety](../kite-connect-safety/SKILL.md) and are not repeated
here: server-side tokens (§3), authorization (§5), order ceiling (§8a), intent-derived
idempotency key (§8b), the `unknown` outcome (§8c–8d) and the rebalance planner (§9). This
skill says how those rules land on each broker. Anything marked "unverified" was not
confirmed in a primary source.

## Core rules

1. The full framework applies to every broker since 2026-04-01; do not gate code on "if my
   broker has gone live" (§1).
2. The broker is the principal. A deployment holding even one outsider's broker token is
   an algo provider and needs empanelment (§2).
3. Every API order is an algo order and is tagged. At or below 10 orders per second only
   registration is waived; the broker sends generic ID `99999` (§3).
4. Order APIs need a broker-whitelisted static IP; home broadband, Lambda and CI runners
   fail. Reads are usually exempt (§4).
5. Hidden-logic "signals plus auto-execute" for other people is a black-box algo and needs
   Research Analyst registration (§5).
6. A self-built algo registered above the threshold serves family only: self, spouse,
   dependent children, dependent parents (§6).
7. Algo orders are never market orders: send a limit price or the broker's protection field (§7).
8. Never reuse one broker's expiry, tag or rate constants for another (§8).
9. A pending, in-transit or unlisted status is never `REJECTED`; unlisted maps to `UNKNOWN`
   and the order is not retried (§9).
10. Entry-side limits (daily loss, trades per day, entry window) block opening orders only;
    a closing or reducing order is never blocked by them (§7).

Primary sources, read 2026-11-11:
- SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013, 4 Feb 2025
  (https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html)
- SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/132, 30 Sep 2025 (the glide path)
- NSE/INVG/67858, 5 May 2025, the implementation standards
  (https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf; alternate host
  https://nsearchives.nseindia.in/content/circulars/INVG67858.pdf)
- NSE/INVG/69255, 22 Jul 2025, the detailed operational modalities, and corrigendum NSE/INVG/69289
- NSE retail algo FAQ, 3 Nov 2025
  (https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf)

## 1. Effective dates

| Date | Event | Source |
|---|---|---|
| 2025-02-04 | Framework issued; first effective date was 2025-08-01 | SEBI CIR/2025/0000013 ¶7 |
| 2025-05-05 | NSE implementation standards | NSE/INVG/67858 |
| 2025-07-22 | NSE detailed operational modalities | NSE/INVG/69255 |
| 2025-07-29 | Start moved to 2025-10-01 | SEBI CIR/2025/108, cited in NSE/INVG/69372 |
| 2025-10-01 | Brokers whose systems were ready went live | SEBI CIR/2025/132 ¶4 |
| 2025-10-31 / 2025-11-30 / 2026-01-03 | Glide path: apply to register, complete registration, attend a mock session | SEBI CIR/2025/132 ¶4 |
| 2026-01-05 | Brokers that missed a milestone cannot onboard new retail API-algo clients | SEBI CIR/2025/132 ¶5 |
| 2026-04-01 | Framework applies to **all** stock brokers | SEBI CIR/2025/132 ¶8 |

**Rule.** Code written today runs under the full framework. Do not gate it on
"if my broker has gone live". **Why.** Since 2026-04-01 the framework applies to every
broker. A pre-framework flow (dynamic IP, untagged orders, market orders) is non-compliant,
and brokers reject it (for example Upstox `UDAPI1154` and `UDAPI1158`).
**Detector.** Grep for comments or flags such as `ALGO_RULES_ENABLED`; they should not exist.

## 2. Who is responsible

**Rule.** The broker is the principal. Any algo provider, fintech or vendor using the
broker's API is its agent (SEBI ¶5.I(a)). Algo providers must be empanelled with each
exchange where they trade (SEBI ¶5.III(a); NSE/INVG/67858 §E.1). Algos from algo
providers must run on the broker's servers. A self-hosted "tech-savvy" client instead
hosts the algo behind their own static IP (NSE FAQ Q4–Q5, citing NSE/INVG/69255 ¶14).

**Why.** A generic agent builds a multi-user SaaS that holds many users' broker tokens and
places their orders from its own cloud. That is an algo provider. It needs empanelment and
a commercial or technical arrangement with each broker. A personal script does not.

**Detector.** Count the distinct broker accounts whose tokens one deployment holds. Even
one account of a person outside the family (§6) means you are an algo provider.

## 3. Every API order is an algo order

**Rule.**
- All orders received through the API count as algo orders and must be tagged (NSE/INVG/69255
  ¶2.8; NSE FAQ Q8).
- The Threshold Order Per Second (TOPS) is **10 orders per second per exchange/segment**. It
  is measured on the broker server's calendar second, and the exchange may change it after
  notice (NSE/INVG/67858 §B.2, §F, 5 May 2025). TOPS starts at 10 orders/s; orders above it need exchange registration. Kite limits: 10/s, 400/min, 5,000/day (<https://kite.trade/docs/connect/v3/exceptions/>).
- **At or below 10 OPS**, the client does not register. The exchange still issues a
  *generic* algo ID, and the broker sends `99999` in the algo ID field (NSE/INVG/69255 ¶8.2.4).
- **Above 10 OPS**, the client registers the algo with each exchange through the broker,
  and orders carry the exchange-issued algo ID (NSE/INVG/67858 §C.1–C.2).
- The broker rejects orders above the limit and may set a lower per-client limit
  (NSE/INVG/67858 §B.5, §F).
- With several API keys, unregistered algos may run through only one predefined key
  (NSE/INVG/67858 §A.4).

**Why.** "Under 10 OPS means no rules" is the common wrong answer. Tagging, static IP and
2FA apply at any rate; only registration is waived. An invented algo ID field is also
wrong. Send an algo ID only where the broker documents one, such as Upstox's `X-Algo-Name`
header or the IDs configured in its Algo Apps settings
(https://upstox.com/developer/api-documentation/announcements/algo-trading-circular).

**Detector.** One client-side limiter per API key covers place, modify and cancel together
on every exchange, with a sliding one-second window set below the broker's limit (§8). Broker
limits count per API key across exchanges (Kite: [kite-connect-safety](../kite-connect-safety/SKILL.md)
8g), so a per-exchange limiter lets two exchanges together exceed it. Auto-slicing
creates separate orders with their own order IDs (Fyers single-order docs), so count every
slice. A test fires 30 intents in one second and expects at most the limit to leave the process.

```python
class SlidingLimiter:   # one per API key, shared by place, modify and cancel on every exchange
    def __init__(self, limit, window=1.0):          # limit set below the broker's own
        self.limit, self.window, self.sent, self.lock = limit, window, deque(), Lock()

    def acquire(self):
        with self.lock:                             # waiters queue here; sleeping holds the window
            while True:
                now = monotonic()
                while self.sent and now - self.sent[0] >= self.window:
                    self.sent.popleft()
                if len(self.sent) < self.limit:
                    self.sent.append(now)
                    return
                sleep(self.window - (now - self.sent[0]))
```

## 4. Static IP, keys and sessions

**Rule.**
- API order access needs a static IP whitelisted by the broker: one primary and an optional
  secondary. Mapped IPs change at most once per calendar week (NSE/INVG/67858 §A.1–A.2, §A.6).
- A static IP maps to one client. Only members of one family may share it, on a written,
  registered-email or 2FA request (§A.7).
- The client's own static IP is needed only when the client runs their own algo. With a
  vendor platform hosted at the broker, the broker server's IP applies (NSE FAQ Q3, Q6, Q10).
- Every API session must be logged out daily before the next trading day starts (§A.8).
  This is why most broker tokens in §8 expire overnight. Dhan's token is valid 24 hours
  from generation (docs.dhanhq.co authentication). Dhan documents no logout or
  revocation call, so renew or regenerate it daily and drop the token at day end. Renew
  (`GET /RenewToken`) works only on an active token; the API key and secret last 12 months.
- Open APIs are not permitted. Access goes only through a unique vendor-client API key plus
  the whitelisted IP. Authentication is OAuth-based and API access needs 2FA (SEBI ¶5.I(d);
  NSE/INVG/67858 §I.c–e).

**Why.**
- Serverless functions, autoscaled containers, CI runners and home broadband egress from
  changing addresses. Order calls from them fail.
- Rotating the IP is rate-limited. On Upstox, changing it invalidates existing access tokens
  (https://upstox.com/developer/api-documentation/announcements/algo-trading-circular).
- Read endpoints are usually exempt: Upstox (same page) and Dhan (https://dhanhq.co/docs/v2/authentication/).
  For Kite, WebSocket data and read endpoints work from any IP; see
  [kite-connect-safety](../kite-connect-safety/SKILL.md) 8h.
  So a deployment can pass every read-path test and still fail on its first order.

**Detector.** Run a startup check: compare the egress IP to the broker's registered IP
(Upstox `GET /user/ip`; Dhan's static IP APIs). Refuse to arm the order path on a mismatch.
Treat a public webhook that places orders without authentication as an open API in spirit
(engineering inference). Put the kite skill §5 middleware in front of it.

## 5. Algo categories: white box and black box

**Rule.** A white-box (execution) algo has logic that is disclosed and replicable. A
black-box algo has logic the user cannot see or replicate (SEBI ¶5.V and footnotes 5–6).
For a black-box algo:
- The provider registers as a SEBI Research Analyst and keeps a research report for each algo.
- Any logic change needs a fresh registration (SEBI ¶5.V).
- Registered black-box algos cannot be modified (NSE/INVG/69255 ¶9.9).
- An RA must become an empanelled algo provider before offering one (NSE FAQ Q4).

NSE's strategy list (NSE/INVG/69255 ¶2.4.5):
- White box: execution, TWAP, VWAP.
- Black box: arbitrage, alpha seeking, high frequency, scalping, others.

**Why.** Selling or offering "signals plus auto-execute" with hidden logic to other people
puts the provider in the RA-registration category. A licence file does not change that.

**Detector.** If the product shows users only entry and exit actions and not the rules,
classify it as black box before writing more code.

## 6. Sharing an algo

**Rule.** A self-built algo registered above the threshold may be used only for the
developer's family: self, spouse, dependent children and dependent parents. It may not be
used for other investors (SEBI ¶5.I(c)).

**Why.** Running it on a friend's account makes you an unempanelled algo provider (§2).
**Detector.** Each account in config must map to a family relation recorded by the owner.

## 7. Kill switch and pre-trade checks

**Rule.**
- The exchange can kill orders from a given algo ID. SEBI defines the kill switch as the
  last line of defence, which halts trading automatically on pre-defined conditions
  (SEBI ¶5.IV(a)(iii), footnote 4; NSE/INVG/67858 §J.3).
- Your own algo needs the matching control. It must account for every executed,
  unexecuted and **unconfirmed** order before releasing more. It must also stop itself
  in a loop or runaway (NSE/INVG/69255 ¶11.1, item 7).
- Algo orders must not be market orders (NSE FAQ Q11, citing NSE/MSD/67753 ¶8.1.1.12).
  NSE's pre-open page (updated 04/09/2026) states one exception: "Algo market orders shall
  be allowed during initial 5 mins of order entry period"
  (https://www.nseindia.in/static/products-services/equity-market-pre-open).
  Brokers enforce this:
  - Breeze: market orders are not permitted.
  - Upstox: error `UDAPI1158`, "Market orders are not allowed".
  - Kite: market protection converts market orders to limit orders.
  - Fyers: market order type `2` carries Market Price Protection (MPP).

**Why.** An agent writes `order_type="MARKET"` by default. It also writes a retry loop
that keeps sending while confirmations lag. That loop is the runaway the rule forbids.

**Detector.**
- Grep the live path for `MARKET`. Every hit sends a limit price or the broker's market
  protection field.
- Run a fault-injection test: the broker returns pending forever. The bot must halt after
  N unconfirmed orders, not after N rejections. This is the kite skill §8d rule with a
  regulatory basis.

**Entry-side limits never trap a position.** This is an engineering rule about your own
client's limits, not a statement of what the exchange or broker kill switch blocks. SEBI's
4 Feb 2025 circular ¶5.IV(a)(iii) and NSE/INVG/67858 §J.3 say the kill switch halts trading
from an algo ID; neither says whether exits pass.
- Daily-loss, trades-per-day and entry-time-window limits gate **opening** orders only: those that
  open or increase a position.
- A closing or reducing order always passes them, so a tripped limit cannot leave a position
  open that the bot can no longer exit.
- Refuse an exit only when it is malformed or larger than the open position, because that would
  flip or open a position. Cap an oversized exit to the position or reject it; never let it
  through as a new entry.

```python
def admit(signed_qty, position, limits_tripped):
    if signed_qty == 0 or signed_qty * position < 0 and abs(signed_qty) > abs(position):
        return False                      # malformed, or an over-sized exit that would flip
    reduces = signed_qty * position < 0
    return reduces or not limits_tripped  # exits skip entry limits; entries obey them
```

**Why.** A daily-loss limit is tripped exactly when the position is most dangerous. If the
same limit also blocks the exit, the bot holds a losing position it was built to cut.

**Detector.** Trip the daily-loss limit, then send an exit for the open quantity: it must go
through. Send an entry in the same state: it must be refused. Send an exit larger than the
position: refused or capped.

## 8. Per-broker deltas

Token expiry and tag limits, read 2026-11-11 from each broker's own docs:

| Broker | Token expiry | Client tag field |
|---|---|---|
| Zerodha Kite | 6 AM next day (kite.trade/docs/connect/v3/user) | `tag`, alphanumeric, max 20 |
| Upstox | 3:30 AM next day, whatever the issue time (upstox.com/developer/api-documentation/get-token) | `tag`, max 40 (`UDAPI1119`) |
| Dhan | 24 hours from generation (dhanhq.co/docs/v2/authentication) | `correlationId`, max 30, `[a-zA-Z0-9 _-]` |
| Angel One | Until 12 midnight (smartapi.angelone.in/docs, User and FAQ) | `ordertag`, under 20 chars (`AB4008`) |
| ICICI Breeze | 24 hours or midnight, whichever is earlier; generated manually each day (icicidirect.com FAQ "What is a session key") | `user_remark`, no spaces or special characters; length unverified |
| Fyers | 6:30 AM daily; refresh-token lifetime unverified (fyers.in/api-docs, validate-auth-code) | `orderTag`, 1–30 alphanumeric, not the client ID or `Untagged` |

Read [references/broker-deltas.md](references/broker-deltas.md) for each broker's auth flow,
order rate limits, full not-yet-final status lists, sandbox availability and extra traps
(Upstox order window, Fyers daily block, Breeze NSE-only). Read it before building the
status tables in section 9 or a limiter.

**Rule.** Do not reuse one broker's constants for another. **Why.** Hard-coding Kite's 6 AM
expiry or 20-char tag across brokers breaks Upstox at 3:30 AM, and silently truncates or
rejects Dhan and Fyers keys.

**Detector.** Keep one constants module per broker, and have it cite its docs URL and
verification date. Write a test that checks expiry for every broker at 03:29, 03:31,
06:01 and 06:31 IST.

## 9. Portability adapter: normalise, fail closed

**Rule.**
- Each broker adapter maps raw status to one internal set:
  `PENDING | OPEN | PARTIAL | FILLED | CANCELLED | REJECTED | EXPIRED | UNKNOWN`.
- Keep the mapping as an explicit lookup table per broker, built from the status lists in [references/broker-deltas.md](references/broker-deltas.md).
- Normalise case and whitespace before the lookup (Upstox is lowercase, Kite uppercase,
  Fyers uses integers, Breeze uses words).
- **A status the table does not list maps to `UNKNOWN`.** `UNKNOWN` follows the kite
  skill §8d path: no retry, no auto-cancel, suspend the account.
- `TRANSIT`, Fyers `id_fyers` acknowledgements and every "pending" state are `PENDING`,
  never `REJECTED`.
- Derive the tag from the kite skill §8b key, store the tag that was sent in the order
  record, and reconcile by it (kite skill §8b owns that rule). This skill owns the
  per-broker lengths: the portable short form is alphanumeric and at most 19 characters,
  so it fits Angel's under-20 rule and every stricter alphabet.

**Why.**
- A default branch that returns `REJECTED` invites a retry, and the retry is a double order.
- Substring matching marks Upstox `not cancelled` as cancelled, although that order is
  still live.

```python
STATUS = {   # exact lookup per broker, keys lowercased; extend from the reference lists
    "dhan":   {"transit": "PENDING", "pending": "PENDING"},
    "fyers":  {4: "PENDING", 6: "PENDING"},
    "upstox": {"open pending": "PENDING", "not cancelled": "PENDING", "not modified": "PENDING"},
}

def normalise(broker, raw):
    key = raw.strip().lower() if isinstance(raw, str) else raw
    return STATUS[broker].get(key, "UNKNOWN")   # never substring, never default REJECTED

def portable_tag(intent_key: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", intent_key)[:19]   # under Angel's limit, inside every other
```

Dhan `TRANSIT` gives `PENDING`, so the bot does not resend and reconciles by `correlationId`.
A 32-character hex UUID as tag breaks Kite (max 20) and Angel (under 20); `portable_tag`
returns 19 characters of it.

**Detector.**
- For each broker, a test feeds every documented status and expects a mapped value.
- A random string must map to `UNKNOWN`.
- `grep -rnE "default:|\.get\(status, |in status" src/*adapter*` must find no
  fallback other than `UNKNOWN` and no substring match.
- A property test checks that every generated tag passes all six brokers' tag rules.

## Verifying an implementation

- No flag gates the framework on a broker's go-live date (§1).
- 30 intents in one second let at most the limiter's limit through, slices included (§3).
- The startup egress-IP check refuses to arm the order path on a mismatch (§4).
- No live-path `MARKET` order type without a limit price or protection field (§7).
- Expiry tests pass at 03:29, 03:31, 06:01 and 06:31 IST per broker (§8).
- Every documented status maps; a random string maps to `UNKNOWN`; `TRANSIT` never
  maps to `REJECTED`; every generated tag passes all six brokers' rules (§9).

## Scope

Engineering guidance on the SEBI retail-algo framework and broker APIs, current to
2026-11-11. It is not legal or investment advice, and it does not certify any algo as
compliant. Re-check circulars and broker docs before relying on a limit. Companion skills:
[kite-connect-safety](../kite-connect-safety/SKILL.md),
[indian-equity-charges](../indian-equity-charges/SKILL.md).
