# Tasks: The fault that only shows up in company

**Feature**: `specs/030-global-operation-guard` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: three defences that make a test's dependence on being alone fail
alone — a trigger that raises inside the offending transaction, bait that makes a
fresh database behave like an aged one, and a refusal at the import line.

**Tests**: this feature's acceptance mechanism *is* a test battery. FR-017 and
SC-001 require the seven recorded instances to be reintroduced one at a time and
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

- [ ] T001 Record provenance in `specs/030-global-operation-guard/baseline.txt`: the submodule commits and tags this feature starts from, confirming `relay-platform` is at `part3-ch9` and both parent pins match their submodule HEADs
- [ ] T002 Record the pre-change baseline in `specs/030-global-operation-guard/baseline.txt` — unit and integration counts per package, coverage figures, every per-file ratchet in force, and the **wall-clock time of the integration lane**, which SC-004 measures against. Chapter 3.9 finished on 242 unit, 223 integration, 3m15s
- [ ] T003 **Record the polluted-database census** in `specs/030-global-operation-guard/baseline.txt` — unpublished outbox rows, due deliveries, undelivered notifications, sweepable endpoints and total environments on the development database. Research R1 measured 190 / 8,364 / 14 / 35 / 17,542; the numbers only go up, and the whole feature rests on the gap between this and a fresh database
- [ ] T004 **Prove the fresh database currently proves nothing** (quickstart V1): create and migrate a database, run the api integration lane against it, and record that it passes. Research measured 177 passed. This is the number SC-001 is a delta against — today zero of seven instances fail under the conditions the feature promises
- [ ] T005 [P] Add a reusable `specs/030-global-operation-guard/fresh-db.sh` that creates, migrates and optionally drops a scratch database. Every verification step below runs against a fresh one, and a step that needs six manual commands is a step that gets skipped

**Checkpoint**: the starting numbers exist, and the gap the feature closes is measured rather than asserted.

---

## Phase 2: Foundational — the sentinel

**Blocking.** US1 and US2 both need the sentinel to exist. Nothing observable yet.

- [ ] T006 Create `services/api/src/testing/sentinel.ts`: the sentinel's six identifiers as named constants, using the reserved prefix `00000000-0000-4000-8000-0000000000NN` and the name `__sentinel__` (data-model). Literal UUIDs rather than generated ones, so a failure message can be matched against the document by eye
- [ ] T007 **Derive the bait sizes from the exported batch constants**, never literals (research R7): `2 × max(BATCH_SIZE)` where the maximum is `outbox/relay.ts`'s 100 and `sweepDisabledEndpoints`'s 100. A literal goes stale the first time a default rises, and it goes stale silently — the bait simply stops being bait
- [ ] T008 **The sentinel human carries no email address** in `services/api/src/testing/sentinel.ts`, with the reason recorded beside it (research R4): 200 addressable bait notifications turned one suite's drain into 200 SMTP sends and a ten-second timeout. Unaddressable makes each bait row cost one log line, through the branch FR-WHK-07's unaddressable case already covers
- [ ] T009 Write the planting function in `services/api/src/testing/sentinel.ts` — **delete the sentinel's rows then re-insert**, rather than `ON CONFLICT`. The sentinel is identifiable by `environment_id`, so the delete is exact, and the seeder must not become the accumulation it exists to simulate (FR-003)
- [ ] T009a **Watch `services/api/src/testing/sentinel.ts` fail to plant once before trusting it.** Research hit `webhook_endpoints_disabled_check` re-planting the endpoint: a row cannot be `enabled` with a `disabled_reason` set. Plant against a fresh database and read the constraint errors rather than assuming the insert order is right

**Checkpoint**: the bait can be planted and re-planted, and its sizes track the constants.

---

## Phase 3: User Story 2 — a writer-shape fault names itself (Priority: P1 in build order)

**Built first despite being spec-P2**, because it is the control the other two only prompt for, and because it needs no bait.

**Goal**: a test that mutates rows belonging to no test fails in its own stack, alone.

**Independent test**: quickstart V3 — reintroduce instance 6 into `notifications.itest.ts` and run only that file against a fresh database.

- [ ] T010 [US2] Write `services/api/src/testing/sentinel.sql`: the `__sentinel_guard()` PL/pgSQL function and one `BEFORE UPDATE OR DELETE` row trigger per guarded table, fired `WHEN (OLD.environment_id = …0004)`. Guarded tables are those carrying `environment_id`: `webhook_endpoints`, `webhook_deliveries`, `webhook_disable_notifications`, `channels`, `users`
- [ ] T010a [US2] **Record in `sentinel.sql` that `outbox` cannot be guarded** and why — it carries no `environment_id` because it is platform bookkeeping, so its bait is protected by the reader mechanism only. A gap named in the file that would otherwise look complete
- [ ] T011 [US2] Match the refusal message to `contracts/guard.md` exactly: the `global-operation guard:` prefix, the schema and table, the row id, and the clause `which belongs to no test`. **No suggested fix** — the right alternative depends on what the test meant, and a guess printed as advice is worse than silence
- [ ] T012 [US2] Make the exemption a session setting in `services/api/src/testing/sentinel.sql`, `SET relay.allow_global = 'on'`, read with `current_setting('relay.allow_global', true)` so that a session which never set it gets null and null is refusal. **Verified during research**: non-exempt raises, exempt returns `UPDATE 1`
- [ ] T013 [US2] Create `services/api/src/testing/global-setup.ts` to install the function and triggers once per lane, and wire it as `globalSetup` in `services/api/vitest.integration.config.mts`
- [ ] T013a [US2] **The trigger must exist only in test databases.** It is created from `services/api/src/testing/global-setup.ts` and never from `services/api/migrations/` — otherwise the api service ships a trigger whose only purpose is to reject its own legitimate sweeps (constitution IV, plan's Complexity Tracking). Assert it: a test that confirms `migrations/` contains no `CREATE TRIGGER`
- [ ] T014 [US2] Create `services/api/src/testing/exempt.ts` — **a list of paths, each with its reason beside it**, never a pattern (FR-015). A pattern silently absorbs the next file added, which is the failure mode this whole feature is about
- [ ] T014a [US2] Populate it with the six measured in research R5: `outbox/outbox.itest.ts`, `webhooks/deliveries.itest.ts`, `webhooks/test-event.itest.ts`, `webhooks/attempts.itest.ts`, `notifications/notifications.itest.ts`, `dispatcher/dispatcher.itest.ts`. **The exemption list is a precondition, not a refinement** — an ordinary lane run disabled the sentinel endpoint before any deliberate fault existed
- [ ] T015 [US2] Create `services/api/src/testing/setup.ts` as `setupFiles`: set the exemption when the file under test is on the list, and not otherwise. **No test sets it directly** — a test that can exempt itself is not guarded
- [ ] T016 [US2] Give `services/dispatcher/vitest.integration.config.mts` the same two hooks, keeping its 120-second timeouts
- [ ] T017 [US2] **Verify instance 6 fails alone** (quickstart V3): reintroduce `sweepDisabledEndpoints(db)` into `notifications.itest.ts`'s `disable()` helper, run only that file against a fresh database, confirm the trigger's message appears in that test's own stack, revert with `git checkout --` and confirm byte-identical by `md5sum`
- [ ] T017a [US2] **Commit before the reintroduction, not just before the battery.** Chapter 3.9 lost a fix to exactly this revert step, in the chapter that warned about it twice in bold — because "commit before the battery" is satisfiable once and the battery is a loop

**Checkpoint**: the writer shape fails alone, and the six suites that operate globally on purpose still pass.

---

## Phase 4: User Story 1 — a reader-shape fault fails on the first run (Priority: P2 in build order)

**Goal**: a fresh database behaves like an aged one, so a test that asserts on an unbounded global batch fails immediately.

**Independent test**: quickstart V4 — reintroduce instances 1 to 5, one at a time, each against a fresh database.

- [ ] T018 [US1] Plant the bait **per file**, in a `beforeAll` from `services/api/src/testing/setup.ts`. Research R2 measured three of the four baits eaten in a single lane pass, so a one-shot `globalSetup` seeder protects whichever suite runs first and nothing after it
- [ ] T018a [US1] Record in `setup.ts` that the trigger makes the bait durable for non-exempt files, so re-planting is only strictly needed after an exempt suite runs — and that planting happens per file anyway, because deciding which case applies at runtime is more machinery than the inserts cost
- [ ] T019 [US1] Confirm planting is idempotent across repeated lane runs on the same database (quickstart V6): the bait is the same size at the end of a run as at the start, and the sentinel environment holds exactly one endpoint
- [ ] T020 [US1] **Verify each of instances 1 to 5 fails alone**, one at a time, each against a fresh database, each reverted and confirmed byte-identical: the sweep's missing bound and the drain that held a lock in `deliveries.itest.ts`, the fixed catch-up budget in `consumer.itest.ts`, the `count(*)` comparison in `signup.itest.ts`, and the default batch in `dispatcher.itest.ts`
- [ ] T020a [US1] **Commit before every one of the five**, per T017a
- [ ] T021 [US1] Exclude `services/api/src/testing/**` from coverage in `relay-platform/vitest.coverage.config.mts`, beside `**/main.ts` and `**/*.module.ts`, for the reason recorded there: counting how much of the lane's own scaffolding a test touched is not what "business logic" means

**Checkpoint**: all seven instances fail alone. SC-001 is met.

---

## Phase 5: User Story 3 — the fault is harder to write (Priority: P3)

**Goal**: the compiler and the linter object before the code runs.

**Independent test**: quickstart V7 — add a global-admin import to any non-exempt `*.itest.ts` and run lint.

- [ ] T022 [P] [US3] Remove the default from `sweepDisabledEndpoints(db, limit = 100)` in `services/api/src/db/repository.ts`, making all five cross-environment functions consistent in requiring one
- [ ] T022a [US3] **Record in `services/api/src/db/repository.ts`, beside the signature, that this would not have prevented instance 6** (research R8). `sweepDisabledEndpoints(db, 10_000)` is worse, not better. The required argument is a prompt to think about whose rows are in scope; the trigger is the control. A comment claiming otherwise would be a comment that teaches the wrong lesson
- [ ] T023 [US3] Fix every caller the removed default breaks. The compiler finds them; record how many there were in `specs/030-global-operation-guard/baseline.txt`
- [ ] T024 [US3] Add the `no-restricted-imports` entry to `relay-platform/eslint.config.mjs` using `importNames` for the six global-admin functions — `drainOutbox`, `drainDueDeliveries`, `drainDisableNotifications`, `sweepDisabledEndpoints`, `outboxDepth`, `pendingDeliveryDepth` — restricted in `*.itest.ts`, alongside the existing `pg`, `drizzle-orm` and `ioredis` entries whose comment states the principle
- [ ] T024a [US3] Include the two `*Depth` functions in `relay-platform/eslint.config.mjs`'s entry and say why: they return counts across every environment, which is the exact shape of instance 4 — a global `count(*)` compared against itself, twice in one file, four chapters apart
- [ ] T025 [US3] Write the lint message to name the alternative, per `contracts/guard.md`. Unlike the trigger, the rule knows the call site, so it can be specific — and it points at `exempt.ts` for files that legitimately drive a drain
- [ ] T026 [US3] Add the six exempt files to the ignores list in `relay-platform/eslint.config.mjs`, and **confirm it agrees with `services/api/src/testing/exempt.ts`**: a file exempt from the trigger but not from lint, or the reverse, is a trap for whoever adds the seventh
- [ ] T027 [US3] **Record what the rule does not catch** in `relay-platform/eslint.config.mjs`'s message and in `contracts/guard.md`: indirect calls through a helper, and raw SQL. The trigger covers both. A rule trusted further than it goes is worse than no rule

---

## Phase 6: Fix what this exposes

**Sized by measurement, not estimate.** Research R3 found two failures on a fresh database with a one-shot seeder. Per-file planting will find more, and the count is a finding to record rather than a number to predict.

- [ ] T028 Run the whole integration lane against a fresh database with the bait and the trigger in place, and **record every failure** in `specs/030-global-operation-guard/baseline.txt` before fixing any of them
- [ ] T029 Fix `outbox.itest.ts` invariant 7, which research R3 measured failing: the relay's default batch of 100 never reaches the test's own rows. **Record which of the two shapes it was** — reader — beside the fix
- [ ] T030 Fix `notifications.itest.ts`'s content test, which research R3 measured timing out at 10 seconds. Note that T008's unaddressable sentinel may already resolve it; if so, say that rather than claiming a fix
- [ ] T031 Fix every other failure T028 recorded in `specs/030-global-operation-guard/baseline.txt`, each labelled reader or writer in the file it fixes. **A fix that changes an assertion from a global result to the test's own row is a reader fix; a fix that stops the test performing a global operation is a writer fix.** The labels are what makes the count meaningful next time
- [ ] T032 **Grep `services/*/src/**/*.itest.ts` for the class while the first instance is on screen.** Chapter 3.7's finding, and the reason instance 4 existed: chapter 3.3 fixed the identical assertion a hundred lines up in the same file and did not look further down. Fixing an instance is not fixing a class

---

## Phase 7: Verification

- [ ] T033 Run both lanes and coverage; confirm every pre-existing suite passes and record the counts. Coverage must not fall below 89.50% statements and 82.73% branches
- [ ] T034 **Twenty consecutive integration runs, zero false positives** (quickstart V9, SC-003). This is the step most likely to be skipped for costing twenty times three minutes, and the step that says the guard does not cry wolf. Chapter 3.7 spent four attempts and about four hours getting twenty clean runs, and found four faults doing it
- [ ] T035 Measure the lane's wall-clock time against T002's baseline and record it in `specs/030-global-operation-guard/baseline.txt`, confirming growth under 10 seconds (SC-004). Record the number, not the verdict
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
- [ ] T044 Decide and record whether the PL/pgSQL exception needs an entry in `docs/06-adr-deep-dives.md`. The plan's recommendation is a note rather than a numbered ADR, since it binds no product decision — but constitution VII asks for "a superseding ADR with profiling evidence" for a second language, and a recommendation is not a decision
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

**The one ordering that matters**: T014a before T017. An ordinary lane run
disables the sentinel endpoint, so the trigger without its exemption list fails
six suites for the right reason and the wrong cause.

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

**Then Phase 4**, because four of the seven instances were reader-shape and all
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
