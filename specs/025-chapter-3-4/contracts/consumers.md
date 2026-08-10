# Phase 1 — Contracts: Chapter 3.4

Chapter 3.3 made the platform's first promise about what it *emits*. This chapter
adds the other half: what a consumer may assume, and what it must do to be
correct. No public route changes and no existing response changes.

---

## The stream

| Stream | Subjects | Storage | Retention | Owner |
|---|---|---|---|---|
| `EVENTS` | `events.>` | file | limits | created by 3.3, **configured here** |

Every setting is now deliberate (research R2). Two of them — `retention` and
`storage` — are immutable on an existing stream and are carried through rather
than resubmitted (research R1).

| Setting | Value | Source |
|---|---|---|
| `max_age` | 7 days | NFR-REL-08 floor is 24 h; a week covers a weekend |
| `max_bytes` | 1 GiB | an unbounded stream fills the database's disk |
| `discard` | `old` | at the bound, drop the oldest — never refuse a publish |
| `duplicate_window` | 120 s, inherited | deliberately not the guarantee (research R3) |
| `num_replicas` | environment-derived | ADR-02 specifies R3; compose is one node |

**Applying the configuration is idempotent.** Two api instances start together
and both apply it. The second is a no-op, not an error.

---

## The subject grammar

```
events.{domain}.{action}.{environment_id}
```

ADR-02's, verbatim. It lives in `@relay/protocol` — the package whose whole job
is the shapes both sides share (chapter 1.3) — and is built there and nowhere
else.

**Why that is a contract rather than a tidiness preference**: a consumer that
assembles its own subject filter receives nothing the day the grammar changes.
No error, no warning, just an empty stream position. The failure mode of a
duplicated grammar is silence, which is why the grammar has exactly one home.

The wildcard every consumer subscribes to is `events.>`, and every subject the
builder produces is matched by it — asserted, not assumed.

---

## The durable consumer

A durable name is a **position in the stream**, not a process. Every instance
using that name shares the one position.

| Property | Value | Meaning |
|---|---|---|
| durable | `recorder` | the shared position |
| delivery | pull, bounded batches | the consumer asks when it is ready (research R6) |
| ack policy | explicit | nothing is acknowledged the runtime did not decide to acknowledge |
| `max_deliver` | 5 | bounded — forever is not a retry policy |
| `ack_wait` | 30 s | long enough for a real handler, short enough that a killed instance's work returns |
| `max_ack_pending` | 100 | back-pressure against a stalled consumer |

**Created if absent, left alone if present.** Two api processes started together
divide the stream between them; neither creates a second position by accident.

---

## Delivery semantics, from the receiving end

| Property | Value | Where it comes from |
|---|---|---|
| Delivery | at-least-once | the outbox republishes; the broker redelivers unacknowledged work |
| Duplicates | **expected**, absorbed at the consumer | the ledger, in the effect's transaction |
| Ordering | **not guaranteed** | 3.3's `SKIP LOCKED` relay, unchanged (research R8 of 3.3) |
| Exhaustion | after `max_deliver`, the message leaves the consumer's view | **nothing catches it** (research R4) |
| Broker outage | the api starts and serves writes regardless | lazy connection (3.3's research R9) |

**What a consumer must do**: nothing. That is the point. The runtime claims the
event in the same transaction as the effect, so a handler cannot forget to
deduplicate — it has no way to. SAD risk R5 asks for a template with dedup built
in; built in means a handler is given nothing to forget.

**What orders what**: `data.seq` orders messages within a channel (FR-MSG-03,
ADR-03). Event arrival order is not that guarantee and must not be used as one.

---

## The handler contract

```ts
type EventHandler = (event: OutboxEvent, context: EventContext) => Promise<void>;
```

**Returns → handled. Throws → not handled, try again.** That is the entire
vocabulary.

A handler **cannot** acknowledge, negatively acknowledge, retry, deduplicate, or
see the raw message. This is not an oversight in the interface; it is the
interface. Every capability withheld is a way SAD risk R5 could otherwise
materialise.

`context.attempt` is the broker's delivery count. A handler may **log** it. It
must not use it to decide correctness — a handler that behaves differently on
attempt three is a handler whose behaviour depends on a timeout somewhere else.

**The limit of the pattern**: the effect and the claim share a transaction only
because the effect is in Postgres. Chapter 3.5's dispatcher calls a customer's
endpoint and cannot roll that back. Stated here, in the chapter that establishes
the pattern, rather than discovered there.

---

## The consumer's operational surface

Not an API — what an operator can see.

| Signal | Meaning |
|---|---|
| consumer `pending` | how far behind this position is |
| consumer `ack_pending` | work handed out and not yet acknowledged |
| consumer `redelivered` | how often work has come back — the gap, made visible |
| consumer log lines | one per handled event, carrying identifiers and counts — never a payload |

**Explicitly not built here**: alerting, metrics export, a dashboard panel,
ledger pruning, a dead-letter store. Named with owners, so the chapter does not
imply an operational story it has not written.

---

## Invariants the tests must hold

Twelve. Ten need a real broker and a real database; two are pure and live in the
Docker-free lane.

| # | Invariant | Requirement | Lane |
|---|---|---|---|
| 1 | The stream's settings read back exactly as configured | spec FR-009, SC-002 | integration |
| 2 | Applying the configuration twice is a no-op, not an error | spec FR-009, SC-010 | integration |
| 3 | An event is delivered, handled once, and acknowledged | spec FR-013 | integration |
| 4 | A kill between handling and acknowledgement is redelivered — and handled once | spec FR-019, **SC-003** | integration |
| 5 | Deduplication survives a restart | spec FR-013, SC-004 | integration |
| 6 | Two instances sharing a durable name divide the work | spec FR-012, SC-005 | integration |
| 7 | A handler that always throws stops being retried | spec FR-017, SC-006 | integration |
| 8 | An unparseable payload is terminated on the first attempt | spec FR-016, SC-007 | integration |
| 9 | A consumer stopped for N publishes receives all N on restart | spec FR-018, SC-008 | integration |
| 10 | A handler that throws is retried, never acknowledged | spec FR-014 | **unit** |
| 11 | A duplicate claim is acknowledged, not handled again | spec FR-013, SAD risk R5 | **unit** |
| 12 | A consumer log line carries counts, never payloads | spec FR-021, NFR-SEC-06 | integration |

**On 10 and 11.** These are pure because `decideOutcome` takes its claim as an
argument and therefore has no database of its own to reason about. What the
integration lane proves is that the runtime wires the decision to NATS and
Postgres correctly; what the unit lane proves is that the decision it wires up is
the right one. They are the two the chapter's argument rests on: throw →
redelivery, duplicate → acknowledge without re-handling.

**Sabotage check**: removing the ledger claim from the runtime — leaving
everything else exactly as it is — must fail invariants 3, 4 and 6. A suite that
passes with the mechanism removed is a suite that holds nothing.
