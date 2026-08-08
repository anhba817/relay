# Phase 1 — Contracts: Chapter 3.3

This chapter adds no public route and changes no existing response. What it adds
is a contract in the other direction: the platform's first promise about what it
*emits*.

---

## The subject

```
events.msg.created.{environment_id}
```

The shape SAD §6.1's own comment specifies. One stream covers it:

| Stream | Subjects | Storage | Owner |
|---|---|---|---|
| `EVENTS` | `events.>` | file | created by this chapter if absent; **configured properly by 3.4** |

This chapter creates the minimum a publisher needs in order to be provable. Every
real decision about the subject space — the full FR-WHK-02 type list,
per-environment sharding, retention, replicas — belongs to chapter 3.4, and the
chapter says so rather than pretending the design is settled.

---

## The event envelope

```json
{
  "id": "8f14e45f-ceea-4f6a-9b2c-1d2e3f4a5b6c",
  "type": "message.created",
  "environment_id": "3f2a…",
  "occurred_at": "2026-08-08T13:31:09.229Z",
  "data": {
    "id": "57d5cdf0-e145-4bca-b7fa-a7a43e8ffbb6",
    "channel_id": "ce419dc5-b06e-441c-ab38-49451f87210e",
    "seq": 1,
    "user": "tuan",
    "text": "B2, north ramp",
    "created_at": "2026-08-08T13:31:09.229Z"
  }
}
```

`id` is also sent as the broker's deduplication id, so a republished event is
recognisable as the same event by identity rather than by comparing payloads.

**Compatibility promise, such as it is**: nothing consumes this yet. The envelope
is shaped for FR-WHK-02's remaining seven types — same five top-level fields,
different `type` and `data` — so adding a type is additive rather than a
redesign. That is a design intent, not a stability guarantee, and the chapter
should not pretend otherwise before a single consumer exists.

---

## Delivery semantics

| Property | Value | Where it comes from |
|---|---|---|
| Loss | none once the write commits | the row commits with the message (ADR-06) |
| Duplicates | possible, on relay restart between publish and mark | at-least-once, embraced (ADR-06) |
| Ordering | **not guaranteed** across events | `SKIP LOCKED` + concurrent relays (research R8) |
| Latency | seconds under normal conditions | poll interval; FR-ANL-04 allows 60 s |
| Broker outage | writes unaffected; events accumulate and drain on recovery | SAD §7's own claim, tested here |

**What a consumer must do**: deduplicate on `id`. A consumer that does not is
incorrect, and no amount of care in this relay makes it correct — which is why
ADR-06 calls consumer idempotency a system-wide discipline rather than a
per-consumer choice.

**What orders what**: `data.seq` orders messages within a channel, and it is
already the platform's ordering guarantee (FR-MSG-03, ADR-03). Event arrival
order is not that guarantee and must not be used as one.

---

## The relay's operational surface

Not an API — the things an operator can see, which the chapter must show rather
than assert.

| Signal | Meaning |
|---|---|
| outbox depth (`published_at IS NULL`) | how far behind the relay is; the single number worth alarming on later |
| oldest unpublished `created_at` | age of the backlog, which matters more than count when the broker is down |
| relay log lines | one per batch, carrying count and duration — never a payload, never a credential |

**Explicitly not built here**: alerting, metrics export, a dashboard panel,
pruning. Named, with owners, so the chapter does not imply an operational story
it has not written.

---

## Internal seam: what starts and stops the relay

The relay runs inside the api service (ADR-06's decision) and must be:

- **startable and stoppable independently of request handling**, so that
  integration suites which want a quiet database simply do not start it;
- **safe to run more than once**, because the api is stateless and runs more than
  once — this is the ordinary deployment, not an edge case;
- **lazy about the broker**, so the api starts and serves writes when the broker
  is unreachable (research R9).

These three are the contract the implementation must satisfy; how they are
expressed in code is the implementation's business.

---

## Invariants the tests must hold

| # | Invariant | Requirement | Lane |
|---|---|---|---|
| 1 | A committed message has exactly one outbox row | spec FR-009 | integration |
| 2 | A rolled-back write leaves no outbox row | spec FR-010 | integration |
| 3 | A recognised idempotent retry adds no second row | FR-MSG-04, research R1 | integration |
| 4 | Both doors — REST and socket — produce one event each, identical in shape | spec FR-009 | integration |
| 5 | `SIGKILL` between commit and publish loses nothing: the row is present and unpublished | spec FR-015, SC-002 | integration |
| 6 | The same `SIGKILL` against publish-after-commit loses the event | SC-003 | integration |
| 7 | The relay publishes pending rows and marks them, and does not republish marked ones | spec FR-011 | integration |
| 8 | Two concurrent relays publish every row exactly once | SC-006 | integration |
| 9 | With the broker stopped, writes succeed and rows accumulate; on restart the backlog drains | SC-007 | integration |
| 10 | The envelope carries a stable `id` that survives a republish | spec FR-013 | unit + integration |
| 11 | No credential and no message text appears in a relay log line | spec FR-017 | integration |
| 12 | The publishing destination is replaceable without touching the code that writes events | spec FR-014 | unit |
