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

- [X] T001 Pin the lane environment in `specs/044-revision-watermark/baseline.txt` — the nine variables from `quickstart.md`, and what a run looks like when they are missing. Bring the stack up with `RELAY_POSTGRES_PORT=15432`: this machine's own Postgres holds 5432, and `docker compose up` without it binds the wrong port and reads as a broken lane.
- [X] T002 Measure and record SC-004's and SC-005's baselines **before any code changes**, on this lane and not from `docs/11-scalability-measurement-2026-09-06.md`: run `relay-platform/scripts/scale/load.mjs` at 10,000 connections for the reconnect rate, and time an edit and a delete for the revision cost. **Those published figures are another machine's on another day** — the 10% in SC-004 is against a baseline taken here.
- [X] T003 Record in `baseline.txt` which changed files are fenced, **in two columns — chapters and appendix — because they are two different numbers**: `internal.ts` 11 + 1, `repository.ts` 23 + 1, `frames.ts` 5 + 1, `session.ts` 16 + 0, `schema.ts`, `resume.ts`, `repository.itest.ts` likewise from `grep -rl 'title="<path>"'` over `app/(en)` and `fences/` separately. A single total conflates a chapter that teaches a file with the appendix that amends it, and this feature's own plan and research quote the chapter-only figures. **`session.itest.ts` is excerpt-only and no gate can see it.**
- [X] T004 Establish the green baseline in `specs/044-revision-watermark/baseline.txt`: every gate, with each exit code captured into a file **outside any pipeline**. **Count them before claiming a number** — this feature's six instruments in `specs/044-revision-watermark/` did not exist when the count of fourteen was written, so the real figure is eight until they are copied in and re-pointed. `fail=1` inside `for … | sort` runs in a subshell and dies with it, which has printed "ALL GATES: GREEN" over a red one — feature 043 reproduced that mistake three times.

**Checkpoint**: the lane is green and the two performance baselines exist to compare against.

---

## Phase 2: Foundational — the counter itself

**Blocking.** Every story reads this column; nothing works until it rises correctly.

- [X] T005 Write `relay-platform/services/api/migrations/0015_channel_revision_sequence.sql` by hand — `revision_sequence bigint not null default 0` on `channels`. **Hand-written and reviewed against SAD §6.1**: feature 043 retired `drizzle-kit`, and `services/api/src/db/migrations.test.ts` fails if the generator, its config or its snapshots return. `bigint` matches `channels.last_sequence`; `default 0` is why existing channels start at zero. **State the non-rewrite property in the migration**: the constitution requires migrations "executable without downtime", and `ADD COLUMN … NOT NULL DEFAULT` is metadata-only from PostgreSQL 11 — on 10 and below it rewrites the table. This lane holds ten thousand channels and a customer's holds more, so the version the property depends on belongs in the file rather than in somebody's memory. **A counter and not a timestamp** — a clock the client and platform disagree about produces wrong repairs in both directions, and a counter answers "how many" for free. (FR-001, FR-010)
- [X] T006 Add the column to `relay-platform/services/api/src/db/schema.ts`, beside `lastSequence`. (FR-001)
- [X] T007 Raise the counter in `editMessage` in `relay-platform/services/api/src/db/repository.ts`, **inside the existing transaction and after the compare-and-set that already refuses a deleted message**. A count that rose for an edit the transaction then refused would describe a revision that never happened. (FR-002, FR-003)
- [X] T008 Raise the counter in `deleteMessage` in `relay-platform/services/api/src/db/repository.ts`, in the same transaction. **A deletion is a revision** — US1 scenario 3 fails if only edits count. (FR-002, FR-003)
- [X] T009 Change `channelsForUser` in `repository.ts` to return `{ channel_id, revision_sequence }` with a join to `channels`, and map to ids in **both callers** — `relay-platform/services/api/src/internal/memberships.controller.ts` and `relay-platform/services/api/src/internal/session.controller.ts`. **Both, in this task, or the phase cannot end green**: `session.controller.ts` assigns the result straight to `channel_ids: string[]`, so leaving its repair to a later phase breaks typecheck at a boundary the strategy says to commit at. Giving each caller its own query instead would be the two-lists-that-must-agree defect `gaps.md` 3.23-4 records about `targets.ts`. One query, one source. (FR-014)
- [X] T010 Write the counter's tests in `relay-platform/services/api/src/db/repository.itest.ts`: an edit raises it by one, a delete raises it by one, three revisions raise it by three, **and a send does not move it** (FR-011). This file drives the repository directly and so sidesteps the route-level credential rules T017 must obey. The send assertion is the one that catches the failure a customer sees — a counter bumped on send makes every active channel report a repair after every absence.
- [X] T010a Append an amendment hunk to `relay-tutorial/fences/post-series.md` for each fenced file this phase changed — `services/api/src/db/schema.ts`, `db/repository.ts`, `db/repository.itest.ts`, `internal/session.controller.ts`, `internal/memberships.controller.ts` — and re-run `check:fences`. **This task was missing.** T018 and T022 append hunks for their own phases and nothing covered this one, so five fenced files would have reached US1 unamended and `check:fences` would have failed there for a reason belonging two phases back. Found by running the gate at the phase boundary rather than by reading the list. (FR-015)

**Checkpoint**: the count is correct in the database. Nothing reads it yet.

---

## Phase 3: User Story 1 — a reconnecting client learns which channels changed (Priority: P1)

**Goal**: the signal, end to end.

**Independent test**: connect, note a message; disconnect; edit it; reconnect and confirm the ack reports a higher count for that channel than the client presented.

- [ ] T011 [US1] Add `revisionCountSchema` and the ack's `revisions` field to `relay-platform/packages/protocol/src/frames.ts`. **Not `cursorSchema`** — it is `.positive()` and every unrevised channel is **zero**, so reusing it makes an unrevised channel unrepresentable and collapses the two states FR-007 turns on (research R4). **This task comes first in the phase because both consumers import from here**; defining the shape twice is the two-lists defect T009 warns about, one file apart. (FR-004)
- [ ] T012 [US1] Add `channel_revisions` to `internalSessionResponseSchema` in `relay-platform/packages/protocol/src/internal.ts`, **importing `revisionCountSchema` from `./frames.js`** rather than spelling the record shape again — that import direction already exists for `messageSchema` and `MESSAGE_TEXT_MAX`. Give it `.default({})`, following `banned`'s precedent in this same schema: an api built before this feature still satisfies it during a rolling deploy, and the gateway then behaves as it does today. (FR-004, FR-014)
- [ ] T012a [US1] Build the protocol package — `pnpm --filter @relay/protocol build` — **before anything consumes the new fields**. `packages/protocol/package.json` exports `./dist/index.d.ts` and `./dist/index.js` with no tsconfig path mapping to source, so T011 and T012's schema changes are **invisible to the api and the gateway until this runs**, and the three tasks below would fail for a reason that is not theirs. Then `tsc --noEmit` in both consumers: the compiler's list of call sites is the inventory, not a grep. (FR-004, FR-014)
- [ ] T013 [US1] Fill `channel_revisions` in `relay-platform/services/api/src/internal/session.controller.ts`, at the `channel_ids:` field, from T009's rows. **Cited by field and not by line**: T009 changes `channelsForUser`'s return shape in an earlier phase, so a line number recorded now is stale before this task runs — feature 043 had a task name the wrong line and it would have caused a defect. `channel_ids` keeps its shape: eleven chapters publish that field and widening it into objects would edit all of them for a field they do not read. (FR-004)
- [X] T014 [US1] **No request parameter — decided, built and reverted.** A draft had the client present its counts on the upgrade URL so the gateway could compare; `parseRevisions` was written in `relay-platform/services/gateway/src/resume.ts` and then removed, because the ack carries every count and the client can compare against its own. The file records why where the function stood. **A parameter the server parses and never acts on is a contract it can never remove**, and the rsplit rule that made a third cursor field impossible stays intact. (FR-005)
- [X] T015 [US1] Fill the ack's `revisions` in `relay-platform/services/gateway/src/session.ts` from the session response's `channel_revisions`. **The gateway reports; it does not compare** — it never learns what a client holds, so it cannot be wrong about it. Report **every** channel the user belongs to, including zeros and channels the client asked nothing about — a client needing no repair still needs a baseline to store. A presented count higher than the platform's is treated as no repair and **must not refuse the connection**: refusing over a number the client supplied is a denial of service the client controls. **Reporting every channel is FR-007a**: a client told nothing about a channel has no baseline to store, and its next reconnect is the first one again. (FR-006, FR-007a, FR-008, FR-009)
  **Measured on the implementation, not asserted**: the premise probe re-run against the built
  gateway reported `revisions: {<channel>: 2}` on an ack whose `CLIENT_SAW_THE_EDIT` was
  `false` and whose replay carried zero sequences. Two revisions happened, the client received
  neither, and the count is the only thing on the wire that says so.
- [X] T016 [US1] Verify the rewritten FR-007 against the three absences in `specs/044-revision-watermark/contracts/ws-reconnect.md`, and confirm the implementation answers each the same way. **The amendment itself is already made** — this task asked for it and the first analysis pass performed it, which is why the task now verifies rather than edits. A task whose work is silently done is one somebody ticks having done nothing.

  **Verified. All three absences reach the same two lines of code, because the gateway does not
  branch on them at all**:

  | FR-007's absence | Contract row | What the code does |
  |---|---|---|
  | a first connection | *receives every count, stores them, repairs nothing* | `session.ts:1237` — the `presented === undefined` arm calls the same `ack()` |
  | built before this feature | *ignores the new field entirely* | additive field on the ack payload; the client never sends anything, so there is no request shape to be missing |
  | a channel joined during the absence | *repairs nothing, stores the reported count* | `revisions` is `connection.revisions` whole, never scoped by the presented cursor — so a channel absent from the cursor still gets its count |

  **One `ack()` helper, three call sites** — fresh connect, degraded resume, successful resume —
  and `revisions: connection.revisions` sits inside the helper rather than at each site. The
  earlier draft's defect was a comparison; there is now no comparison to get wrong, and the
  three cases are indistinguishable to the gateway by construction rather than by three matching
  branches somebody has to keep matching.
- [X] T017 [US1] Write the transport tests. In `relay-platform/packages/protocol/src/frames.test.ts`: the ack accepts a count of zero and `cursorSchema` still rejects it. In `relay-platform/services/gateway/src/resume.itest.ts`: the three acks a connection can get — fresh, resumed, degraded — each carrying the counts, and the resumed one carrying a channel the presented cursor never mentions. In `relay-platform/services/gateway/src/session.itest.ts`: the chain end to end against a real api. **Both the send and the edit need an end-user token**: an application credential may send only as a bot (`sender_not_permitted`) and the edit route refuses an API key outright (`wrong_credential_type`). Mint one with `/auth/dev-token` — a probe of this feature's own premise hit both rules, in that order, before it ran.

  **THE TASK ASKED FOR FOUR `cursor`/`rev` COMBINATIONS AND THERE ARE NONE**, because T014
  removed the parameter: a client sends nothing to obtain this signal, so there is no request
  shape to vary. What varies is which ack a connection gets, and there are three — the
  `presented === undefined` arm, the successful resume, and the degrade. All three go through
  one `ack()` helper, so `revisions` rides them by construction rather than by three branches
  somebody has to keep matching. The pre-upgrade row the task singled out is not a fourth case
  at all: an un-upgraded client takes whichever of the three its cursor selects and ignores a
  field it does not know.

  **And the file moved.** The cursor cases went to `resume.itest.ts`, because only a stubbed api
  lets a test SAY what the counts are — which is the only way to assert a channel the cursor
  never mentions. `session.itest.ts` got the end-to-end instead: a real edit over REST raising a
  real count on a real ack. `repository.itest.ts` proves the column moves and `resume.itest.ts`
  proves the ack carries what the api reports; **neither proves the two are connected**, and a
  repository counting correctly into a field nobody read would pass both.

  **FORCED RED BEFORE IT WAS BELIEVED.** `editMessage`'s bump was removed, the api rebuilt, and
  the suite re-run: `expected 2 to be 3` at the edit assertion, the deletion assertion behind it.
  Restored and re-run green. Two probes in this project have failed to go red while appearing to
  test something.

  **AND IT FOUND TWO FILES NOBODY LISTED.** `revisions` is required on `connectionAckSchema` —
  right, because the platform BUILDS the ack — which turned three fixtures red for the same
  reason: `frames.test.ts`'s valid specimen, and the forged-frame builders in `session.itest.ts`
  and `isolation.itest.ts`. Those last two assert that a WELL-FORMED outbound frame is refused
  for its DIRECTION; a sample missing a required field is refused a phase earlier as
  `invalid_frame`, and nine direction assertions quietly become nine parser assertions.
  **Chapter 3.23 made the identical repair to the identical pair** for `message.deleted`, and
  each file's comment says so. Second incident, same two builders.

- [X] T018 [US1] Append an amendment hunk to `relay-tutorial/fences/post-series.md` for each fenced file changed in this phase, and re-run `check:fences`. **Regenerate at a wider context if a pre-image matches twice.** (FR-015)

  **THE TASK NAMED FIVE FILES AND THIRTEEN NEEDED HUNKS.** The five were the ones the plan
  predicted; the other eight are `auth.ts`, `registry.ts`, `session.controller.ts` and five test
  fixtures that had to state a revision count. `session.itest.ts` is the fourteenth changed file
  and needs none — it is published only as `(excerpt)`, so no gate compares it to anything. This
  is the plan's file count moving for the third time, and in the same direction each time:
  **a plan counts the fix and not what the fix drags with it.**

  **The generator replays the checker's own code rather than a second copy of it.** A hunk
  generated against a different reconstruction of the chain is a hunk the checker rejects for
  reasons neither of them explains — so `check-fence-chain.mjs` was copied, truncated at the HEAD
  comparison, made to dump its 240-file end state, run, and deleted. The diffs are that state
  against the working tree.

  **`-U6` WAS NOT ENOUGH FOR ONE FILE, AND THE FAILURE IS THE INTERESTING PART.**
  `resume.itest.ts` carries eight session stubs that are byte-identical for far more than six
  lines — they differ only in their `backfill` bodies. The checker said `pre-image matched 2
  times (need exactly 1)`, which is the property it exists to enforce: a hunk that could apply in
  two places is not a proof that it applied in the right one. Raising the context to `-U10` made
  all nine unique, and it was verified to apply clean before it was pasted rather than after.
  `-U8` was tried and was worse in a way worth recording — `[1, 1, 3]` — because widening context
  merges adjacent hunks, and a merged hunk can span more repetition than either half did.

- [X] T019 [US1] Verify against `quickstart.md` scenarios 1 through 5. Scenario 2 is the story's acceptance and scenario 3 is its negative — **a signal that fires for everyone is as useless as one that never fires**. (SC-001, SC-002)

  **All five ran green**, against a real api and a real gateway on the lane:

  | | Result |
  |---|---|
  | 1 — rises per revision, not on a send | `0 → 0` (send), `→ 1`, `→ 2` (edits), `→ 3` (delete) |
  | 2 — a client that missed one is told which channel | held 3, reported 4, **missed 1**, channel named |
  | 3 — a client that missed nothing is told nothing | held 4, reported 4 |
  | 4 — a pre-upgrade client is not sent on a repair | payload keys `user, cursor, resume_ok, truncated, revisions`; `resume_ok: true`, cursor unchanged |
  | 5 — the cursor still parses, and gained no third field | presented `<uuid>:1`, resolved to `1` |

  **SCENARIOS 4 AND 5 HAD TO BE REWRITTEN BEFORE THEY COULD BE RUN**, because both described the
  `?rev=` parameter T014 removed. Scenario 4's whole point survives the rewrite and gets stronger:
  the case it guarded against — an absent count read as zero, signalling a repair to every client
  that never stored one — **cannot arise now**, because the platform compares nothing. A branch
  that handles a case is worse than a design in which the case does not exist. `plan.md` and
  `research.md` carried the same stale parameter and were corrected in the same pass; R2's
  decision now records that its own answer was built and reversed, and why the reversal is not
  about parsing at all.

  **AND SCENARIO 1 COULD NOT BE FOLLOWED AS WRITTEN.** Its printed order was
  `send → edit → delete → edit again`, and editing a deleted message answers **403**. Second time
  a scenario in this file has been unrunnable — the first was the credential rules, now in
  Prerequisites. The order is corrected, and the 403 turned into an assertion worth keeping: after
  the refusal the count stays at 3, because FR-003 puts the increment inside the transaction that
  applies the revision, so a revision that does not commit raises nothing.

**Checkpoint**: US1 is independently shippable. A client that missed a revision can find out.

---

## Phase 4: User Story 2 — the repair is bounded (Priority: P2)

**Goal**: a client repairs only what changed, and knows how much changed.

**Independent test**: belong to several channels, revise one during an absence, and confirm only that channel reports a raised count.

**Most of this is verification of US1's design rather than new code**, because FR-009 puts the per-channel shape in US1's build. That is stated rather than hidden: a phase whose tasks are mostly tests is honest when the design already carries the property, and dishonest when it is used to look busy.

- [ ] T020 [US2] Handle the channel joined during the absence in `relay-platform/services/gateway/src/session.ts`: the client held nothing in it, so it must not be reported as needing repair even though the platform's count exceeds the absent one. Its messages arrive by the ordinary replay. **This is FR-007's third absence** and the reason FR-007 was rewritten: the earlier "treated as presenting zero" signalled a repair here. (FR-007, FR-007a)
- [ ] T021 [US2] Write the boundedness tests in `relay-platform/services/gateway/src/session.itest.ts`: revisions in one channel of several raise only that channel's count; three revisions produce a difference of exactly three; a newly joined channel signals no repair. Same credential rules as T017. (SC-002, SC-003)
- [ ] T022 [US2] Append amendment hunks to `relay-tutorial/fences/post-series.md` for anything this phase changed, and re-run `check:fences`. (FR-015)

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
