# Contract — how a cap refusal reaches a client

The external surface this chapter adds is one refusal. It is a protocol contract
rather than an HTTP one: no route is added, no request body changes, and no
response shape moves.

---

## The shape

Three refusals in `session.ts` now share one shape, and each arrived at it by
declining `refuseUpgrade` for the same reason. This is the third.

    1. the handshake COMPLETES
    2. an error frame is sent on the socket
    3. the socket is closed with a close code
    4. one server-side log line, `connection.rejected`, with a reason

```
client                                    gateway
  |-- GET /v1/ws?token=... (upgrade) -------->|
  |<------------------ 101 Switching Protocols|   the handshake completes
  |<-- {"type":"error","payload":{...}} ------|   the detail
  |<-- close(<code>, "<reason>") -------------|   what the client branches on
```

**Why the handshake completes for a refusal.** Because a browser cannot read the
body of a *failed* upgrade — `session.ts:729` states it — so refusing at the
upgrade seam gives a browser a bare connection failure with no code and no message.
EIR-WS-05 and EIR-WS-06 both ask for a close code on a connection-level refusal,
and a close code needs a socket to arrive on.

**Why not `refuseUpgrade`'s HTTP 429.** Its entire justification was `Retry-After`,
and FR-004 forbids that header here: no interval makes a cap refusal succeed. The
argument for the HTTP shape evaporates with the header, which is the sentence
chapter 3.11 wrote when it made the same call for quota exhaustion.

---

## The close code

**Close code `4004`, meaning `connection limit reached`**, added to `CLOSE_CODES` in
`packages/protocol/src/codes.ts`. Drawn from the same unassigned space chapters 1.3
and 3.15 used, and the next free number after 3.15's `4003`.

**The error code is `connection_limit_reached`**, and the name is chosen against a
collision rather than for its sound: `rate_limited` is one word away in the register
and means the opposite thing — it throttles a tenant's establishments per window, and
its own message reads *"too many connections; retry after the window resets"*.
Retrying is precisely what this code must not suggest. Both names are decided here
and nowhere else.

`packages/protocol/src/codes.test.ts:19` pins the set, so this is a visible
decision:

    before   [4001, 4002, 4003, 4008, 4009]
    after    the same five, plus one

**Why no reuse works.** EIR-WS-06 names four classes to distinguish —
authentication, quota, shutdown, protocol violation — and a cap is none of them.
`codes.ts` states the test twice: *"a client that cannot tell them apart retries the
wrong one for ever."*

| if it reused | the client would | and that is |
|---|---|---|
| `4001` invalid token | re-authenticate and reconnect | an infinite loop: the token was always valid |
| `4008` quota exhausted | wait for the quota window | never successful; the remedy is available now |
| `4003` banned | tell the person they are barred | false: four of their connections work |
| `4002` protocol violation | ship a client fix | false: the client did nothing wrong |

**What the correct remedy is, and therefore what the code must mean:** close one of
the connections you already hold, then reconnect. Immediately. No waiting.

---

## The error frame

One new entry in `ERROR_CODES`, registered rather than written at the call site —
`codes.ts` records why chapter 3.2 put `wrong_credential_type` in the registry
instead of inventing it inline, and `codes.test.ts` enforces uniqueness.

The frame carries what a close reason cannot, because a close reason is a short
string — **and it carries it in `message`, not in fields of its own.**

    errorFrameSchema.payload   code · message · docs_url · request_id · field?
                               z.strictObject — unknown keys are REJECTED

**The first version of this contract promised `limit` and `count` as payload
fields, and the schema forbids them.** `errorFrameSchema` at
`packages/protocol/src/frames.ts:143` is a strict object with those five keys, so
adding two more would mean widening a shape every error frame in the protocol
shares, for one code's benefit.

The precedent settles it. `codes.ts` describes `quota_exceeded` as *"the message
names the dimension, the figures and the date it resumes"* — **figures go in the
message**, and the reference's own section for it reads the same way. So:

| what | where |
|---|---|
| the limit and the count held | inside `message`, as a sentence: five of five |
| the code a client branches on | `code`, the new `ERROR_CODES` entry |
| where to read more | `docs_url`, from `docsUrl(code)` as every frame does |
| correlating one refusal to one log line | `request_id`, which `sendError` mints |

**`field` is not used.** It exists to name the payload key that failed schema
validation — `invalid_frame`'s job — and a cap refusal has no offending field.

**Deliberately absent: anything about which slots are held, which instances hold
them, or when the oldest last reported.** The spec's Q1 considered including the
oldest report time and rejected it: it publishes one user's connection topology to
anyone holding their token. Slot numbers are allocation detail and no requirement
exposes them (`data-model.md`).

**Deliberately absent: `Retry-After` or any equivalent.** FR-004.

---

## What a conforming client does

    on close code <the new one>:
        do NOT reconnect on a timer
        do NOT re-authenticate
        surface the message and offer to close one — the figures are IN it,
          so a client displays the sentence rather than parsing fields
        reconnect only after the person acts, or after another connection closes

This is the only close code in the set whose correct handling is **not** a retry of
some kind, which is why it could not be one of the other five.

---

## What does not change

- No REST route, request or response.
- `refuseUpgrade` and chapter 3.8's HTTP 429 stay exactly as they are; the
  connection-*rate* limit is a different limit with a different remedy
  (`research.md` R6 records an arithmetic problem in its sizing and hands it on).
- `connection.ack` is unchanged. A connection that is accepted cannot tell the cap
  exists.
- The five already-open connections observe nothing. FR-005 and SC-012: no
  connection is ever closed because another was opened.
