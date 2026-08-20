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
