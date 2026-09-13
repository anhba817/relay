# Implementation Plan: Chapter 4.2 — ClickHouse from zero

**Branch**: `047-chapter-4-2` · **Date**: 2026-09-13 · **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/047-chapter-4-2/spec.md`

## Summary

Chapter 4.1 measured Postgres answering FR-ANL-05's question in **585.9 ms** over a million
rows, and its plan said why an index does not help: the join is ~140 ms of a 698 ms plan and
**the sort is 656**, because `count(DISTINCT user_id)` per day orders a million rows before it
counts anything. This chapter builds the store whose ordering is that sort's answer, and the
rollup that maintains the distinct count instead of computing it.

**It builds a schema and a comparison, not a pipeline.** No ingester, no consumer, no producer:
the corpus goes in through ClickHouse's own `postgresql()` table function, which reads the
operational database directly and returned the lane's exact row count on the first try. **The
chapter adds zero dependencies.**

**Phase 0 found three published documents wrong**, and one of the three is a conflict between
two requirements:

- **`compose.yaml`'s ClickHouse has never been reachable from outside its container** and its
  health check has been green since chapter 1.2, because `/ping` neither authenticates nor is
  network-restricted while the `default` user is loopback-only (R1).
- **SAD §6.2's DDL does not apply, in two places.** `TTL ts + INTERVAL 90 DAY` on a
  `DateTime64` is refused with `BAD_TTL_EXPRESSION` (R2); and `user_id UUID` **silently converts
  a deleted author's NULL to the zero UUID**, which `uniqExact` counts as a distinct user. The
  column is `Nullable(UUID)`, and the SAD is amended twice.
- **DR-10 and FR-ANL-06 cannot both hold above ~65,000 distinct senders.** `uniq` is exact to
  60,000 and off by 0.51% at 70,000; FR-ANL-06's bound is 0.1%, and DR-10 forbids the
  reconciliation from reading raw events (R4).

## Technical Context

**Language/Version**: TypeScript 5.x / Node 22 where any script is needed — and **this chapter
needs almost none**. The schema is SQL; the load is one `INSERT … SELECT`.
**Primary Dependencies**: **none added.** The lockfile contains no ClickHouse client and gains
none (R6). `@clickhouse/client` belongs to the ingester, two chapters out.
**Storage**: PostgreSQL, read-only and unmodified; ClickHouse 25.3, single node (ADR-08).
**Testing**: no lane runs against ClickHouse. Verification is **A** — the comparison against
4.1's recorded numbers — and **D** for the schema ledger's idempotence.
**Target Platform**: the compose stack on `RELAY_POSTGRES_PORT=15432`
**Project Type**: monorepo — `relay-platform/compose.yaml`, a new `analytics/` schema
directory, and `relay-tutorial/app/…/part-4/chapter-02/`
**Performance Goals**: none set here. FR-ANL-08's two seconds over ninety days is the bar the
store must eventually clear; this chapter measures one tenant with a million rows, which 4.1
established is the easy case.
**Constraints**: no change to the operational schema, to `schema_migrations`, or to the
Postgres runner; no analytical query against Postgres at this tag (constitution III); the
compose amendment must be additive (chapter 1.2's rule).
**Scale/Scope**: 1,000,000 in-window rows — the same corpus 4.1 measured — one raw table, one
materialised view, one ledger, ~2,000–4,000 prose words.

**Unknowns**: two, both recorded at the end of [research.md](./research.md) and neither
blocking. The schema ledger's shape is a Phase 1 decision, and R4's clause conflict is filed
for movement IV rather than settled here.

## Constitution Check

*GATE: evaluated before Phase 0 and re-evaluated after Phase 1. Both results below.*

| Principle | Bearing | Verdict |
|---|---|---|
| **I — Tenant isolation** | `ORDER BY (environment_id, ts)` makes the tenant the first key, so isolation is the thing the store is fastest at — `EXPLAIN indexes=1` shows 4 parts of 12 when one environment of three is named. No route, no reader, no API surface. The corpus load reads Postgres through a table function and writes one ClickHouse table. | **PASS** |
| **II — No acknowledged message lost** | Nothing on the send path changes. The operational database is read and not written. | **PASS** |
| **III — Two data paths, never crossed** | This is the chapter that builds the second path's store. **4.1 executed an analytical query against Postgres as a deliberate exception; that is not repeated** (FR-014). The analytical store holds no message text — `text_length`, not `text` (FR-ANL-11, DR-08). | **PASS** |
| **IV — Single writer** | The corpus load is the only writer, and it runs once, by hand, before any measurement. | **PASS** |
| **V — API-first** | No public surface changes. No route, no error code, no frame. | **PASS** |
| **VI — Requirement-driven** | 16 requirements and 8 criteria tracing to FR-ANL-05/09/11, DR-07/08/09/10, ADR-08 and SAD §6.2. **VI's 70% coverage clause does not reach this chapter**: `vitest.coverage.config.mts`'s `include` is `packages/*/src/**/*.ts` and `services/*/src/**/*.ts`, and nothing here is under either. | **PASS** |
| **VII — Boring by design** | **No new service, no new language, no new dependency.** ClickHouse is already in `compose.yaml` and ADR-08 already accepts it. The one amendment is additive. | **PASS** |

**THE ONE WORTH ARGUING IS THE COMPOSE AMENDMENT, AND IT IS ADDITIVE.** Chapter 1.2 fences
`compose.yaml` as a whole body under an additive-only rule, so every later chapter may add and
none may rewrite. This chapter adds an `environment:` block and replaces the health check's
command — **and the replacement is the part to justify.** The current check runs `/ping`, which
passes while every query is refused (R1). A check that cannot fail for the reason you care
about is not a check, and replacing it is a correction rather than a rewrite. The fence-chain
cost is one hunk.

**NO ADR IS EXPECTED, AND THE PLAN SAYS SO IN ADVANCE.** ADR-08 already decides single-node
ClickHouse with a cluster-shaped schema, and this chapter builds what it describes. **If one
becomes necessary the likeliest cause is R4** — if the rollup's approximation forces a change
to DR-10 or FR-ANL-06, that is an amendment to a requirement and possibly an ADR about what a
rollup may approximate. It is filed for movement IV, so this chapter should not produce one.

### Post-design re-evaluation

Re-run after `data-model.md`, `contracts/` and `quickstart.md`. **No verdict changed.** Two
design decisions were checked against the gate:

- **The schema ledger is a ClickHouse table**, which is a second table this chapter creates.
  VII's "smallest number" was tested against it: the alternative is `CREATE … IF NOT EXISTS`
  and no record of what ran, which is `check-fence-chain`'s silent-zero shape — idempotent and
  unable to say whether it did anything.
- **`delivery_latency_ms` is created with no producer** (R7). Principle VI asks that behaviour
  trace to a requirement: the column traces to FR-ANL-10, which is a later chapter's, and the
  chapter names it as unfilled rather than creating it silently.

## Project Structure

### Documentation (this feature)

```text
specs/047-chapter-4-2/
├── plan.md · spec.md
├── research.md          # Phase 0 — eight questions, three documents found wrong
├── data-model.md        # Phase 1 — the raw table, the rollup, the ledger
├── quickstart.md        # Phase 1 — reproducing the comparison
├── contracts/
│   └── schema.md        # Phase 1 — the DDL the ingester will be written against
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — not created here
```

### Source code

```text
relay-platform/
├── compose.yaml                      AMENDED — an environment block, and a health check
│                                     that runs a query instead of /ping (R1)
├── analytics/
│   ├── 0000_message_events.sql       NEW — SAD §6.2's table, with R2's one divergence
│   ├── 0001_daily_usage.sql          NEW — DR-10's rollup
│   └── apply.mjs                     NEW — applies what has not been applied, and says so
└── scripts/scale/
    └── load-analytics.mjs            NEW — one INSERT … SELECT through postgresql() (R6)

relay-tutorial/
├── app/(en)/part-4/chapter-02/<slug>/{page.mdx,figures.ts}
└── app/(vi)/vi/part-4/chapter-02/<slug>/page.mdx
```

**Structure Decision**: the analytical schema lives in `relay-platform/analytics/` beside
`services/api/migrations/`, not inside it — **the two stores' ledgers are separate** (FR-012),
and putting ClickHouse DDL under a directory the Postgres runner reads is how one runner ends
up with a version string it has never seen, which `gaps.md` 045-69 is the record of.

Nothing under `services/` changes. `docs/05-sad.md` gains **two** amendments to §6.2 — the TTL's cast and `user_id`'s nullability.

## Complexity Tracking

No Constitution Check violations. Table omitted.
