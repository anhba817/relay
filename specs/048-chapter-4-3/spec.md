# Feature Specification: chapter 4.3 — the consumer that was promised

**Feature**: `specs/048-chapter-4-3/` · **Part 4, movement II, chapter 3 of 22**
**Created**: 2026-09-13
**Status**: specified

## Why this chapter is not the one the plan said

`docs/12-part-4-structure.md` planned chapter 3 as *"A second store needs a second
ledger"* — a migration runner and an identity scheme for a store the Postgres runner
cannot serve — and §7.1 said **"decide it before ch 2 is written."** Chapter 4.2 did more
than decide it. Checked item by item against that brief:

| ch 3's brief | state |
|---|---|
| a second runner for a store the Postgres runner cannot serve | shipped, `analytics/apply.mjs` |
| an identity scheme | shipped, a filename + checksum ledger |
| idempotence that reports what it did | shipped, demonstrated by 047 T037/T038 |
| 045-69's lesson, that identity going wrong is expensive | shipped, a checksum refusal tested red |

So movement II has one subject left, and it is the one the plan called chapter 4:
**the ingester**. Part 4 contracts from 23 chapters to 22 and every ordinal after 3 moves
down by one; milestones land at 9, 17 and 22. This is the second contraction — movement I
did the same during grooming — and `docs/12` §3 already accepts that ordinals churn while
movements absorb it.

## The premise, run rather than assumed

Asked of the broker with the stack up:

```
ANALYTICS    messages 31    bytes 15,139    consumers 0
```

**Something has been publishing into that stream since chapter 3.20 and nothing has ever
read it.** `services/api/src/webhooks/analytics.ts` publishes a record for every webhook
delivery attempt; `jetstream.publisher.ts` creates the stream with seven-day retention and
`discard: old`; and every reference to `ANALYTICS_STREAM` outside the protocol package is
in that publisher, creating or updating the stream. The one consumer runtime in the
repository (`services/api/src/consumer/runtime.ts`) filters on `events.>`.

The stream's own comment says so in as many words: *"no acknowledgement anywhere: nothing
consumes this stream in this chapter."* This is that chapter.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The stream drains into the store (Priority: P1)

An operator starts the ingester. The records that have been accumulating in `ANALYTICS`
become rows in the analytical store, and new attempts arrive without anyone running a
script.

**Why this priority**: it is the chapter's reason to exist and the first time a *service*
writes to ClickHouse rather than a loader invoked by hand.

**Independent test**: publish a known number of attempt records, start the ingester, and
count rows in the analytical store against the stream's delivered count.

**Acceptance scenarios**

1. **Given** a stream holding N attempt records and an empty target table, **When** the
   ingester runs, **Then** the table holds N rows and the consumer reports zero pending.
2. **Given** a running ingester, **When** a webhook delivery attempt is published,
   **Then** it appears in the store within one batch interval.
3. **Given** fewer records than the batch threshold, **When** the batch interval elapses,
   **Then** they are written anyway rather than waiting for a full batch.
4. **Given** a running ingester, **When** the send path is exercised, **Then** no request
   waits on an analytical write (FR-ANL-02).

### User Story 2 - The analytical store can be gone (Priority: P2)

ClickHouse is stopped. Messaging continues, webhook deliveries continue, and the records
accumulate in the queue rather than being lost. When the store returns, the backlog drains.

**Why this priority**: NFR-REL-05 is the clause that makes a second store affordable. If
losing it degrades messaging, the separation bought nothing.

**Independent test**: stop the store, exercise the platform, confirm messaging is
unaffected and the stream's message count rises; restart it and confirm the backlog drains
to zero with no gap in the rows.

**Acceptance scenarios**

1. **Given** the analytical store is unreachable, **When** attempts are published, **Then**
   the send path and the delivery path report no error attributable to the store.
2. **Given** a backlog accumulated while the store was down, **When** the store returns,
   **Then** every record in the backlog is written and the count matches what was published.
3. **Given** the store is unreachable, **When** the ingester tries to write, **Then** it
   does not acknowledge the records it failed to write.
4. **Given** an outage longer than any redelivery limit would allow, **When** the store
   returns, **Then** every record is still delivered — and the consumer's own pending count
   and the queue's depth are reported together, because **a consumer that has given up
   reports nothing outstanding while the queue is still full.**

### User Story 3 - A redelivered record does not become a second row (Priority: P3)

The queue delivers at least once. The analytical store has no uniqueness constraint and no
upsert. A redelivery after a partial failure must not inflate what the dashboard shows.

**Why this priority**: it is the defect that would be invisible until a customer disputes a
bill, and it is the one this chapter is uniquely placed to prevent.

**Independent test**: force a redelivery of a batch already written, then compare the row
count and the per-key counts against the number of distinct records published.

**Acceptance scenarios**

1. **Given** a batch already written to the store, **When** the same records are delivered
   again, **Then** the store's count for those keys is unchanged.
2. **Given** a partially written batch, **When** the ingester restarts, **Then** no record
   is lost and none is counted twice.

### Edge Cases

- A record whose payload does not parse — it must not stall the stream behind it, and it
  must not be silently dropped without a count. Under FR-006a it would otherwise retry
  forever.
- An outage long enough that records are stranded **and** then age out of the queue. That is
  the only path to genuine loss, and it needs both bounds to line up.
- A record naming an environment that no longer exists. The analytical store carries no
  foreign keys; the row is written and the orphan is a reporting question.
- The stream reaching `max_bytes` with `discard: old` while the ingester is down: the
  oldest records are dropped by the broker, and the chapter must say what that means rather
  than discovering it in a dashboard.
- Two ingesters running at once — whether that is supported, refused, or merely survivable.
- A batch larger than the store will accept in one insert.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A service MUST consume the `ANALYTICS` stream and write its records to the
  analytical store. It MUST be the only consumer of that stream.
- **FR-002**: Records MUST be written in batches, bounded by both an elapsed interval and a
  row count (DR-11 publishes 2 s or 10,000 rows), and the chapter MUST publish what those
  bounds cost and why they are two bounds rather than one.
- **FR-003**: The ingester MUST NOT acknowledge a record it has not written.
- **FR-004**: A redelivered record MUST NOT produce a second row, and the mechanism MUST be
  stated rather than left to chance (US3).
- **FR-005**: The analytical store being unreachable MUST NOT affect the send path, the
  delivery path, or any request (NFR-REL-05, FR-ANL-02).
- **FR-006**: Records MUST accumulate in the queue while the store is unreachable and drain
  on recovery, with the count reconciled against what was published.
- **FR-006a**: The consumer MUST NOT impose a redelivery limit shorter than the queue's own
  retention. A finite limit makes FR-006 false: once it is exhausted the consumer is never
  offered the record again, and **it reports nothing outstanding while the record is still in
  the queue.** The only bound on how long a record may wait is the queue's retention.
- **FR-006b**: A record that can never be written MUST be terminated at the point the defect
  is detectable rather than retried against the limit in FR-006a. Unlimited redelivery and
  poison handling are one rule with two arms: **retry forever on transport or store failure,
  terminate immediately on a payload that will fail the same way every time.**
- **FR-007**: The target table MUST be added through the ledger chapter 4.2 built — a new
  statement file, applied and recorded by `analytics/apply.mjs`, never by hand.
- **FR-007a**: The write MUST refuse a record it cannot map, rather than accepting it with a
  default. A column left at its default by a mismatched or missing field is indistinguishable
  from a real value, and for the timestamp it is worse than indistinguishable: an epoch
  timestamp is **older than the retention**, so the row is deleted at insert and the loss is
  reported as success.
- **FR-008**: The target table's shape MUST be derived from the record the publisher
  already sends, and the architecture document MUST be amended to publish it. SAD §6.2
  publishes `message_events` as *representative* and names `emoji_events`; no table for
  delivery attempts is published anywhere.
- **FR-009**: The ingester MUST NOT write to PostgreSQL, and MUST NOT read it on the
  ingestion path (constitution III).
- **FR-010**: A malformed record MUST be counted and set aside rather than retried forever
  or dropped silently.
- **FR-011**: The chapter MUST state what `discard: old` at `max_bytes` means for the
  records that are dropped, and whether seven days is the right retention now that
  something consumes the stream.
- **FR-012**: The chapter MUST NOT build the reconciliation job (FR-ANL-06), the query
  surface (FR-ANL-07), or latency percentiles (FR-ANL-10). It MUST NOT add a producer for
  `delivery_latency_ms`.
- **FR-012a**: The ingester's decision-bearing code MUST carry automated tests, and the
  measured branch coverage of the deduplication and tenant-carrying paths MUST be recorded
  against constitution VI's 100% clause rather than left unstated. **Where it falls short the
  gap is pinned at the measurement and named**, which is this project's established handling
  of that clause — `vitest.coverage.config.mts` records `repository.ts` at 89.51% and says
  why a threshold nothing can pass is worse than an honest one.
- **FR-013**: Every gate MUST be green at close-out, with `check:fences` reported as a
  **delta** broken down by kind and locale, against an opening measured in this feature.
- **FR-014**: The chapter MUST record whether the existing consumer runtime
  (`services/api/src/consumer/runtime.ts`, which already takes a `filterSubject`) is reused
  or replaced, and why. Reusing it is cheaper; its acknowledgement shape may not suit a
  batching consumer, and that is the argument either way.

### Key Entities

- **Attempt record** — what `publishAttempt` sends today: a delivery id, an attempt number,
  an environment, an outcome. Its broker deduplication key is `{deliveryId}:{attempt}`,
  chosen in the webhook dispatcher chapter after the delivery id alone collapsed seven
  retries into one message.
- **The ingester** — a consumer of `analytics.>` and a writer to the analytical store.
  Nothing else.
- **The attempt table** — a new analytical table, added through 4.2's ledger, shaped by the
  record above rather than by a document that does not publish it.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every record published to the stream during the chapter's measurement appears
  exactly once in the analytical store, and the two counts are published side by side.
- **SC-002**: With the analytical store stopped, messaging and webhook delivery continue
  with no error attributable to the store, and the queue's depth is published before and
  after recovery.
- **SC-003**: A forced redelivery leaves the store's counts unchanged, published as a
  before-and-after pair rather than asserted.
- **SC-004**: The batch bounds are measured, not quoted: the chapter publishes what the
  interval and the row count each cost at a stated publish rate.
- **SC-005**: The ingester writes no row to PostgreSQL and issues no query against it on
  the ingestion path, verified rather than asserted.
- **SC-005a**: The deduplication path has automated tests, and its measured branch coverage
  is published beside constitution VI's 100% requirement — met, or pinned with the shortfall
  stated as a number.
- **SC-006**: The new table is applied by `analytics/apply.mjs`, and a second run reports
  that it applied nothing.
- **SC-007**: `check:fences` is reported as a delta against an opening measured in this
  feature, broken down by kind and locale.
- **SC-008**: The chapter's prose stays inside the 2,000–4,000 word bound measured outside
  code fences — **and the bound is expected to decide a split rather than be met quietly.**
  The only precedent for introducing a service is chapter 3.19, which brought
  `services/dispatcher` in at **5,889 prose words and 47 titled fences** against 4.2's 2,580
  and 2. The ingester is a smaller job than the dispatcher was, and the figure to beat is on
  record rather than assumed.

---

## Assumptions

- **The ingester is a new service.** `services/` holds `api`, `dispatcher` and `gateway`.
  A fourth is the shape the SAD describes; whether it is a service or a mode of an existing
  one is a planning decision, recorded either way.
- **`delivery_latency_ms` stays without a producer.** It belongs to whoever measures
  delivery, not to the consumer that writes what it is given. 047-2 stays open.
- **The 31 messages currently in the stream are lane debris**, not production data. They are
  the evidence that nothing drains it, not a corpus — the chapter publishes its own.
- **Seven-day retention is inherited, not chosen here.** Chapter 3.20 set it while nothing
  consumed the stream. FR-011 asks whether it still holds; it does not presume an answer.
- **Constitution VII applies.** A fourth service in TypeScript needs no argument; anything
  else would.

## Dependencies

- Chapter 4.2's `analytics/apply.mjs` and the `relay_analytics` database (`part4-ch2`).
- The `ANALYTICS` stream and `publishAttempt`, both shipped in chapter 3.20.
- NATS JetStream, already in `compose.yaml` and healthy.

## Out of scope

The reconciliation job, the customer-facing query surface, latency percentiles, a producer
for `delivery_latency_ms`, connection open/close events (movement III, chapter 5), and API
request events (movement III, chapter 4).
