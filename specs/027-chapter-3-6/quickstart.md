# Quickstart — validating chapter 3.6

Prerequisites: the `part3-ch5` state and Docker. No new infrastructure — this
chapter adds columns and a stream, not a service.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  docker compose up -d --wait postgres redis nats
pnpm build
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" node services/api/dist/db/migrate.js
```

**The environment variables that cost an hour if you get them wrong.** Two Redis
knobs, not interchangeable: `RELAY_REDIS_URL` is read by production code,
`RELAY_REDIS_PORT` by the integration tests, which build their own URL. The e2e
harness spawns real gateways, so it needs the first. Chapters 3.4 and 3.5 both
recorded this; it is still true.

This chapter also needs `RELAY_INTERNAL_CREDENTIAL` and
`RELAY_WEBHOOK_SECRET_KEY`, both as 3.5 established.

---

## V1 — Nothing regressed

```bash
pnpm lint && pnpm typecheck && pnpm test
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" \
  RELAY_NATS_URL="nats://localhost:14222" pnpm test:integration
```

Expected: every 3.5 suite passes with assertions unchanged in substance. Read exit
codes, not output — chapter 3.2 shipped two failures past a grep over a build log.

## V2 — The attempt event reaches the stream

```bash
node scripts/stream-info.mjs ANALYTICS
```

Expected: the stream exists with `analytics.>`, a seven-day `max_age` and
`discard: old`, and its message count rises as deliveries are attempted.

**That is all this command can tell you, and the distinction matters.**
`stream-info.mjs` prints a stream's configuration and its counters — it never
prints a message body. The payload properties (identifiers, status, latency and
outcome present; no event payload, secret or signature anywhere) are proven by
`services/api/src/webhooks/attempts.itest.ts`, which consumes the stream and
reads the events. A step that claimed to show the payload while running a command
that cannot would be the kind of validation that passes without checking
anything.

## V3 — A backlogged analytics path does not stop a delivery

Stop the broker, or delete the `ANALYTICS` stream, and deliver a webhook.

Expected: the delivery succeeds and the outcome is recorded. One log line reports
the failed publish. **This is the constitution III property**: if a delivery fails
because analytics is unwell, the design is wrong, not the test.

## V4 — An endpoint that fails for an hour is switched off

```bash
node scripts/hostile-endpoint.mjs --mode=fail --secret=hunter2
node scripts/webhook-walk.mjs --secret=hunter2 --fast-forward --watch-disable
```

Expected: the failure run opens on the first failure, grows with each attempt,
and the endpoint is disabled once the run passes an hour with at least 5 attempts.
Exactly one notification row, `delivered_at` null.

`--fast-forward` moves the clock, not the logic. Without it this takes an hour and
five minutes of real time, which is the honest cost of the requirement and the
reason the flag exists.

## V5 — An endpoint that recovers is never switched off

```bash
node scripts/hostile-endpoint.mjs --mode=flaky --secret=hunter2
node scripts/webhook-walk.mjs --secret=hunter2 --fast-forward
```

Expected: the run opens, then clears on the first success, and the endpoint stays
enabled however long the test runs. A platform that switches off endpoints which
sometimes work is worse than one that keeps trying.

## V6 — The quiet endpoint, which is the one research R1 is about

Disable the sweep (`RELAY_DISABLE_SWEEP=off`), drive a single delivery to
dead-letter against `--mode=fail`, then stop sending events.

Expected **with the sweep off**: the endpoint is still enabled, hours later, with
a failure run well past the threshold. That is the bug.

Expected **with the sweep on** (the default): the endpoint is disabled within one
sweep interval of the hour elapsing, with no further events arriving.

Run both halves. The first is what an outcome-only check ships, and reading it is
the only way the second means anything.

## V7 — Proving it works again

```bash
node scripts/hostile-endpoint.mjs --mode=ok --secret=hunter2
curl -X POST .../v1/webhook-endpoints/{id}/test
```

Expected: a signed synthetic event arrives at the endpoint, marked `webhook.test`
and `"test": true`, and the response reports the status and latency. The endpoint
is still disabled — testing does not re-enable — and the failure run is unchanged
by the test's outcome. Then re-enable and confirm all four columns are null.

## V8 — The sabotage check

Five mutations, each reverted afterwards and the file verified byte-identical:

| Mutation | Must fail |
|---|---|
| clear the failure run on failure instead of on success | invariants 6 and 7 |
| drop the `enabled = true` predicate from the disable update | invariant 8 — a second disable and a second notification |
| let a test event's outcome update the failure run | invariant 13 |
| publish the attempt event inside the outcome transaction | invariant 5 — a stalled stream now blocks a delivery |
| remove the sweep, keeping the on-outcome check | invariant 12, via V6's quiet endpoint |

A suite that still passes with a mechanism removed is a suite that holds nothing.

The fourth is the one worth watching. It will keep passing under a healthy broker,
which is exactly why V3 exists — the sabotage must be run against a broker that is
down, or it proves nothing.

## V9 — Coverage, and the ratchet that has half a point of headroom

```bash
pnpm coverage
```

`repository.ts` sits at 89.51 branches against a ratchet of 89. This chapter adds
five operations to that file. Check this as each operation lands, not at the end —
chapter 3.5 deferred it and found four thresholds red with the chapter otherwise
finished, because the new code was reached only from a child process whose
coverage is not attributable.

## V10 — The site

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:fences
```

Expected: exit 0 throughout, the fence chain replays, and
`/part-3/chapter-06/when-to-stop-trying` plus its Vietnamese twin return 200 with
figures rendered as SVG in a headless browser. A page that returns 200 is not a
page that is laid out — chapter 3.5 shipped three blank diagrams past a passing
build because the `Figure` prop was wrong.
