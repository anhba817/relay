# Implementation Plan: Tutorial Chapter 2.1 — Schema with a Spine

**Branch**: `main` (no feature branch — consistent with features 001–017) | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-chapter-2-1/spec.md`

## Summary

Open Part 2 with the system's most important requirement made structural:
versioned forward-only SQL migrations reproducing the SAD §6.1 tables
(environments, users, channels, messages — verbatim where the SAD defines
them; `applications` stub and `members` are recorded decisions filling
genuine SAD gaps), a ~50-line hand-rolled migration runner, and the
repository layer whose constructor **requires** an `environment_id` — every
operation tenant-scoped by construction (D4/FR-TEN-05/constitution I:
"designed out, not tested out"). Two long-promised mechanisms debut: (1) the
**fence amendment mechanism** — the API service's fenced `package.json` gains
`pg`, and the fenced `eslint.config.mjs` gains the raw-`pg`-import ban, both
shown as diff-fences whose pre-image is the fence published in the earlier
chapter and whose post-image must equal the current file; (2) the **named
integration lane** — isolation tests are `*.itest.ts` (invisible to the
fenced root vitest include, so the three-command gate stays Docker-free)
and run via `pnpm --filter @relay/api test:integration` against the compose
Postgres. Tutorial side: Part 2's eight chapters seed the manifest (2.1
published+translated, draft vi titles for Dong), sitemap 32 → 34, second
part-boundary crossing. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: relay-platform's existing stack (TS ~5.9, Node 22,
pnpm 10, tsx for service processes); NEW runtime dependency: `pg`
(node-postgres, current stable pinned at install, package-local to
services/api — R2); relay-tutorial — unchanged

**Primary Dependencies**: `pg` only. No migration framework (plain SQL files
+ a tiny runner, R3), no ORM, no test containers (the compose stack IS the
test database, R6)

**Storage**: PostgreSQL 18 from 1.2's compose stack — the first consumer.
Five tables + two gap-filling ones per R1's schema slice; `messages`
partitioning explicitly deferred (SAD growth note → retention chapter)

**Testing**: Docker-free gate unchanged (lint, typecheck, `pnpm test` —
root vitest include `**/src/**/*.test.ts` never sees `*.itest.ts`); NEW
integration lane: `services/api` script `test:integration` with its own
vitest config including `src/**/*.itest.ts`, requiring the compose Postgres
(`DATABASE_URL`, default `postgres://relay:relay@localhost:5432/relay`);
suite truncates tables in setup (deterministic without `down -v`, R6);
isolation suite attacks with foreign environment_ids (R5). Tutorial: battery
v3 (baseline 18 → 20 rows), the AMENDED fence battery (diff-chain
verification, R4), ID detector, nav battery (Part 2 opens: landing section,
sidebar 1+7, 1.4 next card, sitemap 34), vi parity, allowlist admission

**Target Platform**: any Node ≥18-features machine for the gate; compose
Postgres for the integration lane and demos; tutorial: static pages

**Project Type**: Two-artifact content feature — fifth code chapter, first
of Part 2

**Performance Goals**: None asserted this chapter (hot-path indexes are
created because the SAD §6.3 names them; measuring them is 2.4's business)

**Constraints**: SAD §6.1 SQL reproduced faithfully where defined (C5);
gaps (members, applications) are recorded decisions; edits to fenced files
ONLY via diff-fences (R4); integration tests touch ONLY the local compose
Postgres — never the tutorial site's Neon; commits, pushes, AND the
`part2-ch1` tag are Dong's

**Scale/Scope**: relay-platform: ~6 new files in services/api (migrations/
001_core_tables.sql, src/db/{client,migrate,repository}.ts,
src/db/repository.itest.ts, vitest.integration.config.ts) + 2 diff-fence
edits (api package.json, root eslint.config.mjs); tutorial: 2 page.mdx
(~2,500 prose words each) + 2 figures.ts (3 figures/locale), manifest seed
(Part 2 ×8 entries), battery baseline (20 rows)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation (NON-NEGOTIABLE) | ✅ Pass — this chapter IS the principle | Every persisted record carries `environment_id` directly or via one FK hop (messages → channels, members → channels — exactly the clause's allowance); `applications` and `environments` themselves carry none because they ARE the tenancy anchors the clause is defined over, not records belonging to a tenant — stated in the chapter's schema walk. Repository constructors require `environment_id`; raw `pg` access lint-forbidden outside `src/db` (the eslint diff-fence); the automated cross-tenant suite exists at the repository layer, with the endpoint form and every-build CI enforcement recorded as trajectory (endpoints don't exist yet). |
| II. No acknowledged loss | ✅ Grounded | The schema carries the machinery's anchors (last_sequence for ADR-03, the DR-03 partial unique index, UNIQUE(channel_id, sequence) DR-01) — created now, exercised in 2.2/2.3. |
| III. Two data paths | ✅ Pass | Operational schema only; nothing analytical touches it (CON-01 restated in prose). |
| IV. Single writer | ✅ Pass | The layer lives in services/api and nowhere else; the gateway gains no store access; the lint rule makes the discipline mechanical. |
| V. Developer/reader-first | ✅ Pass | The reader ends with migrations that re-run as no-ops, a layer that makes leaks inexpressible, and a suite that proves it. |
| VI. Requirement-driven, test-verified | ✅ Pass | FR-TEN/DR-01/02/03/NFR-SEC-09 traced; migrations versioned + forward-only per the workflow clause; the isolation suite is the chapter's centerpiece, not an afterthought. |
| VII. Boring by design | ✅ Pass | Plain SQL files + a tiny runner (no framework), `pg` (no ORM), the compose stack as the test database (no testcontainers); one new runtime dependency, pinned, reasoned. |
| Tech & platform constraints | ✅ Pass | PostgreSQL 15+ satisfied (compose pins 18); migrations forward-only; UTC timestamps come from the SAD's own column definitions. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — six files, two disciplined diffs, a
chapter pair, one seed.

## Project Structure

### Documentation (this feature)

```text
specs/018-chapter-2-1/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-2-1-contract.md
├── battery-baseline.txt # regenerated (20 rows) at implementation
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-platform/ (submodule — advances part1-ch4 → part2-ch1)
├── services/api/
│   ├── package.json                    # DIFF-FENCE — + pg dep, migrate + test:integration scripts (R4)
│   ├── vitest.integration.config.ts    # NEW — includes src/**/*.itest.ts only (R6)
│   ├── migrations/
│   │   └── 001_core_tables.sql         # NEW — SAD §6.1 slice + recorded-decision tables (R1)
│   └── src/db/
│       ├── client.ts                   # NEW — pool factory from DATABASE_URL (R2)
│       ├── migrate.ts                  # NEW — the ~50-line versioned forward-only runner (R3)
│       ├── repository.ts               # NEW — createEnvironment (admin surface) + Repository requiring environment_id (R5)
│       └── repository.itest.ts         # NEW — the isolation suite (R5/R6)
└── eslint.config.mjs                   # DIFF-FENCE — raw pg import forbidden outside src/db (R5)

relay-tutorial/ (existing submodule)
├── lib/tutorial.ts                                   # MODIFIED — Part 2's eight chapters seeded; 2.1 published (R7)
└── app/{(en),(vi)/vi}/part-2/chapter-01/schema-with-a-spine/
    ├── page.mdx                                      # NEW ×2 (R8, R9)
    └── figures.ts                                    # NEW ×2

/home/dong/work/relay/ (parent)
└── specs/018-chapter-2-1/battery-baseline.txt        # NEW — 20 rows
```

**Structure Decision**: The layer lives inside services/api (ADR-04: the
single writer owns the invariants — putting it in a shared package would
hand the gateway a loaded gun). The two fenced-file edits are the smallest
possible set and both are the mechanism's teaching examples.

## Implementation Flow (input to /speckit-tasks)

1. **Setup** : pin `pg`'s current version; confirm compose Postgres
   reachable on this machine (remapped port).
2. **Schema + runner** (FR-003): 001_core_tables.sql (SAD-faithful + gap
   decisions), client.ts, migrate.ts; migrate applies fresh + re-runs as
   no-op.
3. **Repository + enforcement** (FR-004): repository.ts (constructor
   requires environment_id), the eslint diff (raw pg ban), Docker-free gate
   still green.
4. **Isolation suite** (FR-006): repository.itest.ts + integration config +
   scripts; suite attacks with foreign tenant ids against compose Postgres.
5. **Manifest seed** (FR-008, R7): Part 2 ×8; build green.
6. **English chapter** (FR-001..005, 007, R8): beats incl. the diff-fence
   teaching moment; fences + diff-fences byte-verified.
7. **Vietnamese chapter** (FR-009, R9): settled register; byte-identical
   fences.
8. **Verify** ([quickstart.md](./quickstart.md)): both gate lanes, the
   amended fence battery (diff-chain reconstruction), battery v3 (20 rows),
   nav battery (Part 2 opens, sitemap 34, allowlist), vi parity.
9. **Handoff**: no commits — Dong's `part2-ch1` sequence + the eight vi
   titles flagged for review.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The diff-fence rule is machine-checkable and self-contained: pre-image =
  the fence text already published in the amending chapter's predecessor
  (1.4's package.json fence; 1.1's eslint fence); applying the chapter's
  diff to it MUST byte-equal the current repo file. 1.4's/1.1's own fence
  checks re-pin to their tags for exactly those files.
- `*.itest.ts` naming is what keeps every fenced config untouched: the root
  vitest include (`**/src/**/*.test.ts`) simply never matches it. No
  vitest.config edit, no fence amendment beyond the two above.
- Integration lane connects via DATABASE_URL default
  `postgres://relay:relay@localhost:5432/relay` — on the reference machine
  the compose stack runs remapped (RELAY_POSTGRES_PORT=15432), so
  verification exports DATABASE_URL accordingly; NEVER the tutorial's Neon.
- SAD-fidelity check for the migration SQL is wrap-tolerant but
  column-exact; `members` and `applications` carry their recorded-decision
  comments in the SQL itself.
- Commits/pushes/tags remain Dong's; the eight draft vi titles are his
  review item; vi read-through before the milestone commit.
