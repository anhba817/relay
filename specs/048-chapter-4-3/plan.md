# Implementation Plan — chapter 4.3, the consumer that was promised

**Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md) ·
**Data model**: [data-model.md](./data-model.md) ·
**Contract**: [contracts/ingester.md](./contracts/ingester.md) ·
**Quickstart**: [quickstart.md](./quickstart.md)

## Summary

A service that drains the `ANALYTICS` stream into the analytical store, in batches, exactly
once. The stream has existed since chapter 3.20 with seven-day retention and **zero
consumers**; the store and its schema runner landed in 4.2. This chapter joins them.

## Technical Context

**Language**: TypeScript on Node 22, as everything else (constitution VII).
**Primary dependencies**: **none added.** `nats` is already a dependency; ClickHouse is
reached by Node's own `fetch` against the HTTP interface, the transport 4.2 established.
**Storage**: ClickHouse `relay_analytics` for writes; **PostgreSQL is not touched on the
ingestion path** (constitution III, FR-009). Deduplication is `ReplacingMergeTree` on the
record's natural key — **not** `insert_deduplication_token`, which the analysis pass
measured to be unusable here.
**Testing**: the api lane's integration harness. Nothing under `analytics/` joins a lane —
`vitest.coverage.config.mts`'s four include globs are `packages/*/src/**` and
`services/*/src/**` — so **a consumer written under `services/` IS collected** and one
written under `analytics/` is not. That is an argument for where the ingester lives.
**Scale**: DR-11 publishes 2 s or 10,000 rows. The stream is bounded at 7 days and 1 GiB
with `discard: old`.
**Constraints**: the analytical store being down must not touch messaging (NFR-REL-05); the
queue must absorb at least 24 h (NFR-REL-08, and 7 days is what it actually holds); and
**the consumer sets no redelivery limit** — `max_deliver: -1`, bounded by that retention and
nothing shorter.

## Constitution check

| principle | how this chapter stands |
|---|---|
| **I — tenancy** | Every record carries `environment_id`, and it is a subject token, already validated as a UUID at publish time. |
| **III — two data paths, never crossed** | The whole point. The ingester reads the queue and writes ClickHouse. **It must not touch Postgres**, and R1 found the obvious reuse would. |
| **VII — boring by design** | A fourth TypeScript service needs no argument. The dedup mechanism is a server setting and a token, not a framework. |

**One gate needs stating rather than passing silently.** The reusable consumer runtime
carries a Postgres-backed claim. Reusing it as-is would cross principle III on the
ingestion path; the chapter either parameterises the claim or writes a second runtime, and
says which (FR-014).

## The design, in one paragraph

Fetch a batch from a durable pull consumer on `analytics.>`. Shape the records. Insert them
in one statement into a `ReplacingMergeTree` ordered by
**`(environment_id, ts, delivery_id, attempt)`** — the record's own natural key.
Acknowledge only after the insert returns. A redelivery writes the same key again and the
engine collapses it; reads take `FINAL`. **The dedup depends on nothing about how the
records were grouped**, which is the property the first design silently assumed and did not
have.

## The design this replaced, and why it does not work

The plan's first version derived an `insert_deduplication_token` from the batch's stream
sequence range. **JetStream batch boundaries are not stable across a redelivery**, measured:

    original batch, max_messages=5   seqs 1,2,3,4,5              token range 1-5
    retry with     max_messages=3    seqs 1,2,3                  token range 1-3
    retry with     max_messages=10   seqs 4,5,1,2,3,6,7,8,9,10   token range 4-10

The retry comes back **out of order and interleaved with newer messages**, so the "range" is
neither contiguous nor the same set. A different token means the duplicate is inserted, and
DR-11's two-second bound makes it worse: batch boundaries then depend on arrival timing, so
even a constant `max_messages` regroups.

**And the token is more dangerous than it looks.** It keys on the token alone, not on the
content: a second insert carrying the same token and 500 **completely different** rows was
dropped, all 500, with no error. So a range like `4-10` colliding with another batch's range
is **silent data loss**, not a duplicate.

**One mechanism, verified against the failure case rather than the happy one.** Three
differently-cut batches over the same 500 records: physical count 500 → 800 → 1,200,
`FINAL` **500** every time.

## What `FINAL` costs, and why it is acceptable here

It is chapter 4.2's `SummingMergeTree` lesson again — correctness lives in the read, not in
a merge somebody has to run. 4.2 paid it with `sum()` and `GROUP BY`; this table pays it
with `FINAL`, and **the chapter measures the cost rather than asserting it is small**. What
makes it acceptable is that the alternative is not "cheaper dedup", it is "no dedup".

**The existing consumer runtime's claim table** would have avoided all of this, and it
writes to Postgres inside a transaction. On this path that is the one thing principle III
forbids.

## The redelivery limit is a bound on a different failure

Both existing consumers set one — `MAX_DELIVER = 5` on the api's runtime, 10 on the
dispatcher, both with a 30-second `ack_wait`. For a webhook dispatcher that is sound: an
endpoint that has failed ten times is probably gone, and retrying it forever helps nobody.

**It does not transfer.** Measured at `max_deliver: 3`: rounds 1–3 delivered, round 4
delivered nothing, and nothing ever again — while the stream still held every message and
the consumer reported **`num_pending 0`**. A store that is restarting is not an endpoint
that is gone, and five attempts at thirty seconds is **two and a half minutes** before an
outage becomes a silent strand.

So this consumer sets `max_deliver: -1` and lets the queue's seven-day retention be the only
bound. That makes the poison case load-bearing rather than tidy: a payload that will never
parse has to be terminated where the defect is detectable, or it retries forever. The
existing runtime already draws that line — *"A payload that will never parse must not consume
five delivery attempts before being dropped anyway. The same bytes fail the same way every
time."* **Retry forever on transport, terminate at parse. One rule, two arms.**

## Project structure

```
relay-platform/
├── services/
│   ├── api/  dispatcher/  gateway/
│   └── <the ingester>               NEW — placement is a Phase 1 decision, and the
│                                    test-lane globs above are an input to it
├── analytics/
│   ├── 0000_message_events.sql      4.2
│   ├── 0001_daily_usage.sql         4.2
│   ├── 0002_schema_applied.sql      4.2
│   ├── 0003_webhook_attempts.sql    NEW — the first statement file added through the
│   │                                ledger since the chapter that built it
│   └── apply.mjs                    4.2, unchanged
└── compose.yaml                     possibly a service entry
```

**Structure decision**: the ingester is a service rather than a script, because it is
long-running, because it is the first thing to write to ClickHouse without a human present,
and because `services/*/src/**` is what the coverage lane collects.

**AND A SERVICE IS SIX FILES AND A PRECEDENT NOBODY HAD PRICED.** `services/dispatcher/`
holds `Dockerfile`, `package.json`, `src/`, `tsconfig.json`, `tsconfig.build.json` and
`vitest.integration.config.mts`. Chapter 3.19 introduced it at **5,889 prose words and 47
titled fences** — against SC-008's 2,000–4,000 bound and 4.2's 2,580 words and 2 fences.
It fenced `package.json` and the sources and **skipped the Dockerfile, both tsconfigs and
the vitest config**; that is the established precedent for scaffolding, and it is followed
knowingly here rather than rediscovered while writing prose.

The ingester is a much smaller job than the dispatcher — fetch, shape, insert, acknowledge,
against HTTP delivery with signing, retries and expansion — so 47 is a ceiling rather than
an estimate. **But a split is likely rather than merely permitted**, and the chapter is
planned on that basis.

**Two edits a fourth service does NOT need**, checked because each would have been a hunked
amendment to a fenced file with its own anchoring risk: `pnpm-workspace.yaml` globs
`services/*`, and `turbo.json` names **no service at all** — zero occurrences of
`dispatcher` or `gateway`.

## Phases

- **Phase 1 — premises.** Re-run every number in `research.md` at this chapter's tag,
  including the stream's depth and the absence of a consumer. Record the fence-chain opening
  broken down by kind and locale.
- **Phase 2 — the table.** `0003_webhook_attempts.sql` through 4.2's ledger, with the
  dedup window set, and the SAD amended to publish it (FR-008).
- **Phase 3 — US1, the drain.** The consumer, the batch bounds, the insert. The stream goes
  to zero pending and the rows appear.
- **Phase 4 — US2, the store is gone.** Stop ClickHouse, exercise the platform, measure that
  messaging is untouched and the queue grows; restart and drain.
- **Phase 5 — US3, the redelivery.** Force one, measure that the counts do not move, and
  prove the refusal fires for its own reason rather than incidentally.
- **Phase 6 — the chapter**, the amendments, the gates, the tag `part4-ch3`.

## What this chapter does not build

The reconciliation job (FR-ANL-06), the query surface (FR-ANL-07), latency percentiles
(FR-ANL-10), a producer for `message_events.delivery_latency_ms`, connection events, and API
request events. **`webhook_attempts.latency_ms` is not `message_events.delivery_latency_ms`**
— one is how long an endpoint took to answer, the other is how long a message took to reach
a client. Nothing produces the second one and this chapter does not change that.
