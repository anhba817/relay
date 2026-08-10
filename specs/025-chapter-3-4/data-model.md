# Phase 1 — Data Model: Chapter 3.4

One new table, one new transaction, and one durable shape that lives in the
broker rather than the database. Unlike 3.3's outbox — which SAD §6.1 defines
outright — the table here is **derived**, and carries a DECISION for it.

---

## `consumed_events` (new — derived)

```sql
CREATE TABLE consumed_events (
    consumer    TEXT        NOT NULL,
    event_id    UUID        NOT NULL,
    handled_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer, event_id)
);
```

No source document defines this table. SAD risk R5 requires the *behaviour* — "a
future consumer forgets to dedupe → double webhooks / double metering", mitigated
by "a consumer template with dedup built in" — and leaves the shape open. This is
a chapter derivation, recorded in `schema.ts` the way 2.1 recorded `members`, 3.2
recorded `api_keys` and 3.3 recorded the outbox's partial index.

Four things are worth saying about it.

**The primary key IS the deduplication.** Composite, `(consumer, event_id)`, and
the `INSERT … ON CONFLICT DO NOTHING … RETURNING` is the check. Not a
SELECT-then-INSERT: two instances fetching the same message concurrently would
both decide they were first. Chapter 2.3 learned this on idempotency keys and 3.1
learned it again on signup; this is the third time the same shape is the answer.

**Keyed per consumer, not globally.** Chapter 3.5's dispatcher and Part 4's
ingester must each receive every event. One ledger shared between them would let
whichever arrived first silence the other — a bug that looks exactly like a
consumer that is working.

**No `environment_id`.** For the reason the outbox has none: this is the
platform's own bookkeeping, not tenant data. One consumer reads every
environment's events, so the repository's scoping rule does not apply. That is
the second deliberate exception in Part 3, and like the first it is recorded here
rather than left for a reviewer to notice (constitution I).

**No event body.** Recording that an event was handled needs none of a tenant's
message text (NFR-SEC-06). The events themselves live in the broker; this table
holds only the fact of handling.

**No foreign key to anything**, for the same reason — there is no events table to
reference.

**Rules**

- **A row is written only by the runtime's claim**, never by a handler. A handler
  has no way to write one, which is what makes forgetting impossible.
- **Rows are never deleted by this chapter.** They stop earning their keep once an
  event is older than the stream's 7-day retention — a message that can no longer
  be redelivered can no longer be a duplicate — but pruning needs a scheduler the
  platform does not have.

---

## The claim transaction (new)

```text
BEGIN
  INSERT INTO consumed_events (consumer, event_id)
    ON CONFLICT DO NOTHING
    RETURNING event_id
  ── if no row came back: somebody already handled this. Return "duplicate".
  ── if a row came back:
  run the handler's effect                            (3.4)
COMMIT
```

**Rule**: the ledger row and the effect share a fate. This is chapter 3.3's
outbox shape pointed the other way — there, the event and the state change
committed together; here, the record of handling and the handling itself do.

**Why the claim is inside the transaction and not before it**: a handler that
throws rolls the claim back with it, so the redelivery finds no claim and runs
again. Claiming outside would leave a claim behind when the handler failed, and
the redelivery would be waved through as a duplicate — **an event silently never
handled, which is worse than one handled twice.**

**The limit, stated because 3.5 will meet it**: the effect must be transactional
for the fate to be shared, which means it must be in Postgres. A handler whose
effect is an HTTP call to a customer cannot be rolled back, and no ledger makes
it so. Chapter 3.5 must choose which way to be wrong; this chapter establishes
the pattern and names where it stops.

---

## The `EVENTS` stream (configuration, not storage)

Not a table, but a durable shape this chapter is responsible for. Two of its
settings can never be changed once the stream exists (research R1).

| Setting | Value | Mutable? |
|---|---|---|
| `subjects` | `events.>` | yes |
| `retention` | limits | **no — fixed at creation** |
| `storage` | file | **no — fixed at creation** |
| `max_age` | 7 days | yes |
| `max_bytes` | 1 GiB | yes |
| `discard` | old | yes |
| `duplicate_window` | 120 s (inherited, deliberately) | yes |
| `num_replicas` | environment-derived | yes |

**Rule**: applying this configuration is idempotent. Two api instances start
together and both apply it; the second must be a no-op rather than an error. On
an existing stream the mutable settings are merged and the immutable ones carried
through untouched, because the broker refuses a change to those rather than
reconciling it.

---

## The durable consumer (position, not process)

| Property | Value | Rule |
|---|---|---|
| durable name | `recorder` | a position in the stream, shared by every instance using it |
| filter | `events.>` | built from the shared grammar, never assembled locally |
| ack policy | explicit | the acknowledgement is the whole subject of the chapter |
| `max_deliver` | 5 | bounded; what falls out is caught by nothing (research R4) |
| `ack_wait` | 30 s | long enough for a real handler, short enough that a killed instance's work returns promptly |
| `max_ack_pending` | 100 | back-pressure: a stalled consumer cannot accumulate unbounded work |

**Rule**: the durable is created if absent and left alone if present. Two
instances sharing it divide the stream rather than each receiving everything.

---

## What the model deliberately does not have

- **No dead-letter table.** A message that exhausts `max_deliver` leaves the
  consumer's view and nothing catches it. FR-WHK-04's store belongs to chapter
  3.5, and this chapter states the gap rather than implying a path.
- **No attempts or last-error column.** The broker counts deliveries; duplicating
  that count in Postgres would create a second truth about the same fact.
- **No consumer offsets in Postgres.** The durable name is the position and the
  broker owns it. A cursor stored in both places is a cursor that disagrees with
  itself after a crash.
- **No ledger pruning.** Named and deferred, with the retention window as the
  natural bound.
- **No event types beyond `message.created`.** The consumer filters on the
  wildcard, so FR-WHK-02's remaining seven need no consumer change when their
  producers arrive.
