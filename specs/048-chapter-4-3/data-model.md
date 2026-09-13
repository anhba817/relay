# Data model — chapter 4.3

One new analytical table, in `relay_analytics`, added through the ledger chapter 4.2 built.
**Every statement names the database**, for the reason 047 R14 recorded: `CLICKHOUSE_DB`
creates a database without making it the session's, so an unqualified `CREATE TABLE`
succeeds into `default` and the schema then exists where nothing looks.

## `webhook_attempts` — one row per delivery attempt

Shaped by what the publisher already sends (R2), not by a document — **SAD §6.2 publishes
`message_events` as *representative* and names `emoji_events`; no table for delivery
attempts is published anywhere.** FR-008 amends that.

| column | type | source field | why |
|---|---|---|---|
| `environment_id` | `UUID` | `environment_id` | the tenant; already validated as a UUID at publish time because it becomes a subject token |
| `ts` | `DateTime64(3, 'UTC')` | `attempted_at` | an ISO string on the wire |
| `delivery_id` | `UUID` | `delivery_id` | |
| `endpoint_id` | `UUID` | `endpoint_id` | |
| `event_id` | `UUID` | `event_id` | |
| `attempt` | `UInt8` | `attempt` | 1..7; the retry number, and the half of the dedup key that matters |
| **`status`** | **`Nullable(UInt16)`** | `status?` | **absent means nothing answered.** A non-nullable column would write 0 and claim an endpoint returned status zero |
| **`error`** | **`Nullable(String)`** | `error?` | absent means there was no error, which is not the same as an empty one |
| `latency_ms` | `UInt32` | `latency_ms` | how long the ENDPOINT took. **Not `message_events.delivery_latency_ms`**, which is how long a message took to reach a client and still has no producer |
| `outcome` | `LowCardinality(String)` | `outcome` | |

```
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)                    -- DR-07, as message_events
ORDER BY (environment_id, ts)                -- the same tenant-then-time ordering
TTL toDateTime(ts) + INTERVAL 90 DAY         -- DR-09, and toDateTime because the
                                             -- published form is refused (4.2, SAD 1.2)
SETTINGS non_replicated_deduplication_window = <n>
```

**The `SETTINGS` line is the load-bearing one and it is the easiest to leave out.** Without
it an `insert_deduplication_token` is accepted and ignored — the insert succeeds, the
duplicate lands, and nothing reports anything (R5). `<n>` is a bound on how far back a
redelivery can be recognised, so it is a number to choose against measured redelivery
behaviour rather than a default to inherit.

**`ReplacingMergeTree` is not used**, and R4 is why: it leaves the duplicate physically
present until a merge, so `SELECT count()` returns 2,000 where the truth is 1,000 and only
`FINAL` is correct. That is chapter 4.2's rollup lesson one engine over, and this table can
avoid it entirely by refusing the duplicate at insert instead.

## The dedup key, and why it is not the publisher's

The publisher already sets a **broker-side** deduplication id, `{deliveryId}:{attempt}`,
chosen in the webhook dispatcher chapter after the delivery id alone collapsed seven retries
into one message. That id stops a *publisher* sending the same record twice within the
broker's window. It does nothing about a *consumer* being handed the same record twice,
which is what at-least-once delivery means.

The ingester's token is therefore about the **batch**, not the record: derived from the
stream sequence range the batch covers, so a redelivery of the same range reproduces it
exactly. Two different mechanisms, two different failure modes, and the chapter has to say
so or a reader will assume the first one covers the second.

## What is not in this table

No payload, no headers, no URL, no secret. FR-ANL-11 and DR-08 keep content out of the
analytical store, and an attempt record is one of the places it would be easiest to leak.
