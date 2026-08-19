# Contract — limits, as a client sees them

What an integrating developer can rely on. Every statement here is asserted by a
test named in `quickstart.md`.

---

## Headers, on every limited response

Present on **2xx as well as 429** (FR-RTL-02). This is the part that makes the
limiter something a client can schedule against rather than discover.

| Header | Value |
|---|---|
| `X-RateLimit-Limit` | the allowance for this operation in this window |
| `X-RateLimit-Remaining` | how many are left, after counting this request |
| `X-RateLimit-Reset` | unix seconds at which the window ends and the allowance returns |

`Remaining` decreases monotonically within one window. It does not go negative:
requests beyond the allowance are refused, and the refusal reports `0`.

### While the counter is unavailable

`X-RateLimit-Limit` only. `Remaining` and `Reset` are **absent** — not `-1`, not
`unknown`.

A client that checks for the headers' presence learns the truth: the policy stands,
the accounting does not. A sentinel would require every client to know it, and a
client that did not would read `-1` as a number and conclude it was over its limit.
`Limit` stays because it is policy read from Postgres and is not degraded.

---

## Refusal — REST

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 17
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1755590417
X-Request-Id: 01J...
content-type: application/json

{
  "code": "rate_limited",
  "message": "too many requests for this environment; retry after 17 seconds",
  "docs_url": "https://relay.example/docs/errors/rate_limited",
  "request_id": "01J..."
}
```

`Retry-After` is seconds, and honouring it is sufficient — a request issued after
that interval succeeds (FR-003, and the scenario in `quickstart.md` V2 proves the
sufficiency rather than assuming it).

**`request_id` in the body is new.** The envelope has carried `code`, `message` and
`docs_url` since chapter 1.3, above a comment saying the fourth field would arrive
"in Part 2, when a gateway exists to mint one". It did not. Constitution V requires
four fields; this chapter adds the fourth **to every error response**, not only to
this one, because a four-field envelope on one status and three on the others is
worse than either consistent answer.

**The message never names a credential** (NFR-SEC-06). It names the environment's
condition, not who asked.

---

## Refusal — WebSocket handshake

An establishment refused because the environment is over its connect limit gets an
HTTP `429` **during the upgrade, before the handshake completes**:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 12
Connection: close
```

No WebSocket connection is created. Sockets already open are unaffected (FR-005).

**Deliberately different from a bad token**, which completes the handshake so it
can send close code `4001` — the gateway's own comment says EIR-WS-05 wants the
close code "on a connection we never really opened". The difference is that an
invalid token is a permanent condition needing a precise name, and a rate limit is a
temporary condition with a duration. `Retry-After` has nowhere to live on a close
frame.

**Close code `4008` is not used here.** It reads "quota exhausted" and a rate limit
is not a quota — the distinction this chapter is built on. 4008 waits for chapter
3.9, where a quota can actually be exhausted.

---

## Refusal — a frame on an open connection

An `error` frame, and the connection **stays open**:

```json
{
  "type": "error",
  "payload": {
    "code": "rate_limited",
    "message": "too many frames; slow down and retry",
    "docs_url": "https://relay.example/docs/errors/rate_limited",
    "request_id": "01J..."
  }
}
```

`rate_limited` has been in `packages/protocol/src/codes.ts` since chapter 1.3 with
nothing emitting it. This is the first thing that does.

**The connection is not closed.** Closing it would make the client reconnect, which
costs a handshake and consumes the establishment allowance — a limiter that
punishes the limited into hitting a second limit.

---

## Failed authentication

Counted per source IP, not per environment: the caller has not proved which
environment they are, which is the point.

- A **successful** authentication does not count.
- Past the threshold, further attempts are refused regardless of whether the
  credential presented would have been valid.
- The refusal carries no information about whether the credential was right.
  "Rate limited" and "wrong credential" must be indistinguishable to the caller, or
  the limiter becomes an oracle.

**During a counter outage this limiter does not fail open.** It falls back to an
in-process count with the same threshold, so the guarantee weakens from N per
window across the fleet to N per window per instance. Bounded, and the bound is a
small multiple rather than infinity.

---

## What is never limited

Calls arriving over the internal service seam — dispatcher-to-api,
gateway-to-api — carry a service credential and are exempt (FR-009).

Not a convenience. A limiter that throttles the dispatcher turns one busy
customer's webhook backlog into a stall for every customer, which is the failure
FR-WHK-05 forbids and which chapter 3.5's retry schedule was built to avoid.

---

## Defaults

| Operation | Per environment, per minute |
|---|---|
| REST requests | 600 |
| Message sends | 600 |
| Connection establishment | 60 |
| Failed authentication | 10 per source IP |

Overridable per environment for the first three. The auth threshold is
configuration, not per-environment policy, for the reason above.

**The window is fixed, not sliding**, so up to twice the limit is possible across
one boundary — 1,200 requests in the two minutes spanning a window edge. Stated
because a limiter documented as stricter than it is will be planned against
incorrectly. The limit bounds sustained load; it does not smooth instantaneous
rate.

---

## The notification a customer receives

Not a client-facing API, and contracted here because FR-021 makes its contents a
requirement.

An email to the owners and admins of the organisation, when one of its endpoints
is automatically disabled by chapter 3.6's sweep. It names the endpoint, when it
was disabled, the failure run that triggered it, the last status observed, and how
to re-enable.

It contains **no signing secret, no API key, and no customer credential of any
kind** (NFR-SEC-06). Verified by reading the message the mail service received, not
by inspecting what the sender passed in.

Recipients are resolved at send time from the organisation the notification row
records — not from the endpoint's current owner. Chapter 3.6 denormalised that
column with the reason written down; this is the first code to depend on it.
