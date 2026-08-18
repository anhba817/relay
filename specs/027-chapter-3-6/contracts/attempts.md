# Contract — the attempt event

What the api publishes after every webhook delivery attempt, and what Part 4's
ingester will consume.

**Two words, one thing.** The *attempt record* is the fact — what happened on one
try. The *attempt event* is the message that carries it onto the stream. The
record is what a reader eventually wants; the event is how it travels. Where this
document says event it means the wire message, and nowhere else.

## Subject

```text
analytics.{domain}.{action}.{environment_id}
analytics.webhook.attempt.9f3c1e7a-...
```

Extends chapter 3.4's `events.{domain}.{action}.{env}` rather than inventing a
second convention. The grammar lives in `@relay/protocol`; both the publisher and
any future consumer import it, so the two cannot drift.

## Stream

| Setting | Value | Why |
|---|---|---|
| name | `ANALYTICS` | Separate from `EVENTS` (tenant domain events) and `DELIVERIES` (work) |
| subjects | `analytics.>` | One stream for every analytical event; Part 4 adds more actions |
| retention | `limits` | Nothing acknowledges these in this chapter |
| max_age | 7 days | Long enough for an ingester to be down for a long weekend; short enough that the stream is not a database |
| discard | `old` | At the bound, the oldest analytics is the least interesting |
| storage | file | As `EVENTS` |

The api ensures this stream the same way it ensures the others. The dispatcher
does not know it exists.

## Payload

```json
{
  "delivery_id": "…",
  "endpoint_id": "…",
  "environment_id": "…",
  "event_id": "…",
  "attempt": 3,
  "attempted_at": "2026-08-18T09:14:22.481Z",
  "status": 503,
  "latency_ms": 214,
  "error": null,
  "outcome": "rescheduled"
}
```

| Field | Notes |
|---|---|
| `status` | Absent when nothing answered. A timeout has no status, and inventing one (0, 599) would make a dashboard lie. |
| `error` | Present only when there was no status. Truncated to 2000 characters by the seam's existing schema. |
| `latency_ms` | Already carried by chapter 3.5's outcome contract and discarded until now (research R6). For a timeout this is the timeout, not a measurement of the customer's server. |
| `outcome` | What the api decided: `delivered`, `rescheduled`, `dead_lettered`. The one field the dispatcher could not have supplied. |
| `attempted_at` | RFC 3339, UTC, millisecond precision |

**Never present**: the event payload, the signing secret, the signature, any
header. Sizes, identifiers, statuses and durations only (FR-004, NFR-SEC-06).

**`skipped` is not one of them, and the first draft of this table said it was.**
The dispatcher has a fourth outcome — `deliver.ts` returns `skipped` when the
endpoint has been disabled or deleted since the delivery was scheduled — but it
reports that one to nobody. No outcome is recorded, so no attempt event is
published, and that is right rather than a gap: a skip means no request was made,
and an attempt record for an attempt that never happened would put a row in a
customer's dashboard describing a request their server never received. Invariant 9
is the same fact seen from the other side.

Corrected here rather than quietly, because `outcome` is the one field a consumer
cannot derive from anything else, and a consumer that switched on four values
would have written dead code waiting for a fifth.

## Delivery guarantee

**At-most-once, deliberately.** Published after the outcome transaction commits,
outside it. If the publish fails or the process dies in the gap, the record is
lost and the delivery is unaffected.

This is the trade constitution III asks for in as many words: a backlogged
analytical pipeline must not affect webhook dispatch. The cost is a gap in a
dashboard; the alternative cost is a customer's webhooks stopping because a
metering pipeline is unwell.

## Not queryable in this chapter

**Nothing reads this stream yet.** The api publishes; no consumer exists, no
ClickHouse table exists, and there is no endpoint a customer can call to ask what
happened to their event. Attempts are emitted and retained for seven days, and
that is the whole of it.

**Part 4's analytics ingester is what finishes FR-WHK-06.** It consumes
`analytics.>`, batch-inserts to ClickHouse, and gives the records the query
surface and the 30-day retention the requirement asks for. Until then, an operator
who needs an attempt history reads it off the stream directly.

This is stated here, and not only in the chapter, because a contract that
described the payload without saying nobody can read it would be describing a
feature that does not exist yet (FR-005).

Consumers must therefore treat attempt counts as approximate. `webhook_deliveries.
attempt` remains the operational truth for "how many times has this been tried".

## Invariants

| # | Invariant |
|---|---|
| 1 | Every recorded outcome publishes exactly one attempt event, or none if the publish fails. Never two. A REPEATED report — the idempotent replay, where the delivery has already moved past that attempt — records nothing and so publishes nothing. |
| 2 | The subject's environment matches the payload's `environment_id`. |
| 3 | No payload, secret, signature or header appears in any field. |
| 4 | A publish failure is logged and swallowed: the outcome response to the dispatcher is unchanged. |
| 5 | A stalled or absent `ANALYTICS` stream does not slow or fail an outcome report. |

**On invariant 1's second sentence.** `recordAttemptOutcome` is idempotent on
`(delivery_id, attempt)`: a report for an attempt the delivery has already moved
past returns the decision made the first time and changes no row. The dispatcher
posts, reports, then acknowledges, so a crash in the last gap makes that second
report ordinary rather than exceptional. Publishing on the replay would put two
attempt events on the stream for one attempt, and since nothing on the analytical
path deduplicates, a dashboard would report a retry that never happened. The
publish is therefore conditional on the outcome having been RECORDED, not on the
call having returned.
