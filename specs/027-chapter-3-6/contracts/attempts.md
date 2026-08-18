# Contract — the attempt event

What the api publishes after every webhook delivery attempt, and what Part 4's
ingester will consume.

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
| `outcome` | What the api decided: `delivered`, `rescheduled`, `dead_lettered`, `skipped`. The one field the dispatcher could not have supplied. |
| `attempted_at` | RFC 3339, UTC, millisecond precision |

**Never present**: the event payload, the signing secret, the signature, any
header. Sizes, identifiers, statuses and durations only (FR-004, NFR-SEC-06).

## Delivery guarantee

**At-most-once, deliberately.** Published after the outcome transaction commits,
outside it. If the publish fails or the process dies in the gap, the record is
lost and the delivery is unaffected.

This is the trade constitution III asks for in as many words: a backlogged
analytical pipeline must not affect webhook dispatch. The cost is a gap in a
dashboard; the alternative cost is a customer's webhooks stopping because a
metering pipeline is unwell.

Consumers must therefore treat attempt counts as approximate. `webhook_deliveries.
attempt` remains the operational truth for "how many times has this been tried".

## Invariants

| # | Invariant |
|---|---|
| 1 | Every recorded outcome publishes exactly one attempt event, or none if the publish fails. Never two. |
| 2 | The subject's environment matches the payload's `environment_id`. |
| 3 | No payload, secret, signature or header appears in any field. |
| 4 | A publish failure is logged and swallowed: the outcome response to the dispatcher is unchanged. |
| 5 | A stalled or absent `ANALYTICS` stream does not slow or fail an outcome report. |
