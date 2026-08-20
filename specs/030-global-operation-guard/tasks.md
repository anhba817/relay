# Tasks: The fault that only shows up in company

**Feature**: `specs/030-global-operation-guard` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: three defences that make a test's dependence on being alone fail
alone — a trigger that raises inside the offending transaction, bait that makes a
fresh database behave like an aged one, and a refusal at the import line.

**Tests**: this feature's acceptance mechanism *is* a test battery. FR-017 and
SC-001 require the six recorded instances to be reintroduced one at a time and
each confirmed to fail, so the verification tasks below are the deliverable rather
than an optional extra.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story from spec.md this task serves
- Setup, Foundational, Verification and Close-out tasks carry no story label
- **A lettered id** (`T012a`) is a task inserted after review, numbered against
  the task it belongs beside

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to
`relay-tutorial/`, spec paths to `specs/030-global-operation-guard/`.

---

## Phase 1: Setup & baseline

- [X] T001 Record provenance in `specs/030-global-operation-guard/baseline.txt`: the submodule commits and tags this feature starts from, confirming `relay-platform` is at `part3-ch9` and both parent pins match their submodule HEADs
- [X] T002 Record the pre-change baseline in `specs/030-global-operation-guard/baseline.txt` — unit and integration counts per package, coverage figures, every per-file ratchet in force, and the **wall-clock time of the integration lane**, which is the baseline SC-004 measures against — not a literal. Chapter 3.9 finished on 242 unit and 223 integration; its recorded `3m15s` was measured at **213** integration tests and the final run was never timed, so it is indicative and this task's number is the one that counts
- [X] T003 **Record the polluted-database census** in `specs/030-global-operation-guard/baseline.txt` — unpublished outbox rows, due deliveries, undelivered notifications, sweepable endpoints and total environments on the development database. Research R1 measured 190 / 8,364 / 14 / 35 / 17,542; the numbers only go up, and the whole feature rests on the gap between this and a fresh database
- [X] T004 **Prove the fresh database currently proves nothing** (quickstart V1): create and migrate a database, run the api integration lane against it, and record that it passes. Research measured 177 passed. This is the number SC-001 is a delta against — today zero of six instances fail under the conditions the feature promises
- [X] T005 [P] Add a reusable `specs/030-global-operation-guard/fresh-db.sh` that creates, migrates and optionally drops a scratch database. Every verification step below runs against a fresh one, and a step that needs six manual commands is a step that gets skipped
- [X] T005a Create the `packages/test-harness/` workspace package (`packages/*` is already a `pnpm-workspace.yaml` glob). **A package rather than a directory inside `services/api`**, because five configs across four packages import it and a gateway test lane reaching into another service's `src/` is a worse precedent than a shared package, even in test code
- [X] T005b Give it everything a package here needs, copying **`@relay/e2e`'s shape**: `package.json` with `exports`, its own `pg`, and a `typecheck` script — **and no `test` script**. Without `typecheck` the package is silently skipped by `turbo run typecheck`, so the one thing built to catch mistakes would never be typechecked; with a `test` script and no test files, `vitest run` exits 1 and breaks `pnpm test`. `@relay/e2e` is the existing package with exactly this pair
- [X] T005c Add `packages/test-harness/tsconfig.json`. Both `packages/config` and `packages/service-kit` have one; a package without it is not typechecked even with the script
- [X] T005d **Reference the harness from the five configs by path, not by package name.** By-name would mean adding `@relay/test-harness` to four `devDependencies` plus the repository root, which has no workspace dependencies today. `setupFiles` and `globalSetup` take paths, and `pg` still resolves from the harness's own `node_modules` because Node resolves from the importing file's location rather than the config's
- [X] T005e **Record why the guard is PL/pgSQL before writing any of it**, with research R6 and R10 as the measurements. **Not an ADR**: constitution VII legislates the language services are implemented in, and nine `.sql` files already exist with the constitution's own endorsement, so there is nothing for a superseding ADR to supersede. **Moved here from close-out** because a constitution question settled after the code that depends on it is settled too late
- [~] T005f **Put it in `docs/07-tutorial-plan.md`'s "Work that publishes no chapter" section and in the header of `packages/test-harness/src/sentinel.sql`** — not in `docs/06-adr-deep-dives.md`, which an earlier draft named without anyone opening it. That file is eighteen sections all shaped `## ADR-nn — …` following a fixed Problem/Options/Analysis/Decision/Consequences/Revisit shape, declares itself companion to `docs/05-sad.md` §9 where `ADR-01`…`ADR-18` live, and closes with a heading that counts them: **"Reading the eighteen together"**. A non-ADR note would be the only section of its kind and would sit outside a count baked into a heading. The plan section already records this feature; the SQL header is where a reader meets the procedural SQL

**Checkpoint**: the starting numbers exist, and the gap the feature closes is measured rather than asserted.

---

## Phase 2: Foundational — the sentinel

**Blocking.** US1 and US2 both need the sentinel to exist. Nothing observable yet.

- [ ] T006 Create `packages/test-harness/src/sentinel.ts`: **one sentinel per test file**, its ids derived from the file path so they are stable across runs and unique across files, every row named `__sentinel__:<file>` (data-model, FR-023). **Not one shared sentinel** — files execute in parallel, so a shared one means one file's planting deletes rows another file is mid-test against (research R12)
- [ ] T006a Create the registry the per-file sentinel needs: `__sentinel_environments (environment_id uuid primary key, owner text not null)`, installed beside the trigger. With one sentinel the trigger could compare against a literal uuid; with one per file it tests membership, and `owner` is what lets the refusal name whose rows were taken
- [ ] T007 **Derive the bait sizes from the exported batch constants**, never literals (research R7): `2 × max(BATCH_SIZE)` where the maximum is `outbox/relay.ts`'s 100 and `sweepDisabledEndpoints`'s 100. A literal goes stale the first time a default rises, and it goes stale silently — the bait simply stops being bait
- [ ] T008 **The sentinel human carries no email address** in `packages/test-harness/src/sentinel.ts`, with the reason recorded beside it (research R4): 200 addressable bait notifications turned one suite's drain into 200 SMTP sends and a ten-second timeout. Unaddressable makes each bait row cost one log line, through the branch FR-WHK-07's unaddressable case already covers
- [ ] T009 Write the planting function in `packages/test-harness/src/sentinel.ts` — **delete this file's sentinel rows then re-insert**, rather than `ON CONFLICT`. The environment id makes the delete exact, and the seeder must not become the accumulation it exists to simulate (FR-003)
- [ ] T009a **Plant through a dedicated `pg.Client` that never enters the suite's pool**, created with the exemption in its options and closed before the first test (FR-024). Deleting a sentinel row is exactly what the trigger forbids, so the seeder needs the exemption — and a connection carrying it that a test later reused would leave that test unguarded. Circular until the connection is separate (research R12)
- [ ] T009b **Watch `packages/test-harness/src/sentinel.ts` fail to plant once before trusting it.** Research hit `webhook_endpoints_disabled_check` re-planting the endpoint: a row cannot be `enabled` with a `disabled_reason` set. Plant against a fresh database and read the constraint errors rather than assuming the insert order is right

**Checkpoint**: the bait can be planted and re-planted, and its sizes track the constants.

---

## Phase 3: User Story 2 — a writer-shape fault names itself (Priority: P1 in build order)

**Built first despite being spec-P2**, because it is the control the other two only prompt for, and because it needs no bait.

**Goal**: a test that mutates rows belonging to no test fails in its own stack, alone.

**Independent test**: quickstart V3 — reintroduce instance 6 into `notifications.itest.ts` and run only that file against a fresh database.

- [ ] T010 [US2] Write `packages/test-harness/src/sentinel.sql`: the `__sentinel_guard()` PL/pgSQL function and one `BEFORE UPDATE OR DELETE` row trigger per guarded table, firing when `OLD.environment_id` is **in `__sentinel_environments`**. Guarded tables are those carrying `environment_id`: `webhook_endpoints`, `webhook_deliveries`, `webhook_disable_notifications`, `channels`, `users`
- [ ] T010a [US2] **Record in `sentinel.sql` that `outbox` cannot be guarded** and why — it carries no `environment_id` because it is platform bookkeeping, so its bait is protected by the reader mechanism only. A gap named in the file that would otherwise look complete
- [ ] T011 [US2] Match the refusal message to `contracts/guard.md` exactly: the `global-operation guard:` prefix, the schema and table, the row id, and the clause `which belongs to no test`. **No suggested fix** — the right alternative depends on what the test meant, and a guess printed as advice is worse than silence
- [ ] T012 [US2] Read the exemption in `packages/test-harness/src/sentinel.sql` with `current_setting('relay.allow_global', true)`, so a connection that never carried it gets null and null is refusal
- [ ] T012a [US2] **Carry the exemption as a connection option, not a `SET` statement** (FR-020): the setup file rewrites `process.env.DATABASE_URL` with `?options=-c%20relay.allow_global%3Don`. **Measured**: a `SET` issued through a pool of three landed on two of five checkouts — `["on",null,null,"on",null]` — so the naive version produces an exempt suite that fails two times in five (research R10). The connection string rather than the pool's config object, because that needs no change to `createPool()`
- [ ] T012b [US2] **Rewrite it at `setup.ts`'s module scope, never inside a hook** (FR-026). Measured: a setup file's top-level code runs before the test file's module scope — `setup-toplevel; testfile-module;` — and **four suites create their pool at module scope**: `db/history-drift.itest.ts`, `db/repository.itest.ts`, `messages/history.itest.ts`, `messages/idempotency.itest.ts`. An exemption set in `beforeAll` would arrive after their pool already exists. None of the six exempt suites is written that way today, so the exposure is nil **by luck** — which is the pattern this whole feature is about. Bait planting stays in `beforeAll`, because it is async database work
- [ ] T013 [US2] Create `packages/test-harness/src/global-setup.ts` to install the function and triggers once per lane, and wire it as `globalSetup` in `services/api/vitest.integration.config.mts`
- [ ] T013a [US2] **Migrate before installing.** `globalSetup` runs before every suite, and six suites call `migrate(pool)` in their own `beforeAll` — so on an unmigrated database `CREATE TRIGGER … ON webhook_endpoints` hits a table that does not exist and the lane dies before a single test. CI is safe (`node services/api/dist/db/migrate.js` runs before `pnpm test:integration`) and `fresh-db.sh` migrates, so only a direct developer run is exposed. Calling `migrate()` first is idempotent — it keys on `schema_migrations` — and makes the lane self-sufficient rather than dependent on somebody else having migrated
- [ ] T013b [US2] **The trigger must exist only in test databases.** It is created from `packages/test-harness/src/global-setup.ts` and never from `services/api/migrations/` — otherwise the api service ships a trigger whose only purpose is to reject its own legitimate sweeps (constitution IV, plan's Complexity Tracking). Assert it: a test that confirms `migrations/` contains no `CREATE TRIGGER`
- [ ] T014 [US2] Create `packages/test-harness/src/exempt.ts` — **a list of paths, each with its reason beside it**, never a pattern (FR-015). A pattern silently absorbs the next file added, which is the failure mode this whole feature is about
- [ ] T014a [US2] Populate it with the six measured in research R5: `outbox/outbox.itest.ts`, `webhooks/deliveries.itest.ts`, `webhooks/test-event.itest.ts`, `webhooks/attempts.itest.ts`, `notifications/notifications.itest.ts`, `dispatcher/dispatcher.itest.ts`. **The exemption list is a precondition, not a refinement** — an ordinary lane run disabled the sentinel endpoint before any deliberate fault existed
- [ ] T015 [US2] Create `packages/test-harness/src/setup.ts` as `setupFiles`: set the exemption when the file under test is on the list, and not otherwise. **No test sets it directly** — a test that can exempt itself is not guarded
- [ ] T016 [US2] Give `services/dispatcher/vitest.integration.config.mts` the same two hooks, keeping its 120-second timeouts
- [ ] T016a [US2] **Give the other three lanes exemption handling too** (FR-021): `services/gateway/vitest.integration.config.mts`, `packages/e2e/vitest.integration.config.mts` and `relay-platform/vitest.coverage.config.mts`. The trigger is database state and outlives whichever lane installed it, so every lane pointed at that database meets it. **The coverage lane is the sharp one** — it runs every `*.itest.ts` in one process with no `setupFiles` and no `globalSetup`, so it would meet the trigger with no way to answer and fail all six exempt suites (research R11)
- [ ] T016b [US2] **Bait goes to the api and dispatcher lanes only** (FR-022). The gateway and e2e lanes get exemption handling and no bait: neither holds a reader-shape fault, and planting changes a suite's workload for no return — which is the failure research R4 measured
- [ ] T016c [US2] **Fail a non-exempt file at startup if it has a relay enabled** (FR-025). Both relays catch and log their own errors, so a refusal raised inside one is a log line and a green lane (research R13). Every suite that spawns an api child sets all four flags off today — `harness.ts`, `dispatcher.itest.ts`, `gateway/limits.itest.ts` and `gateway/session.itest.ts`, **four files**, measured rather than estimated — and this makes it checked
- [ ] T017 [US2] **Verify instance 6 fails alone** (quickstart V3): reintroduce `sweepDisabledEndpoints(db)` into `notifications.itest.ts`'s `disable()` helper, run only that file against a fresh database, confirm the trigger's message appears in that test's own stack, revert with `git checkout --` and confirm byte-identical by `md5sum`
- [ ] T017a [US2] **Commit before the reintroduction, not just before the battery.** Chapter 3.9 lost a fix to exactly this revert step, in the chapter that warned about it twice in bold — because "commit before the battery" is satisfiable once and the battery is a loop

**Checkpoint**: the writer shape fails alone, and the six suites that operate globally on purpose still pass.

---

## Phase 4: User Story 1 — a reader-shape fault fails on the first run (Priority: P2 in build order)

**Goal**: a fresh database behaves like an aged one, so a test that asserts on an unbounded global batch fails immediately.

**Independent test**: quickstart V4 — reintroduce instances 1 to 5, one at a time, each against a fresh database.

- [ ] T018 [US1] Plant the bait **per file, into that file's own sentinel**, in a `beforeAll` from `packages/test-harness/src/setup.ts`. Research R2 measured three of the four baits eaten in a single lane pass, so a one-shot `globalSetup` seeder protects whichever suite runs first and nothing after it
- [ ] T018a [US1] Record in `setup.ts` that per-file planting and a per-file sentinel are one decision, not two: files run in parallel — no integration config overrides `fileParallelism` — so planting into a shared sentinel would delete rows another file is mid-test against (research R12). The trigger also makes the bait durable for non-exempt files, which is why only exempt suites can consume it
- [ ] T019 [US1] Confirm planting is idempotent across repeated lane runs on the same database (quickstart V6): each file's bait is the same size at the end of a run as at the start, each sentinel holds exactly one endpoint, and `__sentinel_environments` holds one row per test file rather than one per run
- [ ] T020 [US1] **Verify each of instances 1 to 5 fails alone**, one at a time, each against a fresh database, each reverted and confirmed byte-identical: the sweep's missing bound and the drain that held a lock in `deliveries.itest.ts`, the fixed catch-up budget in `consumer.itest.ts`, the `count(*)` comparison in `signup.itest.ts`, and the default batch in `dispatcher.itest.ts`
- [ ] T020a [US1] **Commit before every one of the five**, per T017a
- [ ] T021 [US1] Exclude `packages/test-harness/src/**` from coverage in `relay-platform/vitest.coverage.config.mts`, beside `**/main.ts` and `**/*.module.ts`, for the reason recorded there: counting how much of the lane's own scaffolding a test touched is not what "business logic" means

**Checkpoint**: all six recorded instances fail alone. SC-001 is met.

---

## Phase 5: User Story 3 — the fault is harder to write (Priority: P3)

**Goal**: the compiler and the linter object before the code runs.

**Independent test**: quickstart V7 — add a global-admin import to any non-exempt `*.itest.ts` and run lint.

- [ ] T022 [P] [US3] Remove the default from `sweepDisabledEndpoints(db, limit = 100)` in `services/api/src/db/repository.ts`. It is the last of the **four** batch-taking functions to carry one — `drainOutbox`, `drainDueDeliveries` and `drainDisableNotifications` already require it
- [ ] T022a [US3] **Record in `services/api/src/db/repository.ts`, beside the signature, that this would not have prevented instance 6** (research R8). `sweepDisabledEndpoints(db, 10_000)` is worse, not better. The required argument is a prompt to think about whose rows are in scope; the trigger is the control. A comment claiming otherwise would be a comment that teaches the wrong lesson
- [ ] T022b [US3] **Record the full taxonomy in `services/api/src/db/repository.ts`** where the functions live (FR-012b): four take a batch size, two return a global count and have nothing to bound, and two cross environments but take an id and are bounded by construction. The missing third category is why three documents asserted "five" when the answer is four — and the next person adding a cross-environment function reads this file, not the spec
- [ ] T023 [US3] Fix every caller the removed default breaks. The compiler finds them; record how many there were in `specs/030-global-operation-guard/baseline.txt`
- [ ] T023a [US3] **Add `packages/test-harness/**` to the `pg`/`drizzle-orm`/`ioredis` ignores list** in `relay-platform/eslint.config.mjs`. That rule ignores five paths today and the harness is on none of them, so the first `pnpm lint` after T005a fails. **A different rule from T024's** — this one restricts the driver, that one restricts the global admin functions, and the two have separate ignores lists that must both be right
- [ ] T024 [US3] Add the `no-restricted-imports` entry to `relay-platform/eslint.config.mjs` using `importNames` for the six global-admin functions — `drainOutbox`, `drainDueDeliveries`, `drainDisableNotifications`, `sweepDisabledEndpoints`, `outboxDepth`, `pendingDeliveryDepth` — restricted in `*.itest.ts`, alongside the existing `pg`, `drizzle-orm` and `ioredis` entries whose comment states the principle
- [ ] T024a [US3] Include the two `*Depth` functions in `relay-platform/eslint.config.mjs`'s entry and say why: they return counts across every environment, which is the exact shape of instance 4 — a global `count(*)` compared against itself, twice in one file, four chapters apart. **They take no batch size and cannot** — a count has nothing to bound — so FR-012a restricts them from tests rather than FR-012 fixing them. An earlier draft's "every cross-environment function must require a batch size" was false of these two
- [ ] T025 [US3] Write the lint message to name the alternative, per `contracts/guard.md`. Unlike the trigger, the rule knows the call site, so it can be specific — and it points at `exempt.ts` for files that legitimately drive a drain
- [ ] T026 [US3] Add the six exempt files to the ignores list in `relay-platform/eslint.config.mjs`, and **confirm it agrees with `packages/test-harness/src/exempt.ts`**: a file exempt from the trigger but not from lint, or the reverse, is a trap for whoever adds the seventh
- [ ] T027 [US3] **Record what the rule does not catch** in `relay-platform/eslint.config.mjs`'s message and in `contracts/guard.md`: indirect calls through a helper, and raw SQL. The trigger covers both. A rule trusted further than it goes is worse than no rule

---

## Phase 6: Fix what this exposes

**Sized by measurement, not estimate.** Research R3 found two failures on a fresh database with a one-shot seeder. Per-file planting will find more, and the count is a finding to record rather than a number to predict.

- [ ] T028 Run the whole integration lane against a fresh database with the bait and the trigger in place, and **record every failure** in `specs/030-global-operation-guard/baseline.txt` before fixing any of them
- [ ] T029 **Confirm or discard R3's first hypothesis**: `outbox.itest.ts` invariant 7, which R3 measured failing because the relay's default batch of 100 never reaches the test's own rows. **R3 measured it under a design that no longer exists** — a one-shot shared sentinel, no trigger — and it passed when re-run alone because the bait had already been eaten. If T028 confirms it, fix it and record the shape (reader) beside the fix; if T028 does not, say so rather than fixing a test that is not failing
- [ ] T030 **Confirm or discard R3's second hypothesis**: `notifications.itest.ts`'s content test, which R3 measured timing out at 10 seconds because 200 addressable bait notifications became 200 SMTP sends. T008's unaddressable sentinel is designed to remove that cause, so this one is expected to be discarded — say that rather than claiming a fix
- [ ] T031 Fix every other failure T028 recorded in `specs/030-global-operation-guard/baseline.txt`, each labelled reader or writer in the file it fixes. **A fix that changes an assertion from a global result to the test's own row is a reader fix; a fix that stops the test performing a global operation is a writer fix.** The labels are what makes the count meaningful next time
- [ ] T032 **Grep `services/*/src/**/*.itest.ts` for the class while the first instance is on screen.** Chapter 3.7's finding, and the reason instance 4 existed: chapter 3.3 fixed the identical assertion a hundred lines up in the same file and did not look further down. Fixing an instance is not fixing a class

---

## Phase 7: Verification

- [ ] T033 Run both lanes and coverage; confirm every pre-existing suite passes and record the counts. Coverage must not fall below 89.50% statements and 82.73% branches
- [ ] T034 **Twenty consecutive integration runs, zero false positives** (quickstart V9, SC-003). This is the step most likely to be skipped for costing twenty times three minutes, and the step that says the guard does not cry wolf. Chapter 3.7 spent four attempts and about four hours getting twenty clean runs, and found four faults doing it
- [ ] T035 Measure the lane's wall-clock time against **T002's** baseline — same machine, same test count — and record it in `specs/030-global-operation-guard/baseline.txt`, confirming growth under 10 seconds (SC-004). Record the number, not the verdict
- [ ] T036 Run quickstart V0 to V11 end to end, reading exit codes rather than output
- [ ] T037 Capture the transcripts into `specs/030-global-operation-guard/captured-output.md`: the trigger's refusal and the exempt session's success, one reintroduction failing alone, the fresh-database baseline from T004, and the twenty-run result. **Capture rather than describe** — chapter 3.8's header bug was found by printing a whole response and not by any of the eighteen tests asserting on its fields
- [ ] T038 Scan `captured-output.md` for leaked credentials, recording the patterns searched rather than only the verdict. The sentinel's signing secret is a literal in `sentinel.ts` and must not reach a transcript

---

## Phase 8: Close-out

- [ ] T039 Generate the fences from the real files and put **every one of them in `relay-tutorial/fences/post-series.md`** — none in a chapter, because this work teaches none (FR-018). Extend existing sections rather than adding second ones for files already amended there
- [ ] T039a **Check `post-series.md`'s title list before generating, not after, and match on the full path.** This feature touches `services/api/src/db/repository.ts`, `eslint.config.mjs` and both vitest configs; `dispatcher.itest.ts`, `deliveries.itest.ts`, `signup.itest.ts` and `credentials.itest.ts` are already amended there, and a second section under an existing diff breaks its pre-image
- [ ] T040 Confirm `docs/07-tutorial-plan.md`'s "Work that publishes no chapter" section still describes what shipped, and correct the instance count if Phase 6 found more
- [ ] T041 Run `pnpm check:fences`, `pnpm check:docs`, `pnpm lint` and `pnpm build` in `relay-tutorial/`, reading exit codes
- [ ] T042 Traceability: confirm every `FR-*`/`NFR-*`/`ADR-*` this feature's **source comments** cite resolves in `docs/` or the constitution. Chapter 3.8 leaked 59 feature-local `FR-0xx` ids into comments written by someone who had just fixed that same leak — so the FR-001…FR-019 in this feature's spec must not appear in a single line of code
- [ ] T043 Write `specs/030-global-operation-guard/chapter-notes.md` from what happened rather than what was planned, including the parts that went badly
- [ ] T043a **Record in `specs/030-global-operation-guard/chapter-notes.md` whether the design survived.** Research replaced the spec's checksum with a trigger before a line was written; the notes should say whether the trigger survived contact with the lane, and what it cost that the plan did not predict
- [ ] T044 **Confirm T005e's note still describes what shipped**, in both places T005f put it. The decision itself moved to the setup phase, because an ADR is immutable once accepted and a constitution question settled after the code is settled too late. This task only checks the note against the delivered design
- [ ] T045 Tag `relay-platform` at the close-out commit. **Not a `part3-chN` tag** — this publishes no chapter, so the tag names the feature

---

## Dependencies

```
Phase 1 (baseline)
    ↓
Phase 2 (the sentinel)  ← blocking: US1 and US2 both need it
    ↓
    ├─→ Phase 3 (US2, the trigger)     ← no bait needed; ship first
    │        ↓
    ├─→ Phase 4 (US1, the bait)        ← durable once the trigger exists
    │        ↓
    └─→ Phase 5 (US3, the call site)   ← independent of both
             ↓
Phase 6 (fix what this exposes)  ← needs Phase 3 and 4 landed
    ↓
Phase 7 (verification) → Phase 8 (close-out)
```

**Story independence.** US2 ships without US1: the trigger needs the sentinel
rows, which Phase 2 provides, and not the bait's sizes. US1 ships without US2,
though its bait is then edible. US3 ships alone and catches the least.

**Three orderings that matter**, all found by the analysis pass rather than the
plan:

- **T014a before T017.** An ordinary lane run disables the sentinel endpoint, so
  the trigger without its exemption list fails six suites for the right reason and
  the wrong cause.
- **T012a before T017.** The exemption must ride every pooled connection. Verified
  with a `SET` through a pool: two of five checkouts carried it. Without T012a an
  exempt suite fails two times in five and the whole feature looks like the
  flakiness it exists to remove.
- **T016a before any lane runs twice.** The trigger is database state. Install it
  from the api lane and a developer's next `pnpm coverage` meets it with no hook at
  all.

**And one that has to happen before code**: T005e, the second-language note. An
ADR is immutable once accepted; a constitution question answered after the
implementation is answered too late.

---

## Parallel opportunities

- **Phase 1**: T005 alongside T001 to T004.
- **Phase 3**: T010 and T014 touch different files. T016 (the dispatcher's config)
  is independent of the api's wiring.
- **Phase 5**: T022 and T024 are different files and can land together; T023
  follows T022 because the compiler decides what it breaks.
- **Phase 6**: every fix T031 covers is its own file, so they parallelise once
  T028 has recorded the list.

---

## Implementation strategy

**MVP is Phase 3.** The trigger alone closes the writer shape — the one this
project caused rather than inherited — and it is the only defence that attributes
exactly and sees raw SQL. Shipping it and stopping would leave the reader shape
where it is today, which is defended by five past fixes and nothing structural.

**Then Phase 4**, because four of the six recorded instances were reader-shape and all
four were in files that Phase 3 now exempts. The composition table in
`contracts/guard.md` is the argument: the bait is the only one of the three
defences that addresses the reader shape at all, and the only one whose absence is
silent.

**Phase 5 last**, and honestly labelled: the required limit would not have
prevented instance 6, and the lint rule catches an import but not a helper and not
raw SQL. It is the cheapest defence and the one a reader is most likely to
overestimate.

---

## Notes

**On T034's twenty runs.** Three runs is not twenty and is not meant to be, but
this feature's whole claim is that the lane stops depending on luck — so the
number that matters is the one large enough to cross a threshold. Chapter 3.7
found two failures on runs 3 and 4 after ten clean ones, which is what a test
passing on headroom rather than on correctness looks like.

**On why the trigger goes first.** The spec ordered the bait P1 and the guard P2,
on the reasoning that the bait covers four of six instances and the guard depends
on it. Research inverted the build order without changing the priorities: the
trigger needs the sentinel *rows*, not the bait's *sizes*, and it makes the bait
durable rather than the other way round. The spec's priorities describe user
value; this is a build sequence.

**On the one thing this feature cannot demonstrate.** SC-008 — that the count of
instances does not increase in the chapter that follows — is verifiable only
later. It is the outcome the work exists for, and every one of the seven previous
instances was discovered exactly that way.

**On what the analysis pass cost, and why it was cheap.** Research R6 verified the
trigger in `psql` and declared attribution solved. The pass that read the harness
instead of the schema found three CRITICAL problems in that conclusion: the
exemption does not survive a connection pool (R10), the trigger outlives the lane
that installed it and three other lanes share the database (R11), and the seeder
needs the exemption it must not hand to a test (R12). All three were invisible in
a single interactive session, which is the one condition the test lane never
provides.

The pattern is the feature's own: **a mechanism verified under conditions the real
system does not have.** Instance 6 was a test that passed alone; R6 was a design
that worked in one session. Worth writing down, because the same reflex produced
both.
