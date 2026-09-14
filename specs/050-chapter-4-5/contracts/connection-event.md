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

**There is no `_none` arm here.** 4.4 needed one because a request can be made by nobody. A
connection event is emitted after a handshake, and a handshake produces an identity. If phase 1
finds a case that contradicts that, it gets its own decision rather than borrowing 4.4's.

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
| `user_external_id` | string | always | the customer's own id for the person |
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
awaited, one at a time : 0.229 ms each   -> 2.3 s for 10,000 closing at once
core publish + flush   : 0.0030 ms each  -> at-most-once, no ack, no dedup
batched 500 per publish: 0.0034 ms each  -> 67x faster than awaiting, keeps both
```

`session.ts`'s close handler already carries the argument, from chapter 3.24: *"a mass
disconnect would turn one event into a burst of HTTP requests."* A burst of awaited publishes is
the same shape on a different transport, and `meter.ts` already shows the answer — hand over,
and let a tick do the sending.

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
