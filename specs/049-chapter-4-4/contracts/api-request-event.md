# Contract — the API request analytical event

**Feature**: `specs/049-chapter-4-4/` · **Date**: 2026-09-14
**Producer**: `services/api` · **Consumer**: `services/ingester` · **Transport**: JetStream,
stream `ANALYTICS`

This is the artifact nothing else reads, which is why 046 and 047 both hid a defect in one.
047's `contracts/schema.md` carried `RELAY_POSTGRES_PORT=15432` on a ClickHouse-only script
for four analysis passes. **Every command in this file is written to be run as printed.**

---

## Subject

```
analytics.api.request.{environment_id}      a request that resolved to a tenant
analytics.api.request._none                 a request that did not
```

`{environment_id}` is validated as a v4-shaped UUID by `analyticsSubjectFor` and **that
refusal does not get a bypass**. The tenantless arm is a separate function returning a
constant token, because R3a measured what a permissive token does:

| token | what the broker did |
|---|---|
| `no.tenant` | published a **five-token** subject; the four-token wildcard `analytics.api.request.*` did not match it |
| `*` | published a subject containing a literal asterisk |

Neither failed at publish time. The sentinel is `_none`: it cannot be a UUID, so no
exact-match tenant filter reaches it — measured in R3b, where tenant A's filter saw 1 record
and tenant B's saw 0 over a stream holding all six candidates.

## Deduplication id

```
id = request_id
```

A v4 UUID minted per request by `newRequestId()`. 3.20 uses `{deliveryId}:{attempt}` because
the delivery id alone collapsed seven retries into one message; a request id has no such
second dimension. Stated rather than assumed, because that is exactly the claim 3.20's id
was.

## Payload

`JSONEachRow`-compatible, snake_case, because it leaves the platform.

| field | type | present | notes |
|---|---|---|---|
| `type` | string | always | the constant `"api.request"`. R11: the payload says what the payload is, not the subject. **Consumed by the router and dropped before the insert — it has no column** |
| `request_id` | string (uuid) | always | the same id as `X-Request-Id` and the api's own log line — **read**, never re-minted |
| `ts` | string (ISO-8601) | always | when the response finished |
| `method` | string | always | |
| `status` | number | always | |
| `latency_ms` | number | always | R10's interval, stated below |
| `endpoint` | string | **only when the router ran** | the template, e.g. `/v1/channels/:channelId/messages`. Absent for a 404 and for every middleware refusal — two different facts, separated by `refused_at` |
| `environment_id` | string (uuid) | when one resolved | absent, never null and never a sentinel |
| `principal_kind` | string | always | `application` \| `user` \| `platform` \| `none` |
| `refused_at` | string | always | `handler` \| `guard` \| `middleware` \| `unmatched`. **`middleware` and `guard` are STAMPED by the refusing layer; `unmatched` and `handler` are inferred** — see below |
| `limited_operation` | string | when the rate limiter refused | `send` \| `rest` \| `signup` — the limiter's own granularity, which is the finest true answer about its refusals |

### `refused_at`, and why `endpoint` needs a second source

`req.route` is set by **Express's router**. A middleware that refuses ends the response before
the router runs, so the template is not there yet — not because there is no route. Measured:

```
/v1/fine       status=200  route=/v1/fine
/v1/mw429      status=429  route=undefined      <- rate-limit.middleware.ts:122, :221
/v1/guard429   status=429  route=/v1/guard429   <- credential.guard.ts:115
```

**The api has two sources of 429 and they are not the same record.** A guard runs after routing
and keeps the template; the rate limiter runs before it and does not. Same status code, same
meaning to a customer, and only one of them attributable to an endpoint — so *"which endpoint is
being rate-limited"*, the question a request log exists to answer, would be unanswerable for
exactly the 429s the rate limiter produces.

`refused_at` makes that visible instead of silent. **The endpoint is not recoverable**, and an
earlier draft of this file said it was, on the strength of a function it had not read.
`operationsFor` returns `[]`, `["rest"]` or `["rest", "send"]` — quota classes, not templates.
The limiter's entire route knowledge is three-valued.

**Which also means the question was wrong.** *"Which endpoint is being rate-limited"* presumes
per-endpoint limits; this platform limits `send` and `rest`. So the record carries
`limited_operation` — the class the limiter actually decided on — and the chapter says plainly
that a finer breakdown of its refusals describes a mechanism that does not exist. Building an
independent path matcher to manufacture one would disagree with the real router eventually,
which is a worse bug than the gap (constitution VII).

`unmatched` is the honest arm: a 404 matched nothing, and its `endpoint` stays absent.

**Two of the four arms cannot be observed, and the producer must be told.** Measured — a guard
refusal and a handler response are identical from `finish`:

```
/v1/fine         status=200 route=set  own keys=["body","route"]
/v1/guard401     status=401 route=set  own keys=["body","route"]
/v1/handler401   status=401 route=set  own keys=["body","route"]
```

So `middleware` and `guard` are **stamped** by the layer that refuses, and `handler` and
`unmatched` are **inferred** from the absence of a stamp plus whether the router ran. The cost
is one line in one file: `CredentialGuard` is the only class implementing `CanActivate` in this
api, applied across 11 controllers, and it throws both the 401 and the `OVER_AUTH_THRESHOLD`
429.

**The inference is only as good as the stamping.** A guard added later that refuses without
stamping is recorded as `handler` — a plausible value, silently wrong, in a column nothing
would flag. That is the fence-chain checker's failure shape: the answer that means *"clean"*
and the answer that means *"never looked"* printed the same line.

**Absent, not empty.** `exactOptionalPropertyTypes` is on in this workspace and 3.20's
`shape()` spreads optional fields in rather than assigning them, because *"an explicit
`undefined` is not the same as an absent key, and the difference is the whole meaning of
'nothing answered'."* The same rule holds here: an absent `endpoint` means the route did not
match, which is a fact, and `""` would be a claim about a route named the empty string.

**What is never present**: request body, response body, header values, credentials, key ids,
user external ids. FR-ANL-07's "truncated payload" is amended out (R8) rather than
implemented narrowly — `POST /v1/channels/:channelId/messages` has a body that is message
text, and truncation keeps the part a person wrote.

## Latency — the interval, named

Start: entry to the analytics middleware. End: the response's `finish` event.

**Excluded**: connection accept, TLS, request-body transfer, and any middleware registered
before it. NFR-PRF-02 takes the same posture with *"excluding network"*. Any figure compared
against this one must use the same endpoints — 046 published a wrong storage number three
times by differencing totals that measured different things.

## Delivery guarantees

**The publish may fail and failing must cost the response nothing.** Constitution III and
FR-ANL-03 in one sentence; 3.20 argued it for a webhook outcome and the argument is stronger
here because the caller is a customer rather than a background job.

- Not awaited on the request path.
- A failure is logged once, at the producer, with no payload and no rethrow.
- So **"every request" is approximate**, and the chapter says so in the paragraph that
  introduces the feature rather than in a footnote. That sentence is 3.20's, and this chapter
  generalises it rather than re-deriving it.

## What the consumer must do

```
type absent          -> attempt record; shape as today
type "api.request"   -> request record; shape to relay_analytics.api_requests
type unknown         -> not mine; do not terminate
```

At this tag the live `ANALYTICS` stream holds **36 records with no `type` field**, written by
a binary that never heard of one. The absent case is a compatibility rule with a test, not a
default.

## The producer's function is `toRequestEvent()`

Not `shape()`. Two functions of that name already sit on this path and do different things:
`services/api/src/webhooks/analytics.ts::shape` takes a record to the wire, and
`services/ingester/src/shape.ts::shape` takes the wire to a row. **The boundary between those
two is where 048's central defect lived** — the publisher sent `attempted_at`, the column was
`ts`, and `JSONEachRow` left the column at a default older than the TTL. A third `shape()`
astride that boundary is a naming choice this chapter in particular should not make.

## Running it

Stack up, on the documented ports:

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d
```

One request, then the record it produced:

```bash
curl -s -o /dev/null -w '%{http_code}\n' localhost:4000/v1/webhooks

curl -s -X POST http://localhost:8123/ \
  -u relay:relay \
  --data-binary "SELECT endpoint, method, status, latency_ms, principal_kind
                   FROM relay_analytics.api_requests FINAL
                  ORDER BY ts DESC LIMIT 5 FORMAT TSV"
```

`FINAL` is not decoration. 048 measured a bare `count()` answered from part metadata without
reading a row — 0.9 ms, reading 1 row, and **wrong by 100,000** against `FINAL`'s 5.3 ms
reading 1.2 M. A `ReplacingMergeTree` read without `FINAL` is a read of whatever has not been
merged yet.
