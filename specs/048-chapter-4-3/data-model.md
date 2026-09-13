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
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ts)                            -- DR-07, as message_events
ORDER BY (environment_id, ts, delivery_id, attempt)  -- tenant-then-time, AND the
                                                     -- record's natural key
TTL toDateTime(ts) + INTERVAL 90 DAY                 -- DR-09, and toDateTime because
                                                     -- the published form is refused
CONSTRAINT ts_is_real CHECK ts > toDateTime64('2020-01-01 00:00:00', 3, 'UTC')
```

**THE CONSTRAINT IS NOT DEFENSIVE PROGRAMMING. IT IS THE ONLY THING BETWEEN A FIELD-NAME
TYPO AND AN EMPTY TABLE.** The publisher's field is `attempted_at` and this column is `ts`.
A `JSONEachRow` insert whose keys do not match column names leaves the column **at its
default, with no error** — and the default for a `DateTime64` is the epoch, which is older
than the ninety-day TTL, so the row is **deleted at insert**. Measured: a 1970 row into this
table gives 0 rows, before and after a merge.

The whole chain reports success. The insert returns OK, the consumer acknowledges, the
stream drains to zero, and the table is empty. With the constraint:

    Code: 469. DB::Exception: Constraint `ts_is_real` ... violated       0 rows

**Two more settings on every insert, and they catch different halves:**

    input_format_skip_unknown_fields = 0    a RENAMED field is Code: 117, loud
                                            (the default is 1, which is why it was silent)
    date_time_input_format = best_effort    the ISO-8601 string parses; the default
                                            `basic` refuses it with Code: 27

The constraint catches an **omitted** field, which `skip_unknown_fields` does not: a row with
no `ts` at all is not an unknown field, it is an absent one, and it takes the default
without complaint.

**The sorting key is the deduplication key, and it has to be both things at once.**
`(environment_id, ts)` is the ordering 4.2's whole argument is about — tenant, then time.
`(delivery_id, attempt)` is what makes a record unique. Putting all four in the sorting key
gets the range scans and the dedup from one declaration, and it is safe **because `ts` comes
from `attempted_at`, a field of the record** rather than from when it was consumed: the same
record always sorts to the same place, however it was batched.

**Reads take `FINAL`.** The duplicate is physically present until a merge collapses it, so
a bare `SELECT count()` over this table over-counts. That is chapter 4.2's rollup lesson one
engine over — there the read contract became `sum()` with `GROUP BY`, here it becomes
`FINAL` — and the chapter measures what it costs instead of asserting it is small.

**Verified against the case that killed the first design**, not against the easy one. Three
differently-cut batches covering the same 500 records:

    batch {1..500}              count   500      FINAL 500
    regrouped retry {1..300}    count   800      FINAL 500
    regrouped retry {101..500}  count 1,200      FINAL 500

**`insert_deduplication_token` is not used**, and the analysis pass is why. It would have
been cheaper — the server refuses the duplicate block at insert, with no read cost — but it
requires a token that is stable across a redelivery, and **JetStream batch boundaries are
not**: a retry returned `4,5,1,2,3,6,7,8,9,10`, out of order and interleaved with newer
messages. Worse, the token keys on **itself and not on the content**: the same token with
500 completely different rows dropped all 500 and reported success. A token that is not
provably unique per batch is not a weak deduplication, it is silent data loss.

## The dedup key, and why it is not the publisher's

The publisher already sets a **broker-side** deduplication id, `{deliveryId}:{attempt}`,
chosen in the webhook dispatcher chapter after the delivery id alone collapsed seven retries
into one message. That id stops a *publisher* sending the same record twice within the
broker's window. It does nothing about a *consumer* being handed the same record twice,
which is what at-least-once delivery means.

The ingester therefore dedups on the **record**, never on the batch. `{delivery_id,
attempt}` is the same pair the publisher already treats as identity, which is the strongest
argument for it: the two mechanisms then agree about what a distinct record is, at two
different layers, for two different failure modes. The chapter has to say so, or a reader
will assume the publisher's id already covers the consumer's problem — it does not, because
at-least-once is about being handed the same record twice, not about sending it twice.

## What is not in this table

No payload, no headers, no URL, no secret. FR-ANL-11 and DR-08 keep content out of the
analytical store, and an attempt record is one of the places it would be easiest to leak.
