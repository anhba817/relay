# Quickstart: verifying the global-operation guard

Exit codes, not greps over output. Every step below was rehearsed during research
except where marked.

**A note on where to run it.** A long-lived developer database already supplies
the adversarial condition by accident — the machine that shipped chapter 3.9 held
8,364 due deliveries and 17,542 environments (research R1). So the steps that
matter are the ones on a **fresh** database, which is what CI and a new clone
actually run. Several steps therefore begin by creating one.

---

## V0 — Baseline, before anything changes

```bash
cd relay-platform
docker compose up -d --wait postgres redis nats clickhouse mailpit
pnpm build
pnpm turbo run test:integration --concurrency=1
```

Expected: green, 223 tests. **Record the wall-clock time — this run is the baseline
SC-004 measures against.** Chapter 3.9's `3m15s` is indicative only: it was
measured at 213 integration tests, and the chapter finished on 223 without the
final run being timed.

## V1 — The fresh database currently proves nothing

```bash
psql "$DATABASE_URL" -c "CREATE DATABASE relay_fresh"
DATABASE_URL=…/relay_fresh pnpm --filter @relay/api test:integration
```

Expected: **green, 177 tests**. Measured during research. This is the step that
shows why the feature is needed rather than that it works: a fresh database is the
*easy* condition, and a new reader-shape fault written today would pass here and
on CI.

## V2 — The trigger refuses, and names the culprit

With the trigger installed and no bait consumed:

```bash
psql "$DATABASE_URL_FRESH" -c \
  "UPDATE webhook_endpoints SET enabled=false WHERE id='00000000-0000-4000-8000-000000000005'"
```

Expected:

```
ERROR:  global-operation guard: this statement modified sentinel row
        public.webhook_endpoints (id 00000000-0000-4000-8000-000000000005),
        which belongs to no test
```

Then the same statement in an exempt connection:

```bash
psql "$DATABASE_URL_FRESH?options=-c%20relay.allow_global%3Don" -c \
  "UPDATE webhook_endpoints SET enabled=false WHERE id='…0005'"
```

Expected: `UPDATE 1`. Both halves verified during research (R6).

**And the half R6 did not check** — that the exemption survives a connection pool:

```bash
node -e '…open five checkouts from a pool of three, read current_setting…'
```

Expected: `["on","on","on","on","on"]`. A `SET` issued through `pool.query()`
instead returns `["on",null,null,"on",null]`, which is the measurement that
replaced the mechanism (research R10). Run this before trusting V5.

## V3 — Instance 6 fails alone

The one this project caused. Reintroduce it: change
`notifications.itest.ts`'s `disable()` helper back to `sweepDisabledEndpoints(db)`
and run **only that file**, on a fresh database.

```bash
pnpm --filter @relay/api test:integration src/notifications
```

Expected: fails, with the trigger's message, in that test's own stack — with no
second suite present. Today it passes.

Revert with `git checkout --` and confirm the file is byte-identical by `md5sum`.
**Commit before every reintroduction, not just before the battery**: chapter 3.9
lost a fix to exactly this revert step, in the chapter that warned about it.

## V4 — Instances 1 to 5 fail alone

Each is a reader-shape fault, so each needs the bait rather than the trigger.
Reintroduce one at a time, run only its own file on a fresh database, and expect a
failure:

| # | File | Reintroduce |
|---|---|---|
| 1 | `deliveries.itest.ts` | drop the `10_000` from the sweep call |
| 2 | `deliveries.itest.ts` | restore the drain that held a lock |
| 3 | `consumer.itest.ts` | restore the fixed catch-up budget |
| 4 | `signup.itest.ts` | restore `count(*) FROM organisations` before and after |
| 5 | `dispatcher.itest.ts` | drop the `batchSize: 10_000` |

Expected: five failures, five reverts, five byte-identical files.

## V5 — A legitimate global operation still passes

The six exempt suites drive global drains on purpose (research R5), and the
sentinel endpoint was disabled by an ordinary lane run before any exemption
existed.

```bash
pnpm --filter @relay/api test:integration src/outbox src/webhooks
pnpm --filter @relay/dispatcher test:integration
```

Expected: green. Each exemption is discoverable by reading
`packages/test-harness/src/exempt.ts`, which carries the reason beside the path.

**Then the lane an earlier draft forgot**, which shares the database and had no
hook at all:

```bash
pnpm coverage
```

Expected: green. The trigger is database state, so the coverage lane meets it
whether or not it installed it — and it runs all six exempt suites in one process
(research R11).

## V6 — The bait survives a lane run

Research R2 measured three of the four baits eaten in a single pass. With
per-file planting:

```bash
DATABASE_URL=…/relay_fresh pnpm --filter @relay/api test:integration
psql "$DATABASE_URL_FRESH" -tAc "
SELECT s.owner,
       count(*) FILTER (WHERE d.state = 'pending')            AS due_deliveries,
       count(*) FILTER (WHERE n.delivered_at IS NULL)         AS undelivered,
       count(DISTINCT e.id)                                   AS endpoints
  FROM __sentinel_environments s
  LEFT JOIN webhook_deliveries d              ON d.environment_id = s.environment_id
  LEFT JOIN webhook_disable_notifications n   ON n.environment_id = s.environment_id
  LEFT JOIN webhook_endpoints e               ON e.environment_id = s.environment_id
 GROUP BY s.owner ORDER BY s.owner"
```

Expected: **one row per test file**, each showing its bait at the planted size and
exactly one endpoint. `__sentinel_environments` itself holds one row per file, not
one per run. A count larger than the planted size means planting is not idempotent
(FR-003) — the seeder becoming the accumulation it exists to simulate.

The query is inlined rather than kept in a file, because an earlier draft of this
step pointed at `bait-count.sql`, which nothing created.

## V7 — The call site refuses

```bash
# the required limit
pnpm --filter @relay/api exec tsc --noEmit    # after removing the caller's argument
# the lint rule
pnpm lint
```

Expected: the compiler rejects `sweepDisabledEndpoints(db)`, and lint rejects a
global-admin import added to any `*.itest.ts` not on the exempt list — with a
message naming the alternative.

## V8 — Nothing was lost

```bash
pnpm turbo run test --force
pnpm turbo run test:integration --concurrency=1 --force
pnpm coverage
```

Expected: unit 242, integration 223 or more, coverage no lower than 89.50%
statements and 82.73% branches. `packages/test-harness/src/**` is excluded from
coverage, for the reason `main.ts` and `*.module.ts` are.

## V9 — Twenty runs, zero false positives

```bash
for i in $(seq 1 20); do pnpm turbo run test:integration --concurrency=1 --force || break; done
```

Expected: twenty green runs (SC-003). This is the step that says the guard does
not cry wolf, and it is the one most likely to be skipped for taking twenty times
three minutes. Chapter 3.7 spent four attempts and roughly four hours getting
twenty consecutive clean runs and found four faults doing it.

## V10 — The lane is no slower

Compare against V0's recorded time. Expected: under 10 seconds of growth
(SC-004). Per-file planting is roughly 600 inserts times seventeen files.

## V11 — The paperwork

```bash
cd relay-tutorial && pnpm check:fences && pnpm check:docs && pnpm build
```

Expected: the chain replays; every fence this feature produces is in
`fences/post-series.md` and none in a chapter, because this work teaches none.
`docs/07-tutorial-plan.md` already records it under "Work that publishes no
chapter".
