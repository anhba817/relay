# Tasks: Chapter 4.19 — Everything, including what was deleted

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/message-versions.md`, `quickstart.md`

**Tests**: requested. Every clause this chapter discharges is verified by demonstration, and
FR-004's refusal has to be *attempted* rather than asserted — chapter 4.18's rule, applied to
a second append-only table.

**Organisation**: by user story, so each is independently testable. US1 is the MVP.

---

## Phase 1: Setup and measurement

**Purpose**: every number this chapter will be compared against, taken before anything changes.
All nine append to one file, so none is parallel however independent the measurement is.

- [ ] T001 Pin the lane environment in `specs/065-chapter-4-19/baseline.txt` — the compose services running, `RELAY_POSTGRES_PORT=15432`, and the row counts that make a lane an instrument: `messages`, `message_edits`, tombstones, environments.
- [ ] T002 Record every lane's REAL exit code in `specs/065-chapter-4-19/baseline.txt` — `pnpm lint`, `pnpm exec turbo run typecheck`, `pnpm test`, `pnpm test:integration`, `pnpm coverage` — **with the counted line beside each, not the colour**. Capture the code **outside** the pipeline: seven occurrences of `$?` reading `tail`'s so far, and 4.17's was caught by the counted line rather than the status.
- [ ] T003 Record `check:fences` in `specs/065-chapter-4-19/baseline.txt` as an **absolute number**, not a delta — 055's rule, because a delta compares a total to a total and never asks which file.
- [ ] T004 Record the CI baseline in `specs/065-chapter-4-19/baseline.txt`: the last pushed run's four job conclusions and its `##[error]` set, normalised. **The current baseline is an empty set** — two consecutive green runs at 064's close — which is the hardest kind to match and the easiest to read as "nothing to compare".
- [ ] T005 **Re-run the premise, against the code rather than against `research.md`.** Re-measure the two-of-three arithmetic, the 403 on `/edits` with a user token, and FR-MOD-02's 204. Record in `specs/065-chapter-4-19/baseline.txt`. The spec's Context is a measurement from 2026-10-03 and this task asks whether it still holds; **an artifact agreeing with another artifact is what fifteen analysis passes found in 4.9**.
- [ ] T006 **Count the fence bill against the tree**, from `relay-tutorial`: `grep -rl 'title="<path>"' app/ fences/` for each of `repository.ts`, `schema.ts`, `messages.service.ts`, `messages.controller.ts`, `messages.schema.ts`, `frames.ts`. `plan.md` has 52 / 34 / 27 / 18 / 12 / 12 to check against. **And add `services/api/src/messages/messages.itest.ts` — 18 pages — which that list misses and T025 must edit**: the exact-key-set assertion at line 1416. The second analysis pass found it; the first version of this bill was six files written from the plan rather than from what the work touches. **Read it as a floor**: 4.18's list of 21 files grew by six during implementation and every one came from running something rather than reading it.
- [ ] T007 Count the `MessageRow` construction sites in `specs/065-chapter-4-19/baseline.txt`, both ways: how many build one, and how many read paths fill `edited_at`. **14 and 10 by grep** — the number T014a's decision turns on, and a grep is an estimate of it.
- [ ] T008 Record what `message_edits` holds today in `specs/065-chapter-4-19/baseline.txt`: row count, distinct `(message_id, edited_at)` pairs, and the number of tombstones with zero version rows. **4,859 / 4,859 / and the third is unmeasured** — it is the size of the history this chapter can never recover.
- [ ] T009 Record in `specs/065-chapter-4-19/baseline.txt` that `message_edits` has no trigger and `audit_log` does, with the `UPDATE` that is accepted today. The before half of T030's probe.

---

## Phase 2: Foundational — the two decisions, before any migration

**Purpose**: `ended_by`'s vocabulary and the response's field names. Blocking, because the
alternative is a spec question with `0022` already applied — the ordering constraint 4.18
recorded when FR-005 and FR-012 could not both hold.

- [ ] T010 **Decide `ended_by`'s values** in `specs/065-chapter-4-19/baseline.txt`: `edit` and `deletion`, with a check constraint and no default. Record why there is no third value and what would have to be true for one to arrive — a message's text stops being current for exactly two reasons today, and a third is a clause rather than a column default.
- [ ] T011 **Decide whether `ended_by` is required**, in `specs/065-chapter-4-19/baseline.txt`, with T007's count in hand. **`repository.ts` already argues both sides of this in a comment** — `attachments` is required *so the compiler names the sites*, and `edited_at?` is optional for write-path convenience, which that same comment calls *"exactly what made the attachments chapter's `internalSendResponseSchema` a break waiting to happen"*. One writer and one reader by grep; confirm before committing.
- [ ] T012 **Decide the response's field names** in `specs/065-chapter-4-19/baseline.txt` and amend `contracts/message-versions.md` if the decision moves: `ended_at` and `ended_by` added, `prior_text` and the `edits` key kept. **Both renames that read better are breaking under CON-05**, and the cost of not renaming is `edited_at` and `ended_at` carrying the same value on every row. Record the duplication as a decision with its reason rather than letting a reader find two names for one instant.
- [ ] T013 **Decide whether `deleted_at` on `MessageRow` is required or optional** in `specs/065-chapter-4-19/baseline.txt`. `edited_at?` is optional and the file says why; this field has the same shape and the opposite argument available. **Required names every construction site**; T007 says how many that is.
- [ ] T014 **Resolve the erasure collision in writing** in `specs/065-chapter-4-19/baseline.txt`, before the trigger ships. Row 22 must delete a user's words and version rows hold them; an append-only table refuses that `DELETE`, exactly as `audit_log` does. **This chapter writes the collision down and does not pre-solve it** — but it must say which of the two mechanisms row 22 will have to defeat, because by then there will be two.
- [ ] T014a **Check the premise of T011 and T013 by reading the code, not the grep.** A count from `grep -c` is an estimate: 4.11's regex over `targets.ts` found 47 where the file's own `method:` count said 51, and 4.18 found the population was 24 where six documents said 25. Open every site the grep names.

---

## Phase 3: User Story 1 — the final version is recoverable (P1) 🎯 MVP

**Goal**: a message edited twice and then deleted yields three texts, in order, the last one
marked as ended by a deletion — **and none of the three can be rewritten afterwards**.

**Independent test**: run `quickstart.md` §1. It reports two of three today and must report
three of three. Then run §4: both write attempts are refused and the rows survive.

**T030–T034 ARE HERE AND THEIR IDS JUMP**, which is the second analysis pass showing in the
file. They were phase 5's, building a trigger that no requirement mentioned and that US3's
independent test did not exercise — five unmapped tasks. The spec now carries FR-011, FR-012
and SC-012, and the value is US1's: *a recovered text the application can rewrite is not an
answer to what did it say, it is a note.* They are placed after T025 rather than renumbered,
because five renumberings would move every cross-reference between them.

**And both migrations are now written in one phase**, which is the other thing the move buys:
`0022` and `0023` are authored before either is applied, where two phases apart was T015's
whole hazard.

- [ ] T015 [US1] Write migration `relay-platform/services/api/migrations/0022_message_versions.sql`: `ALTER TABLE message_edits ADD COLUMN ended_by text`, the check constraint, and the backfill of existing rows to `'edit'` **before** the `NOT NULL`. A column added `NOT NULL` with no default fails on a table with 4,859 rows, and the order is the whole of it.
  **AND THE TRIGGER IS NOT IN THIS FILE.** It is `0023` (T030), and the separation is not tidiness: `migrate.ts` records `schema_migrations.version` **by filename with no checksum**, so a trigger appended to this file after this task has run would never apply on any machine that already ran it, while the ledger reports the migration done. Chapter 4.18 recorded that hazard as something to guard against; two files two phases apart would have made it a certainty. **A migration file is written once, before it is ever applied.**
- [ ] T016 [US1] Declare the column in `relay-platform/services/api/src/db/schema.ts` and **correct the comment R1 found**. It reads *"a deletion writes no row here, because a tombstone has no text to preserve"* — true after the deletion, false at the write site, and the sentence is why four chapters did not look. **34 pages publish this file.**
- [ ] T017 [US1] Write `ended_by: "edit"` at the existing write site in `relay-platform/services/api/src/db/repository.ts`'s `editMessage`, around line 5386.
- [ ] T018 [US1] Write the final version in `relay-platform/services/api/src/db/repository.ts`'s `deleteMessage`, inside the transaction it already has, **on the branch that actually deletes**. The already-deleted branch returns before it, which is FR-004: a retried deletion records no second version, for the same reason it emits no second event (FR-009 of chapter 3.23) and writes no second audit entry (chapter 4.18).
  **THE ROW TAKES THE INSTANT THE `.returning()` ALREADY GAVE BACK**, not a fresh clock reading. `deleteMessage` sets `deletedAt: sql`now()`` and reads it back into `deletedAt` before this point, so the value is in scope and costs nothing. **`editMessage` carries the reason in a comment at `repository.ts:5325`**: *"ONE CLOCK READING FOR BOTH WRITES… two `now()` calls would be two instants, and the history row's own primary key is (message_id, edited_at), so a caller reading the history could not match an entry to the message state it produced."* A second reading here gives the version row a primary key the tombstone's `deleted_at` does not match, and **T028's assertion is what would catch it** — after the fact, where this line catches it first.
- [ ] T019 [US1] Return the two new fields from `relay-platform/services/api/src/db/repository.ts`'s `listMessageEdits`, around line 5696, mapping the column to both `edited_at` and `ended_at` per T012's decision.
- [ ] T020 [US1] **Assert the ordering property rather than assuming it**, in `relay-platform/services/api/src/db/repository.itest.ts`: an edit and a deletion on one message never collide on `(message_id, edited_at)`, because FR-010 refuses an edit on a tombstone. *Cannot collide by construction* is the kind of claim this project has had to withdraw.
- [ ] T021 [US1] Write the write-side suite at `relay-platform/services/api/src/messages/versions.itest.ts`: two edits then a deletion yields three rows in order, the last `ended_by: "deletion"` and carrying the text the message held at deletion.
- [ ] T022 [US1] Assert the zero-edit case in `relay-platform/services/api/src/messages/versions.itest.ts`: a message deleted with no edits yields **one** version where it yields zero today. **The case the arithmetic is worst in**, and the one a test over an edited message would never reach.
- [ ] T023 [US1] Assert FR-004 in `relay-platform/services/api/src/messages/versions.itest.ts`: a second deletion adds no version, **counted before and after** rather than read off the 204. *Two 204s prove nothing — idempotence is about what the second call DID.*
- [ ] T024 [US1] Assert the route in `relay-platform/services/api/src/messages/versions.itest.ts`, not only the repository: `GET …/edits` returns the three versions through HTTP. **A repository test proves a check exists; only a route test proves it fires.**
- [ ] T024a [US1] **Assert the credential refusal in a suite, not only in `baseline.txt`** (FR-005, SC-006), in `relay-platform/services/api/src/messages/versions.itest.ts`: a user token on `GET …/edits` answers **403 `wrong_credential_type`**, asserted **by code and not by status** — `webhooks.itest.ts` passed for three chapters while the body said `internal_error`. **Run it red by deleting `@Accepts("application")`**, which is how chapter 4.18 found that its own 403 branch was unreachable while the decorator beside it was the whole defence and had no test. **This chapter adds rows to that route**, so the refusal is now protecting more than it was.
  **AND `targets.ts:208` ALREADY NAMES THE HAZARD**: *"THE TWO VALUES MUST AGREE AND NOTHING COMPARES THEM. This entry and the decorator are the same authorisation fact written twice."* The entry says `accepts: "application"` and the decorator enforces it; this test is the first thing in the repository to check the enforcing half.
- [ ] T025 [US1] **Check FR-008 per action**: re-run `messages.itest.ts` and the edit/delete suites **unedited** and record the result in `specs/065-chapter-4-19/baseline.txt`. A suite that needed editing to stay green is a behaviour change and the chapter says so rather than editing it.
  **ONE ASSERTION IS EXPECTED TO FAIL AND IT IS THE RIGHT ONE.** `messages.itest.ts:1416` is `expect(Object.keys(edits[0]!).sort()).toEqual(["edited_at", "prior_text"])` — an **exact key set**, with a comment saying why it is exact: *"an absent key and an undefined value are the same to a truthiness check and different to a contract."* This chapter adds `ended_at` and `ended_by` to every row, so that assertion moves, and it is a contract test doing its job rather than FR-008 being broken. **Update it to the four-key set and record it here as the one expected edit**; every other red in this run is a finding.
  **And `toHaveLength(1)` eight lines above it does NOT move** — that message is edited, not deleted, so it still has one version. Checked rather than assumed, because the two assertions look alike and only one of them is about this chapter.
- [ ] T030 [US1] Write migration `relay-platform/services/api/migrations/0023_message_edits_append_only.sql` — the trigger function and the `BEFORE UPDATE OR DELETE` trigger — with the justification in a comment: FR-MSG-07 says *immutable*, nothing enforced it, and **ADR-35 measured that `REVOKE` is inert against a superuser** a chapter ago. **A new file rather than an edit to `0022`**, for the reason T015 states: an applied migration cannot be appended to, because the ledger keys on the filename. **And the order between the two files is load-bearing** — `0022`'s backfill is an `UPDATE` on `message_edits`, which this trigger would refuse. Filenames apply in order, so `0023` is the only safe number and this task asserts the backfill ran before writing it.
- [ ] T031 [US1] **Run the trigger red before anything depends on it**: apply the migration, attempt `UPDATE` and `DELETE` through `psql`, record both refusals in `specs/065-chapter-4-19/baseline.txt`. **Assert the trigger exists first** — `select tgname from pg_trigger where tgrelid = 'message_edits'::regclass` — because `schema_migrations` records filenames with no checksum. **The two-file split removes the way this went wrong in the first draft and not every way it can.** `0023` is a new filename, so it applies; but a machine that ran `0023` before this task edited it would not re-run it, and the ledger would still say done. **Ask the catalogue, not the ledger.**
- [ ] T032 [US1] **Run the two bypasses and record them** in `specs/065-chapter-4-19/baseline.txt` — `SET session_replication_role = replica` and `DROP TRIGGER`. ADR-35 published the scope for `audit_log`; this task asks whether it is the same scope here rather than assuming a second table behaves like the first.
- [ ] T033 [US1] Clean up T031's and T032's rows before anything else is counted, and say so in `specs/065-chapter-4-19/baseline.txt`. **The cleanup needs the bypass**, as 4.18's did — and **quote the values**: a prior text contains spaces, and `tr -d ' '` is how 4.18 wrote a corrupted row into the table it had just made append-only.
- [ ] T034 [US1] Check that `relay-platform/packages/test-harness/src/no-trigger-in-migrations.test.ts` **still passes unedited**. 4.18 narrowed it from *no trigger* to *not the sentinel guard* and asserted the narrowing; a second permitted trigger should need no change, and **running it is how you find out** rather than reasoning from the narrowing's wording.

---

## Phase 4: User Story 2 — the removal instant, from history alone (P2)

**Goal**: a client catching up through history can tell a removal from a message that never
had text, and say when.

**Independent test**: delete a message, read the channel's history as a caller that never saw
the delete, and read the instant off the row.

- [ ] T026 [US2] Add `deleted_at` to the message row type in `relay-platform/services/api/src/db/repository.ts`, in T013's shape, beside the `edited_at?` whose comment argues the other side.
- [ ] T027 [US2] Fill it in the read paths in `relay-platform/services/api/src/db/repository.ts` — `listMessages` and whatever else T007's count named. **The compiler names them if T013 chose required**; if it chose optional, this task's list is a grep and T014a's rule applies to it too.
- [ ] T028 [US2] Assert it in `relay-platform/services/api/src/messages/versions.itest.ts`: a tombstone's history row carries the instant, a live message's carries `null`, **and the instant equals the one the `DELETE` response returned** — three surfaces, one event, which is the reason this field exists.
- [ ] T029 [US2] Record the three-way shape disagreement in `specs/065-chapter-4-19/gaps.md` rather than fixing it: history serves `channel_id` where `messageSchema` declares `channel`, carries an `edited_at` the schema does not, and returns `text: null` against `z.string()`. **Nothing parses one against the other**, so no instrument can see it, and converging them is a reshape where everything this chapter does is an addition.

---

## Phase 5: User Story 3 — the boundary, published (P3)

**Goal**: what a tenant can and cannot recover, counted, so rows 21 and 22 inherit a statement
rather than an assumption.

**Two tasks, and that is the whole story.** The trigger that sat here until the second
analysis pass is US1's — it had no requirement and this story's independent test never touched
it.

**Independent test**: read `clauses.md` and find a count with a clause beside each item, and a
number for how many tombstones can never be recovered.

- [ ] T035 [P] [US3] Write `specs/065-chapter-4-19/clauses.md`: FR-MOD-01's obligations counted, FR-MOD-02's recorded as already met, FR-MSG-07's and FR-MSG-08's each marked met, demonstrated, unmet by decision or unreachable, with where. SC-007 wants a count, not an adjective.
- [ ] T036 [US3] Record in `specs/065-chapter-4-19/baseline.txt` **how many tombstones can never be recovered** — T008's third figure. The chapter publishes a boundary and this is its size.

---

## Phase 6: The probes

- [ ] T037 Delete each tenancy predicate in `listMessageEdits` one at a time, re-run the versions suite and the gauntlet, and record which arms turn anything red in `specs/065-chapter-4-19/baseline.txt`. **Chapters 4.11, 4.12 and 4.18 all measured that an SQL clause carries no JavaScript branch**, and 4.18 found two of three scopes invisible and a third guarding a case that could not arise.
- [ ] T038 Run the isolation gauntlet and record its own counted line in `specs/065-chapter-4-19/baseline.txt` — `N derived, M attacked, K exempt`. Constitution VI names it as gating releases, and 4.9 found three of its attacks returning at their first line and reporting green.
  **AND NAME THE ATTACK THAT ALREADY COVERS FR-006**: `gauntlet.itest.ts:242`, *"GET …/messages/:messageId/edits — a foreign message's history reads as an absent one"*, which predates this feature. **Record that it still passes with version rows present** (SC-005, FR-006) — the route returns more than it did and the attack's claim is unchanged. Writing the citation down is the point: FR-006 has no task of its own and without this line it reads as uncovered, which is how a later chapter adds a second attack for the same property.
- [ ] T039 Measure what the extra row costs the deletion, in `specs/065-chapter-4-19/baseline.txt`: latency with and without, **interleaved** so a warming cache is not charged to the change, min/p50/max and the sample size. 4.18 measured the same shape at 0.43 ms; **this task measures its own** rather than reusing the figure, because the row here is wider and the transaction already existed.
- [ ] T040 Check whether the versions route needs a page bound, in `specs/065-chapter-4-19/baseline.txt`: the largest number of edits on one message in the lane, and what an unbounded list costs at that size. Recorded rather than solved if the number is small — a page bound is a second contract change.

---

## Phase 7: The documents

- [ ] T041 **Read FR-MSG-07 and FR-MSG-08 before editing either**, and record what the reading found in `specs/065-chapter-4-19/baseline.txt`, including *nothing to amend* if that is the answer. Four documents once agreed on two clauses that do not exist, and what found it was opening the SRS to make the edit.
- [ ] T042 Read the clauses **beside** them while `docs/04-srs.md` is open and record what was found — 4.16 found a data-dictionary row describing a table nobody built, two rows from the one it opened the file to edit.
- [ ] T043 Amend **FR-MSG-07** in `docs/04-srs.md` if the measurement warrants it: the clause says *immutable* and this chapter is what makes it true, which is a met-rather-than-amended note.
- [ ] T044 Amend **FR-MOD-01** in `docs/04-srs.md`: what *"complete history"* means now, what it still cannot include, and that FR-MOD-02 was already met before this chapter.
- [ ] T045 Add revision row **1.26** to `docs/04-srs.md`, stating what the chapter demonstrated and what it could not.
- [ ] T046 Amend `docs/05-sad.md` §6.1 with the column and the second trigger, **and check whether the ADR table needs anything**. `plan.md` says no new ADR and gives the reasoning; if a measurement falsified it, this is where that shows up.
- [ ] T047 Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` row 20 CLOSED and `docs/07-tutorial-plan.md` row 20 SHIPPED. Two copies, and amending one is how they drift.
- [ ] T048 **Amend `docs/12` §7.5 itself.** It says *"Check ch 20's premise before writing it… Some of this chapter may already exist."* It was right, the check was run, and the section should record what the check found rather than leaving the warning standing for a chapter that has shipped.
- [ ] T049 [P] Sweep `docs/` for feature-local ids **tree-wide, not by diff**: `grep -rnE 'FR-0[0-9][0-9]' docs/` with every hit classified. 063-4 found the diff-scoped version fires on its own repairs; 064 found `FR-013a` means three unrelated things and that a qualifier to the LEFT of an id defeats a pattern looking to the right.
- [ ] T050 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`.
- [ ] T051 [P] Write `specs/065-chapter-4-19/traceability.md` by **reading**, not by grep. 4.11's mechanical map raised fourteen alarms and all fourteen were false.

---

## Phase 8: The chapter

- [ ] T052 Register 4.19 in `relay-tutorial/lib/tutorial.ts` with all seven fields, at `/part-4/chapter-19/everything-including-what-was-deleted`. An unregistered id throws at build; `path` is checked by no gate.
- [ ] T053 **Open `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx` with the arithmetic** — `docs/07` §4 rule 1, *"the reader must see the bug the design prevents"*. Three texts existed, two come back, and the commands are already in `quickstart.md` §1.
- [ ] T054 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx`, 2,000–4,000 prose words counted outside fences and tables, English only.
- [ ] T055 [P] Write the figures in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [ ] T056 Write the TRAP box in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx`. The candidate is R1's: **a comment that explains an absence as a necessity**, which is why four chapters read past a gap that was one line of code away.
- [ ] T057 Write at least one `WHY` box in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx` linking the preservation to **FR-MSG-08** and the trigger to **FR-MSG-07 and ADR-35**. `docs/07` §4 rule 3 names this component, and 4.14 through 4.18 carry 3, 2, 3, 1 and 2.
- [ ] T058 Publish in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx` the distinction the chapter turns on: **a moderator removes a message and erasure destroys it**, and only the second is licensed to lose a version. A reader who finds that a deleted message's text is still in the database deserves that sentence before they find it.
- [ ] T059 Publish in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx` what the chapter could not do: no recovery of anything deleted before it, no actor on a version, no attachment history, and no bound on how long any of it lasts.
- [ ] T060 Write the chapter's fences in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx`. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled, and 4.14 paid three fences for forgetting it.
- [ ] T061 Generate hunks from the checker's own replay — `pnpm check:fences --dump <dir>` in `relay-tutorial`, then diff against `relay-platform`. Verify every pre-image matches **exactly once** before pasting, widening past `-U6` only when it does not.
- [ ] T062 Put every hunk in `relay-tutorial/fences/post-series.md` — all six files are published by pages this chapter does not own (4.8's rule) — working biggest-first from T006's table.
- [ ] T063 Run `check:fences` to 0 and `pnpm build` green from `relay-tutorial` (SC-010), **after** every source edit.
- [ ] T064 [P] Count the prose words in `relay-tutorial/app/(en)/part-4/chapter-19/everything-including-what-was-deleted/page.mdx` and confirm the bound (SC-011).

---

## Phase 9: The record and the close

- [ ] T065 Write `specs/065-chapter-4-19/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T066 [P] Write `specs/065-chapter-4-19/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: 064-1 (four ADRs with a summary and no argument), 064-2, 064-5 (the media sweep fixture's floor), 063-2, 063-3, 063-4, 050-8, 062-12, 043-1.
- [ ] T067 Add per-file coverage pins for any new file to `relay-tutorial`'s… no — to `relay-platform/vitest.coverage.config.mts`, **after** the fence chain is at zero. **And re-run `pnpm coverage` afterwards.** 4.18's two CI failures were both this task: pins added after the chain was zeroed with `check:fences` not re-run, and a pin set to 100 from a test run that reports no coverage at all.
- [ ] T068 Probe the pins both ways in `specs/065-chapter-4-19/baseline.txt`: a pin on a path that matches no file is silent, and a pin on a real file no lane includes is silent too. **Both halves, and a single-file run cannot catch either** — 4.18's probes used one test file and missed a pin that was wrong.
- [ ] T069 Run `specs/065-chapter-4-19/quickstart.md` end to end and correct it in place, recording each wrong version. **§1 and §2 are MEASURED; the rest are predictions** — the last five chapters' were wrong three, four, three, five and two times.
- [ ] T070 **Check FR-008 rather than trusting it** (SC-008): `git diff --name-only` against `part4-ch18` and confirm every file outside tests and documents is one the chapter is for.
- [ ] T071 Stop the composed services **by name** from `relay-platform` — `docker compose stop api gateway dispatcher media-worker`, and **not `ingester`**, which has no Dockerfile and makes the whole command fail.
- [ ] T072 Run the full lane set with nothing else against the stack and record every REAL exit code, compared **per test** against T002 rather than by colour. **And expect `verify.itest.ts` to be red on a developer host** — `gaps.md` 064-5, the media sweep fixture's floor, which CI passes.
- [ ] T073 Confirm every phase was committed as it closed. **And commit the submodule before the pointer**: 4.18's `git add -A` staged a gitlink that had not moved, because `relay-tutorial` still held the whole chapter uncommitted, and the superproject commit looked complete and carried none of it.
- [ ] T074 **Push submodules first, then the superproject** — `relay-platform`, then `relay-tutorial`, then the root. **And never `git commit -F -` in a backgrounded command**: no stdin, an empty message, git aborts, and the task notification reports the other command's exit code.
- [ ] T075 Compare the CI error set **per error** against T004's baseline, in both directions, and record it in `specs/065-chapter-4-19/baseline.txt` (SC-009). **The baseline is empty**, which cannot be matched by introducing something and removing something else — and 4.18's two red runs failed in different jobs while both reading `failure`.
- [ ] T076 If CI is red, fix the platform, then **re-dump, re-hunk `relay-tutorial/fences/post-series.md` and push both** — repairing a platform file invalidates the appendix hunks that publish it.
- [ ] T077 Tag `part4-ch19` in `relay-platform`, annotated, on a commit CI has proved green: `git tag -a part4-ch19` then `git push origin part4-ch19`.
- [ ] T078 Compress 064's `CLAUDE.md` entry to its headline, measurement block and still-cited findings, and add this one. **`wc -c` before and after.** 064's entry is 9.2 kB and the file closed at 144,386 against a 150,000 budget — **the compression is not optional this time.**
- [ ] T079 Remove the active-plan line from between the `SPECKIT` markers in `CLAUDE.md` when the feature closes, so the next feature's line replaces a plan rather than joining a list.

---

## Dependencies & Execution Order

```
Phase 1  →  Phase 2 (the decisions, which the migration needs)
Phase 2  →  Phase 3 (US1)  →  Phase 4 (US2)
Phase 3  →  Phase 5 (US3)          the trigger protects rows US1 creates
Phases 3-5  →  Phase 6  →  Phase 7  →  Phase 8  →  Phase 9
```

**T005 blocks everything.** If the premise has moved since 2026-10-03 the chapter has moved
with it, and §7.5's warning is about exactly this.

**T011 and T013 block T015 and T026.** A required field is a decision about who the compiler
names, and taking it after the migration exists means taking it with a column already shipped.

**T015 blocks T030, and they are TWO FILES because of how the ledger works.** A `NOT NULL`
column added to 4,859 rows without a backfill fails, and a trigger that exists before the
backfill refuses it — `0022`'s backfill is an `UPDATE` on the table `0023`'s trigger guards.
Filenames apply in order, so the sequence is safe.

**Appending the trigger to `0022` would not be**, and that was this plan's shape until the
first analysis pass: `migrate.ts` records `schema_migrations.version` **by filename with no
checksum**, so a file edited after it has applied never applies again, on any machine that
already ran it, while the ledger reports it done. Chapter 4.18 wrote that hazard down as
something to check for — T031 still does — and two phases writing one file would have turned
a risk into a certainty. **A migration file is written once, before it is ever applied.**

**T031 and T032 block the close.** A mechanism that has not been attacked has not been checked.

**T063 comes after T067**, not before — 4.18's CI went red twice on this and both were the
same task's edits made after the instrument had last run.

### Parallel opportunities

**Six, and the number is small for the same reason as last time.** Every task in phases 1, 6
and 9 appends to `baseline.txt`, so none of them is parallel however independent the
measurement behind it is.

- **Phase 1**: none. Nine measurements, one file.
- **Phase 2**: none. Each decision feeds the next.
- **Phase 3**: none. The migration, the column and the two write sites are one change across
  three files, and the first failure is what tells you the other two are wrong.
- **Phase 4**: none marked. T026 and T027 are the same file.
- **Phase 5**: T035 writes `clauses.md` and nothing else does.
- **Phase 7**: T049 and T051 touch `docs/` and `traceability.md` respectively.
- **Phase 8**: T055 writes `figures.ts`, T064 writes nothing.
- **Phase 9**: T066 writes `gaps.md`.

---

## Implementation Strategy

### MVP

**Phase 1 + Phase 2 + Phase 3.** US1 alone closes the gap the premise check found: three texts
in, three texts out, **and none of them rewritable afterwards**. US2 is a field on a row and
US3 is the boundary published — neither is worth building against a version that does not yet
exist.

### What this feature must not do

- **Change what a deletion does to a message.** FR-008, checked at T025 per action and at T070
  against the diff. The tombstone keeps exactly what FR-MSG-08 names and gains nothing.
- **Break a published response.** Every field is additive. The four renames that read better
  are refused in `plan.md`'s complexity table with what each would cost.
- **Solve erasure's collision with an append-only table.** Row 22 owns it; T014 writes it down
  where that chapter will find it, and notes that there will be two such tables by then.
- **Recover anything deleted before the chapter.** T036 measures how much that is.
- **Absorb a repair.** A defect found in earlier work is recorded with its bill — `gaps.md`
  064-5 is already on the carried ledger and is not this chapter's.
