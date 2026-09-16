# Data model — chapter 4.8

Nothing is created. One table is read, one query shape is added, and one quantity is defined
that did not exist. Every figure is from `research.md`.

---

## The table being read: `relay_analytics.api_requests`

Shipped by chapter 4.4. Read from `SHOW CREATE TABLE` rather than from the migration file,
because chapter 4.6 learned that the server normalises what a file says.

| column | type | note |
|---|---|---|
| `environment_id` | `Nullable(UUID)` | **Nullable on purpose** (4.4). 60.5% of rows are NULL and can never be served to a tenant |
| `ts` | `DateTime64(3, 'UTC')` | milliseconds, and it ties — 43 pairs hold 91 rows |
| `request_id` | `UUID` | the tie-breaker a cursor needs |
| `endpoint` | `LowCardinality(Nullable(String))` | absent for an unmatched route — 22 rows |
| `method` | `LowCardinality(String)` | |
| `status` | `UInt16` | |
| `latency_ms` | `Float32` | fractional: three of four real requests are under 1 ms (4.4) |
| `principal_kind` | `LowCardinality(String)` | `application`, `user`, `platform`, `none` |
| `refused_at` | `LowCardinality(String)` | `middleware`, `guard`, `unmatched`, `handler` |
| `limited_operation` | `LowCardinality(Nullable(String))` | the quota class a 429 refused on |

    ENGINE      ReplacingMergeTree
    PARTITION   toYYYYMM(ts)
    ORDER BY    (environment_id, ts, request_id)
    TTL         toDateTime(ts) + toIntervalDay(30)
    SETTINGS    allow_nullable_key = 1, index_granularity = 8192

**The six fields FR-ANL-07 names** are request id, timestamp, endpoint, method, status and
latency. The table carries four more, and whether the surface returns them is a contract
decision rather than a storage one.

---

## New: the request-log query

A validated value object, not a table. Its shape reuses `historyQuerySchema`'s (R3) rather than
inventing a second pagination vocabulary for the same product.

| field | type | default | rule |
|---|---|---|---|
| `from` | ISO instant | 24 hours ago | inclusive |
| `to` | ISO instant | now | **exclusive**, so an hour boundary belongs to one page only — the half-open rule chapter 4.7 paid for |
| `cursor` | opaque string | absent | encodes `(ts, request_id)`; the platform's other cursor stands on a monotonic sequence and this table has none |
| `direction` | `older` \| `newer` | `older` | |
| `limit` | integer | 50 | 1–200, the bound the message history already uses |

**Validation happens before any value reaches a SQL string** (R9). This is the first
caller-supplied value this platform puts into a ClickHouse statement.

---

## New: the request-log page

| field | type | note |
|---|---|---|
| `rows` | array | at most `limit`, in `direction` order |
| `next_cursor` | string \| null | null when the page is the last one |
| `window` | `{ from, to }` | echoed, because a defaulted window a caller did not send is a window they will misread |
| `retention_edge` | ISO instant | **the answer to R8.** A window older than this returned 0 rows because the data is gone, not because nothing happened |

---

## Defined, not stored: end-to-end delivery latency

FR-ANL-10 names a quantity nobody has defined. It is a duration between two instants, and the
chapter's job is to name them. What exists today:

| instant | recorded where | reachable from the analytical store |
|---|---|---|
| message committed | `messages.created_at` (PostgreSQL) | **no** — constitution III forbids the read |
| event published | outbox row → JetStream | not timestamped into the analytical path |
| webhook POST started | `deliver.ts`, in memory | no |
| endpoint answered | `webhook_attempts.latency_ms`, as a **duration from the POST** | yes, but it is the last leg only |
| frame written to a socket | nowhere | no |

**`message_events.delivery_latency_ms` is the column the SAD reserves for this** —
`Nullable(UInt32)`, 0 rows, 0 writers, carried as `gaps.md` 048-2 through five features.

---

## Percentile row, if phase 5 produces one

| field | type | note |
|---|---|---|
| `environment_id` | UUID | |
| `hour` | DateTime | FR-ANL-10 says per tenant per hour |
| `p50`, `p95`, `p99` | Float | **`quantileExact`, not `quantile`** — R2 measured the sketch wrong at every sample size and worst at the smallest, and an hour of one tenant's deliveries is the smallest |
| `n` | UInt64 | published beside the percentiles, because a p99 over four samples is a maximum wearing a percentile's name |
