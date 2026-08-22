# Contracts — Chapter 3.11, Counting a connection

Four surfaces: the report the gateway sends, the refusal a client meets at the
socket door, the email a third dimension produces, and the figure an operator
reads. Plus one thing that is promised loudly because it would otherwise be
assumed: what the platform admits it can lose.

---

## 1. The report

```
POST /internal/usage/connections
Authorization: Bearer rk_svc_…
Content-Type: application/json
```

```json
{
  "connections": [
    { "connection_id": "0f9c…", "environment_id": "8b21…",
      "period": "2026-08-01", "minutes": 17 },
    { "connection_id": "0f9c…", "environment_id": "8b21…",
      "period": "2026-09-01", "minutes": 3 }
  ]
}
```

`minutes` is the **total** that connection has occupied in that period, not the
increase since the last report (research R3). The two entries above are one
connection that was open when the month turned over.

Response:

```json
{ "credited": 4 }
```

`credited` is the sum of the deltas actually applied, so a replay answers
`{"credited": 0}` and a caller can see that its retry changed nothing.

One field, because there is nothing else the caller can act on. An earlier draft
carried a `refused` count beside it, which described nothing: the only refusal in
this design is the 409 below, and it rejects the whole request rather than an
entry within it.

**Authorisation**: `@Accepts("platform")` and nothing else — the gateway's own
credential, from `RELAY_INTERNAL_CREDENTIAL_GATEWAY`, not the dispatcher's. An `application`
credential is scoped to one environment by construction and a report names
environments in its body; a route that accepted one would either be useless or
would have to ignore the scope, and ignoring a tenant scope is the shape a
cross-tenant hole takes (chapter 3.5's argument, unchanged).

**Refusals**:

| Status | Code | When |
|---|---|---|
| 401 | — | no credential, or one that does not match |
| 403 | `wrong_credential_type` | a good API key or user token |
| 400 | `invalid_request` | schema violation; a negative `minutes`; a `period` that is not the first of a month |
| 409 | `connection_environment_conflict` | this `connection_id` was first reported for a different environment |

The 409 is a tenant-isolation refusal, not a data-quality one: a connection does
not move between tenants, and reconciling one that appears to would be inventing
a fact.

**Batching**: one request carries every connection the instance holds. A report
is idempotent in whole and in part — a partially applied batch is not a state
the caller has to reason about, because reapplying the whole batch credits only
what is still owed.

---

## 2. The refusal at the door — two hops, two shapes

```
  client ──WebSocket──▶ gateway ──HTTP──▶ api
         ◀─ 4008 ──────         ◀── 402 ──
```

An earlier draft of this contract gave both hops the same shape and forwarded an
HTTP status onto a socket. The api speaks HTTP and the client speaks WebSocket;
translating between them is what the gateway is for (research R21).

### 2a. api → gateway

When connection-minutes usage is at or above the hard cap, `POST
/internal/session` answers:

```
HTTP/1.1 402 Payment Required
Content-Type: application/json
```

```json
{
  "code": "quota_exceeded",
  "message": "monthly connection-minute quota exhausted: 50000 of 50000 for 2026-08-01; connections resume on 2026-09-01",
  "docs_url": "https://relay.example/docs/errors/quota_exceeded",
  "request_id": "req_…"
}
```

**That is chapter 3.10's format, extended, not a new one.** `publicMessage()` in
`quotas/quota.error.ts` already produces

```
monthly {noun} quota exhausted: {usage} of {quota} for {period}; sends resume on {date}
```

and an earlier draft of this contract paraphrased it from memory as "quota
exceeded … used; resumes" — different verb, different order, different resume
clause. Two changes are needed to the real one and both are this chapter's:

1. **The noun is a two-way ternary today** —
   `dimension === "messages" ? "message" : "active user"` — so a third dimension
   renders "monthly **active user** quota exhausted" for a connection-minutes
   breach. `Dimension` is `keyof QuotaConfig`, so it widens on its own when the
   config key lands: the compiler catches nothing and the wrong word ships.
2. **"sends resume on" is wrong for this dimension.** What resumes is connecting.
   The resumed operation has to follow the dimension, in `publicMessage()` and in
   `resumesOn()`'s own doc comment, which also says "sends".

The code is **named by the thrower**, not inferred from the status:
`ProtocolErrorFilter` infers a code for four statuses and calls everything else
`internal_error`, which chapter 3.10's second analysis pass found the hard way.
So `session.controller.ts` catches `QuotaExceededError` and rethrows it as an
`HttpException` carrying the code, the way `messages.service.ts` already does.

**No `Retry-After`, and that is the whole difference from a rate limit.** A
client that retries after the header is right for a rate limit and wrong for a
quota, which will still be exceeded in an hour. The resume date is in the message.

### 2b. gateway → client

The handshake **completes**, an `error` frame goes out, and the socket closes
with `4008`:

```json
{ "type": "error",
  "payload": {
    "code": "quota_exceeded",
    "message": "monthly connection-minute quota exhausted: 50000 of 50000 for 2026-08-01; connections resume on 2026-09-01",
    "docs_url": "https://relay.example/docs/errors/quota_exceeded",
    "request_id": "req_…" } }
```

```
close 4008 "quota exhausted"
```

**This is the 4001 path's shape, for the 4001 path's reason.** Chapter 3.8's
comment in `session.ts` says the bad-token refusal "COMPLETES the handshake in
order to close it — because EIR-WS-05 asks for a close code on a bad token, and a
close code needs a socket to arrive on". EIR-WS-06 asks the same of quota
exhaustion, and `CLOSE_CODES[4008]` has read `"quota exhausted"` since chapter
1.3 with nothing emitting it.

It also reaches a browser. A raw HTTP response on a failed upgrade does not — the
page gets no status and no body, which is the wall chapter 3.8 met with its 429
and could not get around, because a `Retry-After` has nowhere else to go. A quota
refusal has somewhere else to go.

`quota_exceeded` joins `ERROR_CODES` in `packages/protocol/src/codes.ts`. The
frame schema types `code` as `z.string().min(1)`, so nothing forces this; the
registry is the documented vocabulary and `codes.test.ts` enforces its
uniqueness, which is why chapter 3.2 registered `wrong_credential_type` there
instead of writing it inline.

**`refuseUpgrade` is not extended.** Its raw 429 stays chapter 3.8's, for chapter
3.8's refusal. After this chapter the two refusals at one door are visibly
different on the wire: a rate limit never completes the handshake and carries a
`Retry-After`; a quota completes it and closes with a code and a date.

**`docs_url` resolves to nothing**, exactly as `rate_limited`'s and
`quota_exceeded`'s already do. Inherited deliberately; chapter 3.12's problem,
and this chapter adds no third instance of it.

## 3. The threshold email

Same table, same relay, same at-most-once constraint as chapter 3.10. What
changes is one value in the `dimension` column and the copy that renders it.

Subject: `Relay: 80% of your connection-minutes quota for August 2026`

The body names the dimension in the customer's words — "connection-minutes", not
`connection_minutes` — the period, the figure, and the cap that was configured
when the crossing happened. At 100% of a **soft** threshold it says that nothing
has been refused, because a soft threshold refuses nothing and an email that
implies otherwise generates a support ticket.

At 100% of a **hard** cap it says what stops and what does not: new connections
are refused, connections already open keep working, sends over REST keep
working, and history reads keep working.

---

## 4. The usage read

`usageFor(db, environmentId, period)` gains two fields:

```ts
{
  period: "2026-08-01",
  messagesSent: 1204,
  activeUsers: 37,
  connectionMinutes: 48210,          // new
  messageQuota: 10000,
  activeUserQuota: null,
  connectionMinuteQuota: 50000,      // new
}
```

`null` means no cap configured, and it stays `null` all the way to the reader
rather than becoming `Infinity` or `-1` — chapter 3.8's rule for nullable limit
columns, kept.

`connectionMinutes` is read from `usage_periods`, one indexed row, not summed
over `usage_connections`.

---

## 5. What the platform admits it can lose

Written as a contract because the alternative is that it becomes folklore.

| Event | Effect on the recorded figure |
|---|---|
| A report is lost in flight | none — the next report carries the same total |
| A report is delivered twice | none — the second credits zero |
| Reports arrive out of order | none — a lower total credits nothing and lowers nothing |
| The api is unreachable for an hour | none, for connections still open when it returns |
| The gateway is stopped gracefully **and the api answers** | none — a signal handler closes the server and awaits a final report (R11) |
| The gateway is stopped gracefully **and the flush fails** | the same loss as a kill: there is no second attempt, because the process is leaving |
| A connection closes between two reports | none — the close hands its final total to the meter, which is retained until a report carrying it is accepted (R19) |
| **A closed connection's total is discarded at the retention cap** | **that connection's minutes since its last accepted report are never counted** — logged and counted, never silent (FR-029) |
| **The gateway is killed** | **up to one reporting interval per open connection is never counted**, plus anything retained for connections that had already closed |
| Clock skew between instances | a bucket may land in the wrong minute, or at a boundary in the wrong period; bounded by the skew |

The last two are under-counts, and that is the direction chosen deliberately.
The alternative to a bounded under-count is billing a connection until somebody
notices nobody is holding it, which is an unbounded over-count, and a customer
forgives the first.

**Overshoot, in the other direction.** Past a hard cap, connections already open
stay open (FR-RTL-08) and keep accruing:

> overshoot ≤ (connections open when the cap was crossed) × (minutes until each
> closes) + one reporting interval

Nothing in the platform bounds how long a client holds a socket, so the
right-hand side has no numeric ceiling. Said plainly rather than replaced with a
number that would be wrong.
