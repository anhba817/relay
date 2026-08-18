# Contract — disable, re-enable, and the test event

Additions to chapter 3.5's public webhook surface. All routes are environment
scoped and authenticated as an application principal.

## Endpoint representation — new fields

```json
{
  "id": "…",
  "url": "https://…",
  "enabled": false,
  "disabled_at": "2026-08-18T09:14:22.481Z",
  "disabled_reason": "6 consecutive failures over 1h04m; last status 503",
  "failure_run_started_at": "2026-08-18T08:10:02.113Z",
  "failure_run_attempts": 6
}
```

`disabled_at` null with `enabled` false means the customer disabled it themselves.
Both set means the platform did (FR-009).

## `POST /v1/webhooks/{id}/enable` — amended

Already exists. Now also clears `failure_run_started_at`,
`failure_run_attempts`, `disabled_at` and `disabled_reason`, in one transaction
(FR-017). The hour is measured from the next failure, not the old run.

## `POST /v1/webhooks/{id}/test` — new

Sends a synthetic event to this endpoint and reports what it answered.

**Request**: no body.

**Response** `200`:

```json
{
  "delivered": true,
  "status": 200,
  "latency_ms": 143,
  "error": null,
  "event_id": "…"
}
```

`delivered` is true for any 2xx. A non-2xx or a timeout returns `200` with
`delivered: false` — the *test* succeeded in finding out, and an HTTP error here
would conflate "we could not run the test" with "the endpoint is unhealthy".

**Behaviour** (research R8):

| Rule | Reason |
|---|---|
| Delivered to this endpoint only, not fanned out by subscription | A test is aimed; fanning out surprises every other endpoint |
| Delivered even when the endpoint is disabled | Testing is how a customer establishes it is fixed before re-enabling |
| Outcome does not touch the failure run | A failed test must not push an endpoint toward disablement, and a successful one must not mask a real outage |
| One attempt, no retry schedule | A caller is waiting; a silent two-hour retry would report a stale answer |
| Signed exactly as a real event | A test signed differently proves nothing about real deliveries |

**The synthetic envelope**:

```json
{
  "id": "…",
  "type": "webhook.test",
  "environment_id": "…",
  "occurred_at": "…",
  "test": true,
  "data": { "message": "This is a test event from Relay." }
}
```

Marked twice — `type` and `test` — so a recipient switching on the type and a
recipient inspecting the body can each tell without knowing about the other
(FR-014).

**Errors**: `404` when the endpoint is not in this environment — the same answer a
foreign tenant gets, so a probe cannot distinguish "no such endpoint" from "not
yours".

## Auto-disable semantics

| # | Invariant |
|---|---|
| 6 | An endpoint whose failure run exceeds 1 hour **and** contains at least 5 attempts is disabled. |
| 7 | Any delivered outcome clears the run. An endpoint succeeding once an hour is never disabled. |
| 8 | Disablement happens at most once per run: no second disable, no second notification. |
| 9 | A disabled endpoint receives no new deliveries, and deliveries already scheduled for it are not attempted. |
| 10 | Disabling one endpoint changes nothing for any other endpoint, in any environment. |
| 11 | Disablement writes exactly one notification row, with `delivered_at` null. |
| 12 | The check fires from two places — on a recorded outcome, and from the relay's sweep — and both are idempotent against invariant 8. |
| 13 | A test event's outcome never opens, extends or clears a failure run. |

Invariant 12 exists because of research R1: an outcome-only check never fires for
a low-traffic endpoint, whose next attempt after 35m36s falls at 2h35m36s and may
never come at all.


---

## Corrections made while building this

**The route prefix.** This document said `/v1/webhook-endpoints/{id}/…` in two
places. Chapter 3.5's management surface is mounted at `/v1/webhooks`, and a
chapter that documented a path the platform does not serve would have been found
by the first reader to run `curl`.

**`deliveryMaterial` had to learn about test events.** Invariant 9 says a disabled
endpoint receives no attempts, and it was enforced where the dispatcher asks for
the material to make one. FR-013 says a test event reaches a disabled endpoint.
Those two meet in exactly one predicate, and the first run of
`test-event.itest.ts` failed there — the route created the delivery, and the
material request answered 404.

`synthetic` is the discriminator, which is what that column is for. A
soft-deleted endpoint is still refused: deleted means gone from the customer's own
API, and delivering to one would be the platform reaching a url the customer
believes it has forgotten.

**The timeout answer.** The contract describes what a test returns when the
endpoint answers or fails to. It did not say what happens when NOTHING makes the
attempt — no dispatcher running. The route waits ten seconds and then answers
`200` with `delivered: false` and an error naming the platform rather than the
customer. A 5xx would have been easier and would have told a customer their
endpoint was broken when the platform simply had not looked.
