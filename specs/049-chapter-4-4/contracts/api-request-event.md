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
| `type` | string | always | the constant `"api.request"`. R11: the payload says what the payload is, not the subject |
| `request_id` | string (uuid) | always | the same id as `X-Request-Id` and the api's own log line — **read**, never re-minted |
| `ts` | string (ISO-8601) | always | when the response finished |
| `method` | string | always | |
| `status` | number | always | |
| `latency_ms` | number | always | R10's interval, stated below |
| `endpoint` | string | when the route matched | the template, e.g. `/v1/channels/:channelId/messages` |
| `environment_id` | string (uuid) | when one resolved | absent, never null and never a sentinel |
| `principal_kind` | string | always | `application` \| `user` \| `platform` \| `none` |

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

At this tag the live `ANALYTICS` stream holds **37 records with no `type` field**, written by
a binary that never heard of one. The absent case is a compatibility rule with a test, not a
default.

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
