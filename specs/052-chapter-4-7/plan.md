# Implementation Plan: chapter 4.7, "the job that checks the meter"

**Branch**: `052-chapter-4-7` · **Date**: 2026-09-15 · **Spec**: [spec.md](./spec.md)

**Read [research.md](./research.md) first.** Eight of its ten items were run against the lane
and two changed what the chapter is — including one that changed the job's shape.

## Summary

Movement IV's second chapter. `docs/12` row 8: *"FR-ANL-06's reconciliation job, built to be
callable in isolation (§2.3)."*

The clause asks for metered totals to agree with operational counts within 0.1%. **Three
things stand in the way, and none of them is the reconciler's to fix:**

    message_events has no producer      analytical 0 vs operational 9,624      100%
    uniq is approximate above ~65,000 distinct                                 0.51%
    the TTL boundary, at any cardinality                                       0.49%

And one thing the clause simply does not say: **which number is *"counts derived from
operational data"***. There are two, `messages` at 9,650 and `usage_periods.messages_sent` at
9,624, and FR-ANL-06 chooses neither.

**That ambiguity reshaped the job, and its measured divergence did not survive contact with
analysis pass 1.** The 0.2694% is a fixture artifact — raw-SQL writers and a sentinel cleanup
that deletes counter rows, with all 31 disagreeing tenants belonging to test applications and
none to anything else. A first draft of this plan carried it as a fourth obstacle. **What
survives is the shape it forced**: the aggregate reads 0.2694% and nobody looks, while the
per-tenant split shows one tenant wrong by 100% — so the job compares one tenant at a time and
never aggregates before a verdict. That decision is what found the fixtures.

So the chapter builds the job, runs it, and has it correctly alert on its own platform — and
publishes why a green number here would have been the most misleading artifact in the series.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22; ClickHouse SQL 25.3; Postgres 16
**Primary Dependencies**: none added
**Storage**: reads only — `relay_analytics.daily_usage_billing`, Postgres `usage_periods` and
`usage_active_users`
**Testing**: `vitest` — unit for the verdict logic, `.itest.ts` for anything touching a store
**Target Platform**: the composed stack, `RELAY_POSTGRES_PORT=15432`
**Project Type**: monorepo — `relay-platform` code, `relay-tutorial` prose and gates
**Performance Goals**: none stated by any clause; the job is daily and reads two rollups
**Constraints**: the job **writes nothing** — it is a comparison, and R7's period argument
means it takes an explicit period rather than reading a clock
**Scale/Scope**: one module, one thin script, one integration suite, one SRS amendment, one
`docs/12` amendment, one chapter

**No NEEDS CLARIFICATION remain.** The two the spec could have carried — which operational
number, and what "alert" means on a platform with no alerting — were settled by measuring
(R1) and by finding the one precedent (R6).

## Constitution Check

**This section does not say PASS.** 4.5's plan wrote *"PASS, with one open case"* and the case
did not exist; 4.6's named a conflict it could not resolve. The failure mode to avoid is a
check that waves.

### III. Two Data Paths, Never Crossed — **THE JOB READS BOTH, AND THAT IS THE POINT**

> Analytical queries MUST NEVER execute against the operational database (PostgreSQL);
> billing, metering, and dashboard analytics read only from the analytical store (ClickHouse).

**A reconciler cannot obey this clause and do its job.** FR-ANL-06 requires metered totals to
be compared against operational counts, which requires reading both stores in one process. The
same constitution requires both.

The resolution is narrow and has to be stated rather than assumed: **the reconciler is not
billing, metering, or dashboard analytics.** It is an auditor of the boundary, and an auditor
that may only stand on one side of a fence cannot check the fence. That reading is available
in the clause's own words — it enumerates three roles and the reconciler is none of them — but
nothing in the constitution says so, and `gaps.md` 051-2 already records one conflict in this
family that the constitution must settle.

**Phase 6 states this explicitly**, in the shape 4.5 used for ADR-07 and 4.6 used for III's
first prohibition: name the reading, name the alternative, say which document owns the
amendment.

### III, fourth bullet — **THIS IS THE CLAUSE THE CHAPTER IMPLEMENTS**

> Metered totals MUST reconcile against operational counts to within 0.1%, verified by a daily
> job that alerts on breach.

The constitution carries FR-ANL-06 as a principle. **The chapter will show the bound cannot
hold for three of the four quantities, and one of the reasons is that the constitution's own
`message_events` has no producer.** That makes the amendment FR-ANL-06's and possibly the
constitution's, and phase 6 decides which.

### I. Tenant Isolation — satisfied, and R1 made it load-bearing

Every comparison is per tenant; the report never aggregates before a verdict. That is not only
isolation hygiene — R1 measured that aggregating turns 19 breaches into one passing number.

### VI. Requirement-Driven, Test-Verified — satisfied, with the verdict logic as the testable part

The comparison is arithmetic over two numbers and a threshold, so unlike 4.6's schema work it
**has branches**: pass, breach, not-comparable, and no-data. Those are unit-testable without a
store, which is what makes §2.3's CI half cheap.

**The quickstart MUST run unmodified.** 4.6 shipped two commands in it that had never been
run — `CORPUS_DAYS=60`, which the script refuses, and a `load-analytics.mjs` invocation missing
`--corpus`. Every block in this one is executed before it is written down.

### VII. Boring by Design — satisfied

No dependency. One module, one script, one suite, and amendments.

## Project Structure

```
specs/052-chapter-4-7/
├── spec.md              # 23 FR, 13 SC
├── plan.md              # this file
├── research.md          # R1–R10, eight measured
├── data-model.md        # the report, and what each verdict means
├── contracts/
│   └── reconcile.md     # what the job takes, returns, and may not touch
├── quickstart.md
├── baseline.txt
└── checklists/requirements.md
```

```
relay-platform/
├── services/api/src/metering/
│   ├── reconcile.ts           # the comparison, callable in isolation
│   ├── reconcile.test.ts      # the verdict logic, no store
│   └── reconcile.itest.ts     # both stores, and the planted drift
├── scripts/reconcile-usage.mjs  # a thin caller — R5's shape
└── vitest.coverage.config.mts   # pins

relay-tutorial/
├── app/(en)/part-4/chapter-07/<the chapter's slug>/{page.mdx,figures.ts}
└── lib/tutorial.ts
```

**Why `services/api/` and not the ingester — counted, not asserted.** The job needs both
stores, so the question is which service is cheaper to give the half it lacks.

    services/ingester  3 dependencies: @relay/protocol, @relay/service-kit, nats
                       reads ClickHouse over `fetch`, no client library
                       has NO `pg` — Postgres would be a fourth dependency plus a
                       whole data-access layer
    services/api      14 dependencies including `pg` and `drizzle-orm`
                       owns the repository, `periodOf`, and the quota code this job checks
                       needs NO new dependency: ClickHouse speaks HTTP

**Zero new dependencies against one, and the api already holds the definitions the comparison
is made of.** That is the same shape of argument ADR-07 is made of, and the reason 4.5 could
spend it: a dependency count is checkable and a preference is not.

**BUT THE READ IS NOT FREE, AND A FIRST DRAFT OF THIS SECTION SAID IT WAS.** It claimed the
analytical read is routine *"because `analytics/apply.mjs` and `load-analytics.mjs` already do
it without a client library"* — and both of those run on the **host**. Measured: `services/api/src`
contains exactly one reference to ClickHouse and it is inside a `.itest.ts`; the api's compose
block carries `RELAY_NATS_URL` and `RELAY_REDIS_URL` and **no `RELAY_CLICKHOUSE_*`, and no
`depends_on: clickhouse`**. So the api container cannot reach the store today.

**Which makes this chapter's compose change the same event 4.5's was**: the gateway gained
`RELAY_NATS_URL` and with it a place in ADR-07's argument. Here **the api becomes the first
operational service to read the analytical store**, which is the sharpest available form of the
constitution III question the Check above already has to answer — and a better one than the
abstract auditor argument, because it names the service that *is* the operational path.

## Phases

**MVP is phases 1–4.** The job exists, compares per tenant, reports four verdicts, and a
planted drift raises.

### Phase 1 — Premises, and the openings

Everything in `research.md` re-run into `baseline.txt`, plus:

- The two operational counters' gap, aggregate and per tenant, with the number of tenants over
  the bound. **And the cause of the 26**, which R1 left open: one `insert(messages)` path
  increments the counter in the same transaction, so something else writes messages.
- Both sides' tenant counts — 4 analytical against 675 operational.
- `pnpm check:fences` by kind, locale and both HEAD classes.
- The fenced-file exposure for every file this chapter will touch, **counted**, with the locale
  of each. 4.6 found two vi whole bodies among eleven files, both already stale.
- The eleven gates' colours. **`pnpm test:integration` reports one failure where three lanes
  fail** (051-3), so this opening is taken by running the suites directly.

### Phase 2 — Foundational: the verdict, with no store in sight

The comparison's arithmetic and its four outcomes as a pure function: two numbers, a threshold,
and a source name in, a verdict out. Unit tests only, both sides of the tolerance boundary, and
the zero-against-zero case that must not read as agreement.

**This is where constitution VI's coverage clause binds**, and unlike 4.6 the file has real
branches.

### Phase 3 — US1: the job reads both stores

`reconcile.ts` gathers the analytical totals from `daily_usage_billing` and the operational
totals from Postgres, per tenant per period, and applies phase 2's verdict.

Three of four quantities have an operational counterpart (R3). The stored count has none and
reports **not comparable** — a first-class outcome rather than an omission.

### Phase 4 — US2 and US3: the planted drift 🎯 **MVP**

§2.3's CI half. Plant a discrepancy larger than the threshold, assert the raise; remove it,
assert no raise; and exercise the boundary from both sides. **Both halves of the probe** — 4.6
ran the threshold probe both ways for the fifth time and the silent half was silent again.

The job is called directly with a tenant and a period, returns its report as a value, and two
identical invocations produce identical reports because it writes nothing.

### Phase 5 — The four obstacles, measured and published

R1's two operational counters, R4's 671 one-sided tenants, and R9's two carried items re-run at
today's corpus. FR-012's 0.1% measurement needs a corpus, and with it `gaps.md` 051-2's bind:
the loader is the cross-path read constitution III's first prohibition names.

### Phase 6 — The amendments

FR-ANL-06 where the measurements show the clause as written cannot hold; `docs/12` row 8; the
constitution reading in the Check above, stated rather than assumed. **047-1 and 048-1 closed
or restated** — filed for this movement, carried through four features.

### Phase 7 — The chapter

Title and slug fixed once before anything references them. Prose and traps counted, figures
from `baseline.txt`, fences generated from the checker's own replay, eleven gates, `gaps.md`
with every carried item re-measured, `traceability.md`, the SPECKIT block, the tag.

## Dependencies & Execution Order

```
Phase 1  premises + openings       ── blocks everything
Phase 2  the verdict, pure         ── blocks 3
Phase 3  US1 both stores           ── blocks 4
Phase 4  US2/US3 drift    🎯MVP    ── blocks 5
Phase 5  the obstacles             ── needs 4
Phase 6  the amendments            ── needs 5's numbers
Phase 7  the chapter               ── needs all
```

## Complexity Tracking

| Thing | Why it is not simpler |
|---|---|
| A pure verdict function separate from the gathering | §2.3's CI half has to run without a corpus, and 0.1% of a small number cannot fail for its own reason. The branches are the testable part. |
| Per-tenant comparison with no aggregation | R1 measured aggregation turning 19 breaches into 0.2694%. |
| A fourth verdict, "not comparable" | R3: the stored count has no operational counterpart, and R4: 671 tenants have one side only. Collapsing either into "breach" or "missing" hides a different thing. |

## Risks, each with what would catch it

- **The chapter publishes a percentage that reads as agreement.** FR-014 forbids it and phase 5
  is where it would happen. The guard is that every quantity's verdict carries its reason.
- **The 0.1% measurement is taken at lane volume.** §2.3 names this exact defect. Phase 5 uses
  a corpus and states the volume.
- **The corpus is loaded and not removed.** 4.6's cleanup had to reach three rollups and an
  inner table, and a mutation is not a delete. Phase 5 plans the removal with the load.
- **`check:fences` charges for a file this chapter edits.** Phase 1 counts the exposure before
  phase 2 writes anything; 4.6's first draft went 110 → 113 for two excerpts published with a
  `title=`.
