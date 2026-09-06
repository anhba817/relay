# Tasks: A reconnecting client can tell it missed a revision

**Feature**: `specs/044-revision-watermark/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**Format**: `- [ ] TNNN [P?] [USn?] description with a file path`. `[P]` means parallelisable —
different files, no dependency on an incomplete task. Story labels appear only in story phases.

**Tests are not optional here.** Constitution VI is requirement-driven, test-verified delivery,
and every requirement in `spec.md` carries an acceptance scenario. Test tasks are named rather
than assumed.

**Which files are fenced was measured, not guessed** (T003 records it). Eight of nine changed
platform files are fenced and carry an amendment hunk; `services/gateway/src/session.itest.ts`
is published only as `(excerpt)`, so an edit to it is **invisible to `check:fences`** and carries
no hunk. That is a trap, not a convenience.

---

## Phase 1: Setup

- [ ] T001 Pin the lane environment in `specs/044-revision-watermark/baseline.txt` — the nine variables from `quickstart.md`, and what a run looks like when they are missing. Bring the stack up with `RELAY_POSTGRES_PORT=15432`: this machine's own Postgres holds 5432, and `docker compose up` without it binds the wrong port and reads as a broken lane.
- [ ] T002 Measure and record SC-004's and SC-005's baselines **before any code changes**, on this lane and not from `docs/11-scalability-measurement-2026-09-06.md`: run `relay-platform/scripts/scale/load.mjs` at 10,000 connections for the reconnect rate, and time an edit and a delete for the revision cost. **Those published figures are another machine's on another day** — the 10% in SC-004 is against a baseline taken here.
- [ ] T003 Record in `baseline.txt` which changed files are fenced, **in two columns — chapters and appendix — because they are two different numbers**: `internal.ts` 11 + 1, `repository.ts` 23 + 1, `frames.ts` 5 + 1, `session.ts` 16 + 0, `schema.ts`, `resume.ts`, `repository.itest.ts` likewise from `grep -rl 'title="<path>"'` over `app/(en)` and `fences/` separately. A single total conflates a chapter that teaches a file with the appendix that amends it, and this feature's own plan and research quote the chapter-only figures. **`session.itest.ts` is excerpt-only and no gate can see it.**
- [ ] T004 Establish the green baseline: all fourteen gates, every exit code captured into a file **outside any pipeline**. `fail=1` inside `for … | sort` runs in a subshell and dies with it, which has printed "ALL GATES: GREEN" over a red one — feature 043 reproduced that mistake three times.

**Checkpoint**: the lane is green and the two performance baselines exist to compare against.

---

## Phase 2: Foundational — the counter itself

**Blocking.** Every story reads this column; nothing works until it rises correctly.

- [ ] T005 Write `relay-platform/services/api/migrations/0015_channel_revision_sequence.sql` by hand — `revision_sequence bigint not null default 0` on `channels`. **Hand-written and reviewed against SAD §6.1**: feature 043 retired `drizzle-kit`, and `services/api/src/db/migrations.test.ts` fails if the generator, its config or its snapshots return. `bigint` matches `channels.last_sequence`; `default 0` is why existing channels start at zero. **State the non-rewrite property in the migration**: the constitution requires migrations "executable without downtime", and `ADD COLUMN … NOT NULL DEFAULT` is metadata-only from PostgreSQL 11 — on 10 and below it rewrites the table. This lane holds ten thousand channels and a customer's holds more, so the version the property depends on belongs in the file rather than in somebody's memory. **A counter and not a timestamp** — a clock the client and platform disagree about produces wrong repairs in both directions, and a counter answers "how many" for free. (FR-001, FR-010)
- [ ] T006 Add the column to `relay-platform/services/api/src/db/schema.ts`, beside `lastSequence`. (FR-001)
- [ ] T007 Raise the counter in `editMessage` in `relay-platform/services/api/src/db/repository.ts`, **inside the existing transaction and after the compare-and-set that already refuses a deleted message**. A count that rose for an edit the transaction then refused would describe a revision that never happened. (FR-002, FR-003)
- [ ] T008 Raise the counter in `deleteMessage` in the same file, in the same transaction. **A deletion is a revision** — US1 scenario 3 fails if only edits count. (FR-002, FR-003)
- [ ] T009 Change `channelsForUser` in `repository.ts` to return `{ channel_id, revision_sequence }` with a join to `channels`, and map to ids in **both callers** — `relay-platform/services/api/src/internal/memberships.controller.ts` and `relay-platform/services/api/src/internal/session.controller.ts`. **Both, in this task, or the phase cannot end green**: `session.controller.ts` assigns the result straight to `channel_ids: string[]`, so leaving its repair to a later phase breaks typecheck at a boundary the strategy says to commit at. Giving each caller its own query instead would be the two-lists-that-must-agree defect `gaps.md` 3.23-4 records about `targets.ts`. One query, one source. (FR-014)
- [ ] T010 Write the counter's tests in `relay-platform/services/api/src/db/repository.itest.ts`: an edit raises it by one, a delete raises it by one, three revisions raise it by three, **and a send does not move it** (FR-011). The send assertion is the one that catches the failure a customer sees — a counter bumped on send makes every active channel report a repair after every absence.

**Checkpoint**: the count is correct in the database. Nothing reads it yet.

---

## Phase 3: User Story 1 — a reconnecting client learns which channels changed (Priority: P1)

**Goal**: the signal, end to end.

**Independent test**: connect, note a message; disconnect; edit it; reconnect and confirm the ack reports a higher count for that channel than the client presented.

- [ ] T011 [US1] Add `revisionCountSchema` and the ack's `revisions` field to `relay-platform/packages/protocol/src/frames.ts`. **Not `cursorSchema`** — it is `.positive()` and every unrevised channel is **zero**, so reusing it makes an unrevised channel unrepresentable and collapses the two states FR-007 turns on (research R4). **This task comes first in the phase because both consumers import from here**; defining the shape twice is the two-lists defect T009 warns about, one file apart. (FR-004)
- [ ] T012 [US1] Add `channel_revisions` to `internalSessionResponseSchema` in `relay-platform/packages/protocol/src/internal.ts`, **importing `revisionCountSchema` from `./frames.js`** rather than spelling the record shape again — that import direction already exists for `messageSchema` and `MESSAGE_TEXT_MAX`. Give it `.default({})`, following `banned`'s precedent in this same schema: an api built before this feature still satisfies it during a rolling deploy, and the gateway then behaves as it does today. (FR-004, FR-014)
- [ ] T012a [US1] Build the protocol package — `pnpm --filter @relay/protocol build` — **before anything consumes the new fields**. `packages/protocol/package.json` exports `./dist/index.d.ts` and `./dist/index.js` with no tsconfig path mapping to source, so T011 and T012's schema changes are **invisible to the api and the gateway until this runs**, and the three tasks below would fail for a reason that is not theirs. Then `tsc --noEmit` in both consumers: the compiler's list of call sites is the inventory, not a grep. (FR-004, FR-014)
- [ ] T013 [US1] Fill `channel_revisions` in `relay-platform/services/api/src/internal/session.controller.ts`, at the `channel_ids:` field, from T009's rows. **Cited by field and not by line**: T009 changes `channelsForUser`'s return shape in an earlier phase, so a line number recorded now is stale before this task runs — feature 043 had a task name the wrong line and it would have caused a defect. `channel_ids` keeps its shape: eleven chapters publish that field and widening it into objects would edit all of them for a field they do not read. (FR-004)
- [ ] T014 [US1] Parse `?rev=<channel_id>:<count>` in `relay-platform/services/gateway/src/resume.ts`, **with the same rsplit rule as `cursor` and as a separate parameter**. A third cursor field would rsplit `<channel>:<seq>:<rev>` into channel `"<channel>:<seq>"` and sequence `rev` — every resume silently resuming from the wrong place, which produces plausible numbers rather than an error (research R2). Malformed degrades rather than refuses, matching `cursor`. (FR-005)
- [ ] T015 [US1] Compare and fill the ack in `relay-platform/services/gateway/src/session.ts`. Report **every** channel the user belongs to, including zeros and channels the client asked nothing about — a client needing no repair still needs a baseline to store. A presented count higher than the platform's is treated as no repair and **must not refuse the connection**: refusing over a number the client supplied is a denial of service the client controls. **Reporting every channel is FR-007a**: a client told nothing about a channel has no baseline to store, and its next reconnect is the first one again. (FR-006, FR-007a, FR-008, FR-009)
- [ ] T016 [US1] Verify the rewritten FR-007 against the three absences in `specs/044-revision-watermark/contracts/ws-reconnect.md`, and confirm the implementation answers each the same way. **The amendment itself is already made** — this task asked for it and the first analysis pass performed it, which is why the task now verifies rather than edits. A task whose work is silently done is one somebody ticks having done nothing.
- [ ] T017 [US1] Write the transport tests. In `relay-platform/packages/protocol/src/frames.test.ts`: the ack accepts a count of zero and `cursorSchema` still rejects it. In `relay-platform/services/gateway/src/session.itest.ts`: the four cursor/`rev` combinations from `contracts/ws-reconnect.md` — absent/absent, present/absent, present/present, absent/present. **Assert the pre-upgrade row explicitly**; it is the one a literal reading of FR-007 gets wrong. **This file is excerpt-only, so no gate compares it to anything** (T003).
- [ ] T018 [US1] Append an amendment hunk to `relay-tutorial/fences/post-series.md` for each fenced file changed in this phase — `internal.ts`, `frames.ts`, `resume.ts`, `session.ts`, `frames.test.ts` — and re-run `check:fences` after each. **Regenerate at `-U6` if a pre-image matches twice.** (FR-015)
- [ ] T019 [US1] Verify against `quickstart.md` scenarios 1 through 5, including scenario 5's cursor-still-parses check with a channel id containing a colon if one can be produced. Scenario 2 is the story's acceptance and scenario 3 is its negative — **a signal that fires for everyone is as useless as one that never fires**. (SC-001, SC-002)

**Checkpoint**: US1 is independently shippable. A client that missed a revision can find out.

---

## Phase 4: User Story 2 — the repair is bounded (Priority: P2)

**Goal**: a client repairs only what changed, and knows how much changed.

**Independent test**: belong to several channels, revise one during an absence, and confirm only that channel reports a raised count.

**Most of this is verification of US1's design rather than new code**, because FR-009 puts the per-channel shape in US1's build. That is stated rather than hidden: a phase whose tasks are mostly tests is honest when the design already carries the property, and dishonest when it is used to look busy.

- [ ] T020 [US2] Handle the channel joined during the absence in `relay-platform/services/gateway/src/session.ts`: the client held nothing in it, so it must not be reported as needing repair even though the platform's count exceeds the absent one. Its messages arrive by the ordinary replay. **This is FR-007's third absence** and the reason FR-007 was rewritten: the earlier "treated as presenting zero" signalled a repair here. (FR-007, FR-007a)
- [ ] T021 [US2] Write the boundedness tests in `relay-platform/services/gateway/src/session.itest.ts`: revisions in one channel of several raise only that channel's count; three revisions produce a difference of exactly three; a newly joined channel signals no repair. (SC-002, SC-003)
- [ ] T022 [US2] Append amendment hunks for anything this phase changed, and re-run `check:fences`. (FR-015)

**Checkpoint**: US2 is independent of US3.

---

## Phase 5: User Story 3 — a client developer can find the obligation (Priority: P3)

**Goal**: the contract is published, not inferred.

- [ ] T023 [US3] Document the count in `docs/05-sad.md` §5.2, the runtime view that already carries `connection.ack {resume_ok}` in its sequence diagram. **There is no public protocol reference to put this in** — the implementation review lists one as absent and it is Part 4's — so §5.2 is the nearest published home, and this task records that choice rather than leaving a reader to wonder why it is in the SAD. (FR-012)
- [ ] T024 [US3] Amend **SRS FR-016a and SRS FR-016b** in `docs/04-srs.md` to name the signal, so the documented limit and the documented remedy sit together. Add revision **1.10** to Appendix D, appended below 1.9 — `check-revision-order.mjs` fails on a descent. (FR-013, SC-007)
- [ ] T025 [US3] Verify `quickstart.md` scenario 7, and **read the amended §5.2 and the two clauses as somebody who has not seen this feature** — SC-006 asks whether the repair can be implemented from the published text alone, and no instrument in these repositories can answer that. `specs/036-chapter-3-18/reader-protocol.md` is the procedure. Then re-run `check:docs`: `docs/04-srs.md` and `docs/05-sad.md` are both mirrored into `relay-tutorial/content/docs/`, so `pnpm sync:docs` must run or the drift check fails.

**Checkpoint**: all three stories complete.

---

## Phase 6: Polish and close-out

- [ ] T026 Run the coverage lane with the pinned variables and read `coverage/coverage-summary.json`, **not the text table** — the text reporter omits a file at 100% on all four metrics, which is the set this feature needs to see.
- [ ] T027 Re-pin the changed files in `relay-platform/vitest.coverage.config.mts`, and **prove the pins are live**: a per-file threshold whose key matches no file is ignored silently and protects nothing. Demand 101% of a file at 100% and confirm vitest names the key.
- [ ] T028 [P] Read every new test's title against its assertion, one at a time, in the three files this feature adds tests to — named rather than described: `relay-platform/services/api/src/db/repository.itest.ts`, `relay-platform/packages/protocol/src/frames.test.ts`, `relay-platform/services/gateway/src/session.itest.ts`. **Expect the count to be wrong** — chapter 3.24's task named nine files and the tree held twenty-two. **Strip any task id from a title** — requirement ids belong there, task ids do not. Feature 043's own audit caught two titles that overclaimed.
- [ ] T029 [P] Run the credential scan over this feature's diff across **all three repositories**, and record every pattern searched and every hit classified in `baseline.txt`. Never report only "clean".
- [ ] T030 Write `specs/044-revision-watermark/gaps.md`, carrying feature 043's twenty-four items **re-measured against the tree rather than copied** — three of 043's closed on re-measurement without anyone working on them. Close nothing that this feature did not close.
- [ ] T031 Run the twenty-run battery of `pnpm test:integration` from a cleared lane with the sequencer caches removed — including the **root** `node_modules/.vite/vitest`, which a `packages/*` and `services/*` glob misses. **Nothing else runs on the machine.**
- [ ] T032 Re-measure SC-004 and SC-005 against T002's baselines using `relay-platform/scripts/scale/load.mjs`, and record both in `specs/044-revision-watermark/baseline.txt`. **If either moved more than 10%, record which of three was chosen and why**: accept it with the measurement attached, move the cost off the handshake, or drop the feature's shape. Do not let the baseline quietly become whatever the lane now costs.
- [ ] T033 Run all fourteen gates last — `pnpm typecheck`, `pnpm lint`, `pnpm build` in `relay-platform`; `pnpm check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` in `relay-tutorial`; and this feature's instruments in `specs/044-revision-watermark/` — with every exit code written to a file outside any pipeline.
- [ ] T034 Commit the close-out records, then trim `CLAUDE.md` and update the `SPECKIT` block to point past this feature.

---

## Dependencies

    Phase 1 (T001-T004)  ──▶ Phase 2 (T005-T010)  ──┬──▶ US1 (T011-T019)  P1, MVP
                                                     ├──▶ US3 (T023-T025)  P3, docs only
                                                     └──▶ US1 ──▶ US2 (T020-T022)  P2
                                                                    │
                                              Phase 6 (T026-T034) ◀─┘

**US2 depends on US1** — it verifies and extends the signal US1 builds, and cannot be tested
before the signal exists. This is the one story pair that is not independent, and saying so is
better than claiming an independence the tasks do not have.

**US3 depends on US1, and an earlier draft of this graph said it did not.** The documentation
describes the count *in the context of the reconnect response*, and FR-012 requires it to state
what a client does when the count rises — which is the signal US1 builds. **Publishing a contract
for a field the platform does not yet send is the shape feature 043 spent a whole story on**: a
declared event type nothing emits produces a permanently silent endpoint, and a documented ack
field nothing populates would produce a permanently silent client.

## Parallel opportunities

- **T028 and T029** are different files and different questions.
- Within US1, **almost nothing is parallel, and the restructure is why.** T011 defines the shape
  both consumers import, T012 imports it, T012a makes both visible, and T013 through T015 depend
  on that build. The one genuine pair is **T013** (api) and **T014** (gateway parsing), which
  touch different services once T012a has run.
- **T005 and T006** must be sequential despite touching different files: the migration defines
  what the schema model describes, and a model that describes a column no migration created is
  the drift the pair exists to prevent.

## Implementation strategy

**MVP is Phase 1 + Phase 2 + US1.** That is the whole defect closed: a client that missed a
revision can find out. US2 makes the repair bounded and US3 publishes the obligation, and both
are improvements on a signal that already works.

**Commit each phase.** `git checkout` on a file with uncommitted work has destroyed it twice in
this project.

**Expect the file count to be wrong.** The plan estimates twelve and feature 043 estimated
seventeen against fifty-eight — because a plan counts the fix and not the verification. Every
unplanned file in 043 came from running something rather than reading it.
