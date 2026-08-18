# Research — chapter 3.6, "When to stop trying"

Phase 0. Each item is a decision with the reason attached, and two of them were
settled by arithmetic against chapter 3.5's tier table rather than by preference.

---

## R1 — When is the disable evaluated? (measured, and it changed the design)

**The question.** FR-WHK-07 says an endpoint failing continuously for more than
an hour is disabled. The obvious place to check is where failures are already
recorded: inside `recordAttemptOutcome`, in the same transaction, the way chapter
3.4 put the claim and the effect together. No new loop, no new state to poll.

**What the tier table actually produces.** Computed from
`RETRY_TIERS_MS = [0, 1s, 5s, 30s, 5min, 30min, 2h]` for one delivery that fails
every time, measured from its first attempt:

```text
attempt 1  at +0h00m00s   (within the 1h window)
attempt 2  at +0h00m01s   (within the 1h window)
attempt 3  at +0h00m06s   (within the 1h window)
attempt 4  at +0h00m36s   (within the 1h window)
attempt 5  at +0h05m36s   (within the 1h window)
attempt 6  at +0h35m36s   (within the 1h window)
attempt 7  at +2h35m36s
```

Six attempts land inside the first hour. **The seventh lands at 2h35m36s**, and
it is the last one — after it the delivery is dead-lettered.

**Why that breaks the obvious design.** A check that runs only when an outcome is
recorded cannot fire at one hour, because nothing happens at one hour. For a
single failing delivery the next event after 35m36s is at 2h35m36s, so the
endpoint is disabled ninety-five minutes late. Worse: if no further events arrive
for that environment, the dead-lettered delivery was the last attempt that will
ever be made, and **the endpoint is never disabled at all**. It sits enabled and
failing forever, which is the exact state FR-WHK-07 exists to end.

A busy environment hides this. New events keep arriving, attempts keep happening,
and the check fires close enough to the hour that nobody notices. The endpoint
that stays broken silently is the quiet one — the low-traffic customer, which is
also the customer least likely to be watching.

**Decision.** Two triggers, not one.

1. **On outcome** — the check runs inside `recordAttemptOutcome`'s existing
   transaction. This catches every busy endpoint at the first failure past the
   hour, and it is the path the tests drive.
2. **A sweep** — one query for endpoints whose failure run has outrun the hour,
   run from the loop the delivery relay already has. Not a new deployable, not a
   new loop, not a new deployment concern: one more statement per drain in a
   worker that is already awake and already polling.

**Alternatives considered.**

- *Outcome-only.* Smaller, and it is what the spec's first draft implied. Rejected
  because it silently exempts exactly the endpoints the requirement is about.
- *A dedicated scheduler.* A third background service, or a cron. Rejected under
  constitution VII: the relay loop is already running, already owned by the api,
  and already has the database connection.
- *Compute the disable lazily at read time.* An endpoint is "disabled" if its run
  exceeds an hour, evaluated when anything looks at it. Rejected because
  disablement has effects — a notification, a stopped delivery path — and an
  effect that only happens when somebody looks is not an effect.

---

## R2 — Where the failure run lives

**Decision.** Two columns on `webhook_endpoints`:
`failure_run_started_at` and `failure_run_attempts`, both nullable, both null
when the endpoint is healthy.

**Why not a table.** A run is one row per endpoint by definition — it is the
*current* run, and there is only ever one. A table would need a "which row is
current" rule, and that rule is the bug.

**Concurrency.** Two dispatcher instances can report outcomes for two deliveries
to the same endpoint at the same moment. Both would read the run, both would
decide, and without a lock both could disable and both could notify — FR-008 says
at most once. The update takes `SELECT … FOR UPDATE` on the endpoint row inside
the transaction that records the outcome, which serialises the pair. The lock is
held for the length of one small update, and it is per endpoint, so two customers
never contend.

**Clearing.** Any delivered outcome sets both columns to null. So does
re-enabling (FR-017). The run is not history — history is the attempt event
stream — it is the single fact auto-disable needs, and keeping it small is what
lets it be read on every outcome without a second query.

---

## R3 — The minimum-attempts floor

**The question.** FR-006 requires an hour *and* a minimum number of attempts. The
hour alone is not enough: the 2h tier means one failure at t=0 followed by silence
satisfies "failing for more than an hour" with a single data point.

**Decision: 5.**

From R1's timeline, one failing delivery reaches 5 attempts at +5m36s and 6 at
+35m36s, both inside the hour. So a single delivery that keeps failing clears a
floor of 5 with room to spare, and the floor never becomes the reason a genuinely
dead endpoint stays enabled. Set it to 7 and a single-delivery run could never
trigger, because the 7th attempt falls outside the window.

Below 5 the floor stops doing its job: 2 or 3 attempts is reachable in the first
six seconds, which is a blip rather than an outage.

**Alternatives considered.** A rate ("more failures than successes in the hour")
— rejected as harder to explain to a customer and harder to test than a run that
any success clears. A byte-count or error-class rule — rejected as policy the
requirement does not ask for.

---

## R4 — The attempt event: which stream, which subject, who publishes

**Decision.** The **api** publishes, to a **new `ANALYTICS` stream**, on subject
`analytics.webhook.attempt.{environment_id}`.

**Why the api and not the dispatcher.** The dispatcher has the latency and the
status, so it looks like the natural publisher. Three reasons it is not:

- The dispatcher already reports the outcome to the api. Having it *also* publish
  means two writes to two systems for one fact — the dual write chapter 3.3 spent
  itself removing, reintroduced one hop later.
- The api already owns a publisher (`createJetStreamPublisher`), already has the
  outbox pattern, and already knows how to ensure a stream exists.
- The attempt event needs identifiers the dispatcher does not hold — the
  environment, for the subject, and the endpoint — without another lookup.

**Why a new stream.** `EVENTS` carries tenant domain events with a seven-day
retention shaped for consumers that must not miss one. `DELIVERIES` carries work.
Attempt records are neither: they are high-volume, they are allowed to be lossy
(see R5), and Part 4's ingester will want to consume them without also consuming
every message event. Separate stream, separate retention, separate consumer
position.

**Subject grammar.** `analytics.{domain}.{action}.{environment_id}`, which extends
chapter 3.4's `events.{domain}.{action}.{env}` rather than inventing a second
convention. The grammar goes in `@relay/protocol` beside the other two.

---

## R5 — The attempt event is allowed to be lost, and that has to be said out loud

**The tension.** FR-WHK-06 says *every* delivery attempt shall be recorded.
Constitution III says analytical events are emitted asynchronously and that
"failure or backlog of the analytical pipeline MUST NOT affect message delivery,
API availability, or webhook dispatch."

Those two cannot both be maximised. Recording every attempt without loss means
the attempt record shares a transaction with the outcome — the outbox pattern —
and then a stalled analytics path backs up an operational table. Guaranteeing
independence means the publish happens outside the transaction, and a crash
between commit and publish loses the record.

**Decision.** Independence wins. The publish happens **after** the outcome
transaction commits, outside it, and a failure to publish is logged and dropped.

**Why.** The two failure modes are not equal. A lost attempt record costs a gap in
an analytics dashboard. A blocked outcome transaction costs a customer's webhooks
— the delivery path stops moving because a metering pipeline is unwell, which
constitution III names as a design failure in as many words.

**What this obliges the chapter to say.** That FR-WHK-06's "every" is approximate,
in the same paragraph that introduces the feature — not in a footnote. This is the
second thing in the chapter that is deliberately half-delivered, and a chapter that
hides one of them has hidden both.

**Alternatives considered.** Route attempts through the existing `outbox` table so
they inherit 3.3's guarantee — rejected: it puts analytical volume through the
operational store and couples the two paths constitution III separates. Buffer
in memory and batch — rejected as Part 4's ingester's job, not this chapter's.

---

## R6 — The latency is already crossing the seam, and the api throws it away

Chapter 3.5's `internalDeliveryOutcomeRequestSchema` carries `latency_ms` as a
required, non-negative integer. The dispatcher measures it and sends it on every
attempt. Neither `dispatch.controller.ts` nor `recordAttemptOutcome` mentions the
field: it is validated and discarded.

So FR-001's hardest-sounding column — how long the customer took to answer — costs
nothing to obtain. The data has been arriving since 3.5 shipped; this chapter is
the first thing to want it.

**Decision.** Take it as it is, and do not widen the contract. Nothing new is
needed on the seam for the attempt record beyond what 3.5 already defined.

---

## R7 — The notification record

**Decision.** A `webhook_disable_notifications` table: the endpoint, the
organisation to tell, when, the window that triggered it, the last status and
error, and a `delivered_at` that stays null until a transport exists.

**Resolving the organisation.** `webhook_endpoints.environment_id` →
`environments.application_id` → `applications.organisation_id`. Three joins, all
present, none added by this chapter.

**Why a table and not columns on the endpoint.** The endpoint gains
`disabled_at` and `disabled_reason` regardless (FR-009 — a customer must be able
to tell an automatic disablement from their own). The notification is a different
thing: it is an *outbound obligation* with a lifecycle, and `delivered_at` is the
column that makes the unmet half of FR-WHK-07 visible in the schema rather than
only in prose. Chapter 3.7 will set it.

---

## R8 — The test event (FR-WHK-09)

**Decision.** A synthetic event of type `webhook.test`, delivered through the
ordinary path — expansion, a real delivery row, the real signature — with three
deviations, each for a stated reason:

| Deviation | Reason |
|---|---|
| Delivered to **one** endpoint, named by the caller, not fanned out by subscription | A test is aimed. Fanning it out would send every endpoint in the environment a surprise. |
| Delivered even when the endpoint is **disabled** | Testing is how a customer establishes the endpoint is fixed before re-enabling. Refusing here would make the loop unclosable. |
| Its outcome **does not touch the failure run** | A test event is a diagnostic, not traffic. Letting a failed test push an endpoint toward disablement would punish a customer for checking, and letting a successful one clear the run would let a customer mask a real outage with a test. |

**Marking it.** The envelope's `type` is `webhook.test` and the payload carries
`"test": true`. Both, because a recipient switching on `type` and a recipient
inspecting the body should each be able to tell without knowing about the other.
The signature is computed exactly as for a real event — a test whose signature
worked differently would prove nothing about real deliveries (FR-014).

**Attempt limit.** One attempt, no retry schedule. A test that quietly retried
for two hours would report a stale answer to somebody standing at their terminal.

---

## R9 — Re-enabling

**Decision.** Re-enabling through the existing endpoint clears
`failure_run_started_at`, `failure_run_attempts`, `disabled_at` and
`disabled_reason` in one transaction (FR-017).

There is no automatic re-enable and no health probing. A platform that probes a
disabled endpoint on a timer has rebuilt, at lower volume, the capacity drain that
disabling was meant to stop — and research R1 in chapter 3.5 measured what that
costs when a dead endpoint holds a slot.

---

## R10 — The fence budget, costed before rather than after

Chapter 3.5 budgeted 22–26, revised to 25–29, then to 37–41 once test files and
container files were counted, and shipped 39. The two revisions were not drift;
they were categories that had been left out. This estimate counts them from the
start.

**Amendments to files earlier chapters fenced:**

| File | Why |
|---|---|
| `services/api/src/db/schema.ts` | two failure-run columns, two disable columns, one new table |
| `services/api/src/db/repository.ts` | the run update, the disable, the sweep, the notification, the test event |
| `services/api/src/webhooks/delivery-relay.ts` | the sweep rides its loop |
| `services/api/src/webhooks/webhooks.controller.ts` | test-event route, re-enable clearing |
| `services/api/src/webhooks/webhooks.service.ts` | test-event orchestration |
| `services/api/src/internal/dispatch.controller.ts` | outcome handler now publishes |
| `packages/protocol/src/internal.ts` | the analytics subject grammar |
| `services/api/src/outbox/jetstream.publisher.ts` | ensure the ANALYTICS stream |
| `vitest.coverage.config.mts` | ratchets, again (R11) |

Nine amendments. **New files:** the migration, an `analytics.ts` publisher module,
and a `disable.ts` policy module — three. **Test files:** `disable.test.ts` (the
policy arithmetic), `analytics.test.ts`, `attempts.itest.ts`, `test-event.itest.ts`,
and amendments to `deliveries.itest.ts` and `internal.test.ts` — six. **Scripts:**
amendments to `stream-info.mjs` (it hardcodes `EVENTS`) and `webhook-walk.mjs`
(`--watch-disable`) — two, and both exist because the quickstart already invokes
behaviour neither script has.

*This count was wrong on the first pass and is corrected here rather than
silently: it named an amendment to `dispatcher.itest.ts` that nothing in the plan
touches, and omitted `analytics.test.ts`, `internal.test.ts` and both scripts. Net
three files more than estimated, which is the same failure mode as chapter 3.5's
first two budgets — a whole category left uncounted.*

**Budget: 18–22**, revised upward from 15–19 by the recount. Still about half of
3.5's 39, and the reason is that 3.5 built a service while this chapter adds
columns to one. If implementation approaches 22, the signal to check is whether the
test event (FR-WHK-09) has grown past the modest widening it was accepted as.

---

## R11 — Constitution VI, and the ratchet that 3.5 raised

`repository.ts` now sits at 97.28 / 89.51 / 100 / 98.99 against ratchets of
97 / 89 / 100 / 98. **There is between 0.28 and 0.51 of a point of headroom**, and
this chapter adds five operations to that file.

Chapter 3.5's baseline predicted "expect to raise the ratchet rather than discover
it broken at the end" and then discovered it broken at the end, because the new
code was reached only from a child process whose coverage is not attributable. The
same trap is live here: the sweep runs in the relay loop, and the attempt publish
happens after a transaction commits — both are easy to exercise in a way the
instrument cannot see.

**Decision.** Coverage is checked at the point each operation lands, not once at
the end, and every new operation gets a test that calls it directly rather than
through a spawned service.
