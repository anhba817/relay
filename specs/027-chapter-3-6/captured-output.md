# Captured output — chapter 3.6

Every transcript the chapter quotes, from a real run. Nothing here is typed by
hand; where a line is elided it says so.

Environment: compose stores on 15432 / 16379 / 14222, `part3-ch5` plus this
chapter's commits, `RELAY_WEBHOOK_SECRET_KEY` set to CI's value.

---

## The walk, against a permanently failing endpoint

`node scripts/hostile-endpoint.mjs --mode=fail --quiet --secret=hunter2` in one
terminal, then:

```console
$ node scripts/webhook-walk.mjs --secret=hunter2 --fast-forward --watch-disable
=== 5. the whole schedule, without waiting for it =
  tiers: now → 1s → 5s → 30s → 300s → 1800s → 7200s
  7 attempts, then the delivery is dead-lettered.

  the waits are REAL in production. This rewrites next_attempt_at so a
  reader can watch the end of the schedule without waiting two hours —
  it is a fast-forward through the clock, not a shortcut around the logic.

  attempt 2                failed → rescheduled as attempt 3
    endpoint               run open · 2 failures · enabled=true
  attempt 3                failed → rescheduled as attempt 4
    endpoint               run open · 3 failures · enabled=true
  attempt 4                failed → rescheduled as attempt 5
    endpoint               run open · 4 failures · enabled=true
  attempt 5                failed → rescheduled as attempt 6
    endpoint               run open · 5 failures · enabled=true
  attempt 6                failed → rescheduled as attempt 7
    endpoint               run open · 6 failures · enabled=true
  attempt 7                failed → dead
    endpoint               run open · 7 failures · enabled=true

  delivery b9a68bee        attempt=7 state=dead next=2026-08-18T14:52:26.767Z

dead letters               1
  3e2acaf8                 attempts=7 last_status=500

=== 6. when to stop trying ========================
  The run above is what auto-disable reads — two columns on the endpoint,
  never the attempt stream. A backlogged analytics path cannot delay a
  disablement, and a broker being unwell cannot block one.

  The rule: longer than 60 minutes AND at least
  5 failures. Both, never either — the hour alone would let one
  failure followed by a two-hour retry gap disable an endpoint.

failures in the run        7
enabled                    true
  aging the run past the hour (the clock moves, the rule does not)...

endpoints the sweep disabled 1

enabled                    false
disabled_at                2026-08-18T14:52:29.830Z
disabled_reason            7 consecutive failures over 1h04m; last status 500

notification rows          1
  run of 7                 last_status=500 delivered_at=null

  `delivered_at` is null and stays null. FR-WHK-07 asks for the
  organisation to be notified BY EMAIL, and this platform has no email
  transport of any kind. The row is the obligation; the null is the
  admission. Chapter 3.7 needs the same transport for quotas.

a second sweep disables    0
```

The dispatcher's own JSON log lines are interleaved in the real output and are
removed above; they are one `delivery.attempted` per attempt and say nothing this
transcript does not.

**Read the two lines before section 6.** The delivery is `dead`, the run holds
seven failures, and `enabled` is still `true`. That is research R1's quiet
endpoint, reached by running rather than by arithmetic: the schedule is exhausted,
so no further outcome will ever be reported for this endpoint, and a check that
only runs on a recorded outcome would never fire again. The endpoint would sit
enabled and failing for ever.

The sweep disables it. A second sweep disables nothing — the `enabled = true`
predicate in the update is what makes that true, rather than a check somebody
remembered to write.

`disabled_reason` names the count, the window and the last status, which is what
FR-009 asks for and what stops the first support message being "disabled, why?".

`delivered_at=null` is the unmet half of FR-WHK-07, visible in the data rather
than only in prose.


---

## Quickstart V6 — the same walk with the sweep switched off

`RELAY_DISABLE_SWEEP=off`, everything else identical:

```console
=== 6. when to stop trying ========================
  The run above is what auto-disable reads — two columns on the endpoint,
  never the attempt stream. A backlogged analytics path cannot delay a
  disablement, and a broker being unwell cannot block one.

  The rule: longer than 60 minutes AND at least
  5 failures. Both, never either — the hour alone would let one
  failure followed by a two-hour retry gap disable an endpoint.

failures in the run        7
enabled                    true
  aging the run past the hour (the clock moves, the rule does not)...

endpoints the sweep disabled 0

enabled                    true
disabled_at                null
disabled_reason            null

notification rows          0

  `delivered_at` is null and stays null. FR-WHK-07 asks for the
  organisation to be notified BY EMAIL, and this platform has no email
  transport of any kind. The row is the obligation; the null is the
  admission. Chapter 3.7 needs the same transport for quotas.

a second sweep disables    0
```

**This is the bug, and it is worth staring at.** Seven failures, the run more than
an hour old, the delivery dead-lettered — and the endpoint is enabled. Nothing
further will ever be reported for it, so a check that runs only when an outcome is
recorded has already run for the last time.

Research R1 arrived at this by arithmetic against chapter 3.5's tier table before
any of it was built. Reading the two transcripts side by side is what makes the
second trigger something other than belt-and-braces.

---

## The sabotage battery

Seven mutations, each reverted and each file verified byte-identical afterwards.

```console
=============== mutation 1: clear the run on failure instead of on success
mutated 1 -> services/api/src/db/repository.ts
  RESULT: caught
         × invariant 6: a failure opens the run, and further failures extend it 84ms
         × invariant 7: any success clears the run 26ms
         × SC-003: an endpoint that succeeds once an hour is never disabled 50ms
         × invariants 6 and 11: an hour of failures past the floor disables it, once, with one notification 119ms
         × invariant 8: further failures do not disable it again or notify again 107ms
         × invariant 8 under concurrency: two overlapping reports disable once 127ms
=============== mutation 2: drop the enabled = true predicate
mutated 2 -> services/api/src/db/repository.ts
  RESULT: caught
         × invariant 8 under concurrency: two overlapping reports disable once 55ms
         × still disables only once when the pair crosses the threshold together 65ms
=============== mutation 3: let a test event touch the failure run
mutated 3 -> services/api/src/db/repository.ts
  RESULT: caught
         × invariant 13: the outcome leaves the failure run exactly as it was 146ms
=============== mutation 4: publish the attempt inside the transaction
mutated 4 -> services/api/src/webhooks/analytics.ts
  RESULT: caught
         × invariant 5: an outcome is recorded and answered with the ANALYTICS stream deleted 29ms
=============== mutation 5: remove the sweep from the relay loop
mutated 5 -> services/api/src/webhooks/delivery-relay.ts
  RESULT: caught
         × disables an endpoint with nothing but start() and time 20100ms
=============== mutation 7: drop SELECT FOR UPDATE on the endpoint
mutated 7 -> services/api/src/db/repository.ts
  RESULT: caught
         × counts BOTH of two overlapping failures — the lost update the lock prevents 65ms
=============== mutation 6: dedupe on the delivery id alone
mutated 6 -> services/api/src/webhooks/analytics.ts
  RESULT: caught
         × deduplicates on the delivery AND the attempt, not the delivery alone 3ms
=============== files restored byte-identical?
  YES
    f534eedd0ea59bfd297b5f325189bb8a  services/api/src/db/repository.ts
    eda6a842bd8e53d2d33ccf5b04d1628d  services/api/src/webhooks/analytics.ts
    b268a0ab8d7caaa72febe3f00567ae48  services/api/src/webhooks/delivery-relay.ts
  rebuild exit 0
SABDONE
```

**Three of these did not work the first time, and that is the useful part.**

*Mutation 4* was `try {` → `{`, which left a dangling `catch` and failed to
COMPILE. The battery reported it caught, and it was caught by `tsc` — which tells
you nothing about whether any test holds the property. Rewritten to remove the
swallow instead: the publish failure propagates, and `attempts.itest.ts`'s
invariant-5 case fails because a deleted analytics stream now turns an outcome
report into a 500.

*Mutation 5* removed `await sweepOnce()` from the relay's loop and **nothing
failed** — 49 passes. Every test drove `sweepOnce` or `sweepDisabledEndpoints`
directly, so the sweep was covered and its place in the loop was not. That is the
same shape as chapter 3.5's unfalsifiable "terminated, not retried" assertion. A
test that calls `start()` and then only waits now covers it.

*Mutation 7* dropped `SELECT … FOR UPDATE` from the endpoint read and **nothing
failed** either — and this one changed what the code says about itself. The comment
claimed the lock was what stopped a concurrent pair producing two disablements. It
is not: the `enabled = true` predicate does that alone. The lock prevents a LOST
UPDATE on `failure_run_attempts` — two transactions both read 4, both write 5, and
the run undercounts, so the endpoint quietly needs an extra failure to reach
FR-007's floor. Nothing anywhere reports that. There is now a test for the counter,
and the comment says what the lock actually does.

One more thing the battery taught, at its own expense: the revert step is
`git checkout --`, so the first re-run silently discarded an UNCOMMITTED comment
correction and the byte-identical check failed. Commit before running a battery
that reverts by checkout.


---

## Quickstart V2 — the ANALYTICS stream, as the broker reports it

Created by the api on its first publish. Nothing in the test suite or the
quickstart declares it — one definition of a stream, which chapter 3.5 established
for `DELIVERIES` and this chapter had to learn again the hard way (see the
`max_bytes` note below).

```console
$ node scripts/stream-info.mjs ANALYTICS
stream ANALYTICS
  messages           0
  bytes              0.0 MiB
  consumers          0
configuration
  subjects           ["analytics.>"]
  retention          limits   (immutable once created)
  storage            file    (immutable once created)
  replicas           1
  max_age            604800s
  max_bytes          1.00 GiB
  discard            old     (at the bound, drop the OLDEST)
  duplicate_window   120s   (the broker's dedupe, not ours)
consumers
```

`stream-info.mjs` took no argument before this chapter; it had `"EVENTS"` in three
places. The quickstart step that inspects `ANALYTICS` would have printed the wrong
stream's configuration and passed, because every field shown here exists on both.

**`max_bytes 1.00 GiB` is there because of a mistake worth recording.** The
attempts suite deletes this stream to prove a delivery survives without it, and its
teardown originally recreated the stream with its own hand-written configuration —
which omitted `max_bytes`. For two hours the stream a reader would have inspected
was the test's stream wearing the api's name, unbounded where the api bounds it.
The teardown now calls the api's own `ensureAnalyticsStream`.

## One attempt event, off the stream

Seven attempts against `--mode=fail`, so seven events. This is the first:

```console
analytics.webhook.attempt.b0fc170b-58dc-435d-b452-3f7df834e90f
{
  "delivery_id": "eb8fa3c9-606f-49a1-b872-b577efefe793",
  "endpoint_id": "2678590a-addc-489c-9ef5-3f8a807ddb16",
  "environment_id": "b0fc170b-58dc-435d-b452-3f7df834e90f",
  "event_id": "9f0667a3-c049-459d-9291-c70cffb35871",
  "attempt": 1,
  "attempted_at": "2026-08-18T16:06:13.509Z",
  "status": 500,
  "latency_ms": 12,
  "outcome": "rescheduled"
}
```

Read the fields that are NOT there: no event payload, no signing secret, no
signature, no url, no header. FR-004 asks for identifiers, statuses and durations
only, and the publisher builds the record by naming every key it copies rather than
by spreading what it was handed — an allow-list fails closed when somebody adds a
field, and a spread fails open.

`outcome` is the field the dispatcher could not have supplied. It has the status
and the latency; only the api knows whether a 500 meant "try again in five minutes"
or "that was the seventh, write the dead letter".
