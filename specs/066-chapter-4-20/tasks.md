# Tasks: Chapter 4.20 — The messages that expire

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/retention.md`, `quickstart.md`

**Tests**: requested. Every clause this chapter discharges is verified by demonstration, and
the central one — FR-003's *MUST NOT be refused by a referential constraint* — has to be run
**red first**, because the refusal is the premise and a test written after the fix cannot show
it was ever there.

**Organisation**: by user story. US1 is the MVP.

**AND ONE RULE APPLIES TO EVERY PHASE, NOT JUST THE LAST ONE.** `relay-platform` is a git
submodule: `git add -A` from the superproject stages a **gitlink**, not the submodule's working
tree. Feature 065 made three "complete" commits that carried none of its code and found out in
phase 6. **At each phase boundary: commit inside `relay-platform` first, then the pointer, and
check with `git -C relay-platform log --oneline -1` rather than the superproject's.**

---

## Phase 1: Setup and measurement

**Purpose**: every number this chapter is compared against, taken before anything changes. All
append to one file, so none is parallel however independent the measurement is.

- [X] T001 Pin the lane environment in `specs/066-chapter-4-20/baseline.txt` — compose services, `RELAY_POSTGRES_PORT=15432`, node and Postgres versions, and the row counts that make a lane an instrument: `messages`, `message_edits`, `media_objects`, `environments`, and **the outbox's row count**, which feature 065 found is now large enough to fail a suite on its own (`gaps.md` 065-5).
- [X] T002 Record every lane's REAL exit code in `specs/066-chapter-4-20/baseline.txt` — `pnpm lint`, `pnpm exec turbo run typecheck`, `pnpm test`, `pnpm test:integration`, `pnpm coverage` — with the counted line beside each. Capture the code **outside** the pipeline (eight occurrences of `$?` reading `tail`'s so far).
  **AND RECORD `Cached:` AND THE ELAPSED TIME, BECAUSE A CACHED TURBO RUN REPLAYS BOTH THE EXIT CODE AND THE COUNTED LINE.** Measured at analysis pass 16 with its control: `pnpm test` answered **EXIT 0, `Tasks: 13 successful`, every `Test Files N passed` line, `Cached: 13 cached, 13 total`, 17 ms** — nothing ran. The same lane under `turbo run test --force` is `Cached: 0 cached, 13 total`, **8.559 s, 81 test files**. **055-4's *assert the counted line, not the exit code* is necessary and NOT sufficient against a cache**, because turbo prints the counted line from it. Either run `--force` or quote the `Cached:` line beside every lane. 050 found this cache hiding a RED; this is it hiding **that nothing ran**, from the instrument built to catch that.
  **KNOWN GOOD AT THE OPEN, measured forced at pass 16**: 13 tasks, **81 test files** — api 42, gateway 11, protocol 9, test-harness 7, media-worker 7, config 2, and one each for service-kit, ingester and dispatcher — **8.559 s, EXIT 0.** **And KEEP THE FULL LOG of any red lane**: 065's first attempt grepped each log for its counted line and deleted it, which is enough for a green lane and useless for a red one — it recorded *4 tests failed* and not which four, and the close-out comparison is per test.
- [X] T003 Record `check:fences` in `specs/066-chapter-4-20/baseline.txt` as an **absolute number**, not a delta (055's rule). A clean run prints no problem line at all, so assert the `replay onto` line.
- [X] T003a **Record all six tutorial gates by name in `specs/066-chapter-4-20/baseline.txt`**, run from `relay-tutorial`, each **outside a pipe** with its **counted line** quoted rather than its exit code — 055-4: five of seven gate scripts exit 0 over an absent corpus. **Read the list off `ci.yml`, not off memory**: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:srs`, `pnpm check:figures`, `pnpm check:fences`. `check:errors` is **not** one of them — it is run by path from the lanes job, which is the two-spellings correction 062 made to 055-3.
  **THIS TASK EXISTED IN 063 AND 064 AND WAS DROPPED AT 065.** Feature 063's T005 and 064's T003 both recorded the gate set; 065 carried no such task and 066 inherited the gap, which is why analysis pass 6 found **two gates validating this feature's own work with no task running them**: `check:srs` is what checks T044's revision 1.27 for an ordering or heading defect, and `check:figures` is what catches a figure passed as `chart` instead of `code` — a defect `pnpm build` compiles green. **A task list is inherited from its predecessor, so a dropped task propagates silently.**
- [X] T004 Record the CI baseline in `specs/066-chapter-4-20/baseline.txt`: the last pushed run's four job conclusions and its `##[error]` set, normalised. **The current baseline is an empty set** — run 37131955482 at 065's close, four green jobs, 0 error lines — which cannot be matched by introducing something and removing something else.
- [X] T005 **Re-run the premise against the platform, not against `research.md`.** Re-measure all four escapes from R1 (delete parent / delete child / `ON DELETE CASCADE` / the named-flag trigger) inside rolled-back transactions, **each with its control**, and record in `specs/066-chapter-4-20/baseline.txt`. *An artifact agreeing with another artifact is what fifteen analysis passes found in 4.9.*
- [X] T006 **Count the fence bill against the tree**, from `relay-tutorial`: `grep -rl 'title="<path>"' app/ fences/` for `repository.ts`, `schema.ts`, `app.module.ts`, `vitest.coverage.config.mts`, `targets.ts` **and `gauntlet.itest.ts`**. `plan.md` has **52 / 34 / 23 / 23 / 13 / 13** to check against, with the appendix hunks each already carries — **5 / 5 / 3 / 16 / 4 / 6**. **Count the rest of the isolation family while you are there** — `attack.ts` (10), `targets.itest.ts` (11), `attack.test.ts` (3) — because 4.18's route addition touched four files in that directory and T014a is what decides whether this one does.
  **THE SIXTH ENTRY IS WHY THIS TASK STILL EXISTS AFTER THE PLAN COUNTED IT.** Analysis pass 1 counted five and every figure was exact; pass 6 found the list was short anyway, because **a gauntlet attack is written inside `gauntlet.itest.ts`** and T026's second half therefore edits a file nobody had billed. **The arithmetic was right and the population was wrong**, which is the failure a re-count cannot catch and a re-derivation can: derive the list from the files the tasks name, not from the files the plan remembered.
  **AND `targets.ts` ALREADY CARRIES FOUR HUNKS IN THE APPENDIX**, so T026's entry is likely to extend one rather than add one: its neighbours are rows the appendix itself adds, which is 4.8's shape, 4.11's `codes.ts` and 4.12's bill on this exact file. **Read it as neither a floor nor a ceiling**: 4.18's list of 21 grew by six and 4.19's list of 8 shrank to 5, because the bill predicts where work *might* land and the chain charges for where it *did*.
- [X] T007 Record in `specs/066-chapter-4-20/baseline.txt` **how many messages cannot be hard-deleted today** — `count(distinct message_id) from message_edits` — and the age histogram the policy would act on. **5,495 and zero-older-than-30-days at planning time**; both move, and the second is why every fixture is backdated.
- [X] T008 Record the media linkage in `specs/066-chapter-4-20/baseline.txt`: that `media_objects` has **no foreign key to `messages`**, the `messages_attachments_gin` index that does exist, and R2's two buffer counts — **107 buffers bound against 3,423 set-wise and 3.1 ms against 127.9**, re-measured at analysis pass 14 — R2 first published 883 and 94,132 and **neither absolute figure reproduced, while every structural signature did**, so quote the mechanism rather than the buffers. The second is the shape the sweep must not be written in.
- [X] T009 Record what the audit log does with a destroyed target in `specs/066-chapter-4-20/baseline.txt`: **no foreign key, 1,435 rows naming a message**, and therefore nothing refuses the delete and nothing repairs the entry. The decision is US3's; this is the measurement.

---

## Phase 2: Foundational — the decisions, before any migration

**Purpose**: the exception's exact shape, settled before DDL exists. The alternative is a spec
question with `0025` already applied, which is the ordering constraint 4.18 recorded.

- [X] T010 **Decide the trigger's exception** in `specs/066-chapter-4-20/baseline.txt`: the condition, the setting's name, and that it is `SET LOCAL`. Record why `TG_OP = 'DELETE'` is part of the condition — an `UPDATE` must stay refused with the flag set, because immutability of a version's **content** is not what expiry needs.
- [X] T011 **Decide the setting's name and who may set it** in `specs/066-chapter-4-20/baseline.txt`. A name in a namespace Postgres will accept as a custom GUC, and one the sweep sets and nothing else does. **Record what stops another caller setting it** — and if the answer is *nothing*, say so, because that is the honest width of the exception and it belongs in the ADR rather than in a comment.
- [X] T012 **Decide whether `retention_days` gains a CHECK constraint** in `specs/066-chapter-4-20/baseline.txt`. FR-MOD-06 enumerates 30 / 90 / 365 / indefinite rather than describing a range, so `45` is a value nothing licenses. A constraint is how the enumeration survives a caller nobody anticipated; the cost is a migration on a column with 0 non-null values.
- [X] T013 **Decide the route's shape** in `specs/066-chapter-4-20/baseline.txt` and amend `contracts/retention.md` if it moves. `PATCH /v1/environments/{id}` is new — **there is no environments controller at all**, measured — so this chapter adds a module, and the question is whether a settings route is the right first thing to put there or whether something narrower is.
- [X] T013b **Decide whether setting a retention policy is a MODERATION ACTION** (FR-014), in `specs/066-chapter-4-20/baseline.txt`, **in this phase and not when a suite goes red in phase 6**. `relay-platform/services/api/src/audit/moderation-routes.ts` holds **24 entries for 24 derived routes — 8 moderation, 16 not — and this chapter's route makes 25.** Chapter 4.18's rule is **standing, not data**, and the file's own precedent is the pair to argue from: `POST /v1/channels/:channelId/archive` is moderation because it *"removes a shared space from use for everyone in it"*, while `POST /v1/channels` is provisioning and is not. **Setting `retention_days = 30` destroys every user's messages past thirty days, for everyone in the environment, with no undo** — which is the archive test met harder.
  **MEASURE THE COST BEFORE DECIDING, BECAUSE IT IS NOT ONE WORD.** `moderation` obliges an entry, and `Repository.recordAction`'s `targetKind` is a closed union of **`"user" | "message" | "membership" | "channel"`** — mirrored by `audit_log_target_kind_check` in `0021_audit_log.sql` **and again** in `schema.ts:1360`. So the honest bill is a fifth union member, a migration altering the CHECK, and **`schema.ts` at 34 pages of fence chain**. Note too that an environment entry's `target_id` IS its `environment_id`, which no existing entry does. **`not-moderation` costs one line and a reason.** Decide it on the clause and record the bill beside the decision, so a reader can see which way the cost pushed.
- [X] T014 **Write ADR-36's TWO decisions, their drivers, rejected alternatives and reversal conditions** into `specs/066-chapter-4-20/baseline.txt` before any code. **Decision 1: a retention sweep is a compliance path** (research R1a) — the constitution's word is *path* and not *endpoint*, so it needs no amendment and FR-MSG-08 and DR-06 do. **Decision 2: the trigger's named exception.** Two decisions in one ADR is ADR-35's own shape, and they belong together because both answer *what is allowed to destroy evidence*. **The number is ADR-36** — `ADR-35` is the last in both homes, checked at analysis pass 1, and it is fixed here so phase 7 does not invent one under pressure. Constitution VII requires all three, and R1 already has the rejected alternatives **with the error each one produced**. The reversal condition is ADR-35's: a separate non-superuser role makes privilege the mechanism and this exception unnecessary.
- [X] T013a **Decide the sweep's query shape and its indexes** in `specs/066-chapter-4-20/baseline.txt`, before T019 writes anything. **Measured at analysis pass 2 and RE-MEASURED END TO END AT PASS 14, WHICH WITHDREW THE RATIO.** As a join across all environments the age bound lands in a `Join Filter` — `Rows Removed by Join Filter: 1018`, **617 buffers** — and per environment with the bound as a constant it is **73**, reaching `channels_environment_last_activity`. **That is not 8x and there is no speedup: 546 of the 617 is the Seq Scan of all 33,051 environments, and the per-environment form pays it too as step 1.** End to end at one policied environment the two shapes are **617 and 546 + 73 = 619**. Take the per-environment form for **pageability, FR-008's re-runnability, and a bound the planner can use** — none of which is a ratio. 4.15: *publishing the ratio publishes the wrong variable*; 4.12 published a 26x-160x index measurement for a query its route did not send and three passes went by before anybody asked what the planner would do with the shipped one.
  **AND DECIDE TWO INDEXES, WITH 4.1's TREATMENT.** There is **no index on `messages.created_at`** — the table carries only its pkey, `(channel_id, sequence)`, `messages_idem` and the attachments GIN — so T020's *keyset, not offset* has nothing to keyset on. And selecting the environments with a policy is a **seq scan of 33,051 rows, 546 buffers, `Rows Removed by Filter: 33050`** every pass, where a partial index on `WHERE retention_days IS NOT NULL` would be nearly empty. **MEASURED AT PASS 14, so this half of the decision is discharged**: `(id) WHERE retention_days IS NOT NULL` takes the enumeration from **546 buffers to 1** and **1.346 ms to 0.018 ms**, at **8,192 bytes** — the same size and the same reason as 4.15's partial index, because a btree over the unfiltered column would index 33,051 NULLs. **The `messages.created_at` half is still unmeasured and is the one 4.1's warning is about**: 4.1 added the index its query obviously needed and bought a gap inside the run-to-run spread for +49% storage.
  **AND THE PARTIAL INDEX HAS A MEASURED PRECEDENT IN THIS PLATFORM**: `media_objects_pending_age`, migration `0019`, is a partial index on `created_at` for the identical sweep shape, and `repository.ts` records what it bought — **93 buffers to 4** on a 50-row batch, *"a top-N heapsort over 3,158 rows"* to an index scan. Measure-first still stands; a prior measurement of the same shape is evidence rather than a reason to skip it.
- [X] T014a **Check T013's premise by reading, not by grepping.** 065's T007 said fourteen `MessageRow` sites and the real number was five, because a grep counts mentions. Open every file the route touches — `app.module.ts`, `targets.ts`, the credential guard's decorators — and confirm what adding a module actually costs.

---

## Phase 3: User Story 1 — expired messages are destroyed (P1) 🎯 MVP

**Goal**: a message past its environment's policy is gone, with its version rows, and the
database no longer refuses it.

**Independent test**: run `quickstart.md` §4 and §5. The backdated message and its versions are
gone; the one inside the policy is untouched.

- [X] T015 [US1] **Write the red probe FIRST**, in `relay-platform/services/api/src/retention/retention.itest.ts`: assert that deleting a message with version rows is refused, and that deleting the versions first is refused too. **Run it green against today's platform.** The refusal is this chapter's premise and a test written after the fix cannot show it was ever there — this is the inverse of the usual order and it is deliberate.
- [X] T016 [US1] Write migration `relay-platform/services/api/migrations/0024_retention_policy.sql`: the CHECK constraint on `environments.retention_days` per T012, **and whichever indexes T013a decided to add** — this file is their carrier and no other task writes one. **If T013a decided against both, say so in the migration's comment**, because a decision recorded only in `baseline.txt` is the shape 4.8 named: *049 measured the retarget and never landed it. A measurement is not a repair.* **Written before `0025` and before either applies** — `migrate.ts` keys the ledger on a filename with no checksum, so a file edited after it has run never re-runs while the ledger reports it done.
- [X] T017 [US1] Write migration `relay-platform/services/api/migrations/0025_expiry_may_delete.sql`: the FK's delete action becomes `ON DELETE CASCADE` **and** the trigger function gains T010's condition. **Both in one file, because they are one decision** — the cascade alone changes nothing, measured, since a cascade issues an ordinary `DELETE` and the row trigger fires on it.
  **AND FROM HERE UNTIL T021, T015's PROBE IS CORRECTLY RED.** It asserts the refusals this migration removes, and T018, T019 and T020 all run with `retention.itest.ts` failing for the right reason. **Expect it; it is the design working.** T021 inverts the probe and the file goes green again — and a red that nobody predicted in that window is a finding.
- [X] T018 [US1] Declare the constraint in `relay-platform/services/api/src/db/schema.ts` and correct any comment the change falsifies. **34 pages publish this file.** 4.19 found two comments in it that were wrong about the table it describes; read the ones near `retentionDays` and near `messageEdits` rather than only adding.
- [X] T019 [US1] Add the expiry reads and the delete, **in two places, because they have opposite isolation properties**.
  **THE ENUMERATION GOES IN A NEW `relay-platform/services/api/src/db/retention-reads.ts`** — an unscoped function listing the environments with a policy. It **cannot** be a `Repository` method: constitution I requires that class's constructor to take an `environment_id`, and this crosses every tenant. **Three siblings already do exactly this** — `storage-reads.ts`, `usage-reads.ts`, `audit-reads.ts` — and the first one's header says why the directory matters: *"chapter 4.7's reconciler was written with its Postgres read inline in `metering/` and failed lint on the import; this file is where that rule puts the read."*
  **THE PAGED QUERY AND THE DELETE STAY IN `repository.ts`**, tenant-scoped, one environment at a time in T013a's shape — a `Repository` constructed per environment, which satisfies the constructor requirement literally rather than by exception. **The query engine lives here and nowhere else**: a `drizzle-orm` import outside `services/api/src/db/**` is refused by a lint rule that is a constitution clause, which 065 met in a test file and 4.7 met in `metering/`.
- [X] T020 [US1] Write the sweep at `relay-platform/services/api/src/retention/sweep.ts`: per environment with a policy, paged, printing a counted line per environment, **in T013a's per-environment shape rather than one join across all of them**. **Keyset, not offset** — 4.13's sweep read one page and the head never moved — **and keyset on whatever T013a found an index for**, because at analysis pass 2 there was none for `created_at` at all.
- [X] T021 [US1] **Run T015's probe again and watch it go red**, then invert it: the delete now succeeds and the version rows are gone. Record both states in `specs/066-chapter-4-20/baseline.txt`. **A probe that was never green proves nothing about the fix.**
- [X] T022 [US1] Assert the boundary in `relay-platform/services/api/src/retention/retention.itest.ts`, **on both sides**: a message one day past the policy is destroyed, one day inside it is untouched. Backdate each fixture **to its own instant** — 4.13's stepped by a second, piled 3,235 rows on one instant, and turned twelve tests red in a way CI never sees.
- [X] T023 [US1] Assert FR-004 in `relay-platform/services/api/src/retention/retention.itest.ts`: an environment with **no** policy loses nothing at any age, counted **absolutely before and after** rather than as a delta — 0 → 0 is satisfied by the sweep not running at all.
- [X] T023a [US1] **Assert the sweep issues its delete inside an EXPLICIT transaction, and that the flag reads `on` at the moment of the delete** — not at the moment it was set. `SET LOCAL` outside a transaction block is a **warning** and leaves the flag unset (measured, analysis pass 13), so a sweep in autocommit has every cascade refused while looking exactly like a trigger doing its job. **Assert the value, not the statement**: `current_setting('relay.expiring', true)` read inside the same transaction as the `DELETE`.
- [X] T024 [US1] Assert FR-008's idempotence in `relay-platform/services/api/src/retention/retention.itest.ts`: run the sweep twice, and pin **what the first run left** rather than that the second changed nothing. *Two 204s prove nothing — idempotence is about what the second call DID.*
- [X] T025 [US1] Add the `PATCH /v1/environments/{id}` route, its module and its schema under `relay-platform/services/api/src/environments/`, and register the module in `relay-platform/services/api/src/app.module.ts` (**23 pages**). `null` and an omitted field are **different requests** and the schema distinguishes them.
- [X] T025a [US1] **Make the route's body schema `z.strictObject` and test an unknown field**, asserting a 400 rather than a silently ignored key. **Constitution VI's fifth bullet is a MUST** — *"unknown fields are rejected on write endpoints"* — and it is the clause of that bullet nobody had reached: the plan's row discussed validation and `gaps.md` 058-3 and stopped. The convention is already here, 7 uses in `channels.schema.ts` and 4 in `messages.schema.ts`. **065 met this schema from the producer's side** and three tests answered `unrecognized_keys`; this is the same strictness from the caller's.
- [X] T026 [US1] Classify the new route in `relay-platform/services/api/src/isolation/targets.ts` **and** write the gauntlet attack for it, **in `relay-platform/services/api/src/isolation/gauntlet.itest.ts`** — attacks live inside that file, and it is **13 pages with 6 appendix hunks**, so this is two edits to two billed files rather than one. 4.8 found that naming a route is not covering it, and the accounting test fails with *"classified but never attacked"* — which is the error message doing its job.
- [X] T026a [US1] **Add the route's entry to `relay-platform/services/api/src/audit/moderation-routes.ts`** (FR-014, SC-014), whichever way T013b decided, with the one-line reason the file's other 24 entries all carry. **`moderation-routes.itest.ts` fails in BOTH directions from a booted application** — *"these routes exist and nobody decided whether they are moderation"* one way, an entry naming no route the other — so this is not optional and the suite is where it surfaces. **`owedADecision` is mutating-and-not-`/internal/`**, which this route is. Zero fence cost: that file is titled on 0 pages.
  **THREE LISTS KEY OFF ONE DERIVED ROUTE SET AND A ROUTE IS NOT ONE EDIT.** `targets.ts`'s `CLASSIFICATIONS` (T026), the gauntlet's `attacked` set (T026) and this one. All three are built from `deriveTargets` reading the express router off a booted app, and all three have a both-directions test. **`grep -rn deriveTargets` is how you enumerate them** — the list is not written down anywhere else.
- [X] T026b [US1] **If T013b decided `moderation`, write the entry and pay its bill** (FR-014): a fifth `targetKind`, **`relay-platform/services/api/migrations/0026_audit_target_environment.sql`** altering `audit_log_target_kind_check` — **0024 and 0025 are T016's and T017's, so this is 0026 and naming it here is what stops a third unnumbered migration colliding with them** — the mirrored `sql` predicate in `relay-platform/services/api/src/db/schema.ts` (**34 pages**), and the write itself through `Repository.recordAction`. **If it decided `not-moderation`, record that as DONE with the reason** rather than leaving the task unticked — 4.8's rule that a measurement is not a repair has a twin: *a decision not to act, left unrecorded, reads as an omission.*
- [X] T027 [US1] **Check FR-011 per action**: re-run `messages.itest.ts`, `repository.itest.ts`, `internal.itest.ts` and the edit/delete suites **unedited**, and record the result. **`internal.itest.ts` IS ON THIS LIST BECAUSE 065 LEFT IT OFF** — a required field reached the strict schema on the internal send seam and broke three tests in a suite its FR-008 check did not name. **The way to find the suites is the TYPE the change touches, not a list somebody wrote.**

---

## Phase 4: User Story 2 — the objects go with the messages (P2)

**Goal**: an expired message's attachments are destroyed unless a live message still references
them.

**Independent test**: expire a message with a sole-referenced attachment and one with a shared
attachment; the first object is gone from the database and the store, the second survives.

- [X] T028 [US2] **THE PREMISE IS CHECKED AND IT DOES NOT FIT. DO NOT CALL `unreferencedMediaIn` FROM THE SWEEP.** Analysis pass 7 found the function and could not check its two arms because it was reading; **pass 15 ran them, and one makes it the wrong function.**
  **THE POPULATIONS ARE DIFFERENT.** The sweep asks *which media_ids of the messages I just destroyed are now unreferenced*. `unreferencedMediaIn(db, env, olderThan)` asks *which objects in this environment with `parent_id IS NULL` and `created_at < olderThan` does no message reference* — **a superset including objects never attached to anything.** Measured in the demo environment `bbda7667…`: 434 candidates and **48 that no message has ever referenced.** Those 48 are **FR-MED-10's orphans, whose reaper is `docs/12` row 22 and deferred**, and a sweep calling this function destroys them under a retention policy that has nothing to do with them.
  **AND IT IS INVISIBLE TODAY**, which is why a test written this week would pass and prove nothing: with a 30-day bound the function returns **0**, because `created_at < olderThan` filters out everything on a lane whose oldest message is 20 days old. That is the dated premise of pass 12 turned load-bearing for a correctness defect rather than for a demonstration.
  **WHAT IS REUSABLE IS THE SECOND QUERY, AND IT IS THE EXPENSIVE HALF.** Extract it — given an environment and an explicit list of candidate ids, which of them does a surviving message still reference — into a function in `relay-platform/services/api/src/db/repository.ts`, **and have `unreferencedMediaIn` call it too**, so there is one implementation of the expensive part and each caller brings its own population. That is the shape, not a second copy.
  **IT BATCHES AND THE BATCH REACHES THE INDEX — MEASURED, pass 15.** 100 containment predicates `OR`ed together plan as a **`BitmapOr` over 100 `Bitmap Index Scan on messages_attachments_gin`**: 976 buffers, 15.166 ms, ≈**9.8 buffers an object** against **107** for one standalone. **4.18's *an `OR` is not a keyset cursor* does NOT transfer** — containment predicates OR into a `BitmapOr` where a cursor's range predicates land in a `Filter:`. Worth saying only because it was checked rather than assumed.

- [X] T029 [US2] Call **T028's extracted reference check** from `relay-platform/services/api/src/retention/sweep.ts`, **with the `media_id` set collected from the messages this sweep destroyed** — not with every old object in the environment — and delete what comes back unreferenced: objects, renditions and stored bytes. **After the messages are gone, not before** — an object referenced only by expired messages is unreferenced only once they are.
  **AND LOOP TO EXHAUSTION, OR SAY IN THE COUNTED LINE THAT YOU DID NOT.** `unreferencedMediaIn`'s `limit = 100` exists because FR-MED-10's reaper is a repeating job; **this sweep has no repeater** (ADR-28), so a bound left in place means object 101 waits for an operator who may never run it. FR-008 asks that a re-run complete the work and nothing re-runs.
- [X] T029b [US2] **Publish the `deleted` storage event for every object T029 destroys** (FR-013, SC-013), from `relay-platform/services/api/src/retention/sweep.ts`, via `publishStorageDelta` in `relay-platform/services/api/src/metering/storage-event.ts`. **The signature is waiting and says so**: *"`deleted` from **nothing yet** … the reaper is `docs/12` row 22's, and this signature is the one it will call."* **`bytesDelta` is signed and negative here, and the file says CARRY it rather than derive it from `cause`** — a reader that infers the sign puts the rule in a second place.
  **THE OPERATIONAL QUOTA NEEDS NOTHING AND THAT IS WHY THIS IS EASY TO MISS.** Committed bytes are a `sum(declared_bytes)` over rows (SRS 1.17), so the delete corrects the quota by itself and every operational assertion stays green. **The analytical meter is a sum of events and has no such property** — which is the drift chapter 4.16 measured at 4,436 MB charged against 30.7 MB held.
- [X] T029a [US2] **Repair the comments that go stale once T029 and T029b have landed — and it runs AFTER BOTH, which is why it sits here rather than beside T029.** **NOTE WHAT PASS 15 CHANGED**: the sweep calls T028's extracted check and **not `unreferencedMediaIn`**, so that function's *"called by nothing yet … row 22 is where it gets a caller"* **stays true and must be left alone** — what gains a caller is the extracted half, and the comment to write is on that. Repairing a comment that is still accurate would be the mirror of leaving a stale one., because both promise a caller this chapter now supplies. `relay-platform/services/api/src/db/repository.ts` — *"called by nothing yet … row 22 … is where it gets a caller"* — and `relay-platform/services/api/src/metering/storage-event.ts`, whose *"the causes are four and the callers are three"* becomes four and four with T029b. **`repository.ts` is 52 pages and is already in the bill**, so this costs sequencing and not a new file. `CLAUDE.md`'s convention is the standard: a claim about when a symbol runs names the thing that runs it, so the replacement names `sweep.ts`. **Six source comments across five files point at row 22** — grep `docs/12. row 22` and fix only the ones this chapter falsifies, because the erasure chapter is still real and still owes the rest.
- [X] T030 [US2] Assert both halves in `relay-platform/services/api/src/retention/retention.itest.ts`: a sole-referenced object is gone from the database **and the store**; a shared one survives. FR-MSG-11 has allowed the same `media_id` in two messages since 3.24, so the shared case is real rather than defensive.
- [X] T031 [US2] Assert that a rendition goes with its parent, in `relay-platform/services/api/src/retention/retention.itest.ts`. Chapter 4.15 gave a rendition's reachability to a composite foreign key with `ON DELETE CASCADE`, so this should need no code — **which is a thing to run rather than to reason about**, exactly as 4.19's T034 was.

---

## Phase 5: User Story 3 — what runs it, published (P3)

**Goal**: FR-MOD-06's three obligations each get a verdict, and nobody reads a compliance
promise into a mechanism that does not exist.

**Independent test**: read `clauses.md` and find a verdict per obligation with where, and a
sentence naming what invokes the sweep.

- [X] T032 [P] [US3] Write `specs/066-chapter-4-20/clauses.md`: FR-MOD-06's three obligations and FR-MED-11's one, each **met / demonstrated / unmet by decision / unreachable** with where. **And FR-MOD-05 beside them**, unbuilt — the export that would let a tenant keep what a policy destroys, which makes the chapter's *no undo* a measured statement rather than a shrug. The fourth clause bounded by ADR-28's absent scheduler, after FR-ANL-06, DR-17 and FR-MOD-03's year.
- [X] T033 [US3] Record in `specs/066-chapter-4-20/clauses.md` **the distinction that makes this clause different from the other three**: they are reporting obligations whose absence costs accuracy, and this is a customer telling an auditor that data does not exist. Same verdict, different sentence.
- [X] T034 [US3] Record the audit-log consequence in `specs/066-chapter-4-20/gaps.md`: an entry outlives its target, **1,435 rows name a message today**, no foreign key refuses it, and repairing it would mean deleting from an append-only log. Stated rather than fixed.

---

## Phase 6: The probes

- [X] T035 **Probe the two isolation properties separately, because they are different kinds of claim.**
  **THE DELETE'S SCOPE IS AN ARM**: delete each tenancy predicate in the per-environment read and delete, one at a time and then in combination, re-run the retention suite and the gauntlet, and record which turn anything red in `specs/066-chapter-4-20/baseline.txt`.
  **THE ENUMERATION'S IS AN ASSERTION ABOUT ITS SIGNATURE, NOT AN ARM.** `pendingMediaObjects` says it for the sweep this one is modelled on: *"the route above it takes no tenant parameter at all, **which is the isolation property to assert rather than a scope to add**. A route that could be asked for one tenant's objects would be a route worth forging."* So assert that the enumeration takes no tenant argument — **a probe looking for an arm to delete here would report nothing red and mean something entirely different by it.** **065 measured three scoped reads where removing any TWO was invisible** and only all three moved one test of 62. **This sweep DELETES**, so a scope that is invisible here is not a leak but a loss.
- [X] T035a **Delete `@Accepts("application")` from the policy route and re-run everything**, recording what turned red in `specs/066-chapter-4-20/baseline.txt`. **This is the strongest defence the chapter adds and reading it is not testing it.** 4.18 ran exactly this probe on a READ route and found that deleting the decorator answers an end-user token **200 with the tenant's whole moderation history**, while the controller's own 403 branch defended a case that cannot arise — *the decorator is the decision, and nothing had tested it.* **Here the consequence is worse than disclosure**: an end-user token that can set a thirty-day policy destroys the tenant's history. If nothing goes red, the chapter has a route whose only real defence is untested, and that is the finding.
- [X] T036 **Run the trigger's old refusals after the change**, in `specs/066-chapter-4-20/baseline.txt`: an `UPDATE` with the flag set, an `UPDATE` without it, a `DELETE` without it. All three must still be refused. **This is the probe that decides whether the exception is as narrow as the ADR claims**, and reading the new condition is not it.
- [X] T036a **Probe the keyword, both directions, and record both in `specs/066-chapter-4-20/baseline.txt`. The mechanism's safety is one word and T010 only DECIDES it.**
  **(a) THE FLAG MUST NOT OUTLIVE ITS TRANSACTION.** Set it with plain `SET` rather than `SET LOCAL`, end the transaction, and on the **same connection** issue a `DELETE` against `message_edits`. **Measured at analysis pass 13: `current_setting` still reads `on` and the delete succeeds, `DELETE 1`.** The api runs a connection pool, so a connection returned with the flag set serves every later request with the append-only guarantee off until it is recycled. **The assertion is the one `data-model.md` makes in prose** — *"a connection returned to the pool carries nothing"* — and nothing tested it.
  **(b) `SET LOCAL` OUTSIDE A TRANSACTION BLOCK IS A WARNING, NOT AN ERROR.** Measured: `WARNING: SET LOCAL can only be used in transaction blocks`, and the flag reads empty. A sweep running in autocommit therefore has **every** cascade refused — and that symptom is indistinguishable from the trigger working correctly, which is why it needs a probe rather than a reading.
  **BOTH ARE SILENT AND THEY FAIL IN OPPOSITE DIRECTIONS.** Drop `LOCAL` and the exception widens from one transaction to a pooled connection's remaining life; keep `LOCAL` and forget `BEGIN` and the exception never exists. **The trigger is written once and the `SET LOCAL` is written at every call site**, which is where the failure will come from. 4.18's rule one layer in: that chapter found a mechanism that fits the tool is not a mechanism that works — this one works, and had never been tried used slightly wrong.
- [X] T037 Run the isolation gauntlet and record its counted figures in `specs/066-chapter-4-20/baseline.txt`. **Derive them from `targets.ts` rather than expecting a printed line** — 065's task asked for `N derived, M attacked, K exempt` and that suite asserts emptiness instead.
- [X] T038 Measure what a sweep costs in `specs/066-chapter-4-20/baseline.txt`: per message destroyed and per object checked, with the sample size. **Interleave** if there is a with/without to compare, so a warming cache is not charged to the change — and say plainly that the figure is from backdated fixtures, because nothing on this lane is old enough to expire **as of 2026-10-04** — the oldest message is 2026-09-14 and crosses thirty days on **2026-10-14**, so date the sentence rather than stating it as a property of the lane.
  **AND NAME WHICH HALF EACH FIGURE CAME FROM, because the two scales do not coincide here.** The busiest message environment holds **1,018 messages and 0 media objects**; the busiest media environment holds **531 objects and 843 messages**. No environment on this lane exercises both halves at size, so an end-to-end cost is a sum of two measurements rather than one observation — and saying so is the difference between a figure and a claim.
- [X] T039 Run `python3 specs/045-part-3-rework/check-lane-scope.py` and record its **counted line** in `specs/066-chapter-4-20/baseline.txt`, not its exit code. This chapter adds an integration file; the standing rule is to run it after adding one. **It was 75 files at 065's close**, and the increment is how the run proves it looked. It cannot see a scope applied in JavaScript (063-7).

---

## Phase 7: The documents

- [X] T040 **Read FR-MOD-06 and FR-MED-11 before editing either**, and record what the reading found in `specs/066-chapter-4-20/baseline.txt`, including *nothing to amend* if that is the answer.
- [X] T041 Read the clauses **beside** them while `docs/04-srs.md` is open and record what was found. 065's T042 found FR-MSG-10 two rows from the one it opened the file to edit, serving a story no artifact had cited.
- [X] T042 Amend **FR-MOD-06** in `docs/04-srs.md`: three obligations, which are met, and that the hard deletion was refused by the platform's own schema until this chapter.
- [X] T043 Amend **FR-MED-11** in `docs/04-srs.md` if the measurement warrants it — in particular that it has no referential integrity behind it and cannot be delegated to the database.
- [X] T043a Amend **FR-MSG-08** in `docs/04-srs.md`: it says hard deletion occurs *"only via the compliance deletion **endpoint**"* and ADR-36 decision 1 reads the constitution's *compliance **path*** as admitting a retention sweep. **Name the second path explicitly** rather than leaving a reader to decide the two words mean the same thing. **And chapter 4.19 cited this clause as the one its defect broke**, so the amendment carries both halves: what it forbade then and what it admits now.
- [X] T043b Amend **DR-06** in `docs/04-srs.md`: *"Deleted messages shall retain their row; only `text` and `attachments` shall be cleared."* A retention sweep destroys the row, and US1 scenario 5 names that population deliberately. **This is the most specific of the three clauses** and the one a reader checking whether a tombstone survives would find first.
- [X] T044 Add revision row **1.27** to `docs/04-srs.md`, stating what the chapter demonstrated and what it could not.
- [X] T045 **Write ADR-36 — both decisions — into BOTH of its homes** — the summary in `docs/05-sad.md` and the argument in `docs/06-adr-deep-dives.md`. 4.5 found an ADR lives in two documents and ten passes amended only the summary; `gaps.md` 064-1 is four ADRs with a summary and no argument. **And it SUPERSEDES ADR-35's scope clause rather than editing it**, because constitution VII makes an accepted ADR immutable — which is the distinction 065's ninth analysis pass caught its eighth getting wrong.
- [X] T046 Amend `docs/05-sad.md` §6.1 with the constraint, the changed delete action and the trigger's condition — **and check every sentence in that section about `message_edits`**, because 4.19 found three sites there and a task naming one would have reached one.
- [X] T047 Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` row 21 CLOSED and **`docs/07-tutorial-plan.md`'s PART 4 row 21** SHIPPED. Two copies, and amending one is how they drift. **Match on the title, not the number**: `docs/07` holds **two** rows numbered 21, Part 3's *"The email nobody was sending"* at line 194 and Part 4's at line 602, 408 lines apart — which is *name a chapter, never number it* inside the task that numbers one. The vocabulary differs by file and is not a typo: `docs/12` says CLOSED, `docs/07` says SHIPPED, checked against 4.19's rows.
- [X] T048 [P] Sweep `docs/` for feature-local ids **both ways**: diff-scoped for what this session added, and tree-wide with every hit classified. 065 found 12 candidates and 1 real, and **one false positive was qualified on the following line** — a line-scoped check cannot see that.
- [X] T049 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`.
- [X] T050 [P] Write `specs/066-chapter-4-20/traceability.md` by **reading**, not by grep — including the two sections a grep cannot produce: what is in the feature with no requirement behind it, and the clauses deliberately not amended.

---

## Phase 8: The chapter

- [ ] T051 Register 4.20 in `relay-tutorial/lib/tutorial.ts` with all seven fields, at `/part-4/chapter-20/the-messages-that-expire`. An unregistered id throws at build.
- [ ] T052 **Open `relay-tutorial/app/(en)/part-4/chapter-20/the-messages-that-expire/page.mdx` with the refusal** — `docs/07` §4 rule 1, *the reader must see the bug the design prevents*. The three failing escapes are in `quickstart.md` §2 and they are the chapter's opening.
- [ ] T053 Write the chapter at that page, 2,000–4,000 prose words counted outside fences and tables, English only.
- [ ] T054 [P] Write the figures in `relay-tutorial/app/(en)/part-4/chapter-20/the-messages-that-expire/figures.ts`, passed as `code` and not `chart`.
- [ ] T055 Write the TRAP box. The candidate is **the cascade** — a reader will assume `ON DELETE CASCADE` is a privileged path and it is generated SQL that a row trigger fires on.
- [ ] T056 Write at least one `WHY` box linking the exception to **FR-MOD-06** and the narrowing to **ADR-36 and ADR-35** — **and a second one for ADR-36's first decision**, which is the more interesting of the two for a reader: three documents reserved hard deletion for the compliance path, FR-MOD-06 asked for it anyway, and the resolution turned on the constitution saying *path* where the SRS said *endpoint*. **A reader who skips it will think the sweep simply ignored a rule.** `docs/07` §4 rule 3, and 4.15 through 4.19 carry 3, 2, 3, 1, 2 and 2.
- [ ] T057 Publish what the chapter could not do: no scheduler, no bound on a single run, no undo, no notification, and nothing measurable about real-data cost because nothing on the lane is 30 days old.
- [ ] T058 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled. 4.19 contributed **0 titled fences** and put every diff in the appendix.
- [ ] T059 Generate hunks from the checker's own replay — `pnpm check:fences --dump <dir>` — then diff against `relay-platform`. **Verify every pre-image matches exactly once before pasting**, widening past `-U6` only where it does not, because widening merges adjacent hunks and a merged hunk can span more repetition than either half.
- [ ] T060 Put every hunk in `relay-tutorial/fences/post-series.md`, **placed last**, working biggest-first from T006's table — **six files, not five**, and `gauntlet.itest.ts` ties `targets.ts` at 13 pages while carrying more appendix hunks than it.
- [ ] T061 Run **all six tutorial gates** green from `relay-tutorial`, **after** every source edit, and compare each counted line against T003a's: `lint`, `build`, `check:docs`, `check:srs`, `check:figures`, `check:fences` to 0. **`check:figures` is the one that validates T054** — it caught three dead diagrams `pnpm build` did not, because MDX props are not type-checked and `chart={fig}` passes `code: undefined`. **`check:srs` is the one that validates T044** — `check-revision-order.mjs` fails on a descent, an unparseable version and a renamed heading.
- [ ] T062 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [ ] T063 Write `specs/066-chapter-4-20/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T063a **Re-measure the refused count and publish both figures** in `specs/066-chapter-4-20/baseline.txt` — SC-012 asks for it *published AND re-measured at the close*, and T007 only measures it at the open. **It moves by one per deletion by construction**, so it is the clearest case of 4.17's rule that a number measured at one moment is a fact about that moment. Publish the pair, not the later figure alone: the open's number is what the chapter argued from.
- [ ] T064 [P] Write `specs/066-chapter-4-20/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. **Re-measure, because 043 re-measured twenty-three carried items and four were wrong while three had closed with nobody working on them.** The list below is 065's table plus this feature's own, with what pass 11 already measured against each:

| carry | what pass 11 found, or what to measure |
|---|---|
| 065-1 the history row and `messageSchema` are three shapes | not re-measured; this chapter adds no reader |
| **065-2 the edit path writes a millisecond `Date`** | **REPRODUCES, AND MEASURED FROM DATA at pass 12**: `ended_by='edit'` is **5,549 of 5,549 millisecond-exact, 100.00%**; `ended_by='deletion'` is **50 of 1,114, 4.49%**, where chance predicts ~0.1%. The 50 are **interleaved** with precise rows rather than preceding 4.19's fix — ms-exact run 11:06→12:17 on 2026-10-03 and the first precise row is 11:11 — so they are not simply pre-fix. **Both writers are in `repository.ts` and the deletion path does use SQL `now()`; the cause of the 49 is not identified from source, and recording the measurement without a theory is the honest version.** From source: **REPRODUCES.** `repository.ts:5376` sets the column from SQL `now()` on `messages`, line 5380 reads it back as `updated.editedAt!` — a millisecond `Date` through the driver — and line 5411 writes that into `message_edits`, whose primary key it is half of |
| 065-3, 065-5 shared-state suites and the outbox's size | **RE-MEASURED AT PASS 16 and it moved the way 065-5 warns**: `outbox` **395,452** against the **386,317** at 065's close — up 9,135 — with **3,399 pending**. `reset-lane.mjs` does not touch it by design. Re-measure once more at T070 |
| **065-4 three scoped reads, removing any two is invisible** | **CARRY IT. T035 is built on this finding and quotes its measurement without carrying the id** |
| 064-1 four ADRs with a summary and no argument | **RE-MEASURED AND EXACT.** ADR-31–34 appear in `docs/05-sad.md` and **zero** times in `docs/06`; ADR-35 is in both, so the carry correctly did not grow |
| 064-5 the media sweep fixture's floor | **carry the MEASUREMENT, not the id**: 065 found it *"did not fail in any of three lane runs on this host"*, and starting from the bare id throws that away |
| 063-4 feature-local ids leaking into `docs/` | re-measure tree-wide at T049. Pass 7 found a fourth instance inside this feature's own spec — `FR-020`, feature 043's id, cited as a clause |
| **058-3 a malformed path parameter answers 500** | **THE NUMBER IS WRONG AND WAS WRONG WHEN WRITTEN: twenty-two, not sixteen.** That entry counted two parameter names in two controllers and never opened `webhooks.controller.ts`, where six routes take an unvalidated `@Param("id")` against a `uuid PRIMARY KEY`. Carried verbatim through 059–065. **Record the correction against 058-3**, the way 062 corrected 055-3 |
| **050-8 nothing drains the records the stack publishes** | **LIVE, AND THIS FEATURE MADE IT SO.** `compose.yaml` has no `ingester` service and FR-013 adds a `deleted` producer to that stream |
| **062-12 68 of 139 files unpinned, lowest 20.00%** | **LIVE.** T065 adds pins for this chapter's several new files |
| 043-1, 063-2, 063-3 | checked, state why each is or is not live here |

**TWO OF THESE WERE "checked, not live here" IN 065 AND BECAME LIVE BECAUSE OF CHANGES ANALYSIS PASSES 7 AND 9 MADE TO THIS FEATURE.** A carried ledger is re-measured against the feature as it stands at close-out, not as it stood when the list was written. **And one NEW entry this feature did not cause and must not drop**: constitution VI's third bullet gates releases on the cross-tenant suite, **dependency vulnerability scans and the OWASP Top 10 scan**, and **two of the three do not exist** — one workflow file, zero matches for `audit|snyk|trivy|owasp|zap|codeql|dependabot`, no `.github/dependabot.yml`, no `pnpm audit` in any of the eight `package.json`. Recorded on bullet four's precedent, which has carried the quickstart's absence from CI since 057 without anybody pretending otherwise.
- [ ] T065 **Re-measure the coverage pins this chapter's edits could move**, in `relay-platform/vitest.coverage.config.mts`, **after** the fence chain is at zero — and add pins for the new files, of which this chapter has several. `repository.ts` measured **92.98 against a pin of 92** at 065's close.
- [ ] T065a **Re-run `check:fences` to 0 after T065 and re-hunk if the pin file moved.** **23 pages publish `vitest.coverage.config.mts`**, and 4.18's first red CI run was exactly this file edited after the chain was last zeroed. Run it even when nothing changed — the control is what tells a clean chain from an unchecked one.
- [ ] T066 Probe the pins both ways in `specs/066-chapter-4-20/baseline.txt`: a pin on a path that matches no file is silent, and a pin on a real file no lane includes is silent too.
- [ ] T067 **Rebuild the api image before running the quickstart** — `pnpm build`, then `RELAY_POSTGRES_PORT=15432 docker compose --profile services build api`, then `up -d --wait`. §2 onward hit `localhost:4000`, which is the **composed container**, and `PATCH /v1/environments/{id}` would answer **404** against an image built before this chapter. 4.11 named this as the third kind of stale build and 065 rediscovered it mid-phase-9. Then run `specs/066-chapter-4-20/quickstart.md` end to end and correct it in place, recording each wrong version. **§0 and §1 are MEASURED; the rest are predictions** — the last six chapters' were wrong three, four, three, five, two and zero times.
- [ ] T068 **Check FR-011 rather than trusting it** (SC-008): `git diff --name-only` against `part4-ch19` and confirm every file outside tests and documents is one the chapter is for.
- [ ] T069 Stop the composed services **by name** from `relay-platform` — `docker compose stop api gateway dispatcher media-worker`, and **not `ingester`**.
- [ ] T070 Run the full lane set with nothing else against the stack and record every REAL exit code, compared against T002, **each with its `Cached:` line and elapsed time or run under `--force`** — otherwise two cache replays compare byte-identical and read as the strongest possible evidence that nothing regressed (pass 16). **Compare CLASS BY CLASS, not test by test**: 065 saw four different files fail across six runs, no two alike, every one green in isolation and all green in CI. A per-test diff would have called that a regression. **And do not edit source while the battery runs** — 065 did, and had to discard and restart it.
- [ ] T070a **Run the sealed suite — `pnpm test:outsider` from `relay-platform`** — and record its counted line in `specs/066-chapter-4-20/baseline.txt`. It is **one of CI's four jobs and is reached by no local lane** (060), so without this task its first execution against this chapter is the push. **The specific risk is T025's new Nest module**: a module that declares a service it does not provide compiles, typechecks and lints, and fails with `Nest can't resolve dependencies` on the first request — 4.10 paid that, and **only a running app asks the question**. The suite talks to the composed container, so run it after T067's rebuild, not before.
  **AND THIS TASK WENT MISSING THE SAME WAY T003a DID.** Feature 063's tasks named the sealed suite 29 times, 064's once, 065's not at all, and 066 inherited the silence — the second instance in one feature of a task list losing a step by being copied forward. 057 found this suite had never run in CI at all, for a one-line reason, and the drift it was feared to be hiding was not there. **The cost of running it is one command; the cost of not running it is a CI round trip.**
- [ ] T071 Confirm every phase was committed as it closed, **submodule before pointer**, checked with `git -C relay-platform log --oneline -1`.
- [ ] T072 **Push submodules first, then the superproject** — `relay-platform`, then `relay-tutorial`, then the root. **And never `git commit -F -` in a backgrounded command**: no stdin, an empty message, git aborts, and the notification reports the other command's exit code.
- [ ] T073 Compare the CI error set **per error** against T004's baseline, in both directions, and record it (SC-009). **The baseline is empty**, which is the hardest kind to match.
- [ ] T074 If CI is red, fix the platform, then **re-dump, re-hunk `relay-tutorial/fences/post-series.md` and push both** — repairing a platform file invalidates the appendix hunks that publish it. **Record it as NOT RUN with the condition if CI is green**, rather than silently skipping.
- [ ] T075 Tag `part4-ch20` in `relay-platform` and the superproject, annotated, on a commit CI has proved green.
- [ ] T076 Compress 065's `CLAUDE.md` entry to its headline, measurement block and still-cited findings, and add this one. **`wc -c` before and after.** The file closed at **147,331 with 2,669 of headroom** after 066's plan line went in — **the tightest it has been**, so this compression is not optional and 065's entry is large.
- [ ] T077 Remove the active-plan line from between the `SPECKIT` markers in `CLAUDE.md` when the feature closes.

---

## Dependencies & Execution Order

```
Phase 1  →  Phase 2 (the decisions, which the migrations need)
Phase 2  →  Phase 3 (US1)  →  Phase 4 (US2)
Phase 3  →  Phase 5 (US3)
Phases 3-5  →  Phase 6  →  Phase 7  →  Phase 8  →  Phase 9
```

**T005 blocks everything.** If the pincer has moved since 2026-10-03 the chapter has moved with
it.

**T015 BLOCKS T016 AND T017, WHICH IS THE INVERSE OF THE USUAL ORDER.** The probe must be green
against today's platform before the migrations exist, because the refusal is the premise. A
test written after the fix can only show the fix working.

**T016 and T017 are written before either applies.** `migrate.ts` records
`schema_migrations.version` by filename with no checksum, so a file edited after it has run
never re-runs while the ledger reports it done.

**T010 and T011 block T017.** The trigger's condition is a decision about how wide a published
guarantee becomes, and taking it with the migration already written means taking it under
pressure to keep what is there.

**T065a comes after T065.** A final `check:fences` has to follow the last edit to any file the
chain publishes, and the pin file is published by 23 pages.

**T013b BLOCKS T026a AND T026b.** Whether setting a policy is a moderation action decides what
goes in the lookup table and whether a migration exists at all — taken in phase 2 because its
cost is a schema change, and a decision taken in phase 4 is taken under pressure to keep what
is already built.

**T029b COMES BEFORE T029a, WHICH READS BACKWARDS AND IS NOT.** T029a repairs
`storage-event.ts`'s *"the causes are four and the callers are three"*, and that sentence is
only false once T029b has supplied the fourth caller. Repair a comment to describe a state and
then build the state, and the chain publishes a file that disagrees with itself in between.

**T036a IS A PROBE AND MUST FOLLOW T017's MIGRATION**, because there is no flag to test before the trigger has its exception. T023a is a build assertion and belongs with the sweep it asserts.

**T003a BLOCKS T061.** The six tutorial gates have to be recorded before the chapter changes
anything, because T061 compares counted lines against them and a gate with no baseline can
only be compared to its exit code — which is 055-4's whole finding.

**ELEVEN TASKS ABOVE WERE INSERTED BY ANALYSIS PASSES 6 THROUGH 13** — T003a, T013b, T023a,
T025a, T026a, T026b, T029a, T029b, T035a, T036a, T070a — **and this block did not mention one
of them until pass 10 walked the list end to end.** The last two, T023a and T036a, were added
after that walk and are listed here as they were added, which is the habit pass 10 asked for. Each was placed with the two or three lines around it in
view, and two landed in the wrong phase: `T026b` is `[US1]` and had been sitting between two
`[US2]` tasks, where phase 4's independent test could not have covered it. **An edit that is
locally correct and globally unplaced is this feature's third instance of one shape**, after a
task dropped by copying a list forward (pass 6) and a requirement added without its
verification (pass 9). **The index of ordering constraints is the thing that goes stale, and it
is the thing a reader executes from.**

### Parallel opportunities

**Five, and the number is small for the usual reason**: every task in phases 1, 6 and 9 appends
to `baseline.txt`.

- **Phases 1, 2, 3, 4**: none. The measurements share a file; the decisions feed each other;
  the migrations and the sweep are one change across three files where the first failure tells
  you the others are wrong.
- **Phase 5**: T032 writes `clauses.md`.
- **Phase 7**: T048 and T050.
- **Phase 8**: T054 and T062.
- **Phase 9**: T064 writes `gaps.md`.

---

## Implementation Strategy

### MVP

**Phase 1 + Phase 2 + Phase 3.** US1 alone makes FR-MOD-06's central verb possible: a message
past its policy is destroyed, with its versions, and the database no longer refuses it. US2 is
the media half and US3 is the boundary published — neither is worth building against a delete
that does not work.

### What this feature must not do

- **Widen the exception past one verb on one table under one named flag.** If it cannot be kept
  that narrow, the honest course is to record FR-MOD-06 as unmet rather than to widen it. T036
  is the probe that decides, and it works by running the OLD refusals rather than reading the
  new condition.
- **Build a scheduler.** Four clauses want one. That is an architecture decision with its own
  ADR.
- **Publish a deadline the platform does not keep.** No `expires_at`, no `retention_edge`.
  Chapter 4.18 refused exactly that for the audit log.
- **Absorb a repair.** `gaps.md` 058-3 — **twenty-two routes, re-measured at pass 11, not the sixteen that entry records** — and 065-2 are both live and neither is this chapter's.
