---

description: "Task list for chapter 3.3 — The outbox"
---

# Tasks: Tutorial Chapter 3.3 — The Outbox

**Input**: Design documents from `/specs/023-chapter-3-3/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/events.md, quickstart.md

**Tests**: Test tasks ARE included. The spec requires them (FR-015) and seven success criteria are worded "verified by an automated test".

**Organization**: Grouped by user story. As in 3.1 and 3.2, the code story (US2) executes before the chapter story (US1) — see Dependencies for why that is a real constraint rather than a preference.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete work)
- **[Story]**: US1 = the chapter, US2 = the canonical code, US3 = English publication

## Path Conventions

Paths are written from the repository root across three trees: `relay-platform/`
(the monorepo), `relay-tutorial/` (the site), `docs/` (the source documents).

---

## Phase 1: Setup

**Purpose**: Record the starting state so any later failure is attributable.

- [X] T001 Record the pre-change baseline: run `pnpm lint && pnpm typecheck && pnpm test` then `pnpm test:integration` in `relay-platform/`, capture the **exit codes** as well as the counts, and save the per-package numbers to `specs/023-chapter-3-3/baseline.txt` (expected: 109 unit, 76 integration — chapter 3.2's closing counts; this file is what SC-008 compares against)
- [X] T002 [P] Bring the stores up including the broker (`RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 docker compose up -d --wait postgres redis nats`), then `pnpm build` and apply existing migrations with `relay-platform/services/api/dist/db/migrate.js`
- [X] T003 [P] Confirm the site baseline in `relay-tutorial/`: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:fences` — all green before any edit

**Checkpoint**: baseline recorded, broker reachable.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Settle the dependency question that decides the module's shape, then put the schema in place.

**⚠️ CRITICAL**: T004 comes first. Chapter 2.6 lost time to an ESM/CJS import failure discovered after the code was written (`ioredis`, TS2351); the api compiles as CommonJS and the NATS clients are ESM-first, so the import is proven before anything is built on it.

- [X] T004 Decide the NATS client empirically: install `nats@2.29.3` and `@nats-io/jetstream@3.4.0` in a scratch check, import each from a CommonJS NestJS context, publish one message to the compose broker, and record which one imports and publishes cleanly — plus the exact failure of the other if it fails — in `specs/023-chapter-3-3/research.md` under R11. Keep only the winner in `relay-platform/services/api/package.json`
- [X] T005 Add the `outbox` table to `relay-platform/services/api/src/db/schema.ts`, reproducing SAD §6.1 column-for-column, plus the partial index on unpublished rows with a DECISION comment recording that §6.1 defines no index (spec FR-008, data-model)
- [X] T006 Generate `relay-platform/services/api/migrations/0004_outbox.sql` with drizzle-kit and review it line by line before applying — read the generated SQL rather than trusting it, and record the review disposition in the file's header as 0002 and 0003 do
- [X] T007 Apply the migration with `relay-platform/services/api/dist/db/migrate.js` and verify with `psql \d outbox` that the table matches §6.1 and that the partial index exists with its predicate (spec FR-008)
- [X] T008 Prove the foundation changed nothing yet: run both lanes in `relay-platform/` and confirm the counts and exit codes match `specs/023-chapter-3-3/baseline.txt`

**Checkpoint**: the table, the index and the client are in place, and nothing has regressed.

---

## Phase 3: User Story 2 — The canonical code advances to `part3-ch3` (Priority: P2)

**Goal**: An event per state change that cannot be lost, a relay that moves it, and twelve invariants that hold.

**Independent Test**: At `part3-ch3` the Docker-free gate passes; with the stores up every integration lane passes including 2.8's journey; `dual-write-walk.mjs --mode=naive` loses an event under a real `SIGKILL` and `--mode=outbox` does not; two relays drain 200 rows with no double-publish.

### Tests for User Story 2 ⚠️

> Write these before the implementation and watch them fail. Every invariant below is a requirement, and a durability test that never failed proves nothing (2.8's rule).

- [X] T009 [P] [US2] Create `relay-platform/services/api/src/outbox/event.test.ts` — the envelope's shape from `data-model.md`, a stable `id` that survives being rebuilt from the same row (invariant 10, spec FR-013), the public field names in `data`, and the rule that no internal identifier appears
- [X] T010 [P] [US2] Create `relay-platform/services/api/src/outbox/publisher.test.ts` — the port is satisfied by a fake with no broker present, proving the destination is replaceable without touching the code that writes events (invariant 12, spec FR-014)
- [X] T011 [US2] Create `relay-platform/services/api/src/outbox/outbox.itest.ts` covering invariants 1–4 and 7–8 over a real database: one row per committed message; none for a rolled-back write (SC-004); **none for a recognised idempotent retry** (research R1 — this is the case a client on a flaky link would otherwise turn into two webhooks); one row per door with identical shape (spec FR-009, SC-005); the relay publishing and marking without republishing marked rows; and two concurrent relays publishing every row exactly once (SC-006)
- [X] T012 [US2] Add invariant 11 to `relay-platform/services/api/src/outbox/outbox.itest.ts`: capture stdout while the relay drains a batch and assert no message text and no credential appears — the relay logs counts and durations, never payloads (spec FR-017)

### Implementation for User Story 2

- [X] T013 [P] [US2] Create `relay-platform/services/api/src/outbox/event.ts` — the envelope built in ONE place, complete, so the relay never authors a field (ADR-04, research R7)
- [X] T014 [P] [US2] Create `relay-platform/services/api/src/outbox/publisher.ts` — the port: publish a subject, a deduplication id and a payload; nothing broker-specific in the signature
- [X] T015 [US2] Extend `relay-platform/services/api/src/db/repository.ts`: insert the outbox row inside `sendMessage`'s existing transaction, on the **inserted branch only** so a recognised retry writes no event (spec FR-009, FR-010, research R1, FR-MSG-04)
- [X] T016 [US2] Create `relay-platform/services/api/src/outbox/relay.ts` — `SELECT … FOR UPDATE SKIP LOCKED` over unpublished rows oldest-first, publish each, mark published, commit; poll on an interval when idle; publish **then** mark, never the reverse (spec FR-011, research R2, R3). State the batch size and interval as chosen numbers with reasons in the comment
- [X] T017 [US2] Create `relay-platform/services/api/src/outbox/jetstream.publisher.ts` — the adapter and the minimal `EVENTS` stream over `events.>` with file storage, created if absent; connection is lazy so the api starts with the broker unreachable (spec FR-012, research R6, R9)
- [X] T018 [US2] Create `relay-platform/services/api/src/outbox/outbox.module.ts` and wire it in `relay-platform/services/api/src/app.module.ts`; the relay is startable and stoppable independently of request handling, on by default, off via `RELAY_OUTBOX_RELAY=off` for suites that want a quiet database (contracts §internal seam)
- [X] T019 [US2] Start and stop the relay with the service in `relay-platform/services/api/src/main.ts`, and confirm by inspection that a failed broker connection does not prevent `listen` from resolving (spec FR-012, research R9)
- [X] T020 [US2] Add `RELAY_NATS_URL` to `turbo.json`'s `test:integration` env list and forward it in `relay-platform/packages/e2e/src/harness.ts` alongside the other store coordinates — Turborepo's strict env mode filters undeclared variables, which is exactly how 2.8's lane first failed
- [X] T021 [US2] Prove nothing broke: run `pnpm test` and `pnpm test:integration` in `relay-platform/`, **checking exit codes rather than grepping output**, and confirm every pre-existing suite passes with assertions unchanged in substance (spec FR-016, SC-008)

### The demonstration, and the crash

- [X] T022 [US2] Create `relay-platform/scripts/dual-write-walk.mjs` with `--mode=naive|outbox`, `--messages=N`, and a marker line printed between the commit and the publish so a parent can kill it there. The naive mode publishes after commit and lives ONLY in this script — no service ever contains that path (research R5)
- [X] T023 [US2] Add the crash cases to `relay-platform/services/api/src/outbox/outbox.itest.ts`: spawn `dual-write-walk.mjs` in each mode, `SIGKILL` it from the parent at the marker, and assert that naive loses the event (invariant 6, SC-003) while outbox keeps it unpublished and recoverable (invariant 5, SC-002). Assert the republished event carries the SAME `id` it was written with (invariant 10's integration half — this is the only place a real republish happens, and a deduplication key that changed on retry would make every consumer's dedupe useless). A real signal, not a thrown exception — an exception proves the error path a crash never reaches (research R4)
- [X] T024 [US2] Add the broker-outage case to `relay-platform/services/api/src/outbox/outbox.itest.ts` (invariant 9, SC-007): stop the broker container, write, assert writes still succeed and unpublished rows accumulate, start it again, and assert the backlog drains with no intervention — SAD §7's claim, tested rather than quoted
- [X] T025 [US2] Run the whole api lane and confirm all twelve invariants pass by name, then deliberately move the outbox insert in `relay-platform/services/api/src/db/repository.ts` outside the transaction and confirm at least one test in `relay-platform/services/api/src/outbox/outbox.itest.ts` fails (spec US2 acceptance 6) before restoring it

**Checkpoint**: events cannot be lost, the relay drains them, and the failure the chapter is about is reproducible on demand.

---

## Phase 4: User Story 1 — The chapter (Priority: P1) 🎯 the deliverable

**Goal**: A chapter that shows the dual-write bug happening before it shows the fix, and quotes only measured output.

**Independent Test**: A reader at the `part3-ch2` checkpoint reproduces both runs — the lost event and the surviving one — using only the chapter, and every claim traces to a document, an earlier chapter, or a recorded decision.

- [X] T026 [US1] Capture what the chapter will quote into `specs/023-chapter-3-3/captured-output.md` — both walk transcripts, the invariant test names as they print, the lane counts, the outbox-depth numbers from the broker-outage run, and the two-relay run — redacting any credential before saving (spec FR-020, SC-007)
- [X] T027 [P] [US1] Write 2–4 mermaid figures into `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/figures.ts` and validate each parses; verify flowcharts in the browser, since the parse harness cannot render them
- [X] T028 [US1] Write the chapter body in `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/page.mdx`: the dual-write problem demonstrated as a run before any solution (spec FR-002), the four options ADR-06 weighed including why publish-before-commit is worse than publish-after-commit (FR-003), the table quoted from SAD §6.1, a DECISION note for the one shape no document defines — the partial index (spec FR-006) — and a WHY box on why the event row joins the message's transaction rather than following it
- [X] T029 [US1] Add the semantics section to `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/page.mdx`: at-least-once stated plainly with the duplicate's resting place named (FR-004), **ordering explicitly not promised** with `data.seq` named as what does order things (research R8), and a TRAP drawn from a real failure met in Phase 3
- [X] T030 [US1] Add the two-guarantees section to `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/page.mdx`: why this event path exists alongside 2.6's Redis fan-out rather than replacing it — at-most-once live delivery beside at-least-once durable events, ADR-07 beside ADR-06 (FR-005)
- [X] T031 [US1] Add the deferrals to `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/page.mdx`, each with the chapter that owns it: subjects taxonomy, streams and consumers (3.4), webhook delivery and dead-lettering (3.5), outbox pruning, and FR-ANL-06's reconciliation job (FR-007)
- [X] T032 [US1] Generate the chapter's fences into `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/page.mdx` — **fifteen, enumerated so the count is checkable rather than approximate**:
  - **Seven hunked amendments** (each verified to apply cleanly to its published predecessor, spec FR-018): `relay-platform/services/api/src/db/schema.ts`, `relay-platform/services/api/src/db/repository.ts`, `relay-platform/services/api/src/app.module.ts`, `relay-platform/services/api/src/main.ts`, `relay-platform/services/api/package.json`, `relay-platform/turbo.json`, `relay-platform/packages/e2e/src/harness.ts`
  - **Five new source files**, whole-file: `event.ts`, `publisher.ts`, `jetstream.publisher.ts`, `relay.ts`, `outbox.module.ts`, all under `relay-platform/services/api/src/outbox/`
  - **One test file**, whole-file: `relay-platform/services/api/src/outbox/outbox.itest.ts` — the one that carries the chapter's argument (the twelve invariants and the crash proof)
  - **Two others**, whole-file: `relay-platform/services/api/migrations/0004_outbox.sql`, `relay-platform/scripts/dual-write-walk.mjs`

  **Not fenced**: `event.test.ts` and `publisher.test.ts`. The chapter describes them and quotes their names from captured output, which is what 3.2 did with three of its four new test files — fencing every test would spend the budget without teaching anything the prose does not already carry. Record the actual count against R11's 12–15 budget in `chapter-notes.md` either way; fifteen sits at its ceiling, so a single unplanned amendment puts this chapter over and that is worth saying out loud when it happens
- [X] T033 [US1] Measure the battery on `relay-tutorial/app/(en)/part-3/chapter-03/the-outbox/page.mdx` — 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one `SKIP AHEAD` naming `part3-ch3`, ≥1 forward reference, 2–4 figures, one closing `CHECKPOINT` — and adjust the prose until every threshold is met
- [X] T034 [US1] Verify traceability BEFORE publication (spec FR-019, SC-009): every `FR-*`/`NFR-*`/`DR-*`/`ADR-*` in the chapter exists in `docs/04-srs.md`, `docs/05-sad.md` or `docs/06-adr-deep-dives.md`, and every table and column named in prose exists in `relay-platform/services/api/src/db/schema.ts`

**Checkpoint**: the chapter is written against measured output and its identifiers are real.

---

## Phase 5: User Story 3 — English publication (Priority: P3)

**Goal**: 3.3 is reachable in English, with the Vietnamese edition honestly absent.

**Independent Test**: The site builds; the English path returns 200 and the Vietnamese 404; the listing shows 3.3 untranslated and 3.4–3.7 forthcoming.

- [X] T035 [US3] Flip the 3.3 entry in `relay-tutorial/lib/tutorial.ts` to `status: "published"` with `translatedIn: []` — English only, no Vietnamese edition (spec FR-001), and confirm 3.4–3.7 remain `forthcoming`
- [X] T036 [US3] Run `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`; the fence chain must replay every published chapter with no drift
- [X] T037 [US3] Serve the build (`pnpm start` in `relay-tutorial/`) and verify `/part-3/chapter-03/the-outbox` returns 200, `/vi/part-3/chapter-03/the-outbox` returns 404, every figure renders as SVG with no page errors, **and the page renders inside the reading shell** — `[data-series-sidebar]` present and the on-this-page rail present, both visible at desktop width (spec SC-010). The shell assertion is not ceremony: chapters 3.1 and 3.2 both passed a 200-and-figures check while rendering with **no sidebar and no rail**, because `app/(en)/part-3/layout.tsx` did not exist and nothing looked for it. A check that only asks whether a page loads cannot see a missing layout

**Checkpoint**: chapter 3.3 is live in English and the site's checks agree with the repository.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T038 Run the whole of `specs/023-chapter-3-3/quickstart.md` V1–V8 as written from the repository root and fix anything that does not reproduce
- [X] T039 Scan for leaked credentials and tenant data (spec FR-017, quickstart V7): search `specs/023-chapter-3-3/captured-output.md` and the published `page.mdx` for credential shapes and for message bodies in relay log lines
- [X] T040 [P] Write `specs/023-chapter-3-3/chapter-notes.md` — tag, fences (budgeted versus actual), amendments, documents touched, commands, verification results, findings the plan did not anticipate, and anything deferred with its reason
- [X] T041 [P] Record the chapter's battery row in `specs/023-chapter-3-3/battery.txt`, measured on the published page
- [X] T042 If Phase 2 or Phase 3 exposed a defect in an earlier chapter, fix it forward in `relay-platform/`, amend the affected chapter's `page.mdx` **in every locale that has one** — 3.2 learned that the hard way when a Vietnamese edition existed that research said did not — and record it in `chapter-notes.md` (spec FR-021)
- [X] T043 Remove temporary diagnostics and scratch checks not intended to ship (including T004's, and any candidate client left in `relay-platform/services/api/package.json`), and confirm `git status` in `relay-platform/` and `relay-tutorial/` shows only intended files

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)** → no dependencies.
- **Foundational (Phase 2)** → after Setup. Blocks every story. T004 blocks T017.
- **US2 (Phase 3)** → after Foundational. The largest phase and the one that must be finished before any prose is written.
- **US1 (Phase 4)** → after US2. A chapter cannot fence code that does not exist.
- **US3 (Phase 5)** → after US1.
- **Polish (Phase 6)** → after everything.

### Within-story ordering

- Tests (T009–T012) before implementation (T013–T020).
- T013 and T014 before T016: the relay moves envelopes through a port, so both must exist first.
- T015 before T011 can pass — but T011 is written first and watched failing, which is the point.
- T017 after T004: the adapter is written against the client that was proven to import.
- T020 before T021: the lane cannot pass if the broker's address is filtered out of the task's environment.
- T022 before T023: the crash test kills the script the walk provides — one artifact, run by a reader and by the suite, so neither can rot alone.
- T024 needs a real broker container to stop, so it comes after T017 wires one.
- T026 (captured output) before T028–T031 (prose).
- T032 (fences) after all code is final, including anything T025's sabotage check changed back.
- T034 is Phase 4's gate: traceability is checked before anything is published.

### Parallel opportunities

- **Phase 1**: T002 and T003 are different repositories — parallel.
- **Phase 2**: none. T004–T008 are one ordered change to the platform's foundations.
- **Phase 3**: T009 and T010 are different files — parallel with each other and with T011's authoring. T013 and T014 are independent modules, both before T016. Nothing from T015 onward is parallel: the transaction, the relay and the adapter form one chain.
- **Phase 4**: T027 (figures) is parallel with the prose tasks.
- **Phase 6**: T040 and T041 touch different files — parallel.

Everything else shares a file or consumes the previous task's output.

---

## Parallel Example: User Story 2

```
# tests first, and these two are independent files:
T009  event.test.ts       (envelope shape, stable id)
T010  publisher.test.ts   (the port is replaceable)

# then the two leaf modules, in parallel:
T013  event.ts            T014  publisher.ts

# then, strictly in order:
T015  repository (the row, inside the transaction, inserted branch only)
    → T016  relay.ts → T017  jetstream.publisher.ts → T018  module wiring
    → T019  main.ts → T020  env plumbing → T021  full lane
```

---

## Implementation Strategy

**MVP scope**: US2 + US1 — the code at `part3-ch3` and the chapter documenting
it. As in 3.1 and 3.2, US1 alone is not shippable: a chapter whose fences match
nothing is the drift this series exists to prevent. US3 is a thin finishing
increment.

**Increment 1 — foundations (Phases 1–2).** The client question is answered
empirically, the table and its index exist. Stops cleanly: nothing behaves
differently yet and every suite still passes (T008).

**Increment 2 — the event path (Phase 3).** Events are written transactionally,
the relay drains them, and the crash is reproducible. There is one risky moment,
T015, because it puts a second write inside the transaction that guards every
message the platform accepts — paired immediately with T021's full lane run.

**Increment 3 — the chapter (Phase 4).** Written against captured output. Stops
cleanly as an unpublished page.

**Increment 4 — publication and polish (Phases 5–6).**

**Standing rule**: if the work exposes a defect in an earlier chapter, fix it
forward and say so (spec FR-021). Every chapter since 2.4 has done this.

**A note on the demonstration.** T022 and T023 build something unusual: code whose
job is to be wrong, and a test that proves it. Both are load-bearing. If the naive
mode ever stopped losing its event, the chapter's argument would collapse — and
the thing that catches that is T023 itself, which asserts the loss rather than
merely allowing it. T025's sabotage check covers the other direction (the outbox
insert leaving the transaction). The walk script is fenced like any other
artifact, so it cannot quietly stop compiling either.

**Not scheduled here — deferred a third time by decision (2026-08-08)**: the
constitution's 100% branch-coverage bar for ordering, idempotency and isolation
code (Principle VI, NFR-MNT-02) remains unmeasurable — no coverage tooling, no
CI. 3.1 deferred it; 3.2 deferred it by explicit decision recording that the
remedy would run **before 3.3**; it did not run, and **the owner has accepted the
third deferral so that 3.3 proceeds**. The tooling-and-CI feature moves to after
this chapter.

The trade is worth naming where the implementer will see it. This chapter claims
no event is ever lost, and it earns that claim with twelve named invariants and a
real `SIGKILL` rather than with prose. What it cannot show is which branches of
the relay and the write transaction those tests never enter. Write the tests as
if the instrument existed.
