# Research — chapter 4.4, every request is an event

**Feature**: `specs/049-chapter-4-4/` · **Date**: 2026-09-14
**Method**: the stack up on its documented ports, probes run against the real broker, the
real Nest version and the real Express version. Every probe that reports a zero carries a
positive control.

---

## R1 — The ingester built last chapter destroys what this chapter publishes

**Question**: `services/ingester` filters on `analytics.>` and `shape()` understands one
record type. What happens to a second type?

**Probe**: a stream with the ingester's own consumer configuration, two records published —
one attempt, one API request — and `ingestOnce` run twice with a `ack_wait` of 2 s and a
3.5 s gap between passes.

```
  published 2 · stream holds 2
  --- pass 1 ---
      [error] ingester.malformed_record {"stream_sequence":2}
  pass 1: written 1  malformed 1
  --- pass 2, after ack_wait: does the terminated record return? ---
  pass 2: written 0  malformed 0
  stream still holds 2 of 2 · first_seq 1 last_seq 2
  consumer: num_pending 0 · ack_pending 0 · redelivered 0
  store was handed 1 row(s): 9f000000-0000-4000-8000-000000000001
```

**Decision**: the ingester must route by record type before shaping, and must not terminate a
well-formed record of a type it does not write.

**And the loss is invisible from both instruments.** The stream still holds 2 of 2 —
`retention: Limits` keeps acknowledged and terminated messages alike — while the consumer
reports `num_pending 0`. Stream depth says the record is there; consumer lag says there is
nothing to do. **Both are true and the record will never be processed.** This is 048's
strand signature exactly, one chapter later and from a different cause: 048 disproved
depth-versus-pending as a strand detector because a clean drain produces the same pair. It
produces the same pair here too, and here the records really are lost.

The only signal is the `error` line, and it carries `stream_sequence` and nothing else — by
design, so an investigation has a handle without the log becoming the leak. That is the right
trade and it means **the count of destroyed records is only visible if somebody is counting
error lines.**

**Positive control**: `written 1`. The attempt record went through, so the probe measured a
difference between record types rather than a broken consumer.

**Alternatives considered**: narrow the ingester's filter to
`analytics.webhook.attempt.*` and let a second consumer take the rest. That works and is R12.
It does not remove the need for R1's fix, because a third record type would hit the same wall
in whichever consumer holds the wide filter.

---

## R2 — Two streams cannot share a subject space, and the grammar therefore decides the topology

**Found by accident**: R1's first run tried to create a probe stream over `analytics.>`.

```
NatsError: subjects overlap with an existing stream
  api_error: { code: 400, err_code: 10065,
               description: 'subjects overlap with an existing stream' }
```

**Decision**: "give API request records their own stream" is not a free option. `ANALYTICS`
owns `analytics.>`, so a second stream requires narrowing that list first — for example to
`analytics.webhook.>`. `subjects` is in `ensureAnalyticsStream`'s `mutable` set, so this is an
update rather than a recreate, but it is a change to a published stream with a live consumer
and it has to be sequenced.

**This is the grammar's cost arriving.** `analytics.{domain}.{action}.{environment_id}` was
introduced so a consumer could filter on a constant. The same structure means the stream's
subject list is a claim about which domains exist, and `analytics.>` claims all of them.

---

## R3 — A subject token for a request that belongs to no tenant

**Question**: FR-009 wants a record for a request with no environment. `analyticsSubjectFor`
refuses a non-UUID. What token can stand in, and can a tenant reach it?

**Probe R3a — what the broker accepts as a token**:

```
     "_none"      published OK
     "-"          published OK
     "none"       published OK
     "_"          published OK
     "no.tenant"  published OK
     "*"          published OK
```

**Every candidate published, including the two that must not.** `no.tenant` produced a
**five-token subject** where four were intended, and `*` produced a subject containing a
literal asterisk. Neither failed at publish time, which is the protocol package's stated fear
measured rather than quoted.

**Probe R3b — what a per-tenant filter sees**, over a stream holding all six candidates plus
one record for tenant A:

```
     tenant A exact  filter p34.api.request.11111111-1111-4111   num_pending 1
     tenant B exact  filter p34.api.request.22222222-2222-4222   num_pending 0
     any one token   filter p34.api.request.*                    num_pending 6
```

Tenant A saw its own record and nothing else. Tenant B saw nothing. The single-token wildcard
saw **6 of 7** — the five-token `no.tenant` subject is the one it missed, which is the silent
direction: a malformed token does not go to the wrong tenant, it goes somewhere no intended
filter reaches.

**Decision**: a sentinel token that cannot be a UUID is safe against every exact-match
tenant filter, and `analyticsSubjectFor`'s UUID refusal must stay exactly as it is. The
tenantless case gets its own function rather than a relaxed argument to that one — a
validator with an escape hatch is a validator with a hole, and the chapter's own probe shows
what falls through it.

**Alternatives considered and rejected**: pass the zero UUID (047 measured what that does —
one phantom active user per environment); pass an empty string (publishes to a subject with
an empty token); widen the UUID regex (removes the guard for every caller to serve one).

---

## R4 — A second producer on a shared stream, and the number that settles it

**Question**: FR-014. `ANALYTICS` is one stream at `max_bytes` 1 GiB, `max_age` 7 days,
`discard: old`, sized when its only producer was one record per webhook attempt.

**Probe**: 1,000 API request records of the shape FR-ANL-07 describes, published to a stream,
and the stream's own byte accounting read back.

```
     1000 records occupy 313,000 bytes -> 313.0 bytes/record
     at max_bytes 1 GiB the stream holds ~3,430,485 records
     7-day retention is reached at 5.7 requests/second sustained
     and at 100 req/s the stream fills in 9.5 hours
```

Measured beside it, the live `ANALYTICS` stream: **37 messages, 17,618 bytes, 476 bytes per
attempt record.** A request record is about two thirds the size of an attempt record and
arrives orders of magnitude more often.

**Decision**: `max_bytes` becomes the binding constraint instead of `max_age`, above **5.7
requests per second sustained**. Under `discard: old` the eviction takes the oldest messages
on the stream regardless of which producer wrote them, so **a busy tenant's request records
evict a quiet tenant's webhook attempt records** — and neither producer nor consumer sees an
error.

**And it falsifies a published number.** `docs/05-sad.md:184` and `:919` both say the stream
absorbs **24 h** while the store is down (NFR-REL-05). At 313 bytes a record, 24 hours fits
only up to **39.7 requests/second**. Above that the SAD's claim is false, and nothing in the
platform would say so. NFR-REL-05's own text names no duration — the 24 h is the SAD's, and
the SAD also calls the retention "24 h" where the stream is configured at 7 days. Two numbers
in one sentence, one of which was never the configuration.

**This does not by itself choose a second stream.** It chooses that the question is answered
with a number in the chapter. R12 takes the topology.

---

## R5 — The middleware sees every request, including the ones that never reach a handler

**Question**: FR-001 says "every API request". Which layer sees them all?

**Probe**: six requests against the running api, then its own log lines.

```
    healthz          -> 200      no credential  -> 401      bad credential -> 401
    unknown route    -> 404      param route    -> 401      internal seam  -> 401
```

All six produced a `"msg":"request"` line from `RequestContextMiddleware`. So the middleware
layer sees a 404, a guard's 401, and a middleware refusal alike.

**Decision**: the producer belongs in the middleware layer, not in a Nest interceptor. Nest's
order is middleware → guards → interceptors → pipes → handler, so a guard that throws 401
short-circuits before an interceptor runs at all, and an unmatched route never reaches one.
**An interceptor would miss exactly the requests an operator most wants in a request log.**

**And the probe showed the field that must not be copied.** One logged line reads

```
"method":"GET","path":"/v1/channels/abc123/messages","status":401
```

— the raw path, carrying the channel id. On `/v1/users/:externalId` it carries a customer's
external id. FR-005 says endpoint, and this is why.

---

## R6 — The matched route template is available where the record is assembled

**Question**: FR-005 wants the template. Is it knowable at `res.on("finish")`?

**Probe A — Express 5.2.1 directly, with a router mounted at `/v1`**:

```
    POST /v1/channels/abc123/messages   status 201  req.route.path = "/channels/:channelId/messages"
    GET  /v1/guarded                    status 401  req.route.path = "/guarded"
    GET  /v1/does-not-exist             status 404  req.route.path = undefined
```

**Probe B — Nest 11.1.28 on Express 5, controllers declaring full paths as this api's do**:

```
    POST /v1/channels/abc123/messages   status 201
         req.baseUrl=""  req.route.path="/v1/channels/:channelId/messages"
    GET  /healthz                       status 200
         req.baseUrl=""  req.route.path="/healthz"
    GET  /v1/does-not-exist             status 404
         req.baseUrl=""  req.route.path=undefined
```

**Decision**: `req.route.path` at `finish` is the template, and for this api it is the whole
template because Nest registers on the root instance and `req.baseUrl` is empty. A 404 has no
`req.route` at all, which is correct rather than awkward: an unmatched request has no
endpoint.

**The two probes disagree for a reason worth keeping.** Under a mounted router the same field
gives `/channels/:channelId/messages` — no `/v1` — so a producer written against Express's
documentation and tested through a mount records a template that collides across versions.
That is the **same failure the middleware beside it already survived**: `req.url` was `/` for
every request from chapter 2.2 until the rate-limiter chapter, because Express rewrites paths
relative to the mount point. The field is safe *here*, because of how these controllers are
declared, and a task must assert that rather than assume it stays true.

---

## R7 — Constitution I forbids the record FR-009 requires

**The clause**, and it is the NON-NEGOTIABLE principle:

> Every persisted operational and analytical record MUST carry a non-null tenant
> (`environment_id`) identifier, directly or through a single foreign-key hop.

FR-ANL-01 requires an analytical event for **every API request**. R5 measured that a large
share of them — every 404, every 401, `/healthz`, signup, and every call the dispatcher and
gateway make on the internal seam — resolve to no environment. `PlatformPrincipal` carries
none *by design*, and its own comment says the absence is what stops it being usable where a
tenant is expected.

**So three readings are available and two of them are wrong.**

| reading | consequence |
|---|---|
| drop the tenantless requests | FR-ANL-01's "every" is false for the busiest routes, silently |
| invent an environment for them | a value that means "unknown" sitting in the column constitution I exists to protect — 047 measured the zero UUID producing one phantom active user per environment |
| the clause governs **tenant data**, and a record with no tenant is not tenant data | the record is unreachable by any tenant-scoped query (R3b measured this), and the rationale — *"no isolation failure"* — is satisfied because there is nothing to leak |

**Decision**: the third, argued explicitly in the chapter and in an SRS amendment rather than
assumed in code. The test that makes it real is R3b's shape, promoted to a requirement: a
tenant-scoped read returns that tenant's records and no tenantless ones.

**This is a gate, not a footnote.** Constitution I is non-negotiable and the governance clause
puts principle changes outside a feature. This resolution does not change the principle; it
records which records it governs, which is the thing no artifact has ever stated. If that
reading is rejected, the chapter loses FR-009 and FR-ANL-01 must be amended instead — and the
plan says so rather than discovering it at implementation.

---

## R8 — FR-ANL-07 asks for something two other clauses forbid

FR-ANL-07 records *"request ID, timestamp, endpoint, method, status, latency, and truncated
payload."* FR-ANL-11 forbids message text in the analytical store. Constitution III repeats
it (*"MUST NOT contain message text — only lengths, identifiers, and metadata"*). Constitution
VI keeps message content out of logs.

`POST /v1/channels/:channelId/messages` has a body whose content is message text. **Truncation
makes it worse rather than better**: it keeps the first *n* characters, which is the part a
person wrote and the part that identifies them.

**Decision**: amend FR-ANL-07 to drop "truncated payload", with the revision-history entry the
governance clause requires. The precedent is FR-RTM-09, FR-RTM-10 and 043's own FR-016 — three
clauses this project amended rather than diverged from.

**The alternative that looks reasonable and is not**: record the payload for routes that carry
no message text, and omit it for the ones that do. That is an allow-list of endpoints
maintained by hand, which is the failure mode of the nine hand-allocated api ports — and it
fails open, because a new route is included by default. 3.20's own `shape()` made this argument
about fields: *"an allow-list fails closed when somebody adds a field; a spread fails open."*

---

## R9 — Where the producer lives

**Decision**: beside `RequestContextMiddleware`, not inside it.

The middleware's contract is one structured log line per request and an `X-Request-Id` header;
it is cited by EIR-API-05 and NFR-OBS-06 and is fenced in the tutorial. Adding a broker publish
to it makes an observability component depend on NATS.

A second middleware in the same chain, registered after it, reads the request id the first one
set and the route the router set. It shares the request id **by reading it** rather than by
minting a second one, which is what keeps the log line and the analytical record talking about
the same request.

**Alternatives considered**: an interceptor — rejected by R5, it cannot see 401s or 404s. A
wrapper around `res.end` — rejected, the api already has a `finish` listener and two
listeners racing to read `res.statusCode` is a bug waiting for a slow response.

---

## R10 — Latency: which interval, and stated rather than implied

Nothing in the api measures a duration today; the existing line has method, path and status
and no time.

**Decision**: measure from the producer middleware's own entry to the response's `finish`
event, and **say so in the contract**. That interval excludes connection accept, TLS, and the
time the request body spent on the wire, and it excludes whatever middleware runs before it.
NFR-PRF-02's "excluding network" is the same posture.

**The number this is compared against must use the same interval.** 046 published a wrong
storage figure three times by differencing two totals that measured different things, and the
rule it produced applies here: a duration is a measurement of the thing that changed only if
the endpoints are the same on both sides.

---

## R11 — Telling record types apart

**Decision**: an explicit `type` field on the wire, written by the producer, checked by the
consumer, with an unknown value routed to "not mine" rather than to "malformed".

**Not by subject.** The consumer could switch on `m.subject`, and that reads well until the
subject is the thing that changed — R3a showed a malformed token producing a subject with a
different number of a tokens, and a router that parses subjects would have to be right about
that too. The payload says what the payload is.

**Not by shape.** Duck-typing two record types works until a third shares a field with one of
them, and the failure is silent misclassification rather than a refusal.

**And the existing records have no `type` field.** 3.20's `AttemptEvent` predates this
question. The consumer must therefore treat an absent `type` as the attempt record —
a compatibility rule that is written down and tested, because **a reader of anything durable
cannot require a field its writer did not have.** That sentence is CLAUDE.md's most-repaid
lesson and the stream holds 37 records written by a binary that never heard of `type`.

---

## R12 — One consumer or two

**Decision**: one ingester process, two record types, one consumer — **provided R11's routing
lands first**. Deferred to the plan's phase ordering rather than settled here, because R4's
number may force the stream split and a stream split changes the answer.

The argument for one: the batching, the retry posture, the poison rule and the ClickHouse
client are all written and tested, and a second consumer duplicates every one of them to
handle a different row shape. The argument for two: the two record types have different
volumes by two orders of magnitude, and 4.3's batch bounds (2 s, 10,000 rows) were chosen for
the quiet one.

**What decides it is R4's measurement in this environment, not preference**, and the chapter
publishes the number either way.

---

## R13 — The table

**Decision**: a second table, not a column on `webhook_attempts`.

FR-ANL-07 says 30 days; `webhook_attempts` has a 90-day TTL. Two retentions in one table is
not expressible in one `TTL` clause, and the column sets do not overlap beyond
`environment_id`, `ts` and `latency_ms`.

Shape follows 4.2 and 4.3 without re-deriving them: `ReplacingMergeTree`,
`PARTITION BY toYYYYMM(ts)`, `ORDER BY` leading with `environment_id`,
`TTL toDateTime(ts) + INTERVAL 30 DAY` — `toDateTime` because 047 measured
`TTL ts + INTERVAL` on a `DateTime64` refused with `BAD_TTL_EXPRESSION` — and the
`ts_is_real` CHECK constraint, because 048 measured that an absent column takes its default
and a `DateTime64` default is older than any TTL, so the row is deleted at insert while every
instrument reports success.

The sorting key ends at `request_id`, which `newRequestId()` already mints as a UUID per
request. **Deduplication is the record's own key**, which is 4.3's conclusion applied rather
than re-argued: a token derived from a batch is not stable across a redelivery.

**Open for the plan**: whether `environment_id` is `Nullable(UUID)` or the tenantless records
go to a separate table. R7 chose the reading; the storage shape is a phase-1 task, and 047's
`Nullable(UUID)` precedent exists because `uniqExact` ignores NULL exactly as Postgres's
`count(DISTINCT)` does.

---

## R14 — `/healthz`, and the requests nobody asked to log

The container runtime polls `/healthz`. Measured in the probe window: **three health checks in
six seconds** from one container's health check alone, with the gateway and dispatcher adding
their own.

At R4's 313 bytes, a 5-second health check is 5.4 MB a week per prober — small. The cost is
not bytes, it is that **the request log's largest endpoint by count is the one nobody wants to
read**, and every percentile computed over the whole table is dominated by it.

**Decision**: record it, and let the read exclude it. Do not filter at the producer. A
producer that drops requests is a producer whose count cannot be reconciled against anything,
and FR-ANL-06's whole subject is reconciliation. **The chapter publishes the health-check
share** so the decision is visible rather than implied.

---

## R15 — The broker deduplication id

3.20 uses `{deliveryId}:{attempt}` and the webhook dispatcher chapter learned why the delivery
id alone was wrong: it collapsed seven retries into the first attempt's message.

**Decision**: the request id, unchanged. It is a v4 UUID minted per request, so the
publisher-side collision case that bit 3.20 cannot arise. Stated rather than assumed, because
"unique by design" is exactly the claim 3.20's was.

---

## R16 — `docs/12` §4 is one ordinal ahead of §3

Recorded in the spec. Five cross-references, all +1, matching the interim 24-chapter numbering
that existed while movement I was two chapters. §7's references match §3's table and are not
affected. **§4 is the section that tells a chapter what it must not re-teach**, so a writer
following it concludes this chapter is not the one that generalises 3.20's pattern.

**Decision**: amend §4 against §3's table in this feature.
