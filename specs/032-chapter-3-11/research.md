# Phase 0 — Research: Chapter 3.11, Counting a connection

Every decision below was taken against the code, not against a memory of it.
Where a number appears it was read out of a file or measured; where a
measurement is still owed, the task that owes it is named.

---

## R1 — The gateway has never spoken for itself, and now it has to

**Finding.** Every internal call the gateway makes forwards the end user's
token. `services/gateway/src/api-client.ts` says so in a comment that is fenced
into chapter 3.2:

> the token the client presented at connect, carried so the internal hop can
> FORWARD it instead of asserting who the caller is. The gateway holds it; it
> does not verify it and holds no secret that could.

A usage report is not a user's action. It is the gateway's own claim about many
connections, potentially across many environments, about time that has already
passed. No user's token authorises it. Worse, the obvious workaround — report
per connection using that connection's token — fails hardest exactly where it
matters: a token expires while the socket stays open, `handleSend` already
carries a branch for the 401 that produces, and the long-lived connection whose
token has expired is the connection with the most minutes on it.

**Decision.** The gateway presents a **platform credential**, the class chapter
3.5 built for the dispatcher: `PlatformPrincipal` in `auth/principal.ts`,
`@Accepts("platform")` on the route, the `rk_svc_` prefix, and the shared secret
in `RELAY_INTERNAL_CREDENTIAL`. The gateway becomes the second service to hold
one.

**Cost, counted.** One environment variable in `compose.yaml` (the `gateway:`
block has none today — `api:` and `dispatcher:` each have one, at lines 128 and
166), one entry in `turbo.json`'s `test:integration` env list, and one config
read in the gateway. No new concept, no ADR.

**Alternatives rejected.** Forwarding a user token, above. Making the report
route credential-free on the grounds that it is internal — the `/internal`
prefix is a routing convention, not a boundary, and FR-011 exists because a
metering route anyone can reach is a billing forgery with a public API.

---

## R1a — `service: "dispatcher"` is hardcoded, and the second caller makes it a lie

**Finding.** `resolvePlatformCredential` in `auth/authenticate.middleware.ts`
ends:

```
  return { kind: "platform", service: "dispatcher" };
```

unconditionally. The field it fills is documented in `principal.ts` as "Which
internal service presented it, for logs. Never the credential." With one caller
the constant was accurate. With two it is wrong for half of them, and the log
line that says which service asked for a write becomes the one field in the
principal that cannot be trusted.

**Decision.** One credential per service. `RELAY_INTERNAL_CREDENTIAL` keeps its
name and its meaning (the dispatcher's), and the gateway gets
`RELAY_INTERNAL_CREDENTIAL_GATEWAY`. The compare becomes a walk over a small map
of `{ env var → service name }`, returning the service whose secret matched.

**What it buys beyond honest logs.** A gateway compromise no longer yields the
dispatcher's reach. The two services have different exposure — the gateway
terminates connections from the public internet, the dispatcher does not — and
sharing one secret between them means the more exposed one sets the blast
radius for both.

**Cost, counted.** One environment variable, one compose line, one turbo entry,
and the constant-time compare moves inside a loop. The compare itself does not
change; it runs at most twice.

**Alternative rejected.** Keep one secret and have the caller name itself in a
header, trusted only for logging. Chapter 3.2 spent itself removing exactly that
— the gateway used to send an environment header and a user header it had
invented — and "it is only for logs" is the sentence under which an asserted
header survives a review.

---

## R2 — The unit: wall-clock minute buckets, charged per connection

`docs/04-srs.md` line 789 records this as open question 4, addressed to Product
and Billing: "Does connection-minute metering need per-second precision, or is
per-minute rounding acceptable?" The chapter answers it (FR-028).

**Decision.** A connection-minute is one calendar minute in UTC during which one
connection was open for any part of it. A five-second socket costs one minute. A
socket open from 00:00:59 to 00:01:01 costs two. One hundred concurrent sockets
open for one minute cost one hundred.

**Rationale.** The three candidates differ in what they charge for reconnect
churn and in what they cost to deduplicate:

| Model | 1,000 × 5-second sockets | Dedup key |
|---|---|---|
| Minute buckets, per connection | up to 1,000 minutes | the bucket identity, already monotonic |
| Seconds, rounded up per connection | 1,000 minutes | a per-connection accumulator |
| Seconds, summed and rounded at read | 83 minutes | a per-connection accumulator |

The third is the most literally accurate and the one a reconnect storm costs
nothing under. The first makes the deduplication fall out of the unit rather
than being bolted on: the set of buckets a connection has occupied only grows,
so a cumulative count of it only grows, and "credit the difference" is the whole
of the idempotency story.

---

## R3 — Reports carry totals, not deltas, and that removes the retry buffer

**Decision.** A report states what a connection has consumed **in total** in a
period, not what it consumed since the last report.

**What this buys, and it is the load-bearing decision of the chapter.** A delta
protocol needs at-least-once delivery, a message identity to deduplicate on, and
somewhere to keep reports that could not be delivered. A cumulative protocol
needs none of the three:

- a report that is lost is repaired by the next one, because the next one
  carries the same total plus whatever accrued since;
- a report delivered twice credits `max(0, reported − credited) = 0` the second
  time;
- reports that cannot be delivered are **dropped**, not queued. The gateway
  holds no outbox, which is the correct amount of durable state for a service
  whose design is that it holds none.

**What it does not buy.** A gateway that dies still loses the minutes accrued
since its last report. That is FR-008's bounded loss and R11 shrinks it for the
graceful case.

---

## R4 — Idempotency state is per connection, not per minute

**The shape that is wrong.** Remember which minutes have been credited. The key
is `(connection_id, minute)`, which for a tenant holding a thousand concurrent
sockets is 1,000 × 43,200 = **43.2 million rows a month**. FR-010 forbids
storage proportional to elapsed time for this reason, and chapter 3.10 refused
the same shape for distinct users, where the bound came from users rather than
from traffic.

**Decision.** One row per `(connection_id, period)` holding the count already
credited. The credit is `max(0, reported − credited)`, applied to the
`usage_periods` roll-up in the same transaction, and the row is updated to the
new total. Bounded by distinct connections in the period.

**Why the roll-up column and not `sum()` over the accounting rows.** Summing is
proportional to the tenant's connection count for the month — 720,000 rows for
the thousand-socket tenant if sockets turn over hourly. That is chapter 3.10's
R1 argument arriving a second time in a different costume, and the answer is the
same: keep the total, pay one indexed write.

---

## R5 — There is still no sweep

Usage rises only when a report arrives, and the report transaction knows the
figure before and after, so it knows which thresholds it crossed and writes the
notification rows itself. `recordCrossings` is reused unchanged in behaviour.

Chapter 3.10 predicted this once and it held; this is the second chapter to
reach the same result by the same argument. Feature 030's guard is expected to
be engaged nowhere and no file should join its exemption list. The prediction is
falsifiable and V7 of the quickstart exists to falsify it.

---

## R5a — What chapter 3.10's SC-008 actually measured

**Finding, and it is not flattering.** The guard's triggers cover five tables,
named in the `FOREACH` loop at the bottom of
`packages/test-harness/src/sentinel.sql`:

```
'webhook_endpoints', 'webhook_deliveries', 'webhook_disable_notifications',
'channels', 'users'
```

Chapter 3.10 added three environment-scoped tables — `usage_periods`,
`usage_active_users`, `quota_notifications` — and extended the guard to none of
them. Its SC-008 read "no new file is added to feature 030's exemption list",
which passed, and is true, and does not mean what the sentence sounds like: no
file needed an exemption partly because the new tables are not guarded, so
nothing there could have been refused.

**Measured, and the extension is not a one-line change.** The guard's refusal
message is

```
RAISE EXCEPTION 'global-operation guard: … row %.% (id %) …',
  TG_TABLE_SCHEMA, TG_TABLE_NAME, OLD.id, …
```

`usage_periods`' primary key is `(environment_id, period)`. It has no `id`
column, so `OLD.id` raises `record "old" has no field "id"` from inside the
guard, at execution time, on the first update. Adding the table to the array
would produce a guard that fails on the writes it is meant to permit.

**Decision for this chapter: do not extend the guard, and say so with the
numbers.** `sentinel.sql` is feature 030's surface, that feature publishes no
chapter, and its fences live in `fences/post-series.md` for exactly that reason.
A published chapter carrying a test-harness diff it does not teach is what
`post-series.md` exists to prevent. The fourth unguarded environment-scoped
table is recorded here, with the `OLD.id` problem, so the work is scoped rather
than remembered.

---

## R6 — `Authentication` has three outcomes and needs a fourth

**Finding.** `services/gateway/src/auth.ts` opens: "Three outcomes, not two."
They are `ok`, `refused` (the api said the credential is bad — close 4001,
retrying will not help) and `unavailable` (we could not ask — close 1011,
retrying will).

`api-client.ts` maps status to outcome:

```
if (res.status === 401 || res.status === 403) return null;
return parse(res, internalSessionResponseSchema, "session");
```

and `parse` throws `ApiError` for anything not `ok`. So a 402 from the session
route lands in the `catch` and closes the socket as **1011, we are broken,
retry** — wrong about whose fault it is and wrong about whether retrying helps.

**Decision.** A fourth outcome. The chapter's comment goes from "three outcomes,
not two" to four, and the upgrade handler gains one branch that writes a raw
402 on the socket beside chapter 3.8's raw 429.

**Cost.** One variant in a union, one branch in `server.on("upgrade")`, one
refusal writer next to `refuseUpgrade`, and one diff fence each in `auth.ts`,
`api-client.ts` and `session.ts`.

---

## R7 — The connect path gains a read, against chapter 3.10's explicit refusal

**Finding.** Chapter 3.10's second analysis pass, finding H2, refused to extend
`environmentLimits` with a usage join specifically because
`internal/session.controller.ts` calls it to hand the gateway its limits, and
"every WebSocket connect would pay for a usage join". This chapter has to put a
usage read on that exact path, because that is where the cap is enforced.

**Decision.** Read caps and connection-minutes usage in the same joined shape
`assertWithinQuota` already uses — `environments` left-joined to `usage_periods`
on two primary keys, one round trip — and exit early when nothing is configured,
which is the unconfigured tenant's whole cost. `environmentLimits` still is not
extended; the quota read is its own call on the same request.

**Owed measurement.** Connect latency before and after, at concurrency, with
`EXPLAIN (ANALYZE, BUFFERS)` for the added read (SC-012). Chapter 3.10's T033
spent three wrong diagnoses on an uncontrolled benchmark that reported 273% to
411% regressions before instrumentation showed 0.56ms per send. The instrument
comes first this time.

---

## R8 — The write cannot go through `Repository`

**Finding.** `Repository` is environment-scoped by construction — every query
closes over `this.environmentId`, which is constitution I expressed as a type. A
platform principal deliberately carries no `environmentId` (`principal.ts`:
"Present and always undefined … a platform principal reaching a tenant-scoped
repository yields the empty scope"). The report route is platform-credentialled
and names its environments in the body.

The precedent is the dispatcher's: `internal/dispatch.controller.ts` calls
standalone exported functions — `expandEventToDeliveries(db, {…})`,
`recordAttemptOutcome(…)` — that take `db` and explicit ids. `usageFor` is
already written that way, and says why: "Admin surface: takes an environment id
rather than being scoped by construction, because the relay and the internal
route both read it on behalf of the platform."

**The obstacle.** `recordCrossings` and `organisationOf` are **private methods**
on `Repository` that read `this.environmentId`. The notification machinery the
third dimension wants to reuse is behind the scoping the report route cannot
satisfy.

**Decision.** Extract both to standalone functions taking `(tx, environmentId,
…)`; the existing private methods become one-line delegations. Roughly forty
lines moved, no behaviour changed, and it is the seam that lets the third
dimension reuse the outbox instead of copying it a fifth time.

---

## R9 — Nothing prunes the accounting rows, and the growth is stated

The per-connection rows accumulate at roughly the tenant's distinct connections
per period. Deleting a finished period's rows is a global operation over an
environment-scoped table — the only sweep this chapter could contain — and it is
out of scope. The number is written into `data-model.md` rather than left for
whoever notices the table first.

---

## R10 — The reporting interval is its own timer

The gateway runs exactly one timer today: `PING_INTERVAL_MS = 30_000`, sized by
EIR-WS-04's requirement that a dead socket be noticed promptly. Billing cadence
and liveness cadence are different requirements, and one number serving both
means the next change to either argues with the other.

**Decision.** A second `setInterval`, default 60 s to match the unit, injectable
the way `pingIntervalMs` already is — `attachSessions` takes it as a parameter
precisely so tests need not wait. `sessions.close()` clears both.

**Consequence, stated as a number.** An ungraceful death loses at most one
interval of minutes per open connection: 60 seconds, or one bucket, or two if
the death straddles a boundary.

---

## R11 — A graceful shutdown flushes, a crash does not — and the gateway had no graceful shutdown

`main.ts` wires `server.on("close", () => { sessions.close(); … })`, and the
first draft of this plan said the flush hangs off that. **The second analysis
pass found that handler never runs.** `serve()` returns a bare `node:http`
Server; nothing in the gateway ever calls `server.close()`, and nothing installs
a signal handler. On `docker stop` the process takes SIGTERM, Node's default
disposition exits, and the close handler is not reached.

Every document said the flush happens — R11, FR-008, `contracts/metering.md` §5,
and the task that wires it. All four agreed, and none of them was the thing that
had to be true.

**Decision.** Install SIGINT and SIGTERM handlers in the gateway's `main.ts`, in
the shape the dispatcher already uses at `services/dispatcher/src/main.ts:313`:

```
  for (const signal of ["SIGINT", "SIGTERM"] as const) {
    process.on(signal, () => {
      void dispatcher.stop().then(() => process.exit(0));
    });
  }
```

`sessions.close()` is `() => void` today and becomes async, because a flush that
is not awaited is the same non-guarantee in a new place. This is the difference
between losing a minute per crash and losing a minute per deploy times every open
socket, and a deploy is the frequent one.

**What stays out.** `CLOSE_CODES[4009]` is `"server shutdown (drain)"`, fixed by
SAD §7, and this chapter builds the first shutdown path the gateway has ever had
— so the code is sitting right there. It stays unused. Draining is telling
clients to reconnect elsewhere, which is a feature with its own semantics, and
adding it because a shutdown handler happened to arrive would be the "reaching
for the code because it was declared" that chapter 3.8 refused by name. R21's
test keeps asserting nothing emits it.

---

## R12 — The clock has to be drivable, or the suite cannot express its own tests

Every acceptance scenario in the specification is stated in calendar minutes.
`periodOf(at: Date)` is already written to take an instant rather than call
`now()` — chapter 3.10 needed the same property for months. `minuteOf(at: Date)`
goes beside it, in the same file, for the same reason, and the meter takes its
clock as a parameter.

---

## R13 — Clock skew bounds attribution, not totals

A connection lives on exactly one gateway instance and its connection id is a
`randomUUID()` minted there, so two instances cannot both report the same
connection and skew cannot double-count. What skew can do is put a bucket in the
wrong minute, and at a month boundary in the wrong period. The error is bounded
by the skew itself. Not corrected here; NTP is an operational answer and
inventing a consensus clock for a billing rounding error is the shape
constitution VII refuses.

---

## R14 — The overshoot bound is honest and it is not small

FR-RTL-08 keeps existing connections open past the cap, and R2 keeps metering
them. So:

> overshoot ≤ (connections open when the cap was crossed) × (minutes until each
> closes) + one reporting interval

and nothing in the platform bounds how long a client holds a socket. There is no
numeric ceiling. The alternatives are to close connections at some multiple of
the cap, which contradicts FR-RTL-08, or to stop metering past the cap, which
makes the recorded figure wrong. Stating the bound and its open right-hand side
is better than either.

---

## R15 — The prediction this chapter has to check

Chapter 3.10 wrote the cost of a third dimension down twice. In
`0009_quotas.sql`:

> chapter 3.11 adds connection-minutes and FR-MED-12 later adds media bytes, and
> neither needs a table migration — a new dimension is a new key … the shape
> below is enforced by a CHECK that ENUMERATES the two dimensions, so a third
> one does cost a one-line constraint change

and in `quotas/config.ts`:

> Chapter 3.11 adds connection-minutes by adding a key here and a line to the
> migration's CHECK

**What is actually enumerated**, read out of the two files — as a **prediction to
be measured**, not an inventory:

| Place | What a third dimension costs |
|---|---|
| `quotaConfigSchema` in `config.ts` | one key |
| `environments_quota_config_shape` CHECK | one `jsonb_typeof` clause + two regex clauses |
| `quota_notifications_dimension_check` | one value in an `IN` list |
| `usage_periods` | one column and its non-negative CHECK |
| `publicMessage()` in `quota.error.ts` | a two-way ternary becomes a three-way one, and "sends resume" stops being right |
| `quota-email.ts` | a key in the `NOUN` map |
| `usageFor` | two fields on its return shape |

**Seven places on this reading, and the reading is not the measurement.** An
earlier draft of this table listed "`Dimension` union in `quota.error.ts` — one
member" and called the total six. The second analysis pass found there is no union
to edit: `Dimension` is `keyof QuotaConfig`, so it widens the moment the config key
lands, which is exactly why the ternary beside it is dangerous — the compiler
catches nothing. Charging for a line that writes itself, and not charging for the
line that silently produces the wrong word, is the shape of a cost estimate
assembled by looking at type declarations.

Seven places on this reading against "a new key plus a one-line constraint
change" in the written prediction. **T066 counts what was actually paid and does
not carry this number into the counting** — a prediction read before a measurement
is how a measurement becomes a confirmation, and this table has already been wrong
once about which places cost anything.

---

## R16 — The fence surface, counted before it is a problem

**Twenty-one** files this chapter is likely to touch already carry **95 titled
fences** between them in the English chapters:

| File | Fences | |
|---|---|---|
| `services/api/src/db/repository.ts` | 15 | |
| `services/api/src/db/schema.ts` | 11 | |
| `packages/protocol/src/internal.ts` | 8 | |
| `services/gateway/src/session.ts` | 7 | |
| `turbo.json` | 7 | build gate |
| `services/gateway/src/session.test.ts` | 6 | |
| `services/api/src/internal/internal.module.ts` | 5 | |
| `services/gateway/src/main.ts` | 4 | |
| `services/gateway/src/registry.ts` | 4 | |
| `vitest.coverage.config.mts` | 4 | build gate |
| `eslint.config.mjs` | 4 | build gate |
| `services/gateway/src/api-client.ts` | 3 | |
| `services/gateway/src/auth.ts` | 3 | |
| `services/api/src/auth/authenticate.middleware.ts` | 3 | |
| `compose.yaml` | 3 | build gate |
| `services/api/src/internal/session.controller.ts` | 2 | |
| `packages/protocol/src/codes.ts` | 2 | |
| `services/api/src/quotas/config.ts` | 1 | |
| `services/api/src/quotas/policy.ts` | 1 | |
| `services/api/src/quotas/quota.error.ts` | 1 | |
| `services/api/src/limits/rate-limit.middleware.ts` | 1 | |

Three of the four build-gate files also carry entries in `fences/post-series.md`
— `turbo.json` 1, `vitest.coverage.config.mts` 2, `eslint.config.mjs` 1,
`compose.yaml` 0 — so a change to any of them has to decide which side of the
series it belongs on before it is written. An earlier draft of this footnote gave
two of the three and omitted `turbo.json`, which is the same undercount the table
above it exists to stop.

**This table has now been wrong in all three analysis passes, and the pattern is
worth more than the number.**

| Pass | Said | Wrong because |
|---|---|---|
| draft | 12 files, 62 fences | omitted `rate-limit.middleware.ts` |
| 1 | 13 files, 66 fences | asserted 4 fences for that file; it has 1 |
| 2 | 17 files, 77 fences | counted only *source* files |
| 3 | 21 files, 95 fences | counted from the pages |

Every correction came from counting. Every error came from extending a list that
already existed. **T006 derives this table from the pages and it is never
hand-edited again** — a hand-maintained inventory of something a script can count
is the shape of all four mistakes above.

The chain applies **hunked diffs**, so the cost is one diff fence per changed
region rather than a restatement of each file — `check-fence-chain.mjs` requires
each hunk's pre-image to appear in the predecessor state exactly once, and the
final state to equal disk.

Chapter 3.10's third analysis pass found that **no task wrote the chapter's
fences** and called it the most expensive finding of three passes in wall-clock
terms, because it surfaces after the chapter is written and translated. The
fence work is scheduled from the start here.

---

## R17 — Phase order, and where the seam is

The estimate is 3,000–3,600 prose words against a 2,000–4,000 gate counted on
the finished page. Chapter 3.10's estimate ran 18% high against the page it
produced; three of Part 3's four splits were discovered mid-chapter.

The seam is the same place it was in 3.10: the notification story goes last. It
is the fourth telling of the outbox and, for this chapter, mostly reuse — a
reader who stops before it has the chapter's subject, which is metering a
duration from a service that cannot write. If the count overruns, US4 moves and
US3 moves with it.

---

## R18 — The minute arithmetic is duplicated, on purpose, with a precedent

**The problem.** The gateway decides which minute buckets a connection has
occupied and which period each belongs to. `periodOf` lives in
`services/api/src/quotas/period.ts`, and the gateway cannot import from the api
service.

**The precedent, and it is exact.** `services/gateway/src/limits.ts` already
duplicates the api's window arithmetic, and says why in a comment that is fenced
into chapter 3.8:

> Floored, so two instances agree without coordinating — the same arithmetic as
> the api's, deliberately duplicated rather than shared: a package for two small
> functions would be an abstraction constitution VII asks to be justified, and
> this one could not be.

**Decision.** Duplicate `periodOf` and `minuteOf` into the gateway's meter — in
`meter.ts`, beside the bucket arithmetic that uses them — with the same argument,
and pin them together with a **drift test**: a unit test in
each package that asserts both implementations agree on the same set of
instants, including a month boundary and a leap-day boundary. Feature 030's R50
established the shape — a drift test is what makes a deliberate duplication
different from a copy somebody forgot about.

**Alternative rejected.** A shared `@relay/usage-time` package for two functions
of four lines each. The comment above already refused that trade once, for the
same reason, in the same directory.

**What makes this one riskier than 3.8's.** A rate-limit window that disagrees
between two services costs one window of over- or under-service. A period that
disagrees puts a tenant's minutes in a month nobody reads — chapter 3.10's
`period.ts` says exactly this about `date_trunc` without a timezone. So the drift
test is not decoration here; it is the only thing standing between two copies of
a calendar.


---

## R19 — The close path, and the hole it opens in R3

**Found by the first analysis pass, and it is a correctness gap rather than a
wording one.** `services/gateway/src/session.ts` removes a connection from the
registry in its `close` handler, on the line after the handler opens:

```
    socket.on("close", (code) => {
      registry.remove(connection.id);
```

The meter walks the registry. So a socket that opens and closes between two
reports is gone before anything can report it, and it is counted **zero**. FR-002
says a five-second socket costs one minute and the specification's US1 scenario 5
says a socket living inside one interval has been counted; the design as planned
satisfied neither.

Worse, it fails at the one thing R2 chose the bucket model *for*. The comparison
table there says the per-connection bucket model charges reconnect churn where
summing seconds does not — and under a registry-only meter, churn is free. A
thousand five-second sockets would have cost nothing.

**Decision.** The close handler hands the connection's final per-period totals to
the meter, which includes them in the next report. Not a synchronous HTTP call
from a close handler: that handler is already documented as "the last place that
should throw", and a mass disconnect would turn one event into a burst of
requests.

**And this is where R3's claim needs narrowing, said plainly rather than left to
be discovered.** R3 says reports carry totals so nothing has to be queued — a lost
report is repaired by the next one. That reasoning holds for a connection that is
still open and **fails for one that has closed**, because there is no next report
to carry the total. So:

- open connections: no retention, exactly as R3 says
- closed connections: retained until a report carrying them is **accepted**

The retained set is bounded by closes since the last accepted report, capped, and
a discard at the cap is logged and counted (FR-029). A cap that drops entries
under-counts, which is the same direction as the crash loss in R10 and the
opposite of billing for a socket nobody holds.

**What it costs the chapter.** One more row in the loss table, one honest
paragraph narrowing a decision made two sections earlier, and the admission that
the design's cleanest claim — "the gateway holds no queue" — is true of most of it
and not all of it.

---

## R20 — A report naming a connection the api has never seen

The specification listed this as a decision the plan must make and state, and the
first draft of the plan did not make it. It is made here.

**Decision.** Accepted, as that connection's first report. The api is never told
when a connection opens — the first it hears of any connection is a report — so
"unknown" and "first" are the same state and there is nothing to distinguish them
with.

**Why not refuse it.** A refusal would need the api to know the set of live
connections, which means the gateway announcing every connect: one extra internal
call on the hot path of the thing chapter 3.2 spent its research budget keeping to
one round trip, to buy a check against a caller that already holds a platform
credential.

**What still gets refused**, and it is the one that matters: a report naming a
connection whose accounting row already carries a *different* environment. That is
the 409 in `contracts/metering.md` §1, and it is a constitution I refusal rather
than a data-quality one.

---

## R21 — The refusal has two hops, and the plan gave both of them the same shape

**What the second analysis pass found, in four places that all point one way.**

1. `packages/protocol/src/codes.ts` has held `4008: "quota exhausted"` since
   chapter 1.3. Nothing emits it.
2. `docs/04-srs.md:226`, EIR-WS-06: "Close codes shall be documented and
   distinguish authentication failure, **quota exhaustion**, server shutdown, and
   protocol violation." P2, verified by inspection.
3. `services/gateway/src/session.test.ts:929` is a live test named "STILL emits
   close code 4008 from nowhere", which greps `session.ts`, `limits.ts`,
   `resume.ts` and `main.ts` for `close(400[89])` and asserts no match. Its
   comment says why: "There is no quota yet — **quotas are a later chapter** — and
   reaching for the code because it was declared would collapse the distinction
   this chapter is built on: a rate limit is a smoothing instruction, a quota is a
   commercial one, and they do not deserve the same signal."
4. Chapter 3.8's own comment in `session.ts` explains why *its* refusal is raw
   HTTP: "A refusal needs to say WHEN to come back. `Retry-After` is an HTTP
   header and a close frame has nowhere to put one." And why the 4001 refusal is
   not: it "COMPLETES the handshake in order to close it — because EIR-WS-05 asks
   for a close code on a bad token, and a close code needs a socket to arrive on."

`contracts/metering.md` §2 declined `Retry-After` in its first draft — that
refusal is the whole point of a 402 over a 429 — and then kept the shape whose
only stated justification was `Retry-After`. It also admitted, two paragraphs
later, that a browser sees nothing of a raw HTTP refusal.

**The mistake underneath it: one refusal was written where there are two hops.**

```
  client ──WebSocket──▶ gateway ──HTTP──▶ api
         ◀── ? ────────         ◀── 402 ──
```

The api answers HTTP and a 402 is right there — it is chapter 3.10's refusal,
unchanged, on a route that is already HTTP. The client speaks WebSocket, and the
gateway's job on that hop is to translate, not to forward a status code onto a
socket that has no place for one.

**Decision.** Two shapes, one per hop.

- **api → gateway**: `402` with `code: "quota_exceeded"`, exactly as chapter 3.10
  shaped it, with no `Retry-After`.
- **gateway → client**: complete the handshake, send an `error` frame carrying
  `quota_exceeded` and the full message including the resume date, then
  `close(4008)`.

This is the 4001 path's shape, for the 4001 path's stated reason. It reaches a
browser, where a raw HTTP refusal does not. It puts the resume date somewhere a
close reason string could not hold it. And it emits, for the first time in
nineteen published chapters, a code the protocol declared in 1.3 and named for
exactly this. Counted, not estimated: 27 chapters have published, part-1 runs
`chapter-01` to `chapter-04`, and nineteen of them come after 1.3.

**What it costs, counted.**

- `quota_exceeded` joins `ERROR_CODES` in `codes.ts`. The frame schema types
  `code` as `z.string().min(1)`, so nothing forces this — the registry is a
  documented convention and `codes.test.ts` enforces its uniqueness, which is why
  chapter 3.2 put `wrong_credential_type` there rather than inventing it inline.
- `session.test.ts:929` **inverts**: `session.ts` now emits 4008, and the test
  becomes "emits 4008 for a quota, and still emits 4009 from nowhere". The
  self-check that makes it honest — "a grep that can only pass is not a check" —
  survives, because 4009 is still absent.
- `refuseUpgrade`'s raw-HTTP path is **not** extended. It stays chapter 3.8's,
  for chapter 3.8's refusal.

**What this does not change.** The distinction `session.test.ts` was protecting
holds and is now demonstrated rather than asserted: a rate limit refuses the
handshake with a 429 and a `Retry-After`, a quota completes it and closes with
4008 and a date. Two refusals at one door, and after this chapter the difference
is visible on the wire.

---

## R22 — The email tests drive a sweep both guards miss, and chapter 3.10 shipped it

**Found by the third analysis pass, reading against the build gates.**

`quotas.itest.ts` drives the threshold emails through `createQuotaRelay(...).drainOnce()`, which calls

```
drainQuotaNotifications(db, batchSize, deliver, onError)
```

— a function that claims undelivered rows **across every environment in the
database**. It belongs to a family the project already treats as dangerous — six
of whose members are named in `eslint.config.mjs`, and this one is not:

```
drainOutbox, drainDueDeliveries, drainDisableNotifications,
sweepDisabledEndpoints, outboxDepth, pendingDeliveryDepth
```

with a message explaining that "an integration test shares that database with
every other suite". **`drainQuotaNotifications` is on neither that list nor
`packages/test-harness/src/exempt.ts`**, whose comment says the two "MUST AGREE".
Chapter 3.10 added the function and listed it nowhere.

**Three mechanisms could have caught it and none does.**

- The **lint rule** does not name the function. Even if it did, `quotas.itest.ts`
  reaches the drain through `createQuotaRelay`, and the rule's own comment says
  what it cannot see: "an indirect call — a helper in another file that calls the
  function, imported here under an innocent name".
- The **sentinel trigger** watches five tables and `quota_notifications` is not
  one of them (R5a).
- The **assertion** is `expect(await relay().drainOnce()).toBeGreaterThan(0)`,
  which is true whether it drained this test's row or somebody else's. A count
  compared against zero survives any amount of interference.

**Not "instance thirteen".** The ledger's highest recorded instance is 12
(`specs/031-chapter-3-10/baseline.txt:479`), and nothing here has failed — no test
is red, no fixture has been damaged. What this is: an operation of exactly the
shape those twelve took, in a place neither guard watches, sitting green. Whether
it becomes the thirteenth depends on what another suite leaves in the database,
which is the property the ledger records and not one this pass can assert.

**Decisions, three of them, because the problem has three halves.**

1. **Add `drainQuotaNotifications` to the lint restriction list.** It protects a
   future direct importer and it makes the family complete. It does **not**
   protect this chapter, and saying so matters more than adding it — a rule
   trusted further than it goes is worse than no rule.
2. **Scope this chapter's assertions to this chapter's rows.** SC-009 reads
   Mailpit for "exactly three emails", and Mailpit is shared by the whole lane.
   Filter by the recipient this test created, and assert on that. This is the
   half that actually protects the chapter.
3. **Do not copy 3.10's `toBeGreaterThan(0)`.** Assert the rows this test wrote
   were delivered, by id.

**What this does to R5's prediction.** R5 says no file joins the exemption list,
and that stays true — the guard does not watch these tables, so there is nothing
to be exempt from. The honest form of the claim is narrower than SC-014's
wording: **the guard's silence about quota tables is not evidence that no global
operation happened.** It is evidence that nobody is looking. SC-014 keeps its
exemption-list check and gains that caveat.

---

## R23 — Three coverage ratchets will go red, and the config says so in advance

`vitest.coverage.config.mts` is not a threshold file, it is a record of every
chapter that made this mistake. Three of its notes apply directly.

**`repository.ts` is pinned at branches 90 / functions 100 / lines 99 /
statements 97**, and the config records what happened the last two times a
chapter grew it:

> CHAPTER 3.5 RAISED THESE, and only after earning it. … branches fell from
> 85.91% to 78.22% … The instrument was right and the code was not tested.

> CHAPTER 3.6 RAISED THEM AGAIN … Measured mid-chapter with the failure run
> written and its tests not yet, this file read 96.46 statements and 88.80
> branches — the instrument saying "you added five operations and tested none of
> them" in the only language it has.

This chapter adds `creditConnectionMinutes` and extracts two functions. The tests
belong in Phase 4, beside the code, not in Phase 8 beside the discovery.

**Pure decision files get pinned at 100, by convention with a written reason
each time**: 3.6 pinned `disable.ts` and `analytics.ts`, 3.8 pinned `bucket.ts`,
`policy.ts` and `fallback.ts` — "they hold no clock, no store and no framework,
so a branch they miss is a case nobody thought of rather than a case nobody could
reach." `quotas/credit.ts` and the pure half of `gateway/src/meter.ts` are that
shape. Entries go in with the chapter, not after it.

**And the trap that is specific to this chapter.** `meter.ts`'s most important
tests spawn a gateway child process, and the config states plainly that a child
process's coverage "is not attributable here". That is exactly how chapter 3.5
lost 7.69 points of branch coverage on `repository.ts`. So the meter's *logic* is
covered by in-process unit tests on a driven clock, and the spawned tests are kept
for the one thing only a process can show: what a signal does.

`**/main.ts` is excluded from coverage entirely. That makes it the right home for
R11's signal handler and the wrong home for anything the handler calls.

---

## R24 — Which lane runs the socket tests, and why not e2e

**The sixth analysis pass found this undecided, with a precedent pointing the
wrong way.** Chapter 3.10 put its equivalent test — a send refused by the cap,
and the socket still open sixty seconds later — in `packages/e2e/src/`, and gave
a reason:

> that lane, because the test needs a live api child to do the refusing, **which
> the gateway's own lane does not spawn**

**That reason is false on the current code.** `services/gateway/src/session.itest.ts:116`
spawns `node dist/main.js`, waits on `/healthz`, and hands the suite a real api
URL. `limits.itest.ts:124` does the same. The gateway's lane has spawned a live
api since chapter 3.2.

**Decision: the gateway's integration lane, and not e2e.** The argument is not
the precedent's and it is stronger than it.

**e2e cannot drive a clock.** There, the gateway is a child process; here,
`attachSessions` is called in-process and already takes `pingIntervalMs` as a
parameter, which is where `meterIntervalMs` goes. Every timing assertion in this
chapter — three minute boundaries, a socket that lives inside one interval, ten
intervals after a kill — is stated in calendar minutes. In e2e each of them would
have to wait in real time, and the quickstart's own rule is that nothing in this
suite sleeps for a minute.

**And the gateway lane can seed Postgres directly.** e2e may not import `pg`,
which is why chapter 3.10 had to add `harness.setQuota` to reach the caps at all.
The gateway lane's `seeder` writes rows, so setting a connection-minutes cap costs
nothing new.

**What follows.**

- `packages/e2e/src/harness.ts` is **not** touched. It carries 6 chapter fences
  and a `post-series.md` entry, and would have been a 22nd file in R16's table.
- The tests split by what they actually exercise. Anything involving a socket goes
  to `services/gateway/src/session.itest.ts`; anything about the meter's lifecycle
  goes to `meter.itest.ts`; **T051 goes to the api's lane**, because a REST send
  and a history read while capped involve no socket at all and putting them in the
  gateway's suite would spawn a gateway to test the api.
- The two tests that need a gateway **process** rather than an in-process gateway
  — the SIGTERM flush and the SIGKILL crash — are the exception, and they are the
  two that deliberately do not drive a clock: they measure what a signal does.
  `meter.itest.ts` therefore runs two children, an api and a gateway, and the
  gateway child's `RELAY_API_URL` points at the api child's ephemeral port.
