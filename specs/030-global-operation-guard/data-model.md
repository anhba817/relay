# Data model: the sentinel and its guard

Nothing here is product data. Every row and every object below exists only in a
test database, is created by the integration lane, and is invisible to a
production migration. That separation is the mitigation for the constitution IV
concern the plan records.

---

## The sentinel environment

One environment, fixed and recognisable, owned by the lane rather than by any
test. Its identifiers are literal UUIDs rather than generated ones so that a
failure message can be matched against this document by eye.

| Row | Identifier | Purpose |
|---|---|---|
| organisation | `…0001` | the notification path resolves recipients from here |
| human | `…0002` | **no email address** — see below |
| membership | (`…0001`, `…0002`) | makes the organisation resolvable and unaddressable |
| application | `…0003` | the environment needs a parent |
| environment | `…0004` | the value the trigger matches on |
| webhook endpoint | `…0005` | bait for the sweep |

All six use the reserved prefix `00000000-0000-4000-8000-0000000000NN` and the
name `__sentinel__`, so a developer reading a failure knows immediately that the
rows are not theirs.

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

Planting is idempotent by deleting the sentinel's rows and re-inserting them,
rather than by `ON CONFLICT`. The sentinel is identifiable by `environment_id`,
so the delete is exact, and the seeder cannot itself become the accumulation it
exists to simulate (spec FR-003).

## The guard

A `BEFORE UPDATE OR DELETE` row trigger on each table carrying `environment_id`,
fired only when the row belongs to the sentinel:

| Object | Kind | Responsibility |
|---|---|---|
| `__sentinel_guard()` | PL/pgSQL function | raise unless the session is exempt |
| `__sentinel_guard_<table>` | row trigger | one per guarded table, `WHEN (OLD.environment_id = …0004)` |

Guarded tables — those where a global operation can reach across tenants:
`webhook_endpoints`, `webhook_deliveries`, `webhook_disable_notifications`,
`channels`, `users`. Not `outbox` or `messages`: the outbox carries no
`environment_id` because it is platform bookkeeping, and messages are scoped
through `channel_id`. The outbox bait is therefore protected by the reader
mechanism only, which is a stated gap rather than an oversight.

### Exemption

A session-level setting, not a row and not a flag in code:

```
SET relay.allow_global = 'on'
```

Set by the lane's setup hook when the file under test appears on the exempt list,
and never otherwise. `current_setting('relay.allow_global', true)` returns null
in a session that has not set it, so the default is refusal.

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

## Verdict

Not a stored entity. The guard's output is a Postgres error raised in the
offending transaction, and its shape is a contract — see
[contracts/guard.md](./contracts/guard.md).
