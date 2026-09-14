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
    endpoint       LowCardinality(Nullable(String)),
    method         LowCardinality(String),
    status         UInt16,
    latency_ms     UInt32,
    principal_kind LowCardinality(String),
    refused_at     LowCardinality(String),
    limited_operation LowCardinality(Nullable(String)),
    CONSTRAINT ts_is_real CHECK ts > toDateTime64('2020-01-01 00:00:00', 3, 'UTC')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (environment_id, ts, request_id)
TTL toDateTime(ts) + INTERVAL 30 DAY
SETTINGS allow_nullable_key = 1
```

**THE LAST LINE WAS MISSING AND THE STATEMENT DID NOT APPLY.** The first version of this
section published the DDL without `SETTINGS`, and ClickHouse 25.3 refuses it:

```
Code: 44. DB::Exception: Sorting key contains nullable columns, but merge tree
setting `allow_nullable_key` is disabled. (ILLEGAL_COLUMN)
```

**This section cited 047's identical finding three lines below the statement that repeated
it.** 047 found SAD §6.2's DDL refused with `BAD_TTL_EXPRESSION` after it had been published
since the first draft; this one was written in the same hour as the sentence recording that,
and was refused for a different reason by the same server. A DDL that has not been run is a
DDL that has not been checked, and the citation of a previous failure is not a substitute for
running this one.

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

### `endpoint` is nullable, and the first draft made 048's mistake on a new column

The contract defends this distinction in a paragraph: *"an absent `endpoint` means the route did
not match, which is a fact, and `""` would be a claim about a route named the empty string."*
The first draft of this table then gave it `LowCardinality(String)`, which cannot hold the
difference. Measured through `JSONEachRow`:

```
                    LowCardinality(String)   Nullable(String)
absent field                ''  (len 0)            NULL
explicit ""                 ''  (len 0)            ""
```

**Indistinguishable.** A field the publisher omits takes the column's default silently — 048's
defect exactly, on a different column. 048's version was fatal because a `DateTime64` default is
the epoch and the epoch falls outside the TTL; this one is quieter, because the row survives and
only the value is wrong.

**And none of 048's three guards reaches it.** `input_format_skip_unknown_fields=0` catches an
*unknown* field, not an absent one. `ts_is_real` catches an absent `ts`. A CHECK cannot help
here at all, because **absent is legal for `endpoint`** — which is the whole point.

`LowCardinality(Nullable(String))` holds all three cases and keeps the encoding, measured:

```
NULL          <- absent
"" (empty)    <- explicit empty string
/v1/webhooks  <- a real template
```

**The sweep is complete rather than illustrative.** The contract has exactly two optional
fields plus `limited_operation`. `environment_id` was already `Nullable(UUID)`; `endpoint` was
the only one landing in a column that could not say "absent".

### The one open decision: `Nullable(UUID)`

`environment_id` is written `Nullable(UUID)` above and that is a **proposal, not a
conclusion**. Two shapes are live:

| shape | for | against |
|---|---|---|
| one table, `Nullable(UUID)` | one insert path, one TTL, one query surface; `uniqExact` ignores NULL exactly as Postgres's `count(DISTINCT)` does (047's precedent) | a nullable tenant column in the store constitution I is about — the reading has to be right |
| two tables, tenant and tenantless | the tenant table's column is `NOT NULL` and the clause needs no reading at all | two TTLs to keep in step, two inserts, and a reconciliation that has to union them |

R7 chose the *reading*; this chooses the *storage*, and phase 3 decides it with the isolation
test in hand rather than here.

**Both arms were measured before this was written, which is what the first version skipped.**
With `SETTINGS allow_nullable_key = 1` and merges stopped so the neighbour is held still, six
inserts — three tenantless and three tenant, each identical to its pair:

```
physical count()   6      count() FINAL      2
tenantless FINAL   1      tenant A FINAL     1      tenant B FINAL  0
```

So deduplication works with a NULL in the sorting key, and the tenantless row is invisible to
both tenant filters — **FR-010 holds at the storage layer, not only at the subject layer.**
The one-table arm is therefore available; it costs one non-default merge-tree setting, and
the setting has to be argued in the chapter rather than pasted.

**`SYSTEM STOP MERGES` is part of that measurement, not hygiene.** The first run of this probe
read `count()` between two insert batches and got **2 after six inserts**, because a merge ran
in the gap — which reads as four inserts vanishing. That is 047's TTL lesson in a different
costume: a row count taken the moment a load finishes is a moment, not a measurement.

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
  full template for this api because Nest registers on the root instance.
- **And `req.route` is absent for two different reasons, which the first draft of this section
  treated as one.** It said *"an unmatched request genuinely has no endpoint"* — true of a 404,
  and false of a request refused in middleware. `req.route` is set by the router; a middleware
  refusal ends the response before the router runs. A **defined** route refused by the rate
  limiter therefore records no endpoint, and that is the request an operator most wants
  attributed.
- **`refused_at` carries the distinction**: `handler`, `guard`, `middleware`, `unmatched`. It is
  the column that makes *"which endpoint is being rate-limited"* answerable at all, because
  without it the two kinds of 429 this api produces are one undifferentiated population.
- **The producer's function is `toRequestEvent()`, not `shape()`.** Two functions named
  `shape` already sit on this path doing different transforms — `webhooks/analytics.ts::shape`
  takes a record to the wire, `ingester/src/shape.ts::shape` takes the wire to a row. A third
  would make `grep 'shape('` return three answers across the exact boundary whose silent
  mismatch was 048's central defect.
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
never will for the records already written — the live stream holds 36 of them at this tag.
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
