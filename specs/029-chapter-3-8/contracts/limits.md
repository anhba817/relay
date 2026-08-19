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

### When a request is counted twice

**The send limit counts messages wherever they enter.** One message per operation on
both transports — there is no batch send.

| Operation | request limit | send limit |
|---|---|---|
| `POST /v1/channels/…/messages` | −1 | −1 |
| a `message.send` frame on an open socket | — | −1 |
| any other public REST call | −1 | — |
| the handshake itself | — | — (it decrements the connect limit) |

**Each operation is counted once, at the door it entered.** The gateway reaches the
api over `/internal/*` routes that forward your own token, so they look like customer
traffic and are deliberately **not** counted again as requests — the gateway already
counted the handshake against the connect limit and the frame against the send limit.
Without that rule a socket send would cost two slots and a reconnect storm would eat
the request budget.

A REST send therefore decrements **both**. The headers describe **whichever has fewer
remaining**, and `Reset` is that same limit's; a tie reports the request limit.

That is the only value a client can plan against. A client with 400 request-slots and
12 send-slots left needs to hear 12 — reporting 400 would be a header that lies by
omission. The two diverge as soon as a client uses the socket, which is when the rule
starts doing work.

One budget covers both doors because a limit a client can lift by moving the same
traffic to the socket is not a limit. A message costs the same downstream whichever
door it came through.

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
sufficiency rather than assuming it). It is the reset of the limit that actually
refused, which for a REST send may be either of the two.

**The message names which limit was reached.** "Too many requests" and "too many
messages" are different problems: one says batch, the other says slow down. The
`code` stays `rate_limited` — it is the protocol constant — and the message carries
the distinction. Neither names a credential (NFR-SEC-06).

**`request_id` in the body is new.** The envelope has carried `code`, `message` and
`docs_url` since chapter 1.3, above a comment saying the fourth field would arrive
"in Part 2, when a gateway exists to mint one". It did not. Constitution V requires
four fields; this chapter adds the fourth **to every error response**, not only to
this one, because a four-field envelope on one status and three on the others is
worse than either consistent answer.

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

**`request_id` on a frame is new too**, and the gateway had none to give — it minted
no ids at all. It now mints one per answered frame, and uses the connection's own id
for a frame nobody asked for. The field is required rather than optional: an optional
fourth field would be the fourth thing this chapter's own subject warns about
(research R13). The only asymmetry with REST is that a frame has no headers, so there
is no `X-Request-Id` duplicate — the id is in the payload either way.

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

**Whose address is counted.** The client's. A handshake authenticated through the
gateway reaches the api from the gateway, and counting the caller would put every
customer's failures in one bucket — ten failures from ten customers would look like
ten failures from one address, and one attacker would exhaust a threshold that then
refuses everybody. The gateway forwards the client address on the internal call.

Being exempt from customer rate limits (FR-009) does not exempt a call from saying
whose failure it carried. The same request is trusted enough not to be throttled and
not trusted to be the origin.

**During a counter outage this limiter does not fail open.** It falls back to an
in-process count with the same threshold, so the guarantee weakens from N per
window across the fleet to N per window per instance. Bounded, and the bound is a
small multiple rather than infinity.

---

## What is never limited

**`/healthz`.** Docker polls it every five seconds and `docker compose up -d --wait`
depends on the answer. A limiter that can refuse a health check can stop a deployment.

**The dispatcher's routes.** They carry the platform credential and reach every
environment. A limiter that throttles the dispatcher turns one busy customer's webhook
backlog into a stall for every customer, which is the failure FR-WHK-05 forbids and
which chapter 3.5's retry schedule was built to avoid.

**The gateway's routes**, as requests. Not because they are trusted — they forward
your token and are user-authenticated — but because the operation behind them was
already counted at the socket. See the table above.

## What is limited without a tenant

**Failed authentication**, per source IP. **Account creation**, per source IP, on the
same counter family and threshold: signup has no tenant to key on, which is the point
of it, and an unlimited account-creation route is not acceptable in a platform that
limits everything else.

---

## Defaults

| Operation | Per environment, per minute |
|---|---|
| REST requests | 600 |
| Message sends | 600 |
| Connection establishment | 3,000 |
| Failed authentication | 10 per source IP |

Each number rests on something stated rather than on judgement: sends are 1% of the
platform's 1,000/s aggregate capacity; establishment is sized so a gateway instance's full
complement of connections can re-establish inside one window, which is what makes a deploy
one reconnection cycle rather than two; the request limit has no independent anchor and is
matched to the send limit so one operation cannot straddle two ceilings.

**The connect limit is not there to shape your capacity.** It exists to stop a client
reconnecting in a tight loop, which does thousands a minute. A fleet of your users
reconnecting after a deploy will not reach it.

Overridable per environment for the first three. The auth threshold is
configuration, not per-environment policy, for the reason above.

**A socket's limits are fixed when it connects.** The gateway has no database and
receives the two socket limits on the authentication response it makes at the
handshake, so an override changed while a connection is open applies to that
connection at its next reconnect, not immediately.

**The window is fixed, not sliding**, so up to twice the limit is possible across
one boundary — 1,200 requests in the two minutes spanning a window edge. Stated
because a limiter documented as stricter than it is will be planned against
incorrectly. The limit bounds sustained load; it does not smooth instantaneous
rate.

**A REST send decrements both the request and the send limit**, so 600 REST sends
exhaust both at once. Mix the transports and they diverge: 300 REST sends and 300
socket frames leave the send limit spent with 300 request-slots unused, and the
headers report whichever is closer.

A socket send is counted by the gateway against the same shared counter the api uses,
which is why the counter lives in Redis rather than in either process — two services
increment one bucket and neither can see the other's memory.

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
