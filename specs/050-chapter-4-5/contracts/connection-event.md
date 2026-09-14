# Contract — the connection analytical event

**Feature**: `specs/050-chapter-4-5/` · **Date**: 2026-09-14
**Producer**: `services/gateway` · **Consumer**: `services/ingester` · **Transport**:
JetStream, stream `ANALYTICS`

Every command here is written to be run as printed. 046 and 047 both hid a defect in a
contracts file, and 047's was a Postgres variable on a ClickHouse-only script.

---

## Subject

```
analytics.connection.opened.{environment_id}
analytics.connection.closed.{environment_id}
```

`{environment_id}` is validated as a UUID by `analyticsSubjectFor` and **that refusal does not
get a bypass**. 4.4 measured what a permissive token does: `no.tenant` publishes a five-token
subject the four-token wildcard does not match, and `*` publishes a literal asterisk — neither
fails at publish time.

**There is no `_none` arm here, and the code is what says so.** 4.4 needed one because a
request can be made by nobody. A connection event is emitted from `registry.add` and from
`meter.closed`, and the only function that reaches either takes a non-optional `Identity` — its
call site passes `result.identity` after the 429, 4001, 1011, 4003 and 4008 refusals have each
returned. An unauthenticated socket never becomes a connection, so there is no record for a
tenantless arm to carry. This paragraph said "if phase 1 finds a case that contradicts that"
until analysis pass 6 went and looked.

## Deduplication id

```
id = {connection_id}:{event}
```

Not the connection id alone. One connection produces two records, and 3.20 learned exactly this
with `{delivery}:{attempt}`: a delivery id alone collapsed seven retries into one message. The
same mistake here would collapse a close into its open.

## Payload

`JSONEachRow`-compatible, snake_case, because it leaves the platform.

| field | type | present | notes |
|---|---|---|---|
| `type` | string | always | `"connection.opened"` or `"connection.closed"` — the router's discriminator. **Dropped before the insert; it has no column** |
| `connection_id` | string (uuid) | always | |
| `environment_id` | string (uuid) | always | from the resolved identity, never from a header |
| `user_external_id` | string | always | the customer's own id for the person. Non-null in the table too — it and `environment_id` come from the same non-optional `Identity` |
| `ts` | string (ISO-8601) | always | the instant of the event, not of the publish. **On an open this is `connection.openedAt`** — the same field the meter reads, stamped before the resume and the ack so a reconnect storm gets no free window. On a close it is the instant the socket closed |
| `close_code` | number | close only | the WebSocket close code the socket reported — an integer, not a reason string. **Not drawn from `CLOSE_CODES`**: that registry is the platform's own 4001–4009, and a clean close is 1000 |
| `duration_ms` | number | close only | close `ts` − open `ts`, in milliseconds |

**Absent, not empty.** `exactOptionalPropertyTypes` is on; optional fields are spread in rather
than assigned, and the columns are `Nullable` because 4.4 measured that
`LowCardinality(String)` cannot tell an absent field from an empty one.

**What is never present**: credentials, tokens, the channel list, message content, headers.

## Buffering — and this is the contract, not an optimisation

**Records are buffered in the gateway and published on a tick. Nothing publishes from a socket
handler.** Measured, 2,000 close records three ways:

```
awaited, one at a time   : 0.229 ms each   -> 2.3 s for 10,000 closing at once
core publish + flush     : 0.0030 ms each  -> at-most-once, no ack, no dedup
pipelined, 500 in flight : 0.0034 ms each  -> 67x faster than awaiting, keeps both
```

`session.ts`'s close handler already carries the argument, from chapter 3.24: *"a mass
disconnect would turn one event into a burst of HTTP requests."* A burst of awaited publishes is
the same shape on a different transport, and `meter.ts` already shows the answer — hand over,
and let a tick do the sending.

### One message per record. The tick batches the WAITING, not the payload

**500 records in one message is not the shape here**, and an earlier draft of this section said
it was. What the tick removes is the serial round trip: 500 publishes go out without awaiting
each one and their acks are collected together. Every record keeps its own message, and that is
load-bearing three times over.

**The subject carries the tenant.** `analytics.connection.{opened|closed}.{environment_id}` —
one message has one subject, and a flush spans many tenants and both events. There is no
subject a mixed batch could be published on, and putting one tenant's records where another
tenant's filter reaches them is what `analyticsSubjectFor` refuses a non-UUID to prevent.

**The deduplication id is per record.** One message carries one `Nats-Msg-Id`, so a batched
payload would have to key on the batch — 048 measured that exactly: *"the same token with 500
different rows dropped all 500 and reported success."*

**The consumer takes one record per message.** `route()` is handed a parsed body; an array has
no `type`, falls to the attempt arm, shapes to `null`, and is **terminated**. A batched message
would not land in the `unclaimed` arm this chapter's phase 2 exists to exercise — it would be
destroyed, 500 records at a time, and counted as one.

## The flush interval, and the budget it spends

**FR-ANL-04 allows 60 seconds** from the originating operation to the event being queryable.
This is the first buffered producer in Part 4 — chapter 4.4's publishes per request, straight
from a `finish` listener, so the clause was satisfied without anyone choosing anything — and
buffering is the first thing here that can spend the budget:

```
gateway flush interval   <- named below
ingester batch bound     up to 2 s   (BATCH_MS = 2_000)
insert                   small
                         ---------
FR-ANL-04 allows         60 s
```

**Copying `METER_INTERVAL_MS` would breach it.** The meter ticks every 60,000 ms, and the whole
posture of this chapter is *be like the meter* — so the obvious number is the wrong one. The
meter feeds a monthly quota and has no latency clause over it; this feeds an analytical store
that does.

**And the two pressures are less opposed than they look.** The tick's win comes from removing
the serial round trip from whatever accumulated, not from waiting longer: at 0.0034 ms a record
the publish is effectively free at any interval, and R3's 2.3-second burst is a property of
publishing **per close**, not of a short tick. So a short interval costs almost nothing and buys the whole
budget. **5 seconds** leaves 53 of headroom, and FR-004d measures the real figure rather than
trusting this arithmetic.

## The buffer is bounded, and the bound is part of the contract

Records accumulate between ticks, and a broker that is unreachable means they accumulate
without leaving. **The buffer has a ceiling and reaching it drops records**, because the
alternative on a service holding 10,000 sockets is an out-of-memory that closes all of them —
which satisfies "a publish failure shall not close a connection" at the record level and
violates it at the service level.

`meter.ts` faced this and wrote the rule down:

> **`MAX_RETAINED_CLOSED = 4_000`** — Bounded by closes since the last ACCEPTED report, not by
> time. … **dropping the oldest under-counts, which is the same direction as every other loss
> in this design.**

So: a stated cap, drop on reaching it, **count the drops**, and say which direction the loss
runs. Dropping the oldest loses the earliest events; dropping the newest loses the ones that
describe the outage. Neither is free and the chapter picks one out loud.

### What the cap is bounding, which is not what a flush buffer is

**The number above bounds a retry queue, and copying it without that changes what it means.**
Eleven lines above the constant, `meter.ts` states the rule the constant serves:

> A lost report is repaired by the next one; a repeated one credits nothing; **a report that
> cannot be delivered is DROPPED rather than queued.** The gateway holds no outbox…
>
> **WITH ONE EXCEPTION, AND IT IS THE HONEST HALF OF THAT CLAIM.** A connection that has CLOSED
> has no next report to repair a lost one, so its final total is **retained until a report
> carrying it is accepted.**

`reportOnce` implements it: a closed entry is deleted only after `api.reportUsage` returns, and
on a throw *"the closed ones stay."*

**Every connection event is in that exception.** An open is sent once and a close is sent once;
there is no later record that carries the same fact again. So the meter's rule for its one
special case is this producer's rule for all of it: **a record whose publish failed stays in the
buffer and goes again on the next tick**, and the cap is what stops that queue growing while the
broker is away. A buffer that emptied on every flush regardless of outcome would never reach the
cap at all — an unreachable broker would drain it every five seconds into failures — so the
bound would be unreachable by construction and the losses would all be somewhere else.

**And the outcomes are per record.** One message per record means a flush of 500 has 500
answers, not one. The failed ones are the ones retained; the accepted ones are gone. The meter
never faces this, because it sends one report for everything and gets one answer — which is
another place where copying its shape needs the question it was answering, not just its code.

## Delivery guarantees

- The publish may fail and failing must cost the connection nothing (constitution III,
  FR-ANL-03).
- A failure is logged once, with no payload and no rethrow.
- So **"every connection" is approximate**, and the chapter says so in the paragraph that
  introduces the feature rather than in a footnote. That sentence is 3.20's.
- **A gateway killed with connections open produces opens with no closes.** That is not a bug to
  engineer around; it is a property a dashboard built on these records must tolerate, and the
  chapter publishes the balance for a clean run and a killed one.

## What the consumer must do

```
type "connection.opened" | "connection.closed"  -> connection record
type absent                                     -> attempt record (3.20's compatibility rule)
type "api.request"                              -> request record
anything else                                   -> not mine; do not terminate
```

The third arm on 4.4's `route()`. Until the ingester writes them, connection records land in the
`unclaimed` arm and are redelivered — which is the first real record to exercise that path
rather than a synthetic one.

## Running it

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d
```

Open and close one connection, then look for its pair:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay \
  --data-binary "SELECT event, connection_id, ts, ifNull(toString(close_code),'~absent'),
                        ifNull(toString(duration_ms),'~absent')
                   FROM relay_analytics.connection_events FINAL
                  ORDER BY ts DESC LIMIT 10 FORMAT TSV"
```

`FINAL` is not decoration. 048 measured a bare `count()` answered from part metadata without
reading a row — 0.9 ms and wrong by 100,000 against `FINAL`'s 5.3 ms.
