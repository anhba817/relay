# Data model — chapter 4.4

**Feature**: `specs/049-chapter-4-4/` · **Date**: 2026-09-14

Three shapes and one routing rule. The wire shape is the contract
(`contracts/api-request-event.md`); this file is the store and the decisions behind it.

---

## 1. `relay_analytics.api_requests`

A second table, not a column on `webhook_attempts`. FR-ANL-07 retains for **30 days** and
`webhook_attempts` for 90, and one `TTL` clause cannot express both.

```sql
CREATE TABLE IF NOT EXISTS relay_analytics.api_requests (
    environment_id Nullable(UUID),
    ts             DateTime64(3, 'UTC'),
    request_id     UUID,
    endpoint       LowCardinality(String),
    method         LowCardinality(String),
    status         UInt16,
    latency_ms     UInt32,
    principal_kind LowCardinality(String),
    CONSTRAINT ts_is_real CHECK ts > toDateTime64('2020-01-01 00:00:00', 3, 'UTC')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (environment_id, ts, request_id)
TTL toDateTime(ts) + INTERVAL 30 DAY
```

**Every line of that carries a measurement from a previous chapter.**

- `toDateTime(ts)` because 047 measured `TTL ts + INTERVAL 90 DAY` on a `DateTime64` refused
  with `BAD_TTL_EXPRESSION`, and the SAD had published the broken form since its first draft.
- `CONSTRAINT ts_is_real` because 048 measured that `JSONEachRow` leaves an unmatched column
  at its default, a `DateTime64` default is the epoch, the epoch is older than any TTL, and
  the row is therefore **deleted at insert while the insert returns OK**. The constraint turns
  an absent column into `Code: 469`; the server setting
  `input_format_skip_unknown_fields=0` turns a *renamed* one into `Code: 117`. Two different
  failures, neither covered by the other.
- `ReplacingMergeTree` with `request_id` last in the sorting key because 048 measured that a
  deduplication token derived from a batch is not stable across a redelivery: a retry at a
  different `max_messages` returned `4,5,1,2,3,6,7,8,9,10` where the original batch was
  `1,2,3,4,5`. **Idempotence belongs to the record's own key.**
- `LowCardinality(String)` on `endpoint` because FR-005 makes it a route template — 41 of
  them at this tag — rather than a path with ids in it, which would be unbounded.

### The one open decision: `Nullable(UUID)`

`environment_id` is written `Nullable(UUID)` above and that is a **proposal, not a
conclusion**. Two shapes are live:

| shape | for | against |
|---|---|---|
| one table, `Nullable(UUID)` | one insert path, one TTL, one query surface; `uniqExact` ignores NULL exactly as Postgres's `count(DISTINCT)` does (047's precedent) | a nullable tenant column in the store constitution I is about — the reading has to be right |
| two tables, tenant and tenantless | the tenant table's column is `NOT NULL` and the clause needs no reading at all | two TTLs to keep in step, two inserts, and a reconciliation that has to union them |

R7 chose the *reading*; this chooses the *storage*, and phase 3 decides it with the isolation
test in hand rather than here.

**What is not open**: no sentinel value. Not the zero UUID — 047 measured it producing one
phantom active user per environment, holding a deleted author's messages. Not an empty
string. A value that means "unknown" inside the tenant column is the failure this whole
section exists to avoid.

### Why `principal_kind` is a column and the principal's identity is not

`application`, `user`, `platform`, or absent. It is the column that makes R7's argument
answerable from the data: *how many records have no tenant, and why not.* Without it the
tenantless rows are one undifferentiated population and the chapter's central number cannot
be computed from the table it is about.

The key id, the user external id and the service name are **not** recorded. `keyId` identifies
a credential; `userExternalId` is a customer's own identifier for a person. Neither is needed
to answer FR-ANL-07's question, and NFR-SEC-06 is the reason to stop at the class.

---

## 2. The wire record

Full field list, types and the tenantless arm in `contracts/api-request-event.md`. The parts
that are data-model decisions:

- **`endpoint` is the matched route template**, `req.route.path`, measured in R6 to be the
  full template for this api because Nest registers on the root instance. A 404 has no
  `req.route`, so `endpoint` is absent and the consumer stores a stated sentinel rather than
  guessing — an unmatched request genuinely has no endpoint.
- **`ts` is the field name on the wire**, not `started_at` or `at`. 048's whole argument was
  one rename that fails silently; this chapter declines to introduce a second one. Where the
  publisher and the column can share a name, they share it.
- **No body, no headers, no credential** (R8).

---

## 3. The routing rule

One stream, two record types, and the consumer has to tell them apart **before** it shapes
anything.

```
type absent            -> attempt record   (the compatibility rule)
type = "api.request"   -> request record
type = anything else   -> not mine: leave it, do not terminate
```

**The absent case is the load-bearing one.** 3.20's `AttemptEvent` has no `type` field and
never will for the records already written — the live stream holds 37 of them at this tag.
A reader of anything durable cannot require a field its writer did not have; that sentence has
cost this project a production incident already, when a required `attachments` on
`outboxEventSchema` terminated every in-flight `message.created` written by the previous
binary.

**And the third arm is the defect this chapter exists not to ship.** R1 measured what today's
consumer does with a record it does not understand: one `error` line carrying a stream
sequence, and `m.term()`. Never redelivered. The stream still reported 2 of 2 messages and
the consumer reported `num_pending 0` — **both instruments agreeing that nothing is wrong.**

---

## 4. Entities and their relationships

| entity | holds | reaches a tenant |
|---|---|---|
| **API request event** | request id, ts, endpoint, method, status, latency, principal kind, environment when there is one | directly, or not at all |
| **Tenantless request event** | the same fields, no environment | never, by construction (R3b) |
| **`api_requests` row** | the above, plus whatever the TTL has not yet removed | through `environment_id` |
| **`webhook_attempts` row** | unchanged by this chapter | through `environment_id`, non-null |

There is no foreign key and no join. The analytical store does not reference the operational
one — constitution III — and `environment_id` is on the row rather than a hop away, which is
the whole reason chapter 4.2 chose `ORDER BY (environment_id, ts)`.
