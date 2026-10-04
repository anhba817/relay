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

- [ ] T001 Pin the lane environment in `specs/066-chapter-4-20/baseline.txt` — compose services, `RELAY_POSTGRES_PORT=15432`, node and Postgres versions, and the row counts that make a lane an instrument: `messages`, `message_edits`, `media_objects`, `environments`, and **the outbox's row count**, which feature 065 found is now large enough to fail a suite on its own (`gaps.md` 065-5).
- [ ] T002 Record every lane's REAL exit code in `specs/066-chapter-4-20/baseline.txt` — `pnpm lint`, `pnpm exec turbo run typecheck`, `pnpm test`, `pnpm test:integration`, `pnpm coverage` — with the counted line beside each. Capture the code **outside** the pipeline (eight occurrences of `$?` reading `tail`'s so far). **And KEEP THE FULL LOG of any red lane**: 065's first attempt grepped each log for its counted line and deleted it, which is enough for a green lane and useless for a red one — it recorded *4 tests failed* and not which four, and the close-out comparison is per test.
- [ ] T003 Record `check:fences` in `specs/066-chapter-4-20/baseline.txt` as an **absolute number**, not a delta (055's rule). A clean run prints no problem line at all, so assert the `replay onto` line.
- [ ] T004 Record the CI baseline in `specs/066-chapter-4-20/baseline.txt`: the last pushed run's four job conclusions and its `##[error]` set, normalised. **The current baseline is an empty set** — run 37131955482 at 065's close, four green jobs, 0 error lines — which cannot be matched by introducing something and removing something else.
- [ ] T005 **Re-run the premise against the platform, not against `research.md`.** Re-measure all four escapes from R1 (delete parent / delete child / `ON DELETE CASCADE` / the named-flag trigger) inside rolled-back transactions, **each with its control**, and record in `specs/066-chapter-4-20/baseline.txt`. *An artifact agreeing with another artifact is what fifteen analysis passes found in 4.9.*
- [ ] T006 **Count the fence bill against the tree**, from `relay-tutorial`: `grep -rl 'title="<path>"' app/ fences/` for `repository.ts`, `schema.ts`, `app.module.ts`, `vitest.coverage.config.mts` and `targets.ts`. `plan.md` has **52 / 34 / 23 / 23 / 13** to check against — all five counted at analysis pass 1 rather than left for this task.
  **AND `targets.ts` ALREADY CARRIES FOUR HUNKS IN THE APPENDIX**, so T026's entry is likely to extend one rather than add one: its neighbours are rows the appendix itself adds, which is 4.8's shape, 4.11's `codes.ts` and 4.12's bill on this exact file. **Read it as neither a floor nor a ceiling**: 4.18's list of 21 grew by six and 4.19's list of 8 shrank to 5, because the bill predicts where work *might* land and the chain charges for where it *did*.
- [ ] T007 Record in `specs/066-chapter-4-20/baseline.txt` **how many messages cannot be hard-deleted today** — `count(distinct message_id) from message_edits` — and the age histogram the policy would act on. **5,495 and zero-older-than-30-days at planning time**; both move, and the second is why every fixture is backdated.
- [ ] T008 Record the media linkage in `specs/066-chapter-4-20/baseline.txt`: that `media_objects` has **no foreign key to `messages`**, the `messages_attachments_gin` index that does exist, and R2's two buffer counts — **883 bound against 94,132 set-wise**. The second is the shape the sweep must not be written in.
- [ ] T009 Record what the audit log does with a destroyed target in `specs/066-chapter-4-20/baseline.txt`: **no foreign key, 1,435 rows naming a message**, and therefore nothing refuses the delete and nothing repairs the entry. The decision is US3's; this is the measurement.

---

## Phase 2: Foundational — the decisions, before any migration

**Purpose**: the exception's exact shape, settled before DDL exists. The alternative is a spec
question with `0025` already applied, which is the ordering constraint 4.18 recorded.

- [ ] T010 **Decide the trigger's exception** in `specs/066-chapter-4-20/baseline.txt`: the condition, the setting's name, and that it is `SET LOCAL`. Record why `TG_OP = 'DELETE'` is part of the condition — an `UPDATE` must stay refused with the flag set, because immutability of a version's **content** is not what expiry needs.
- [ ] T011 **Decide the setting's name and who may set it** in `specs/066-chapter-4-20/baseline.txt`. A name in a namespace Postgres will accept as a custom GUC, and one the sweep sets and nothing else does. **Record what stops another caller setting it** — and if the answer is *nothing*, say so, because that is the honest width of the exception and it belongs in the ADR rather than in a comment.
- [ ] T012 **Decide whether `retention_days` gains a CHECK constraint** in `specs/066-chapter-4-20/baseline.txt`. FR-MOD-06 enumerates 30 / 90 / 365 / indefinite rather than describing a range, so `45` is a value nothing licenses. A constraint is how the enumeration survives a caller nobody anticipated; the cost is a migration on a column with 0 non-null values.
- [ ] T013 **Decide the route's shape** in `specs/066-chapter-4-20/baseline.txt` and amend `contracts/retention.md` if it moves. `PATCH /v1/environments/{id}` is new — **there is no environments controller at all**, measured — so this chapter adds a module, and the question is whether a settings route is the right first thing to put there or whether something narrower is.
- [ ] T014 **Write ADR-36's drivers, rejected alternatives and reversal condition** into `specs/066-chapter-4-20/baseline.txt` before any code. **The number is ADR-36** — `ADR-35` is the last in both homes, checked at analysis pass 1, and it is fixed here so phase 7 does not invent one under pressure. Constitution VII requires all three, and R1 already has the rejected alternatives **with the error each one produced**. The reversal condition is ADR-35's: a separate non-superuser role makes privilege the mechanism and this exception unnecessary.
- [ ] T013a **Decide the sweep's query shape and its indexes** in `specs/066-chapter-4-20/baseline.txt`, before T019 writes anything. **Measured at analysis pass 2**: as a join across all environments the age bound lands in a `Join Filter` — `Rows Removed by Join Filter: 1018`, **604 buffers** — and per environment with the bound as a constant it is **74 buffers**, reaching `channels_environment_last_activity`. **8x.** Decide the per-environment form explicitly, because 4.12 published a 26x-160x index measurement for a query its route did not send and three passes went by before anybody asked what the planner would do with the shipped one.
  **AND DECIDE TWO INDEXES, WITH 4.1's TREATMENT.** There is **no index on `messages.created_at`** — the table carries only its pkey, `(channel_id, sequence)`, `messages_idem` and the attachments GIN — so T020's *keyset, not offset* has nothing to keyset on. And selecting the environments with a policy is a **seq scan of 33,051 rows, 546 buffers, `Rows Removed by Filter: 33050`** every pass, where a partial index on `WHERE retention_days IS NOT NULL` would be nearly empty. **Measure each before adding it**: 4.1 added the index its query obviously needed and bought a gap inside the run-to-run spread for +49% storage.
  **AND THE PARTIAL INDEX HAS A MEASURED PRECEDENT IN THIS PLATFORM**: `media_objects_pending_age`, migration `0019`, is a partial index on `created_at` for the identical sweep shape, and `repository.ts` records what it bought — **93 buffers to 4** on a 50-row batch, *"a top-N heapsort over 3,158 rows"* to an index scan. Measure-first still stands; a prior measurement of the same shape is evidence rather than a reason to skip it.
- [ ] T014a **Check T013's premise by reading, not by grepping.** 065's T007 said fourteen `MessageRow` sites and the real number was five, because a grep counts mentions. Open every file the route touches — `app.module.ts`, `targets.ts`, the credential guard's decorators — and confirm what adding a module actually costs.

---

## Phase 3: User Story 1 — expired messages are destroyed (P1) 🎯 MVP

**Goal**: a message past its environment's policy is gone, with its version rows, and the
database no longer refuses it.

**Independent test**: run `quickstart.md` §4 and §5. The backdated message and its versions are
gone; the one inside the policy is untouched.

- [ ] T015 [US1] **Write the red probe FIRST**, in `relay-platform/services/api/src/retention/retention.itest.ts`: assert that deleting a message with version rows is refused, and that deleting the versions first is refused too. **Run it green against today's platform.** The refusal is this chapter's premise and a test written after the fix cannot show it was ever there — this is the inverse of the usual order and it is deliberate.
- [ ] T016 [US1] Write migration `relay-platform/services/api/migrations/0024_retention_policy.sql`: the CHECK constraint on `environments.retention_days` per T012, **and whichever indexes T013a decided to add** — this file is their carrier and no other task writes one. **If T013a decided against both, say so in the migration's comment**, because a decision recorded only in `baseline.txt` is the shape 4.8 named: *049 measured the retarget and never landed it. A measurement is not a repair.* **Written before `0025` and before either applies** — `migrate.ts` keys the ledger on a filename with no checksum, so a file edited after it has run never re-runs while the ledger reports it done.
- [ ] T017 [US1] Write migration `relay-platform/services/api/migrations/0025_expiry_may_delete.sql`: the FK's delete action becomes `ON DELETE CASCADE` **and** the trigger function gains T010's condition. **Both in one file, because they are one decision** — the cascade alone changes nothing, measured, since a cascade issues an ordinary `DELETE` and the row trigger fires on it.
  **AND FROM HERE UNTIL T021, T015's PROBE IS CORRECTLY RED.** It asserts the refusals this migration removes, and T018, T019 and T020 all run with `retention.itest.ts` failing for the right reason. **Expect it; it is the design working.** T021 inverts the probe and the file goes green again — and a red that nobody predicted in that window is a finding.
- [ ] T018 [US1] Declare the constraint in `relay-platform/services/api/src/db/schema.ts` and correct any comment the change falsifies. **34 pages publish this file.** 4.19 found two comments in it that were wrong about the table it describes; read the ones near `retentionDays` and near `messageEdits` rather than only adding.
- [ ] T019 [US1] Add the expiry reads and the delete, **in two places, because they have opposite isolation properties**.
  **THE ENUMERATION GOES IN A NEW `relay-platform/services/api/src/db/retention-reads.ts`** — an unscoped function listing the environments with a policy. It **cannot** be a `Repository` method: constitution I requires that class's constructor to take an `environment_id`, and this crosses every tenant. **Three siblings already do exactly this** — `storage-reads.ts`, `usage-reads.ts`, `audit-reads.ts` — and the first one's header says why the directory matters: *"chapter 4.7's reconciler was written with its Postgres read inline in `metering/` and failed lint on the import; this file is where that rule puts the read."*
  **THE PAGED QUERY AND THE DELETE STAY IN `repository.ts`**, tenant-scoped, one environment at a time in T013a's shape — a `Repository` constructed per environment, which satisfies the constructor requirement literally rather than by exception. **The query engine lives here and nowhere else**: a `drizzle-orm` import outside `services/api/src/db/**` is refused by a lint rule that is a constitution clause, which 065 met in a test file and 4.7 met in `metering/`.
- [ ] T020 [US1] Write the sweep at `relay-platform/services/api/src/retention/sweep.ts`: per environment with a policy, paged, printing a counted line per environment, **in T013a's per-environment shape rather than one join across all of them**. **Keyset, not offset** — 4.13's sweep read one page and the head never moved — **and keyset on whatever T013a found an index for**, because at analysis pass 2 there was none for `created_at` at all.
- [ ] T021 [US1] **Run T015's probe again and watch it go red**, then invert it: the delete now succeeds and the version rows are gone. Record both states in `specs/066-chapter-4-20/baseline.txt`. **A probe that was never green proves nothing about the fix.**
- [ ] T022 [US1] Assert the boundary in `relay-platform/services/api/src/retention/retention.itest.ts`, **on both sides**: a message one day past the policy is destroyed, one day inside it is untouched. Backdate each fixture **to its own instant** — 4.13's stepped by a second, piled 3,235 rows on one instant, and turned twelve tests red in a way CI never sees.
- [ ] T023 [US1] Assert FR-004 in `relay-platform/services/api/src/retention/retention.itest.ts`: an environment with **no** policy loses nothing at any age, counted **absolutely before and after** rather than as a delta — 0 → 0 is satisfied by the sweep not running at all.
- [ ] T024 [US1] Assert FR-008's idempotence in `relay-platform/services/api/src/retention/retention.itest.ts`: run the sweep twice, and pin **what the first run left** rather than that the second changed nothing. *Two 204s prove nothing — idempotence is about what the second call DID.*
- [ ] T025 [US1] Add the `PATCH /v1/environments/{id}` route, its module and its schema under `relay-platform/services/api/src/environments/`, and register the module in `relay-platform/services/api/src/app.module.ts` (**23 pages**). `null` and an omitted field are **different requests** and the schema distinguishes them.
- [ ] T026 [US1] Classify the new route in `relay-platform/services/api/src/isolation/targets.ts` **and** write the gauntlet attack for it. 4.8 found that naming a route is not covering it, and the accounting test fails with *"classified but never attacked"* — which is the error message doing its job.
- [ ] T027 [US1] **Check FR-011 per action**: re-run `messages.itest.ts`, `repository.itest.ts`, `internal.itest.ts` and the edit/delete suites **unedited**, and record the result. **`internal.itest.ts` IS ON THIS LIST BECAUSE 065 LEFT IT OFF** — a required field reached the strict schema on the internal send seam and broke three tests in a suite its FR-008 check did not name. **The way to find the suites is the TYPE the change touches, not a list somebody wrote.**

---

## Phase 4: User Story 2 — the objects go with the messages (P2)

**Goal**: an expired message's attachments are destroyed unless a live message still references
them.

**Independent test**: expire a message with a sole-referenced attachment and one with a shared
attachment; the first object is gone from the database and the store, the second survives.

- [ ] T028 [US2] Add the reverse reference check to `relay-platform/services/api/src/db/repository.ts`: *is this object still referenced by a message that did not expire?* **One object, operand bound** — 883 buffers against 94,132 for the set-wise form, and `messages_attachments_gin` already exists. 4.12's lesson: the query has to be written so the planner CAN use the index before any ratio means anything.
- [ ] T029 [US2] Delete unreferenced objects, their renditions and their stored bytes from `relay-platform/services/api/src/retention/sweep.ts`. **After the messages are gone, not before** — an object referenced only by expired messages is unreferenced only once they are.
- [ ] T030 [US2] Assert both halves in `relay-platform/services/api/src/retention/retention.itest.ts`: a sole-referenced object is gone from the database **and the store**; a shared one survives. FR-MSG-11 has allowed the same `media_id` in two messages since 3.24, so the shared case is real rather than defensive.
- [ ] T031 [US2] Assert that a rendition goes with its parent, in `relay-platform/services/api/src/retention/retention.itest.ts`. Chapter 4.15 gave a rendition's reachability to a composite foreign key with `ON DELETE CASCADE`, so this should need no code — **which is a thing to run rather than to reason about**, exactly as 4.19's T034 was.

---

## Phase 5: User Story 3 — what runs it, published (P3)

**Goal**: FR-MOD-06's three obligations each get a verdict, and nobody reads a compliance
promise into a mechanism that does not exist.

**Independent test**: read `clauses.md` and find a verdict per obligation with where, and a
sentence naming what invokes the sweep.

- [ ] T032 [P] [US3] Write `specs/066-chapter-4-20/clauses.md`: FR-MOD-06's three obligations and FR-MED-11's one, each **met / demonstrated / unmet by decision / unreachable** with where. **And FR-MOD-05 beside them**, unbuilt — the export that would let a tenant keep what a policy destroys, which makes the chapter's *no undo* a measured statement rather than a shrug. The fourth clause bounded by ADR-28's absent scheduler, after FR-ANL-06, DR-17 and FR-MOD-03's year.
- [ ] T033 [US3] Record in `specs/066-chapter-4-20/clauses.md` **the distinction that makes this clause different from the other three**: they are reporting obligations whose absence costs accuracy, and this is a customer telling an auditor that data does not exist. Same verdict, different sentence.
- [ ] T034 [US3] Record the audit-log consequence in `specs/066-chapter-4-20/gaps.md`: an entry outlives its target, **1,435 rows name a message today**, no foreign key refuses it, and repairing it would mean deleting from an append-only log. Stated rather than fixed.

---

## Phase 6: The probes

- [ ] T035 **Probe the two isolation properties separately, because they are different kinds of claim.**
  **THE DELETE'S SCOPE IS AN ARM**: delete each tenancy predicate in the per-environment read and delete, one at a time and then in combination, re-run the retention suite and the gauntlet, and record which turn anything red in `specs/066-chapter-4-20/baseline.txt`.
  **THE ENUMERATION'S IS AN ASSERTION ABOUT ITS SIGNATURE, NOT AN ARM.** `pendingMediaObjects` says it for the sweep this one is modelled on: *"the route above it takes no tenant parameter at all, **which is the isolation property to assert rather than a scope to add**. A route that could be asked for one tenant's objects would be a route worth forging."* So assert that the enumeration takes no tenant argument — **a probe looking for an arm to delete here would report nothing red and mean something entirely different by it.** **065 measured three scoped reads where removing any TWO was invisible** and only all three moved one test of 62. **This sweep DELETES**, so a scope that is invisible here is not a leak but a loss.
- [ ] T036 **Run the trigger's old refusals after the change**, in `specs/066-chapter-4-20/baseline.txt`: an `UPDATE` with the flag set, an `UPDATE` without it, a `DELETE` without it. All three must still be refused. **This is the probe that decides whether the exception is as narrow as the ADR claims**, and reading the new condition is not it.
- [ ] T037 Run the isolation gauntlet and record its counted figures in `specs/066-chapter-4-20/baseline.txt`. **Derive them from `targets.ts` rather than expecting a printed line** — 065's task asked for `N derived, M attacked, K exempt` and that suite asserts emptiness instead.
- [ ] T038 Measure what a sweep costs in `specs/066-chapter-4-20/baseline.txt`: per message destroyed and per object checked, with the sample size. **Interleave** if there is a with/without to compare, so a warming cache is not charged to the change — and say plainly that the figure is from backdated fixtures, because nothing on this lane is old enough to expire.
  **AND NAME WHICH HALF EACH FIGURE CAME FROM, because the two scales do not coincide here.** The busiest message environment holds **1,018 messages and 0 media objects**; the busiest media environment holds **531 objects and 843 messages**. No environment on this lane exercises both halves at size, so an end-to-end cost is a sum of two measurements rather than one observation — and saying so is the difference between a figure and a claim.
- [ ] T039 Run `python3 specs/045-part-3-rework/check-lane-scope.py` and record its **counted line** in `specs/066-chapter-4-20/baseline.txt`, not its exit code. This chapter adds an integration file; the standing rule is to run it after adding one. **It was 75 files at 065's close**, and the increment is how the run proves it looked. It cannot see a scope applied in JavaScript (063-7).

---

## Phase 7: The documents

- [ ] T040 **Read FR-MOD-06 and FR-MED-11 before editing either**, and record what the reading found in `specs/066-chapter-4-20/baseline.txt`, including *nothing to amend* if that is the answer.
- [ ] T041 Read the clauses **beside** them while `docs/04-srs.md` is open and record what was found. 065's T042 found FR-MSG-10 two rows from the one it opened the file to edit, serving a story no artifact had cited.
- [ ] T042 Amend **FR-MOD-06** in `docs/04-srs.md`: three obligations, which are met, and that the hard deletion was refused by the platform's own schema until this chapter.
- [ ] T043 Amend **FR-MED-11** in `docs/04-srs.md` if the measurement warrants it — in particular that it has no referential integrity behind it and cannot be delegated to the database.
- [ ] T044 Add revision row **1.27** to `docs/04-srs.md`, stating what the chapter demonstrated and what it could not.
- [ ] T045 **Write ADR-36 into BOTH of its homes** — the summary in `docs/05-sad.md` and the argument in `docs/06-adr-deep-dives.md`. 4.5 found an ADR lives in two documents and ten passes amended only the summary; `gaps.md` 064-1 is four ADRs with a summary and no argument. **And it SUPERSEDES ADR-35's scope clause rather than editing it**, because constitution VII makes an accepted ADR immutable — which is the distinction 065's ninth analysis pass caught its eighth getting wrong.
- [ ] T046 Amend `docs/05-sad.md` §6.1 with the constraint, the changed delete action and the trigger's condition — **and check every sentence in that section about `message_edits`**, because 4.19 found three sites there and a task naming one would have reached one.
- [ ] T047 Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` row 21 CLOSED and `docs/07-tutorial-plan.md` row 21 SHIPPED. Two copies, and amending one is how they drift.
- [ ] T048 [P] Sweep `docs/` for feature-local ids **both ways**: diff-scoped for what this session added, and tree-wide with every hit classified. 065 found 12 candidates and 1 real, and **one false positive was qualified on the following line** — a line-scoped check cannot see that.
- [ ] T049 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`.
- [ ] T050 [P] Write `specs/066-chapter-4-20/traceability.md` by **reading**, not by grep — including the two sections a grep cannot produce: what is in the feature with no requirement behind it, and the clauses deliberately not amended.

---

## Phase 8: The chapter

- [ ] T051 Register 4.20 in `relay-tutorial/lib/tutorial.ts` with all seven fields, at `/part-4/chapter-20/the-messages-that-expire`. An unregistered id throws at build.
- [ ] T052 **Open `relay-tutorial/app/(en)/part-4/chapter-20/the-messages-that-expire/page.mdx` with the refusal** — `docs/07` §4 rule 1, *the reader must see the bug the design prevents*. The three failing escapes are in `quickstart.md` §2 and they are the chapter's opening.
- [ ] T053 Write the chapter at that page, 2,000–4,000 prose words counted outside fences and tables, English only.
- [ ] T054 [P] Write the figures in `relay-tutorial/app/(en)/part-4/chapter-20/the-messages-that-expire/figures.ts`, passed as `code` and not `chart`.
- [ ] T055 Write the TRAP box. The candidate is **the cascade** — a reader will assume `ON DELETE CASCADE` is a privileged path and it is generated SQL that a row trigger fires on.
- [ ] T056 Write at least one `WHY` box linking the exception to **FR-MOD-06** and the narrowing to **ADR-36 and ADR-35**. `docs/07` §4 rule 3, and 4.15 through 4.19 carry 3, 2, 3, 1, 2 and 2.
- [ ] T057 Publish what the chapter could not do: no scheduler, no bound on a single run, no undo, no notification, and nothing measurable about real-data cost because nothing on the lane is 30 days old.
- [ ] T058 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled. 4.19 contributed **0 titled fences** and put every diff in the appendix.
- [ ] T059 Generate hunks from the checker's own replay — `pnpm check:fences --dump <dir>` — then diff against `relay-platform`. **Verify every pre-image matches exactly once before pasting**, widening past `-U6` only where it does not, because widening merges adjacent hunks and a merged hunk can span more repetition than either half.
- [ ] T060 Put every hunk in `relay-tutorial/fences/post-series.md`, **placed last**, working biggest-first from T006's table.
- [ ] T061 Run `check:fences` to 0 and `pnpm build` green from `relay-tutorial`, **after** every source edit.
- [ ] T062 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [ ] T063 Write `specs/066-chapter-4-20/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T063a **Re-measure the refused count and publish both figures** in `specs/066-chapter-4-20/baseline.txt` — SC-012 asks for it *published AND re-measured at the close*, and T007 only measures it at the open. **It moves by one per deletion by construction**, so it is the clearest case of 4.17's rule that a number measured at one moment is a fact about that moment. Publish the pair, not the later figure alone: the open's number is what the chapter argued from.
- [ ] T064 [P] Write `specs/066-chapter-4-20/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: 065-1 (the history/`messageSchema` shapes), **065-2 (the edit path still writes a millisecond `Date`)**, 065-3 and 065-5 (shared-state suites, and the outbox's size), 064-1, 064-5, 063-4, 058-3.
- [ ] T065 **Re-measure the coverage pins this chapter's edits could move**, in `relay-platform/vitest.coverage.config.mts`, **after** the fence chain is at zero — and add pins for the new files, of which this chapter has several. `repository.ts` measured **92.98 against a pin of 92** at 065's close.
- [ ] T065a **Re-run `check:fences` to 0 after T065 and re-hunk if the pin file moved.** **23 pages publish `vitest.coverage.config.mts`**, and 4.18's first red CI run was exactly this file edited after the chain was last zeroed. Run it even when nothing changed — the control is what tells a clean chain from an unchecked one.
- [ ] T066 Probe the pins both ways in `specs/066-chapter-4-20/baseline.txt`: a pin on a path that matches no file is silent, and a pin on a real file no lane includes is silent too.
- [ ] T067 **Rebuild the api image before running the quickstart** — `pnpm build`, then `RELAY_POSTGRES_PORT=15432 docker compose --profile services build api`, then `up -d --wait`. §2 onward hit `localhost:4000`, which is the **composed container**, and `PATCH /v1/environments/{id}` would answer **404** against an image built before this chapter. 4.11 named this as the third kind of stale build and 065 rediscovered it mid-phase-9. Then run `specs/066-chapter-4-20/quickstart.md` end to end and correct it in place, recording each wrong version. **§0 and §1 are MEASURED; the rest are predictions** — the last six chapters' were wrong three, four, three, five, two and zero times.
- [ ] T068 **Check FR-011 rather than trusting it** (SC-008): `git diff --name-only` against `part4-ch19` and confirm every file outside tests and documents is one the chapter is for.
- [ ] T069 Stop the composed services **by name** from `relay-platform` — `docker compose stop api gateway dispatcher media-worker`, and **not `ingester`**.
- [ ] T070 Run the full lane set with nothing else against the stack and record every REAL exit code, compared against T002. **Compare CLASS BY CLASS, not test by test**: 065 saw four different files fail across six runs, no two alike, every one green in isolation and all green in CI. A per-test diff would have called that a regression. **And do not edit source while the battery runs** — 065 did, and had to discard and restart it.
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
- **Absorb a repair.** `gaps.md` 058-3 and 065-2 are both live and neither is this chapter's.
