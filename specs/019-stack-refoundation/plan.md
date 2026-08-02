# Implementation Plan: Stack Re-foundation — Turborepo, NestJS, Drizzle

**Branch**: `main` (no feature branches) | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/019-stack-refoundation/spec.md`

## Summary

The series' first revision feature (docs/07 §6 rule 3 performed for real):
chapters 1.1, 1.4, and 2.1 — plus a two-line FR-004 touch to 1.3 — are
revised in both locales so the canonical platform is built on the stack
ADR-15/16/17 record and constitution v1.1.0 binds. relay-platform's
history is rebuilt as five states re-tagged under the existing names;
1.1 raises Turborepo over the unchanged pnpm workspace (gate through the
task graph, false-green trade-off taught), 1.4's api service becomes a
NestJS application while the gateway stays deliberately frameworkless,
and 2.1's repository layer moves to Drizzle with drizzle-kit-generated,
hand-reviewed, forward-only SQL applied by the retained runner. Every
revised chapter carries the new zero-word `<RevisionNote>`; 2.1's
diff-fences are re-derived against revised 1.4; 1.2 and Part 0 pass
through byte-unchanged as the control set. All decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: relay-platform's existing base (TS ~5.9, pnpm 10);
Node engines floor moves to `">=22.12"` in revised 1.1's root
package.json (the `require(esm)` bridge's requirement, carried by the
fence from birth — R2). NEW: `turbo` ^2.10 (root devDep); `@nestjs/{core,common,
platform-express}` ^11.1 + `reflect-metadata` + `rxjs` + `@nestjs/cli`
devDep (services/api); `drizzle-orm` ^0.45 + `drizzle-kit` ^0.31 devDep
(services/api); `unplugin-swc` + `@swc/core` (api vitest, R2). RETIRED:
api's `tsx` devDep (gateway keeps tsx); root `vitest.config.ts`.
relay-tutorial: no dependency changes.

**Primary Dependencies**: turbo (task graph over unchanged pnpm, R1);
NestJS 11 on the Express platform, api package flips to
`"type": "commonjs"`, workspace deps build ESM dist bridged by
`require(esm)` (R2 — verify at implement, tsup dual-emit is the
fallback); drizzle-orm over the existing `pg` Pool via
`drizzle-orm/node-postgres`, drizzle-kit generates SQL that the retained
~50-line runner applies (R3).

**Storage**: PostgreSQL 18 from 1.2's compose stack, unchanged. Schema
content identical to 018's (SAD §6.1 slice + recorded-decision tables);
the migration file is regenerated through the drizzle-kit
generate→review→diff-vs-§6.1 flow so chapter story and repo history
agree (R3).

**Testing**: gate stays three commands, now `turbo run` underneath
(lint = cached whole-repo root task; typecheck/test/build per-package
with `dependsOn: ["^build"]`, R1); per-package vitest defaults keep
`*.itest.ts` invisible to the unit lane; api unit tests transform via
SWC for decorator metadata (R2); integration lane unchanged in shape
(`test:integration`, compose Postgres only, localhost guard). Tutorial:
battery v3 (019 baseline: exactly six changed rows, R6), fence battery
with re-derived 2.1 diff-fences and the new 1.4→protocol diff-fences,
ID detector, vi parity, nav battery asserting NO changes (FR-011).

**Target Platform**: any Node ≥22.12 machine for the gate; compose
Postgres for the integration lane; tutorial: static pages.

**Project Type**: Two-artifact content feature — the series' first
*revision* feature: four chapters touched (three substantively), zero
pages added.

**Performance Goals**: none asserted; turbo cache hit-rate is taught,
not benchmarked (7.3 owns measurement).

**Constraints**: ADR-15/16/17 implemented, not re-argued; 1.2 + Part 0
byte-unchanged (control set); five tags re-cut under existing names,
gate green at every one; fence contract holds series-wide including
en/vi byte-identity; integration tests never touch Dong's Neon;
commits, tags, pushes are Dong's, on explicit go-ahead.

**Scale/Scope**: relay-platform: root package.json + turbo.json +
.gitignore + delete root vitest.config.ts + config/protocol/gateway/
service-kit package.json script additions + service-kit/protocol build
tsconfigs + api service rewritten (~8 files: package.json, tsconfig,
nest-cli.json, vitest.config.ts, src/main.ts, src/app.module.ts,
src/health controller, request-id wiring) + db layer revised (~6 files:
schema.ts NEW, drizzle.config.ts NEW, client.ts, repository.ts,
repository.itest.ts, regenerated migration SQL) + README §rewrite.
relay-tutorial: 4 chapters × 2 locales page.mdx revisions (1.3's
near-nil), 3 figure files likely touched (1.1 gate figure, 1.4 skeleton
figures, 2.1 two-doors/two-lanes), `components/tutorial/revision-note.tsx`
NEW, 019 battery baseline.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation (NON-NEGOTIABLE) | ✅ Pass | The repository layer keeps its constructor-requires-`environment_id` discipline as a plain class beneath the framework (request-scoped DI deferred to 2.2 with the endpoints it exists for); the lint ban *widens* (pg + drizzle-orm outside src/db); the isolation suite survives with Drizzle-shaped assertions. The re-foundation strengthens, not weakens, the principle's machinery. |
| II. No acknowledged loss | ✅ Grounded | Schema content unchanged (sequence anchors, DR-03 partial index) — regenerated through drizzle-kit but diffed against §6.1; the runner stays forward-only. |
| III. Two data paths | ✅ Pass | Untouched; operational schema only. |
| IV. Single writer | ✅ Pass | The layer stays in services/api; the gateway gains no framework and no store access; ADR-15's scope clause is the chapter's own teaching beat. |
| V. Developer/reader-first | ✅ Pass | Revisions announced via `RevisionNote`, not silent; the reader's three-command contract survives the turbo conversion verbatim. |
| VI. Requirement-driven, test-verified | ✅ Pass | ADR-15/16/17 + EIR-API-04/07, NFR-MNT-02/03 traced; every tag's gate is machine-verified; the battery measures the revision's exact blast radius (R6). |
| VII. Boring by design | ✅ Pass | Every choice implements an accepted ADR; framework confined to the api per ADR-15's scope; one migration applier (ours); Express default with Fastify already the ADR's named fallback. Deviations from prior chapters are the POINT of the feature and are ADR-backed. |
| Tech & platform constraints (v1.1.0) | ✅ Pass — this feature is the constraint's implementation | NestJS API-only, Drizzle in-repository with forward-only SQL, Turborepo over unchanged pnpm — the three amended bullets made code. |
| Workflow & quality gates | ✅ Pass | Migrations stay versioned/forward-only; spec-first flow observed; FR-004's escape hatch exercised explicitly for 1.3 (recorded, noted, revision-noted). |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — the design adds no service, no second
migration ledger, no framework outside the api; the only new tutorial
component is the revision note the spec demands.

## Project Structure

### Documentation (this feature)

```text
specs/019-stack-refoundation/
├── plan.md              # This file
├── research.md          # Phase 0 output (R1–R9)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── refoundation-contract.md
├── battery-baseline.txt # regenerated (20 rows) at implementation
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-platform/ (submodule — history rebuilt as five states, re-tagged part1-ch1..part2-ch1)
├── package.json                  # REVISED (1.1) — scripts delegate to turbo; turbo devDep
├── turbo.json                    # NEW (1.1) — lint(root)/typecheck/test/build tasks (R1)
├── .gitignore                    # REVISED (1.1) — + .turbo/
├── vitest.config.ts              # DELETED (1.1) — per-package vitest replaces the root include
├── packages/
│   ├── config/package.json       # REVISED (1.1) — + "test": "vitest run"
│   ├── protocol/package.json     # 1.3 fence + "test" (FR-004); build/dist-exports via 1.4 DIFF-FENCE
│   ├── protocol/tsconfig.build.json  # NEW at S4 (1.4 diff-fence territory)
│   └── service-kit/               # REWRITTEN territory (1.4) — + build, ESM dist
├── services/
│   ├── api/                       # REWRITTEN (1.4 + 2.1)
│   │   ├── package.json           # NestJS deps, type:commonjs, nest scripts; drizzle (2.1)
│   │   ├── tsconfig.json          # decorators+metadata; erasableSyntaxOnly dropped (R2)
│   │   ├── nest-cli.json          # NEW
│   │   ├── vitest.config.ts       # NEW — SWC transform (R2)
│   │   ├── vitest.integration.config.ts  # kept
│   │   ├── drizzle.config.ts      # NEW (2.1, R3)
│   │   ├── migrations/*.sql       # regenerated via drizzle-kit, reviewed vs §6.1 (R3)
│   │   └── src/
│   │       ├── main.ts, app.module.ts, health.controller.ts, request-id wiring
│   │       └── db/{schema.ts NEW, client.ts, migrate.ts kept, repository.ts, repository.itest.ts}
│   └── gateway/                   # frameworkless, tsx — package.json + "test" script only
├── eslint.config.mjs              # 2.1 re-derived diff-fence — ban widens to drizzle-orm
└── README.md                      # "Deliberately not yet" Turborepo entry → adopted per ADR-17

relay-tutorial/ (submodule — content revised, zero pages added/moved)
├── components/tutorial/revision-note.tsx   # NEW — zero-word, props-only (R5)
├── app/(en)/part-1/chapter-01/.../{page.mdx,figures.ts}   # REVISED (turbo)
├── app/(en)/part-1/chapter-03/.../page.mdx                # MINIMAL (fence + note)
├── app/(en)/part-1/chapter-04/.../{page.mdx,figures.ts}   # REWRITTEN (NestJS)
├── app/(en)/part-2/chapter-01/.../{page.mdx,figures.ts}   # REVISED (Drizzle)
└── app/(vi)/vi/...                                        # same four chapters, vi
```

**Structure Decision**: two existing submodules, no new packages beyond
what the ADRs name; the tutorial site's routing/manifest/nav surfaces are
deliberately untouched (FR-011).

## Complexity Tracking

> No constitution violations. The one scope expansion — 1.3 joining the
> revision set — is FR-004's own recorded escape hatch, exercised in R1
> with the smaller alternative (root-task test) rejected for gutting
> ADR-17's granularity promise.
