# Phase 1 — Data Model: Chapter 3.3

One new table, one amended transaction, and one shape that exists only on the
wire. For the first time in Part 3, the table is **quoted rather than derived**:
SAD §6.1 defines `outbox` outright.

---

## `outbox` (new — and documented)

```sql
CREATE TABLE outbox (
    id          BIGSERIAL PRIMARY KEY,
    subject     TEXT NOT NULL,             -- e.g. events.msg.created.{env}
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ                                -- ADR-06
);
```

Reproduced column-for-column from SAD §6.1. Three things are worth saying about
what it does *not* have.

**No `environment_id`.** Every other table below the tenant boundary carries one
(FR-TEN-06). This one carries the environment inside `payload` and inside
`subject`, because an outbox row is not tenant data — it is a record of work the
platform owes itself. The repository's scoping rule does not apply, and that is a
deliberate exception rather than an oversight, in the same family as the key
lookup 3.2 had to leave unscoped.

**No status enum.** `published_at IS NULL` is the queue. A row is pending or it
is done, and there is no third state to get stuck in. Anything richer — attempts,
last error, dead-letter — would be inventing the retry model chapter 3.5 owns.

**No `BIGSERIAL` in the payload.** The id orders the relay's work and never
leaves the database (research R7).

### The one addition, and its DECISION

| Addition | Purpose |
|---|---|
| a partial index on unpublished rows, oldest first | the relay's only query is "the oldest rows with `published_at IS NULL`", and without an index it degrades as the table grows — a full scan over a table that is 99.9% published rows |

SAD §6.1 defines no index. This is therefore a **chapter derivation** and carries
a DECISION note in `schema.ts`, the same way 2.1 recorded `members`, 3.1 recorded
the tenancy containers and 3.2 recorded `api_keys`. The partial predicate is the
point: the index covers only what the relay reads, so published rows cost nothing
to keep and pruning stays optional.

**Rules**

- **A row is written only by the transaction that caused it.** Nothing else
  inserts into this table, and the relay only ever updates `published_at`.
- **A recognised idempotent retry writes no row** (research R1). One message, one
  event, however many times a client retries.
- **Rows are never deleted by this chapter.** Pruning is named and deferred
  (ADR-06 calls it trivial; it needs a scheduler that does not exist).

---

## `messages` write transaction (amended)

The transaction 2.2 opened for the sequence lock gains one insert:

```text
BEGIN
  lock the channel row, read last_sequence          (2.2)
  insert the message                                 (2.2, 2.3's conflict clause)
  ── if and only if a row was actually inserted ──
  insert the outbox row                              (3.3)
  bump last_sequence                                 (2.2)
COMMIT
```

**Rule**: the event and the state change share a fate. There is no ordering
inside the transaction that changes that — a rollback anywhere takes both.

**The cost, stated**: the write path now depends on the outbox table being
writable. A broken outbox breaks message writes. That is the trade the chapter is
making and it should be made out loud: the alternative is a write path that
succeeds while silently owing an event nobody will ever produce, which is the
failure ADR-06 exists to remove.

---

## Event envelope (on the wire, never stored separately)

What `payload` holds, and therefore what a consumer eventually receives.

| Field | Required | Rule |
|---|---|---|
| `id` | yes | UUID, generated in the transaction. The consumer's deduplication key, stable across every redelivery (research R7) |
| `type` | yes | `message.created` — one of FR-WHK-02's names, spelled exactly as that requirement spells it |
| `environment_id` | yes | which tenant this happened in; also the last token of the subject |
| `occurred_at` | yes | when the state change committed, RFC 3339 UTC |
| `data` | yes | the message as the public API returns it: `id`, `channel_id`, `seq`, `user`, `text`, `created_at` |

**Rules**

- **The envelope is written once, complete, inside the transaction.** The relay
  adds nothing at publish time; it moves bytes. A relay that authored fields
  would be a second writer of event data, and ADR-04 has one writer.
- **`data` is the public shape, not the row.** Consumers are customers; they get
  external ids and the field names the REST API uses. `user_id` never crosses
  this boundary.
- **No credential and no internal identifier** appears anywhere in the envelope
  (FR-017, NFR-SEC-06).

---

## What the model deliberately does not have

- **No `attempts` or `last_error` column.** Retry accounting belongs to webhook
  delivery (FR-WHK-03/06, chapter 3.5). The relay retries by simply not marking a
  row published.
- **No dead-letter table.** Same owner, same chapter. This chapter must say what
  happens to a row the broker keeps rejecting — it is retried forever, and that
  is visible as outbox depth — rather than imply a path that does not exist.
- **No consumer offsets, no stream configuration.** Chapter 3.4.
- **No event types beyond `message.created`.** FR-WHK-02 names eight; the platform
  has one public state change that can produce one. Emitting events for state
  changes no route can make would be inventing product (Principle VII).
