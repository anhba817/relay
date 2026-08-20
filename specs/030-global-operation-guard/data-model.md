# Data model: the sentinel and its guard

Nothing here is product data. Every row and every object below exists only in a
test database, is created by the integration lane, and is invisible to a
production migration. That separation is the mitigation for the constitution IV
concern the plan records.

---

## The sentinel environment — one per test file

**Not one shared sentinel.** An earlier draft had a single fixed environment, and
research R12 found that incompatible with the per-file planting research R2
requires: files execute in parallel, so one file's `beforeAll` deletes and
re-inserts rows another file is mid-test against.

Each file gets its own, derived from the file's path so it is stable across runs
and unique across files:

| Row | Purpose |
|---|---|
| organisation | the notification path resolves recipients from here |
| human | **no email address** — see below |
| membership | makes the organisation resolvable and unaddressable |
| application | the environment needs a parent |
| environment | the id the trigger tests for membership |
| webhook endpoint | bait for the sweep |

Every row carries the name `__sentinel__:<file>`, so a developer reading a failure
knows immediately both that the rows are not theirs and which file owns them.

### The registry the trigger needs

With one sentinel the trigger could compare against a literal uuid. With one per
file it cannot, so a small table holds the ids:

```
__sentinel_environments (environment_id uuid primary key, owner text not null)
```

The trigger tests membership in it. That is one extra lookup per guarded row,
against a table holding as many rows as there are test files — seventeen today.
`owner` is the file path, and it is what lets the refusal say whose rows were
taken.

**The human has no email address, and that is load-bearing.** Research R4 found
that 200 addressable bait notifications turned one suite's drain into 200 SMTP
sends and a ten-second timeout. An unaddressable organisation makes each bait
notification cost one log line instead — the branch FR-WHK-07's unaddressable
case already covers.

## The bait

Four kinds, one per global operation the codebase performs. Sizes are **derived
from the exported batch constants**, never written as literals, so a raised
default raises the bait with it (research R7).

| Bait | Table | Predicate it satisfies | Size |
|---|---|---|---|
| a sweepable endpoint | `webhook_endpoints` | `enabled`, open failure run older than the disablement cutoff, attempts past the floor | 1 |
| due deliveries | `webhook_deliveries` | `state = 'pending'`, `next_attempt_at` in the past | `2 × max(BATCH_SIZE)` |
| unpublished events | `outbox` | `published_at IS NULL`, subject `__sentinel__.bait` | `2 × max(BATCH_SIZE)` |
| undelivered notifications | `webhook_disable_notifications` | `delivered_at IS NULL` | `2 × max(BATCH_SIZE)` |

`max(BATCH_SIZE)` is 100 today, in `outbox/relay.ts` and in
`sweepDisabledEndpoints`. Doubling it means a caller who omits a bound reaches
bait before reaching its own rows, which is the whole mechanism.

### Lifecycle

Planted **per file**, in a `beforeAll`, because research R2 measured three of the
four baits eaten in a single lane run — a one-shot `globalSetup` seeder protects
whichever suite runs first and nothing after it.

Planting is idempotent by deleting this file's sentinel rows and re-inserting
them, rather than by `ON CONFLICT`. The environment id makes the delete exact, and
the seeder cannot itself become the accumulation it exists to simulate (FR-003).

**The seeder gets its own connection, and that is not a detail.** Deleting a
sentinel row is exactly what the trigger forbids, so the seeder needs the
exemption — and a connection carrying the exemption must never reach a test, or
that test runs unguarded. So planting uses a dedicated `pg.Client`, created by the
setup file with the exemption in its options and closed before the suite's first
test. It never enters the suite's pool (FR-024, research R12).

## The guard

A `BEFORE UPDATE OR DELETE` row trigger on each table carrying `environment_id`,
fired only when the row belongs to the sentinel:

| Object | Kind | Responsibility |
|---|---|---|
| `__sentinel_guard()` | PL/pgSQL function | raise unless the connection is exempt |
| `__sentinel_guard_<table>` | row trigger | one per guarded table, firing when the row's environment is in `__sentinel_environments` |

**Installation migrates first.** A trigger needs its table, and `globalSetup` runs
before every suite — including the six that call `migrate(pool)` in their own
`beforeAll`. On an unmigrated database the install would fail before a test ran.
`migrate()` is idempotent, so calling it from `global-setup.ts` costs nothing and
removes the lane's dependency on somebody else having migrated first.

Guarded tables — those where a global operation can reach across tenants:
`webhook_endpoints`, `webhook_deliveries`, `webhook_disable_notifications`,
`channels`, `users`. Not `outbox` or `messages`: the outbox carries no
`environment_id` because it is platform bookkeeping, and messages are scoped
through `channel_id`. The outbox bait is therefore protected by the reader
mechanism only, which is a stated gap rather than an oversight.

### Exemption

A **connection option**, not a statement:

```
DATABASE_URL=…?options=-c%20relay.allow_global%3Don
```

Set by the lane's setup file, which rewrites `process.env.DATABASE_URL` for its own
worker when the file under test appears on the exempt list, and never otherwise.

**At the setup file's module scope, never in a hook**, and that is measured rather
than preferred. A setup file's top-level code runs before the test file is
imported — `setup-toplevel; testfile-module;` — and four suites create their pool
at module scope: `db/history-drift.itest.ts`, `db/repository.itest.ts`,
`messages/history.itest.ts`, `messages/idempotency.itest.ts`. An exemption written
in `beforeAll` would arrive after their pool already exists. None of the six exempt
suites is written that way today, so nothing is broken by it — which is the same
kind of luck the whole feature is about (FR-026).

Bait planting stays in `beforeAll`, because it is asynchronous database work.

**Not `SET relay.allow_global = 'on'` through the pool**, which is what an earlier
draft specified. A pool rotates connections, so a statement lands on one of them.
Measured across five checkouts from a pool of three: `["on", null, null, "on",
null]`. An exempt suite would have failed intermittently, in a way indistinguishable
from the flakiness this feature exists to remove (research R10).

The connection string carries it rather than the pool's config object because that
needs no change to `createPool()` — a product function every service calls.
`current_setting('relay.allow_global', true)` returns null in a connection that
never had the option, so the default is refusal.

## The exempt list

A list of paths, in one file, each with its reason beside it. A pattern would
silently absorb the next file added (spec FR-015), which is the failure mode this
whole feature is about.

The six that need it, measured rather than guessed (research R5):

| File | Why it drives a global operation |
|---|---|
| `outbox/outbox.itest.ts` | drives the relay, whose subject is a global drain |
| `webhooks/deliveries.itest.ts` | drives the sweep and the due-delivery drain |
| `webhooks/test-event.itest.ts` | drives the delivery relay |
| `webhooks/attempts.itest.ts` | drives the delivery relay |
| `notifications/notifications.itest.ts` | drives the notification relay |
| `dispatcher/dispatcher.itest.ts` | drives the delivery drain from the dispatcher |

An exempt file is not excused from correctness. It is excused from the trigger,
and it still has to bound its own batches — which is what instances 1, 2, 3 and 5
failed to do while being, in this sense, legitimate.

### Which lanes carry which mechanism

The trigger is database state and outlives the lane that installed it, so every
lane pointed at that database meets it. Bait is not, and should not spread
(research R11):

| Lane | Exemption handling | Bait |
|---|---|---|
| api integration | yes | yes |
| dispatcher integration | yes | yes |
| gateway integration | yes | no |
| e2e | yes | no |
| **coverage** | **yes** | no |

The coverage lane is the one an earlier draft missed. `vitest.coverage.config.mts`
runs every `*.itest.ts` in one process with no `setupFiles` and no `globalSetup`, so
it would have met the trigger with no way to answer it and failed all six exempt
suites.

## Refusal

Not a stored entity. The guard's output is a Postgres error raised in the
offending transaction, and its shape is a contract — see
[contracts/guard.md](./contracts/guard.md).

*This section was headed **Verdict** until the seventh analysis pass — the name the
checksum design gave to "whether the sentinel changed during a run". Nothing
returns a verdict now, because a non-exempt statement never completes.*
