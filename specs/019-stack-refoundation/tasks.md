# Tasks: Stack Re-foundation — Turborepo, NestJS, Drizzle

**Input**: Design documents from `/specs/019-stack-refoundation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/refoundation-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract
battery (C1 per-tag gate matrix, C2 fence contract with BOTH amendment
chains, C3 control-set freeze, C4 revision notes, C5 ADR fidelity, C6
isolation machinery, C7 site surface frozen, C8 bilingual parity).

**Organization**: The series' first revision feature (docs/07 §6 rule 3).
Non-negotiables: **the control set is byte-frozen** (Part 0 + 1.2, both
locales — zero diffs); **five states, five re-used tag names** (S1..S5 per
data-model; each state's gate green before the next layers on); **amendment
chain A re-derived** (2.1 diff-fences: pre = revised 1.4's fences, post =
S5 files) and **chain B born** (1.4 diff-fences: pre = 1.3's fences, post =
S4 files); **fences byte-match their own chapter's state**; **verify library
behavior against INSTALLED packages, never memory** (R2's require(esm)
bridge, SWC metadata, vitest includes); **integration tests touch only the
local compose Postgres — never the tutorial site's Neon**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` /
`git tag` (Dong does all three; the five-state commit sequence is a
handoff artifact, T013). The compose Postgres on this machine runs
remapped (`RELAY_POSTGRES_PORT=15432`). Flag, never delete, anything
verification adds anywhere.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = the revised chapters (en), US2 = the re-founded repo + rebased tags, US3 = revision visibility, vi, and measurement

## Path Conventions

- Platform: `/home/dong/work/relay/relay-platform/` (root files, packages/*, services/*)
- Chapters: `relay-tutorial/app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/`, `.../part-1/chapter-03/the-protocol-package/`, `.../part-1/chapter-04/walking-skeleton/`, `.../part-2/chapter-01/schema-with-a-spine/` (+ vi mirrors under `app/(vi)/vi/`)
- Sources: docs/05 (ADR-15 L904, ADR-16 L925, ADR-17, §6.1, §8), docs/06 (three new deep dives + "Reading the seventeen together"), docs/07 §2 (diff-fence rule) §3 (amended 1.1/1.4/2.1 rows), constitution v1.1.0 (Technology & Platform Constraints)
- State manifest: data-model.md "Tag lineage"; contract makes it binding
- Battery baseline: `specs/019-stack-refoundation/battery-baseline.txt` (20 rows; exactly 6 may differ from 018's)

---

## Phase 1: Setup

**Purpose**: Pin versions and burn down R2's risks against installed packages

- [X] T001 Pin and probe in a scratch dir (`/tmp/claude-1000/.../scratchpad/019-probe/`): `pnpm view` exact current versions (turbo, @nestjs/core, @nestjs/common, @nestjs/platform-express, @nestjs/cli, reflect-metadata, rxjs, drizzle-orm, drizzle-kit, unplugin-swc, @swc/core) — these become the pinned fence values; then prove the three risky mechanics against INSTALLED packages: (a) a CJS package compiled by `nest build` importing an ESM-dist workspace package via Node's `require(esm)` on this machine's Node (check ≥22.12) — boots and resolves types; (b) vitest 4's default include does NOT collect `x.itest.ts` while collecting `x.test.ts`; (c) `unplugin-swc` under vitest emits decorator metadata (a trivial Nest DI `Test.createTestingModule` resolves a type-injected provider). If (a) fails → R2's tsup dual-emit fallback, record it; if (c) fails → DI-free unit tests, record it. Also snapshot pre-feature references: the current sitemap URL set from a fresh `pnpm build` in relay-tutorial, and a copy of 018's battery-baseline.txt for the T016 delta check. Record all findings for T002–T005 (R1/R2/R3)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The five platform states, built sequentially in the working tree — everything the chapters fence

- [X] T002 Build S1 (turbo over the workspace) in /home/dong/work/relay/relay-platform/: root package.json — `turbo` devDep pinned to T001's version; `"engines": {"node": ">=22.12"}` (decided HERE so the 1.1 fence carries the require(esm) bridge floor from birth — remediation I3; 1.4 explains why); scripts keep their three names but delegate (`typecheck`/`test`/`build` → `turbo run …`; `lint` via the R1 root-task wiring so the whole-repo ESLint invocation is cached — exact `//#` naming per installed turbo 2 docs); turbo.json NEW — tasks lint(root)/typecheck/test/build, `dependsOn: ["^build"]` on typecheck/test/build, `outputs: ["dist/**"]` on build; .gitignore + `.turbo/`; DELETE root vitest.config.ts; packages/config/package.json + `"test": "vitest run"`. Verify at this state: `pnpm lint && pnpm typecheck && pnpm test` green with Docker stopped (at TRUE S1 the protocol package does not exist yet; verification of the assembled per-state trees happens in T012 against the snapshots below); second run shows cache hits; `pnpm turbo run test --force` green; run R8's false-green experiment (mutate an undeclared input, observe the stale hit, then declare the input) and RECORD the exact demo for 1.1's prose. **On completion, SNAPSHOT the S1-relevant tree** (working tree minus node_modules/.turbo/.git) into `/tmp/claude-1000/.../scratchpad/019-states/S1/` — Phase 2 is sequential, so each task's completion moment IS its state; later tasks overwrite shared files (remediation I1) (FR-001, C1, C5)
- [X] T003 Build S3's delta (FR-004 minimal): packages/protocol/package.json gains exactly `"test": "vitest run"` under scripts — 2-line diff, KEEP MINIMAL (this byte-shape IS 1.3's revised in-place fence); confirm S2 needs ZERO platform changes beyond inherited root files (compose.yaml and packages/config/src/infra.test.ts byte-untouched; infra test now runs via @relay/config's own test script); gate green; protocol tests visibly collected per-package (`turbo run test` summary lists @relay/protocol). **On completion, snapshot into `scratchpad/019-states/S3/`** (and derive S2/ = S3/ minus the protocol package plus 1.2's compose files — record the derivation) (remediation I1) (FR-004, C2/C3)
- [X] T004 Build S4 (the NestJS walking skeleton): packages/protocol — tsconfig.build.json NEW (ESM emit + declaration to dist), package.json diff: + `"build": "tsc -p tsconfig.build.json"`, exports "." → dist types/default — MINIMAL diff, this becomes chain B's diff-fence in revised 1.4; packages/service-kit — same build treatment (its files are 1.4 fences, rewrite freely, keep the log/request-id surface the gateway shares); services/api REWRITTEN per R2: package.json (`"type": "commonjs"`, @nestjs/{core,common,platform-express} + reflect-metadata + rxjs pinned per T001, @nestjs/cli + unplugin-swc + @swc/core devDeps, scripts dev `nest start --watch` / build `nest build` / test via package vitest, tsx devDep RETIRED), tsconfig.json (drops erasableSyntaxOnly, + experimentalDecorators + emitDecoratorMetadata — teaching comment), nest-cli.json NEW, vitest.config.ts NEW (SWC transform), src/main.ts (Nest bootstrap, port/env as before), src/app.module.ts, src/health.controller.ts (same endpoint + response shape as today's skeleton), request-id + structured-log wiring through service-kit in Nest middleware/interceptor idiom, src/main.test.ts updated (DI boot + health 200 + request-id echo); services/gateway/package.json + `"test": "vitest run"` ONLY (stays ESM + tsx + frameworkless — its package.json must contain NO framework dependency, C5). Verify: gate green Docker-free with turbo showing protocol/service-kit build BEFORE api typecheck/test; both services boot (api `nest build && node dist/main.js`, gateway tsx), health answers, request id in logs; record the ESM/CJS bridge behavior actually observed for 1.4's prose. **On completion, snapshot into `scratchpad/019-states/S4/`** (remediation I1) (FR-002, C1/C5/C6-adjacent)
- [X] T005 Build S5 (Drizzle in the repository layer): services/api/package.json diff — + drizzle-orm pinned, drizzle-kit devDep (MINIMAL — chain A re-derivation target with 018's migrate/test:integration scripts kept); drizzle.config.ts NEW; src/db/schema.ts NEW — SAD §6.1-exact (CHECKs, DR-02 UNIQUEs, DR-01 UNIQUE, DR-03 partial unique index via `uniqueIndex().where()`, §6.3 hot-path indexes, DECISION comments for applications-stub/members exactly as the SQL carried them); run `drizzle-kit generate`, REVIEW the generated SQL, diff it against docs/05 §6.1 and record the diff's disposition (the chapter's ADR-16 beat — R3), place the reviewed SQL as the runner's migrations file (runner-compatible name, content replacing 018's 001_core_tables.sql); src/db/client.ts revised (drizzle over the existing lazy Pool, export the NodePgDatabase handle + Pool for the runner); src/db/migrate.ts KEPT (byte-minimal churn); src/db/repository.ts revised — `constructor(db, environmentId)` same method surface, queries via Drizzle, raw-SQL islands only where the builder falls short (comment them per ADR-16); src/db/repository.itest.ts revised (same four attacks, same TRUNCATE setup, same localhost-only guard); /home/dong/work/relay/relay-platform/eslint.config.mjs — widen no-restricted-imports outside services/api/src/db/** to `pg` + `drizzle-orm` (+ patterns for `drizzle-orm/*`) — MINIMAL diff (chain A's second member). Verify: gate green Docker-free; with `RELAY_POSTGRES_PORT=15432 docker compose up -d --wait postgres`: migrate applies fresh AND re-runs as no-op, `pnpm --filter @relay/api test:integration` green; scratch violations (pg import AND drizzle-orm import in a non-db file) each FAIL lint, then delete; `git -C relay-platform status --porcelain` audited against the S4→S5 file manifest. **S5 needs no copy — the working tree IS S5**, but record its manifest alongside the others (remediation I1) (FR-003, C1/C2/C6)

---

## Phase 3: User Story 1 - Re-read the three revised chapters and build the production-shaped stack (Priority: P1) 🎯 MVP

**Goal**: The four English chapters teach the ADR-15/16/17 stack, fences pasted from the S1..S5 files, both amendment chains in daylight.

**Independent Test**: A reader can follow 1.1→1.2→1.3→1.4→2.1 using only the chapters and reach the passing 2.1 checkpoint on the new stack (spec US1).

### Implementation for User Story 1

- [X] T006 [P] [US1] Create relay-tutorial/components/tutorial/revision-note.tsx per R5: props-only, self-closing usage (locale, date "2026-08", adr id(s), summary string rendered by the component), localized copy (en/vi) inside the component, styled consistently with the existing box components, placed-below-ChapterHeader convention documented in a comment; **usage MUST be a SINGLE line** — `<RevisionNote … />` with all props on that one line, never prettier-wrapped (remediation I2: the battery counter skips only `<`-starting lines; multi-line props would leak words into the canonical count, as Figure caption lines demonstrably do); keep the summary prop short enough that single-line stays readable; document the single-line rule in the component comment (FR-007, C4)
- [X] T007 [US1] Revise en 1.1 in relay-tutorial/app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/{page.mdx,figures.ts} per R1/R8: `<RevisionNote adr="ADR-17">` under the header; root package.json fence re-pasted from S1 (turbo dep, delegating scripts); turbo.json fence NEW; the task-graph beat (why `pnpm -r` was right until a build step existed — ADR-17's own argument); the false-green TRAP (T002's recorded demo: undeclared input → stale green → declared input; cache trust as reviewed code); cache-hit + `--force` shown at the gate beat; root vitest.config.ts's retirement explained (per-package tests, the config package's own test script fence); `<Why source="ADR-17 · D8">`; gate figure updated in figures.ts if it names the old wiring; three-command contract unchanged as the closing CHECKPOINT; Node ≥22.12 noted where engines are discussed (FR-001, C2/C4/C5)
- [X] T008 [P] [US1] Minimal en 1.3 in relay-tutorial/app/(en)/part-1/chapter-03/the-protocol-package/page.mdx: `<RevisionNote adr="ADR-17">` (two-line touch named honestly: the package gained its own test script when the gate moved to the task graph); protocol package.json fence updated to S3 bytes; NO other prose change (the chapter's pnpm-test story stays true — tests still run, now per-package); the note strictly single-line per T006's rule; verify canonical word count UNCHANGED vs 018 baseline — this check is I2's mechanical backstop (FR-004, C3/C4)
- [X] T009 [US1] Rewrite en 1.4 in relay-tutorial/app/(en)/part-1/chapter-04/walking-skeleton/{page.mdx,figures.ts} per R2/R8: `<RevisionNote adr="ADR-15">`; the skeleton-before-muscles spine survives; the api half rebuilt around ADR-15 (module/DI/health controller/request-id/structured logs; fences from S4: package.json, tsconfig with the rescope comment, nest-cli.json, main.ts, app.module.ts, health.controller.ts, vitest.config.ts); the framework-boundary beat (`<Why source="ADR-15">` — the gateway REFUSES the framework; socket mechanics vs wide CRUD surface); the erasableSyntaxOnly rescope taught as ADR-15's stated trade-off (kept for gateway/packages, spent for DI metadata in the api — the TRAP territory: metadata-less DI failing silently or the tsx/esbuild no-metadata trap, per T004's observed behavior); the ESM/CJS bridge beat (workspace stays ESM, framework speaks CJS, Node ≥22.12's require(esm) bridges — as actually observed); chain B diff-fences (```diff title="packages/protocol/package.json" — build script + dist exports; tsconfig.build.json as a NEW-file plain fence); gateway half: tsx story retold gateway-scoped, gateway package.json fence (+test script, no framework dep); figures updated (skeleton topology; add/adjust the framework-boundary figure); SKIP AHEAD names part1-ch4; battery-shaped throughout (FR-002, C2/C4/C5)
- [X] T010 [US1] Revise en 2.1 in relay-tutorial/app/(en)/part-2/chapter-01/schema-with-a-spine/{page.mdx,figures.ts} per R3/R8: `<RevisionNote adr="ADR-16">`; isolation-designed-out spine and the schema derivation walk survive; NEW beats — schema.ts fence (the TS schema next to §6.1's SQL) and the schema-twice drift TRAP replacing the constructor-property beat (drift checked via the generate→review→diff flow, shown with T005's actual diff disposition); drizzle.config.ts fence; the generated-then-reviewed migration fence (regenerated SQL, DECISION comments intact); client.ts/repository.ts/repository.itest.ts fences from S5 (`new Repository(db, envId)` — constructor still requires the tenant; request-scoped DI named as 2.2's arrival in the ForwardRef); chain A diff-fences RE-DERIVED (api package.json vs revised 1.4's fence; eslint.config.mjs with the widened ban vs revised 1.4's fence); figTwoDoors updated (`new Repository(db, …)`), figTwoLanes checked against the unchanged lane story; 2.1's stale "chapter 1.4's guarantee" comment reconciled with the rescope (FR-003, C2/C4/C5/C6)
- [X] T011 [US1] Run the en battery over ALL FOUR chapters per C2/C8's en half: canonical words 2,000–4,000 for 1.1/1.4/2.1 (1.3 unchanged); box minima (≥2 WHY, ≥1 TRAP, 1 SKIP AHEAD naming the right tag, ≥1 ForwardRef, exactly 1 closing CHECKPOINT); figures 2–4 with half-coverage; every plain fence byte-checked against its state's file; chain A and B diff-fences verified mechanically (strip-`+` = predecessor fence text; strip-`-` = state file); ID detector over all four page.mdx + three figures.ts; `pnpm lint && pnpm build` in relay-tutorial; fix findings (C2/C5)

**Checkpoint**: The English series teaches the production stack end to end — MVP delivered

---

## Phase 4: User Story 2 - The repository is re-founded and the tag lineage rebased honestly (Priority: P2)

**Goal**: Five verifiable states, the rebase recipe in Dong's hands, the README record resolved.

**Independent Test**: Each state's gate green (C1); fence checks pass series-wide (C2); control set frozen (C3).

### Implementation for User Story 2

- [X] T012 [US2] Per-state gate verification against the Phase 2 SNAPSHOTS (remediation I1 — states differ by file CONTENT, so pruning the final tree cannot reconstruct them): in each of `scratchpad/019-states/S{1..4}/`, `pnpm install` then `pnpm lint && pnpm typecheck && pnpm test` with Docker stopped; S4 additionally boots both services; S5 is the working tree itself (already verified in T005 — re-run the full C1 matrix incl. the integration lane once more, cold cache); cross-check each snapshot's file manifest against data-model's tag-lineage table; record the matrix results in the feature dir (C1)
- [X] T013 [US2] Write the handoff + resolve the README: specs/019-stack-refoundation/rebase-recipe.md — for Dong: the five commit file-sets in order (exact paths added/modified/deleted per state, from T012's manifests), suggested commit messages, the re-tagging commands for the five names, the optional archive-tag variant (`*-v1`) as a documented choice, and the push-order note (platform first, then tutorial, then parent pins); REWRITE /home/dong/work/relay/relay-platform/README.md — "Deliberately not yet" Turborepo entry becomes an "Adopted (ADR-17)" record preserving the original trigger text as history, and the "Running the services" section updated for the nest/tsx split (FR-005/FR-010, C5)

---

## Phase 5: User Story 3 - The revision is visible, bilingual, and measured (Priority: P3)

**Goal**: vi parity for the revision set, the baseline's exact six-row delta, the site surface provably frozen.

**Independent Test**: RevisionNote on exactly 8 pages; vi structural parity with byte-identical fences; sitemap set unchanged (spec US3).

### Implementation for User Story 3

- [X] T014 [P] [US3] Revise vi 1.1 and vi 1.3 in relay-tutorial/app/(vi)/vi/part-1/chapter-01/the-monorepo-and-the-toolchain/{page.mdx,figures.ts} and .../chapter-03/the-protocol-package/page.mdx: mirror T007/T008 structurally (RevisionNote locale="vi", fences via «Fn» marker substitution for byte-identity, figure labels translated where narrative); vi 1.1 prose revised at the naturalized register (settled glossary; "cửa ải" for the gate, task graph/cache/false green expressed meaning-first without calques); vi 1.3 prose untouched beyond the fence + note; naturalization self-review before presenting (FR-009, C8)
- [X] T015 [P] [US3] Rewrite vi 1.4 and revise vi 2.1 in relay-tutorial/app/(vi)/vi/part-1/chapter-04/walking-skeleton/{page.mdx,figures.ts} and .../vi/part-2/chapter-01/schema-with-a-spine/{page.mdx,figures.ts}: mirror T009/T010 structurally (boxes/figures/fence counts equal; ALL fences incl. diff-fences byte-identical via marker flow); register per glossary ("bộ khung biết đi" stays 1.4's title concept; framework-boundary and schema-twice beats rendered meaning-first); naturalization self-review before presenting (FR-009, C8)
- [X] T016 [US3] vi battery + baseline + surface freeze: run the full battery over the four vi chapters (words in bounds for 1.1/1.4/2.1; 1.3 unchanged; parity counts vs en; fence byte-identity mechanical check); regenerate specs/019-stack-refoundation/battery-baseline.txt (20 rows) and diff against T001's copy of 018's — exactly the six 1.1/1.4/2.1 rows differ (C3); surface freeze per C7: fresh `pnpm build`, sitemap URL set identical to T001's snapshot, `grep -rl RevisionNote relay-tutorial/app/` returns exactly the 8 revision-set pages, lib/tutorial.ts and the suggestions allowlist byte-untouched, spot-check both landings + a Part-1 sidebar render (C3/C4/C7/C8)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T017 Full quickstart sweep + handoff: execute quickstart.md steps 1–6 end to end (per-state gates from T012's assemblies, boot check, migration idempotence + isolation lane + lint-violation probes, fence/battery sweep, surface freeze, README/docs cross-check); audit `git status --porcelain` in BOTH submodules + parent against the plan's Scale/Scope inventory (no stray files); report to Dong: the rebase-recipe.md pointer, suggested commit messages for all three repos, the review list (vi read-throughs for 1.1/1.4/2.1, the 1.3 two-line fence, RevisionNote copy in both locales, tag strategy choice), and confirmation that Neon was never touched (all contracts)

---

## Dependencies

- Phase 1 → Phase 2 (T001's pins/probes feed T002–T005)
- Phase 2 strictly sequential: T002 → T003 → T004 → T005 (each state layers on the last)
- Phase 3 needs Phase 2 complete (fences paste from state files); T006 [P] anytime after T001; T007/T009/T010 sequential-ish (shared battery idioms), T008 [P] alongside
- Phase 4 needs Phase 2 (T012) and benefits from Phase 3 done (T013's recipe references final fence bytes)
- Phase 5 needs Phase 3 (vi mirrors en) and T006; T014 ∥ T015, then T016
- Phase 6 last

## Parallel Example

After T005: launch T006 (component) alongside T007 (en 1.1); after T011: T014 and T015 run in parallel (different files), T016 joins them.

## Implementation Strategy

MVP = Phase 1–3 (the English series teaches the new stack, platform states verified informally). Phases 4–5 make the revision checkable and bilingual; Phase 6 hands the five-commit sequence to Dong. Nothing ships until Dong commits/tags — the working tree + recipe IS the deliverable.
