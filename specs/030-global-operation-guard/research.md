# Research: the fault that only shows up in company

Every finding below was measured, not reasoned about. Two of them changed the
design the spec assumed.

---

## R1 — The developer's database is already adversarial. CI is not.

Measured on the machine that shipped chapters 3.5 through 3.9:

```
outbox unpublished           190
deliveries due             8,364
notifications undelivered     14
endpoints sweepable           35
environments total        17,542
```

The lane passes here. It also passes on a database created and migrated seconds
earlier. Both are true because chapters 3.7 and 3.8 fixed all five reader-shape
instances — so neither condition is currently detecting anything.

That matters for what this feature is *for*. A long-lived developer database
supplies the adversarial condition by accident; a fresh clone and CI do not. So a
**new** reader-shape fault written today passes on CI and on a colleague's fresh
checkout, and fails months later on somebody's aged laptop. The bait's job is to
make fresh behave like aged, which is the reverse of the intuition that a clean
database is the safer place to test.

## R2 — The bait is eaten in a single lane run

Planted 200 unpublished outbox rows, 200 due deliveries, 200 undelivered
notifications and one sweepable endpoint on a fresh database, then ran the api
integration lane once:

```
outbox bait unpublished                0     (200 published)
sentinel notifications undelivered     0     (201 delivered)
sentinel endpoint still enabled        0     (swept)
sentinel deliveries still due        200     (survived)
```

Three of the four baits were gone after one pass. Only the deliveries survived,
and only because most suites run with `RELAY_DELIVERY_RELAY=off`.

**A one-shot `globalSetup` seeder therefore protects whichever suite runs first
and nothing after it.** Planting has to happen per file. This was not in the
spec's assumptions and it is the reason `outbox.itest.ts` failed in the lane and
passed when re-run alone — by then there was no bait left to fail against.

## R3 — Fresh plus bait broke two tests of 177

| Suite | Test | Shape |
|---|---|---|
| `outbox.itest.ts` | invariant 7: the relay publishes pending rows, marks them, and does not republish | reader — the relay's default batch of 100 never reaches this test's own rows |
| `notifications.itest.ts` | sends what the organisation needs | not a reader fault at all — see R4 |

Two, not twenty. The reader shape is better defended than expected, because 3.7
and 3.8 fixed it five times. What the bait protects is the *next* one.

## R4 — The bait changed a suite's workload, not just its arithmetic

`notifications.itest.ts` timed out at 10 seconds. Its relay drains with
`batchSize: 10_000`, so the 200 bait notifications became 200 SMTP sends to the
sentinel address before the test's own row was reached.

That is a different failure from the one the bait is designed to cause. Bait has
to be **cheap to process as well as visible**: the sentinel organisation should
have no addressable member, so each bait notification costs one log line and no
SMTP round trip. Which consumes the bait — looping straight back to R2.

## R5 — Legitimate global operations trip the guard immediately

The sentinel endpoint was disabled by an ordinary lane run. No deliberate fault,
no mutation written for this feature — six suites drive global drains and sweeps
on purpose:

```
services/api/src/outbox/outbox.itest.ts
services/api/src/webhooks/deliveries.itest.ts
services/api/src/webhooks/test-event.itest.ts
services/api/src/webhooks/attempts.itest.ts
services/api/src/notifications/notifications.itest.ts
services/dispatcher/src/dispatcher.itest.ts
```

So the exemption list is a **precondition, not a refinement**. A guard shipped
without it fails the lane on its first run for the right reason and the wrong
suite.

## R6 — THE DESIGN CHANGED: a database trigger attributes; a checksum cannot

The spec assumed a before/after comparison of the sentinel rows around each test,
and conceded in its assumptions that attribution would need serial execution
because integration files run in parallel — a test comparing the sentinel around
itself can observe a mutation another file performed and blame itself.

Combined with R5, that concession is fatal rather than awkward: legitimate global
sweeps happen constantly, so a run-scoped checksum would fire on almost every run
and a test-scoped one would blame bystanders.

A trigger does not have the problem, because it raises **inside the transaction
that did the damage**:

```
NON-EXEMPT session:
  ERROR:  global-operation guard: this statement modified sentinel row
          public.webhook_endpoints (id 00000000-…-000000000005),
          which belongs to no test
  CONTEXT:  PL/pgSQL function __sentinel_guard() line 4 at RAISE

EXEMPT session (SET relay.allow_global = 'on'):
  UPDATE 1
```

Verified against the real schema. The properties this buys:

- **Attribution is exact.** The error surfaces in the offending test's own stack,
  under parallel execution, with no serial diagnosis mode.
- **It catches raw SQL.** A lint rule and a wrapped import both miss a global
  `UPDATE` written by hand; the database does not.
- **Exemption is per session**, set by the lane's setup hook from an auditable
  list of files.
- **It makes the bait durable.** A non-exempt suite cannot eat what it cannot
  modify, which softens R2: re-planting is only needed after an exempt suite runs.

The trigger belongs to the test lane, not to the product. It is created by the
lane's setup against a test database, never by a product migration — otherwise
Relay ships a trigger whose only purpose is to break its own test suite.

**Decision**: replace the checksum guard with a trigger. The spec's FR-006 to
FR-011 keep their meaning; the mechanism named in its assumptions is wrong and is
superseded here.

**Alternatives rejected.** Wrapping the repository's exports in the setup hook
(catches indirect calls, misses raw SQL, and generic path resolution across test
files is awkward). Making the product functions refuse to run under a test flag
(puts test logic in shipped code — constitution VII). Per-suite databases
(chapter 2.1 chose one deliberately, and all seven findings are real
production-shaped problems isolation would hide).

## R7 — The bait's sizes must come from the constants

The largest default batch in the codebase is 100, in two places:

```
services/api/src/outbox/relay.ts:19          BATCH_SIZE = 100
services/api/src/webhooks/delivery-relay.ts  BATCH_SIZE = 50
services/api/src/notifications/…-relay.ts    BATCH_SIZE = 20
services/api/src/db/repository.ts:1142       limit = 100   ← the last default
```

A literal in the seeder goes stale the first time one of those rises. The seeder
derives its sizes from the exported constants, so a raised default raises the
bait with it.

## R8 — `sweepDisabledEndpoints` is the only remaining default

`drainOutbox`, `drainDueDeliveries` and `drainDisableNotifications` all require a
limit; chapter 3.8's T044 established the rule for the newest of them. The sweep
kept its `limit = 100` and is instance 6's proximate cause — not because 100 was
too small, but because omitting the argument let the author skip the question
"of whose rows?" entirely.

Worth stating plainly: **removing the default would not have prevented instance
6.** `sweepDisabledEndpoints(db, 10_000)` is worse, not better. The required
argument is a prompt to think, not a control. The trigger is the control.

## R9 — The lint restriction has an existing shape to copy

`eslint.config.mjs` already restricts `pg`, `drizzle-orm` and `ioredis` by module
path with an ignores list. `no-restricted-imports` also accepts `importNames`, so
the same block can name the global admin functions without banning the repository
module wholesale. It catches the import line — where the decision is actually
made — and misses indirect calls and raw SQL, which is why it is the third
defence and not the first.


---

# Findings from the first analysis pass

R1 to R9 were written before `tasks.md` existed. The pass that followed it opened
the test harness's runtime mechanics — pooling, parallelism, and the other lanes
sharing the database — which none of R1 to R9 had looked at. It found three
CRITICAL problems in the design R6 declared solved.

## R10 — The trigger works in one session and not in a pool

R6 verified the trigger in `psql`: one connection, one session, one `SET`. That is
the one condition the test lane never provides.

`createPool()` returns a bare `pg.Pool`, and a pool rotates connections. Measured
across five checkouts from a pool of three:

```
plain pool, after one SET on one connection: [null,null,null,null,null]
plain pool, after SET via pool.query:        ["on",null,null,"on",null]
connection-string options, every conn:       ["on","on","on","on","on"]
config-object options, every conn:           ["on","on","on","on","on"]
```

The second line is the bug. `SET relay.allow_global = 'on'` issued through
`pool.query()` lands on whichever connection the pool hands out, so two of five
checkouts carried the exemption and three did not. An exempt suite would fail
intermittently, in a way that looks exactly like the flakiness this feature exists
to remove.

**Decision**: set it as a connection option, so every connection the pool opens
carries it. `options` is honoured both in the connection string and in the config
object; the connection string wins because it needs **no product change** — the
setup hook rewrites `process.env.DATABASE_URL` for its own worker before the suite
calls `createPool()`, and `createPool()` reads that variable.

**Alternative rejected**: adding an `options` parameter to `createPool()`. It is a
small passthrough rather than test logic, so it would not violate the
no-test-logic-in-product rule — but it changes a function every service calls in
order to serve a lane, and the environment variable already carries the address.

## R11 — The trigger is database state; the exemption is process state

They have different lifetimes, and the mismatch is the second CRITICAL.

The trigger, once installed, belongs to the database. Every lane pointed at that
database meets it. The exemption is supplied by a vitest hook, and only two lanes
were given one: the api's and the dispatcher's integration configs.

The lanes that share the database and were not given the hook:

| Lane | Config | Touches the database |
|---|---|---|
| coverage | `vitest.coverage.config.mts` | **every `*.itest.ts` in one process**, no `setupFiles`, no `globalSetup` |
| gateway integration | `services/gateway/vitest.integration.config.mts` | `session.itest.ts`, `limits.itest.ts` |
| e2e | `packages/e2e/vitest.integration.config.mts` | `harness.ts`, `webhooks.itest.ts` |

The coverage lane is the sharp one: it runs the six exempt suites with no way to
exempt them, so `pnpm coverage` would fail for the right reason and the wrong
cause.

**Decision**: separate the two concerns the design had fused.

- **Exemption handling goes to every lane** that touches the database — five
  configs, not two. Uniform, so no lane meets a trigger it cannot answer.
- **Bait goes only to the api and dispatcher lanes**, where the reader-shape
  faults live. Planting it in the gateway and e2e lanes would change their
  workload for no return, which is R4's lesson.

The gateway and e2e suites would pass today without any exemption, because none of
them performs a global operation. That is luck rather than design, and luck is
what this feature is about.

## R12 — The seeder has to do the thing the guard forbids

Planting was specified as "delete the sentinel's rows, then re-insert". `DELETE` on
a guarded table for a sentinel row fires the trigger. So the seeder needs the
exemption — and if it takes it on a connection the suite's pool later hands to a
test, the test inherits it and the guard is off for that test. Circular.

Two changes resolve it, and the second also fixes a race the design had not seen.

**The seeder gets its own connection.** A dedicated `pg.Client` created by the
setup hook with the exemption in its options, used to plant, then closed. It never
enters the suite's pool, so nothing a test does can inherit it.

**The sentinel becomes per file, not shared.** Files run in parallel — no
integration config overrides `fileParallelism` — so a shared sentinel meant file
A's `beforeAll` deleting and re-inserting rows while file B was mid-test relying on
them. R2's per-file planting requirement and a shared sentinel are incompatible,
and the plan had both.

Per-file sentinels also change the trigger's shape: its `WHEN` clause can no longer
compare against one literal uuid. A small registry table — `__sentinel_environments`
— holds the ids, and the trigger tests membership. One extra lookup per guarded row,
against a table with as many rows as there are test files.

## R13 — A relay swallows the refusal, so the guard is silent where the stakes are highest

`contracts/guard.md` claims the refusal "surfaces in the test that performed the
mutation". That holds for a test. It does not hold for a relay:

```
services/api/src/webhooks/delivery-relay.ts:197   logger.log("error", "deliveries.drain_failed", …)
services/api/src/notifications/notification-relay.ts:148  logger.log("error", "notifications.drain_failed", …)
```

Both catch and log. A relay is the main global operation in the system, so a
trigger firing inside one produces a log line in a background loop and a green
lane.

Today every suite that spawns an api child sets all four relay flags off —
verified in `harness.ts` and `dispatcher.itest.ts`. So the exposure is nil and the
mitigation is a convention repeated in seven files rather than a property.

**Decision**: two changes, neither of which tries to make a relay throw.

- The contract's claim is narrowed to say what is true: the refusal surfaces in the
  statement's own transaction, which for a test is that test and for a background
  loop is a log line.
- The setup hook asserts that a **non-exempt** file has the relay flags off, and
  fails at startup if not. That turns "we happen to switch them off" into
  something checked, and it is four lines.


---

# Findings from the second analysis pass

The first pass read the harness's *runtime*. This one read the harness's *loading
order*, the workspace layout, and — for the first time in this session — the prose
guide every skill invocation had been instructing us to apply.

## R14 — Where the exemption is written decides whether it works

`setupFiles` gives the test path at **top level**, not only inside a hook, and the
setup file's top-level code runs before the test file is imported. Measured with a
probe:

```
PROBE toplevel testPath  = …/src/__probe/probe.itest.ts
PROBE order so far       = setup-toplevel;testfile-module;
PROBE env visible at test-file module scope = yes
```

That is good news for the per-file sentinel — the path is available where it is
needed — and it comes with a constraint the plan had not stated. **Four suites
create their database pool at module scope**:

```
services/api/src/db/history-drift.itest.ts
services/api/src/db/repository.itest.ts
services/api/src/messages/history.itest.ts
services/api/src/messages/idempotency.itest.ts
```

An exemption written in `beforeAll` arrives after their pool already exists. None
of the six exempt suites is written that way today, so nothing is broken — the same
kind of luck this feature exists to remove. FR-026 states it; the exemption is
applied at module scope and bait planting stays in `beforeAll`, where async
database work belongs.

## R15 — No suite wipes a table, which removes a whole class of worry

Searched every `*.itest.ts` for `TRUNCATE` and for broad `DELETE FROM` against the
guarded tables. **Zero hits.** Had one existed, it would have taken every sentinel's
bait on every run and made the guard useless without anybody writing a fault.

Worth recording as a negative result: it is the kind of thing that would have been
expensive to discover during implementation and cost one grep to rule out.

## R16 — The harness outgrew the service it was going to live in

`services/api/src/testing/` was the plan's home for it. Then the exemption had to
reach every lane, and five configs across four packages ended up importing it —
including the gateway's, which would have meant one service's test lane reaching
into another service's `src/`.

It moves to `packages/test-harness/`. `packages/*` is already a workspace glob, and
`config`, `protocol`, `service-kit` and `e2e` establish that shared code lives
there. The package declares its own `pg` — only `services/api` does today — and it
plants through raw SQL, so it imports nothing from any service.

## R17 — The prose guide had never been opened

Every `/speckit-*` invocation in this session began by instructing us to apply
`.claude/skills/humanizer/PROSE-IN-GENERATED-DOCS.md` before writing prose. It was
read for the first time during this pass, after roughly fourteen thousand words of
specification had been written against it from memory.

Audited afterwards, the documents come out clean on its ranked list: **zero** hits
across all seven files for its twenty-two promotional and AI-vocabulary terms, one
superficial `-ing` tail, and no generic positive conclusions. The four
negative-parallelism hits are all real contrasts.

The exception is the one the guide classes as a *defect* rather than a style
choice. In normative text it asks for one term per concept, and the requirement
block used three for the planted rows — `bait` twice, `planted rows` once,
`sentinel environment's rows` once. Now `bait`, five times, everywhere.

What is worth keeping is not the audit result. It is that a document can be written
correctly against a guide nobody read, and still fail the one rule that guide calls
a defect — because that rule is the one a careful writer would not think to apply
to themselves.
