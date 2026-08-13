---

description: "Task list for chapter 3.5 — Webhooks that survive the customer"
---

# Tasks: Tutorial Chapter 3.5 — Webhooks That Survive the Customer

**Input**: Design documents from `/specs/026-chapter-3-5/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/webhooks.md, contracts/dispatcher.md, quickstart.md

**Tests**: Test tasks ARE included. The spec requires them (FR-024, FR-026) and eleven of fourteen success criteria are worded "verified by an automated test".

**Organization**: Grouped by user story. As in every chapter since 3.1, the code story (US2) executes before the chapter story (US1) — see Dependencies for why that is a real constraint rather than a preference.

> **Regenerated 2026-08-10 after R1 was re-planned.** The measurement in T005–T007
> disqualified the broker-held retry delay: it survives a restart to within 3 ms but
> holds an acknowledgement slot while it waits, so dead endpoints starve healthy
> ones. The schedule is now a `next_attempt_at` column drained by a second relay in
> the api (research R1, R13). **T001–T007 are complete** and carry their `[X]`;
> everything from T008 reflects the re-planned design.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete work)
- **[Story]**: US1 = the chapter, US2 = the canonical code, US3 = publication

## Path Conventions

Paths are written from the repository root across three trees: `relay-platform/`
(the monorepo), `relay-tutorial/` (the site), `docs/` (the source documents).

---

## Phase 1: Setup

**Purpose**: Record the starting state so any later failure is attributable.

- [X] T001 Confirm chapter 3.4 is committed and both submodule pins bumped — verified clean trees in `relay-platform/`, `relay-tutorial/` and the parent repository, at `part3-ch4`
- [X] T002 Record the pre-change baseline in `specs/026-chapter-3-5/baseline.txt` — 133 unit, 97 integration, coverage 88.22%/79.01%, all exit 0, with every ratchet in force
- [X] T003 [P] Bring the stores up and apply existing migrations with `relay-platform/services/api/dist/db/migrate.js`
- [X] T004 [P] Confirm the site baseline in `relay-tutorial/`: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:fences` — 121 fences across 21 chapters

**Checkpoint**: baseline recorded, stores up, trees clean. ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Settle the retry mechanism by measurement, then put the schema in place.

**⚠️ The measurement is done and it changed the design.** Read research R1 before writing any scheduling code — the obvious implementation is the one that was disqualified.

- [X] T005 Measure whether a delayed redelivery survives a restart — recorded in `specs/026-chapter-3-5/research.md` R1: yes, 3 ms late in a fresh process
- [X] T006 Measure whether long-delayed messages hold the outstanding-acknowledgement budget — recorded in `specs/026-chapter-3-5/research.md` R1: yes, and it starves deliveries to healthy endpoints
- [X] T007 Record the decision in `specs/026-chapter-3-5/research.md` R1 and R13 — the schedule is a `next_attempt_at` column drained by a relay in the api, not a broker delay
- [X] T008 Add `webhook_endpoints` to `relay-platform/services/api/src/db/schema.ts` with a DECISION comment recording that FR-WHK-01/08 specify the behaviour and leave the shape open, and that this table **carries** `environment_id` unlike 3.3's and 3.4's (data-model §The rule the last two chapters were exceptions to)
- [X] T009 Add `webhook_deliveries` to `relay-platform/services/api/src/db/schema.ts` — the retry schedule, with `next_attempt_at` and `attempt` as the tier index, and a comment recording that this is chapter 3.3's outbox with one more predicate (research R1)
- [X] T010 Add `webhook_dead_letters` to `relay-platform/services/api/src/db/schema.ts`, tenant-scoped, with the seven-day retention rule stated in the comment (FR-WHK-04)
- [X] T011 Generate `relay-platform/services/api/migrations/0006_webhooks.sql` with drizzle-kit and review it line by line before applying, recording the review disposition in the file header as 0002–0005 do
- [X] T012 Apply the migration with `relay-platform/services/api/dist/db/migrate.js` and verify with `psql \d webhook_endpoints`, `\d webhook_deliveries` and `\d webhook_dead_letters` that all three carry `environment_id` and that the constraints match `specs/026-chapter-3-5/data-model.md`
- [X] T013 Prove the foundation changed nothing yet: run both lanes in `relay-platform/` and confirm counts and exit codes match `specs/026-chapter-3-5/baseline.txt`

**Checkpoint**: the retry mechanism is decided by measurement, three tables exist, nothing has regressed.

---

## Phase 3: User Story 2 — The canonical code advances to `part3-ch5` (Priority: P2)

**Goal**: Webhook endpoints with rotatable, encrypted signing secrets; a due-time retry schedule the api drains; and a new deployable service that signs, posts and reports.

**Independent Test**: At `part3-ch5` the Docker-free gate passes; every integration lane passes including 2.8's journey, 3.3's outbox suite and 3.4's consumer suite; a hostile endpoint drives the six tiers and the dead-letter path; stopping the dispatcher leaves message delivery untouched; a not-yet-due delivery holds no acknowledgement slot.

### The secret, and why it is not a hash

- [X] T014 [P] [US2] Write the failing unit test first in `relay-platform/services/api/src/webhooks/secret.test.ts`: a stored secret must be recoverable for signing, which is the property a hash cannot provide — the test that makes chapter 3.2's resemblance a trap rather than a template (research R3)
- [X] T015 [US2] Implement envelope encryption in `relay-platform/services/api/src/webhooks/secret.ts` using `node:crypto` AES-GCM, with the key read from configuration and never from the database, and a comment recording why NFR-SEC-02's second branch applies (spec FR-010)

### The management surface

- [X] T016 [P] [US2] Write cross-tenant tests first in `relay-platform/services/api/src/webhooks/webhooks.itest.ts`: no environment may list, read, rotate or delete another's endpoints (invariant 3, spec FR-011, constitution I)
- [X] T017 [P] [US2] Write the limit test in `relay-platform/services/api/src/webhooks/webhooks.itest.ts`: creating beyond the maximum is refused with an error that names the limit (invariant 1, FR-WHK-01)
- [X] T018 [P] [US2] Write the secret-exposure test in `relay-platform/services/api/src/webhooks/webhooks.itest.ts`: the secret is returned once at creation and by no subsequent read (invariant 2, spec FR-010)
- [X] T019 [US2] Add scoped endpoint operations to `relay-platform/services/api/src/db/repository.ts` — create, list, rotate, set-enabled, **soft-delete** — through the environment-bound constructor, never raw. A soft-deleted endpoint is excluded from every read (constitution I, data-model)
- [X] T020 [US2] Implement `relay-platform/services/api/src/webhooks/webhooks.service.ts`: the five-endpoint limit, URL validation (HTTPS, no loopback/link-local/private ranges) with a DECISION comment recording that no requirement mandates it (research R9, spec FR-008)
- [X] T021 [US2] Implement `relay-platform/services/api/src/webhooks/webhooks.controller.ts` — create, list, rotate-secret, enable/disable, delete — behind the existing credential guard, with errors that name the limit rather than the failure (spec FR-009, FR-012)
- [X] T022 [US2] Wire the webhooks module in `relay-platform/services/api/src/app.module.ts`

### The dispatcher package — scaffolded before anything is written into it

- [X] T023 [US2] Create `relay-platform/services/dispatcher/package.json` and `tsconfig.json` — frameworkless and ESM, mirroring `services/gateway`, with **no new dependency** (research R10, ADR-15). Scaffolded here because the signature tests below live in this package and cannot run until the workspace knows it exists

### The signature — pure, and verified by something that is not the signer

- [X] T024 [P] [US2] Write invariant 4 in `relay-platform/services/dispatcher/src/signature.test.ts`: a delivery's signature verifies against a verifier **written independently from the documented recipe**, not by calling the signing code (spec FR-017, SC-002)
- [X] T025 [P] [US2] Write invariant 5 in `relay-platform/services/dispatcher/src/signature.test.ts`: re-serialising the body before verifying fails — the documented trap, asserted rather than warned about (contracts/webhooks.md §Verifying)
- [X] T026 [US2] Implement `relay-platform/services/dispatcher/src/signature.ts`: HMAC-SHA256 over a canonical string of timestamp and raw body, with a scheme version, using `node:crypto` (spec FR-017, research R4)
- [X] T027 [US2] Write invariant 6 in `relay-platform/services/api/src/webhooks/webhooks.itest.ts`: across the **24-hour** rotation window both secrets verify; after it, only the new one — the window is a customer-facing promise fixed in `contracts/webhooks.md` §Rotation, not a tuning parameter (spec FR-010, research R4)

### The internal seam

- [X] T028 [P] [US2] Add the `platform` principal kind to `relay-platform/services/api/src/auth/principal.ts`, with a comment recording why an API key would be wrong — an `application` principal is scoped to one environment by construction (research R6)
- [X] T029 [US2] Accept the new kind on internal routes only in `relay-platform/services/api/src/auth/credential.guard.ts`, and write the test in `relay-platform/services/api/src/auth/credentials.itest.ts` that a public route rejects it (constitution I)
- [X] T030 [P] [US2] Define the dispatch contract schemas in `relay-platform/packages/protocol/src/internal.ts` — expand, fetch delivery material, report outcome — so both sides validate against one definition (chapter 2.5's pattern)
- [X] T031 [US2] Implement `relay-platform/services/api/src/internal/dispatch.controller.ts` exposing those three operations, wired in `relay-platform/services/api/src/internal/internal.module.ts` (contracts/dispatcher.md)

### The retry schedule — the re-planned core

- [X] T032 [US2] Write invariant 8 in `relay-platform/services/api/src/webhooks/deliveries.itest.ts`: one event matching N endpoints produces N delivery rows **in one transaction**, and expansion runs once however often the event is redelivered (research R2, R5)
- [X] T033 [US2] Implement expansion in `relay-platform/services/api/src/db/repository.ts`: chapter 3.4's claim and the N `webhook_deliveries` rows in a single transaction, so a partly-expanded event is impossible (research R2)
- [X] T034 [US2] Define the tiers as data in `relay-platform/services/api/src/webhooks/schedule.ts` — an immediate first attempt then 1 s, 5 s, 30 s, 5 min, 30 min, 2 h — each carrying its reason, with `attempt` as the index into it. **Seven attempts**: FR-WHK-03 contradicts itself and the author took the delay list over the count on 2026-08-10 (DECISION recorded in the file)
- [X] T035 [US2] Implement `recordAttemptOutcome` in `relay-platform/services/api/src/db/repository.ts`: idempotent on `(delivery_id, attempt)`, and in **one transaction** either mark delivered, or set the next tier's `next_attempt_at`, or dead-letter (contracts/dispatcher.md)
- [X] T036 [US2] Write invariants 9 and 10 in `relay-platform/services/api/src/webhooks/deliveries.itest.ts`: exactly six attempts with each `next_attempt_at` matching its tier; nothing published before it is due; **and a not-yet-due delivery holds no acknowledgement slot** — the assertion that would have caught the original design (FR-WHK-03, spec FR-024, SC-003, SC-004, research R1)
- [X] T037 [US2] Implement `drainDueDeliveries` in `relay-platform/services/api/src/db/repository.ts` — `SELECT … FOR UPDATE SKIP LOCKED` over pending rows where `next_attempt_at <= now()`, the shape `drainOutbox` already has with one more predicate (research R13)
- [X] T038 [US2] Implement the delivery relay in `relay-platform/services/api/src/webhooks/delivery-relay.ts`, reusing `createRelay` from chapter 3.3 rather than writing a second loop (research R13)
- [X] T039 [US2] Start and stop the delivery relay in `relay-platform/services/api/src/main.ts` and wire it in `relay-platform/services/api/src/app.module.ts`, with an off switch for suites that want a quiet table — chapter 3.3's finding 4 applies again, in advance this time
- [X] T040 [US2] Add the relay's env var to `relay-platform/turbo.json` and forward it in `relay-platform/packages/e2e/src/harness.ts`

### The new deployable

- [X] T041 [US2] Implement `relay-platform/services/dispatcher/src/api-client.ts`: the only road to state, with responses **parsed rather than assumed**, following `services/gateway/src/api-client.ts`
- [X] T042 [US2] Implement `relay-platform/services/dispatcher/src/main.ts`: two consumers, lazy connections, startable and stoppable — the api must serve writes with the dispatcher absent (spec FR-016)
- [X] T043 [US2] Implement `relay-platform/services/dispatcher/src/expand.ts`: consume `events.>`, call the api's expand operation, acknowledge — the dispatcher never writes the rows itself (constitution IV)
- [X] T044 [US2] Write invariant 7 in `relay-platform/services/dispatcher/src/dispatcher.itest.ts`: an endpoint receives only its subscribed event types (spec FR-021, SC-008). **Restore the `test:integration` script in `relay-platform/services/dispatcher/package.json` in the same commit** — it was removed when the package was scaffolded, because a declared lane with no test files exits 1, and `--passWithNoTests` would have bought a green lane by making an empty suite indistinguishable from a passing one (research R12's failure mode, in miniature)
- [X] T045 [US2] Implement `relay-platform/services/dispatcher/src/deliver.ts`: consume the deliveries stream, fetch material, sign, POST, report the outcome, then acknowledge — **never claim before posting**, because a crash in that gap loses a webhook silently (research R5)
- [X] T046 [US2] Write invariant 13 in `relay-platform/services/dispatcher/src/dispatcher.itest.ts`: a hanging endpoint is abandoned on the timeout and does not delay deliveries to other endpoints (FR-WHK-05, spec FR-020, SC-007)
- [X] T047 [US2] Implement the per-attempt timeout and per-endpoint concurrency bound in `relay-platform/services/dispatcher/src/deliver.ts`, with both numbers carrying their reasons as 3.4's acknowledgement deadline does (research R7)
- [X] T048 [US2] Write invariant 11 in `relay-platform/services/dispatcher/src/dispatcher.itest.ts` — **the invariant that decided the design**: a pending retry survives a restart of **both** the dispatcher and the api, because the schedule is a row held by neither (spec FR-023, SC-005)
- [X] T049 [US2] Write invariant 12 in `relay-platform/services/api/src/webhooks/deliveries.itest.ts`: an exhausted delivery is dead-lettered, retrievable, and replayable with its original event id so a deduplicating customer is unharmed, driven against the hostile endpoint (FR-WHK-04, spec FR-024, SC-006)
- [X] T050 [US2] Implement dead-letter recording and replay in `relay-platform/services/api/src/db/repository.ts` and `relay-platform/services/api/src/internal/dispatch.controller.ts`, using current endpoint configuration on replay (data-model)
- [X] T051 [US2] Write invariant 15 in `relay-platform/services/dispatcher/src/dispatcher.itest.ts`: no dispatcher log line contains a signing secret or a tenant's message body, at any level **including the error paths**, which is where a secret gets printed by accident (spec FR-025, SC-011, NFR-SEC-06 — the invariant chapter 3.4 carried and this chapter must not drop while handling a decryptable credential)
- [X] T052 [US2] Write invariant 16 in `relay-platform/services/dispatcher/src/dispatcher.itest.ts`: a delivered body is chapter 3.3's envelope and carries the event `id` a recipient deduplicates on — the field every claim about at-least-once rests on (spec FR-018)
- [X] T053 [US2] Write invariant 14 in `relay-platform/packages/e2e/src/webhooks.itest.ts`: with the dispatcher stopped, messages are delivered to end users normally and the backlog drains on its return (spec FR-016, SC-009)
- [X] T054 [US2] Write `relay-platform/services/api/Dockerfile` and `relay-platform/services/gateway/Dockerfile` — **the repository's first containers**, decided by the author on 2026-08-10 rather than leaving the dispatcher as the only containerised service. Multi-stage, pnpm workspace-aware, running the same `dist/` entry point the host runs
- [X] T055 [US2] Write `relay-platform/services/dispatcher/Dockerfile` in the same shape as the two above
- [X] T056 [P] [US2] Write `relay-platform/.dockerignore` covering `node_modules/`, `.git/`, `dist/`, `coverage/`, `*.log`, `.env*` — without it every build context is the whole workspace including every `node_modules`
- [X] T057 [US2] Add **all three services** to `relay-platform/compose.yaml` — api, gateway and dispatcher, each building from its Dockerfile — plus the dispatcher's tasks and env in `relay-platform/turbo.json`. Until now compose ran only the four stores

### The artifacts a reader runs

- [X] T058 [P] [US2] Write `relay-platform/scripts/hostile-endpoint.mjs` — fails, hangs or succeeds on command — the same artifact the integration suite drives, so neither it nor the tests can rot alone
- [X] T059 [P] [US2] Write `relay-platform/scripts/webhook-walk.mjs`, including `--print-signing-material` so a reader can verify a signature by hand in another language (quickstart V5)

### Measurement and regression

- [X] T060 [US2] Add the dispatcher's surface to `relay-platform/vitest.coverage.config.mts` and a dispatcher job to `.github/workflows/ci.yml` — a deployable outside the instrument leaves every ratchet green while measuring the wrong scope (research R12, Principle VI)
- [X] T061 [US2] Raise the `repository.ts` branch ratchet in `relay-platform/vitest.coverage.config.mts` to the level this chapter's work achieves — it sits at 86.30% against a ratchet of 85 and this chapter adds four operations to that file
- [X] T062 [US2] Run the sabotage check per `specs/026-chapter-3-5/quickstart.md` V3 — five mutations, including dropping the `next_attempt_at <= now()` predicate, which must fail invariants 9 and 10. Restore each file and verify byte-identical
- [X] T063 [US2] Run both lanes and confirm every pre-existing suite passes unchanged in substance, recording the chapter-end counts in `specs/026-chapter-3-5/baseline.txt` (spec FR-027, SC-012)
- [X] T064 [US2] Run `pnpm coverage` with the stores up, confirm exit 0 and that the dispatcher's files appear, recording the summary in `specs/026-chapter-3-5/captured-output.md` (quickstart V7)

**Checkpoint**: the code is provable, measured, separable, and its tests hold something.

---

## Phase 4: User Story 1 — The chapter (Priority: P1) 🎯

**Goal**: The prose, written from what the code actually does.

**Independent Test**: A reader at `part3-ch4` can follow the chapter to a signed delivery at an endpoint of their own, and verify the signature by hand using only the chapter.

- [X] T065 [US1] Capture every transcript the chapter will quote into `specs/026-chapter-3-5/captured-output.md` — R1's measurement, the invariant run, all three hostile-endpoint modes, the by-hand verification, the dispatcher-stopped demonstration, and the coverage summary (spec FR-031)
- [X] T066 [US1] Write the English chapter at `relay-tutorial/app/(en)/part-3/chapter-05/…/page.mdx`: 3.4's pattern applied to an HTTP effect and shown to fail; the guarantee chosen and the identifier handed over; the signature and its verification; the schedule; the dead letter (spec FR-002, FR-003, FR-004, FR-005, FR-006)
- [X] T067 [US1] Add the section to `relay-tutorial/app/(en)/part-3/chapter-05/…/page.mdx` explaining why the dispatcher is a separate service when the relay and recorder were not, and what it costs (spec FR-007)
- [X] T068 [US1] Add the section to `relay-tutorial/app/(en)/part-3/chapter-05/…/page.mdx` that names the dual write as a recurring pattern rather than solving it a third time in silence — R1's measurement, why the obvious retry mechanism was disqualified, and that the dual write is the standing cost of every hop between systems that cannot share a transaction (research R1)
- [X] T069 [P] [US1] Write the figures in `relay-tutorial/app/(en)/part-3/chapter-05/…/figures.ts` — the pattern breaking, the schedule as a due-time column, and where the dispatcher sits
- [X] T070 [US1] Measure the battery on the published page and record it in `specs/026-chapter-3-5/battery.txt`, confirming the SKIP AHEAD names `part3-ch5` and counting the fences against R11's revised 25–29 budget
- [X] T071 [US1] Traceability: every `FR-*`/`NFR-*`/`ADR-*` cited exists in a source document, every table and column named exists in `relay-platform/services/api/src/db/schema.ts` (spec SC-013)

**Checkpoint**: the chapter says only what the code does.

---

## Phase 5: User Story 3 — Publication in both locales (Priority: P3)

**Goal**: 3.5 reachable in English and Vietnamese, with fences mirrored.

**Independent Test**: Both locale paths return 200 with the reading shell and every figure rendered; the fence chain replays every published chapter.

- [X] T072 [US3] Translate the chapter to `relay-tutorial/app/(vi)/vi/part-3/chapter-05/…/page.mdx` and `figures.ts`, fences mirrored byte for byte (spec FR-001)
- [X] T073 [US3] Amend `relay-tutorial/lib/tutorial.ts`: 3.5 published, `translatedIn: ["vi"]`, with `readerProduces` in both languages
- [X] T074 [US3] Verify publication of `/part-3/chapter-05/…` and `/vi/part-3/chapter-05/…`: both 200, figures rendering as SVG in a headless browser, the reading shell present — a page that loads is not a page that is laid out (spec SC-014, quickstart V9)
- [X] T075 [US3] Run `pnpm check:fences` in `relay-tutorial/` and confirm every fenced file replays — **including every file this chapter's prose asserts**, the rule chapter 3.4 broke (spec FR-029)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T076 Amend `docs/07-tutorial-plan.md` to record the narrowed scope, the follow-on chapter, and the renumbering of Part 3's remaining chapters (spec FR-033)
- [ ] T077 [P] Run quickstart V1–V9 end to end from `specs/026-chapter-3-5/quickstart.md`, reading exit codes rather than grepping output
- [ ] T078 [P] Scan `specs/026-chapter-3-5/captured-output.md` for leaked credentials — **including signing secrets**, new this chapter and the most likely to be quoted innocently in a transcript showing a delivery; this scan covers the captured transcript while invariant 15 covers the running service's log output, and neither substitutes for the other (spec SC-011)
- [ ] T079 Write `specs/026-chapter-3-5/chapter-notes.md` from what happened rather than what was planned, including the budget-versus-actual fence count and what R1's measurement changed
- [ ] T080 Fix forward any defect this chapter exposes in an earlier chapter, in every locale that chapter has, and record it in `specs/026-chapter-3-5/chapter-notes.md` (spec FR-032)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: complete.
- **Foundational (Phase 2)**: T005–T007 complete, and they re-planned the design. T008–T013 block all of US2.
- **US2 (Phase 3)**: depends on Phase 2.
- **US1 (Phase 4)**: depends on **all** of US2.
- **US3 (Phase 5)**: depends on US1.
- **Polish (Phase 6)**: depends on all stories.

### Why US2 precedes US1, despite the priorities

The chapter is P1 and the code is P2, and the code is still built first. Prose in
this series is written from measured output: every fence must byte-match a
repository that runs (spec FR-028), and every transcript must come from a real run
(spec FR-031). Five of the last seven chapters changed a claim once their code was
real — and this chapter changed its *design* once a measurement was real. The
priority ordering describes value; the dependency describes physics.

### Within User Story 2

- The failing secret test (T014) before the implementation (T015) — it is what makes 3.2's resemblance a trap rather than a template.
- Cross-tenant tests (T016) before the management surface exists, so isolation is designed in rather than audited later.
- The dispatcher package (T023) before anything is written into it — a test in a package the workspace does not know about cannot run.
- The independent verifier (T024) before the signer (T026) — a verifier written after, from the signing code, proves only that the code agrees with itself.
- The internal contract (T030) before both sides that use it.
- **Expansion (T033) before the relay (T037–T038)**: there is nothing to drain until deliveries exist as rows.
- **The tier table (T034) before `recordAttemptOutcome` (T035)**: the outcome computes the next `next_attempt_at` from it.
- Each invariant test before the implementation that satisfies it.
- Coverage and CI wiring (T060) is part of creating the service, not a follow-up.

### Parallel Opportunities

- **Phase 2**: none. T008, T009 and T010 have no logical dependency on each other but all three edit `schema.ts`, so none carries `[P]` — the marker means "different files", and sharing one is exactly when it does not apply.
- **Phase 3**: the three management-surface tests (T016, T017, T018) are independent; the two signature tests (T024, T025) are independent; the three Dockerfiles (T054, T055) and the `.dockerignore` (T056) are independent of any service's source; the two scripts (T058, T059) are independent. **T057 is not** — compose cannot reference images the Dockerfiles have not defined.
- **Phase 4**: figures (T069) can be drawn while the prose is written.
- **Phase 6**: T077 and T078 are independent.

**Not parallel, despite appearances**: the invariants in
`services/dispatcher/src/dispatcher.itest.ts` (T044, T046, T048, T051, T052) all
edit one file, and those in `services/api/src/webhooks/deliveries.itest.ts` (T032,
T036, T049) edit another.

---

## Implementation Strategy

### MVP scope

**US2 through T045** — endpoints, encrypted secrets, the management surface, the
signature, the internal seam, delivery rows, the api's relay, and the dispatcher
posting one signed delivery successfully. At that point the chapter's central claim
is demonstrable: an event reaches a customer's endpoint with a signature they can
verify, from a service that cannot write the database, on a schedule that lives in
a column.

Everything after T045 is what the chapter's title is about — surviving the
customer — and it is where the risk lives.

### Incremental delivery

1. **Phase 1–2** → the mechanism is decided by measurement, three tables exist.
2. **T014–T022** → endpoints exist, tenant-isolated, with a secret that can sign.
3. **T023–T027** → the dispatcher package exists, and a signature a customer can verify.
4. **T028–T031** → the seam the dispatcher reaches state through.
5. **T032–T040** → deliveries are rows, and the api drains them when due. **The re-planned core.**
6. **T041–T045** → the service exists and delivers once. **MVP.**
7. **T046–T053** → it survives a customer who fails, hangs or never recovers.
8. **T054–T059** → all three services are containerised, compose runs them, and a reader can run the walk.
9. **T060–T064** → the instrument measures it and nothing regressed.
10. **Phase 4–6** → the chapter, the translation, the plan-of-record amendment.

### The three places this chapter is most likely to go wrong

**T036's second clause.** "A not-yet-due delivery holds no acknowledgement slot" is
the assertion that would have caught the original design. It is easy to write the
first clause, skip the second, and quietly reintroduce the starvation the
measurement found.

**T060/T061.** A new deployable outside the coverage instrument leaves every
existing ratchet green while measuring the wrong scope. And `repository.ts` has 1.3
points of margin before this chapter adds four operations to it.

*Done, and both halves of that prediction were wrong in the same direction —
the instrument was fine and the code was not.*

- **No config change was needed for inclusion, and no CI job either.** The
  coverage globs are `services/*/src/**`, so the dispatcher was measured the
  moment it existed; every CI command already runs at the workspace root, so a
  `dispatcher` job would have run the same commands twice. Running the
  instrument was the whole task — reading it, not extending it.
- **What running it found:** `expand.ts` at **0%**. The dispatcher's own suite
  reached expansion by calling `expandEventToDeliveries` against the database
  directly, so the consumer that decodes an event, asks the api to expand it and
  decides ack-or-terminate had never once executed under test. Four tests now
  drive it through the broker; the file is at 92%.
- **`repository.ts` went DOWN, not up** — 86.30% → **78.22%** branches, failing
  all four thresholds. `deliveryMaterial` and `pendingDeliveryDepth` were called
  only by the dispatcher, whose suite runs the api as a CHILD PROCESS whose
  coverage is not attributable. The one function in the platform that returns a
  customer's signing secret in plaintext was, by the only measure the
  constitution names, untested. Eleven tests later: **97.28 / 89.51 / 100 /
  98.99**, and the ratchet was raised to 89 branches / 97 statements rather than
  lowered to meet the code.
- **Two assertions were found to be vacuous while proving this.** The
  security test in `credentials.itest.ts` read `RELAY_INTERNAL_CREDENTIAL` and
  returned early when unset — and CI never set it, so the check standing between
  a platform credential and a public route did nothing on every build. And the
  dispatcher's "terminated, not retried" assertion could not fail, because
  `ack_wait` was 30 s and the test waited 2. Both are now unskippable, and the
  second required splitting `ackWaitMs` per consumer — a single knob shortened
  the DELIVER consumer too, and under the coverage lane's slower clock the
  broker redelivered attempts that were still in flight.

**T058/T059 — what the walk found.** The walk against `--mode=fail` stopped dead
after one attempt, and the fault was in the platform, not the script. The delivery
relay deduplicated its publishes on `row.id`, which is the SAME for all seven
attempts, so JetStream collapsed every retry into the first attempt's message. The
publish reported success, no message reached the dispatcher, and the row kept the
`dispatched_at` its claim had set — which only an outcome report clears, and no
outcome was ever coming. **Every failing webhook was retried exactly zero times**
and the whole of FR-WHK-03's schedule was unreachable.

Nothing caught it. `deliveries.itest.ts` drives `drainDueDeliveries` directly, with
no broker in the path; the dispatcher's suite used a fresh delivery for every case,
so the same delivery had never been published twice in any test. The key is now
`{delivery_id}:{attempt}` — a republished attempt is still recognisably the same
work, a NEW attempt is allowed to say it is new — and the dispatcher suite has the
regression test, verified to fail against the old key.

Two smaller things fell out of the same run. `--print-signing-material` was signing
the payload object as the script had built it, while the platform signs what comes
back out of `jsonb`, and PostgreSQL does not preserve key order — so the printed
signature was for a rendering that never went on the wire. And `deliver.ts`'s
`skipped` branch turned out to be covered only by accident, by leftover deliveries
other suites had left pointing at endpoints they had deleted, which made a ratchet
pinned on it move on its own. Both now have deliberate coverage.

**T045's ordering.** Post, then report, then acknowledge. Claiming before posting
turns the terminal hop at-most-once and loses webhooks silently — the failure
chapter 3.3 spent itself removing, reintroduced at the last hop.

---

## Notes

**On the fence budget.** R11 budgets **25–29**, revised upward by R1's re-plan and by
a wide margin the largest in the series. 3.3 budgeted 12–15 and shipped 19; 3.4
budgeted 15–18 and shipped 17, the first to land inside its estimate. If T070's
count approaches 29, that is the signal to check whether the narrowing decision
held — not to absorb the overrun quietly.

**On the second relay.** T038 is the moment the reader sees that chapter 3.3's
outbox was not a one-off for events but a general shape for any work the platform
owes itself and must not lose. Reuse `createRelay` rather than writing a second
loop; the reuse *is* the lesson, and a hand-rolled copy would hide it.

**On one artifact, not two.** T058's hostile endpoint is the same file the
integration suite drives, and T059's walk is the same script the chapter shows.
Chapters 3.3 and 3.4 each made this argument for their own walks.

**On the verifier that must not be the signer.** T024 is the one test a reasonable
engineer will be tempted to write the easy way. Calling the signing function to
verify proves the function agrees with itself, which is exactly what a customer —
who has only the documentation — cannot rely on. Write it from
`contracts/webhooks.md`, not from `signature.ts`.

**On what this chapter deliberately does not build.** The attempt log (FR-WHK-06)
and auto-disable (FR-WHK-07) belong to the follow-on chapter by the author's
decision, because auto-disable needs continuous-failure history and that history is
the attempt log. Email notification is deferred with no owner — FR-RTL-07 will need
the same infrastructure, and it deserves a home rather than arriving as a side
effect of a webhook chapter.
