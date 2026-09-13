# Contract — the analytics ingester

## What it is

One process. It consumes `analytics.>` from the `ANALYTICS` stream and writes to
`relay_analytics`. It does nothing else, and in particular it does not read or write
PostgreSQL on the ingestion path (constitution III, FR-009).

## The loop

| step | behaviour |
|---|---|
| **fetch** | A durable pull consumer on `analytics.>`, **`max_deliver: -1`**. Batch bounded by **both** a row count and an elapsed interval — DR-11 publishes 2 s or 10,000 rows — because a count alone stalls a quiet tenant forever and an interval alone gives no bound under load. The batch's shape carries no meaning: deduplication is on the record (see **insert**). |
| **shape** | Allow-list, mirroring the publisher's own. A field nobody mapped is dropped loudly at review time rather than silently at runtime. |
| **insert** | One statement. No deduplication token: the table is a `ReplacingMergeTree` keyed on `(environment_id, ts, delivery_id, attempt)`, so a re-inserted record collapses regardless of how it was batched. **The insert carries no assumption about grouping**, which is the property the first design needed and did not have. |
| **acknowledge** | **Only after the insert returns.** A record that was not written is not acknowledged (FR-003). |
| **malformed** | Counted and **terminated at the parse** (FR-006b). With no redelivery limit this is what keeps a poison record from retrying forever: retry forever on transport or store failure, terminate on bytes that will fail the same way every time. |

## What it guarantees, and what it does not

**Guarantees**: every record acknowledged is in the store; a redelivery of an
already-written batch adds no row; the store being unreachable loses nothing that the
stream still holds.

**Does not guarantee**: that a record waits indefinitely. With `max_deliver: -1` the only
bound is the queue's seven-day retention — which makes retention exhaustion the single path
to actual loss, rather than one of two.

**Does not guarantee**: that nothing was lost *before* it ran. The stream is bounded at
seven days and 1 GiB with `discard: old`, and the broker drops the oldest records without
telling anyone. An ingester that has been down long enough cannot distinguish "there was
nothing" from "there was something and it is gone" — FR-011 requires the chapter to say so
rather than imply completeness.

**Does not guarantee** that a bare `SELECT` is correct. The duplicate is physically present
until a merge, so every read of this table takes `FINAL`. A caller that forgets over-counts
by however many redeliveries happened — which is the cost of buying deduplication that does
not depend on batch boundaries, and the chapter publishes it rather than burying it.

## Isolation

| | |
|---|---|
| **Writes** | `relay_analytics` only. |
| **Reads** | the stream only. |
| **PostgreSQL** | never, on this path. The reusable consumer runtime's claim table is Postgres-backed (R1), which is exactly why it cannot be reused unchanged. |
| **The send path** | unaffected by anything here, including this process being absent (NFR-REL-05). |

## Schema changes

Through `analytics/apply.mjs` and nothing else. `0003_webhook_attempts.sql` is one
statement, names `relay_analytics`, and is recorded in the ledger by filename and checksum.
A second run of the runner reports that it applied nothing.

**This is the ledger's first real use since the chapter that built it**, which makes it the
first chance to find out whether the refusals 4.2 tested red fire for somebody who is not
trying to make them fire.
