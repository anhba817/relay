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

- [X] T011 [US1] Add `revisionCountSchema` and the ack's `revisions` field to `relay-platform/packages/protocol/src/frames.ts`. **Not `cursorSchema`** — it is `.positive()` and every unrevised channel is **zero**, so reusing it makes an unrevised channel unrepresentable and collapses the two states FR-007 turns on (research R4). **This task comes first in the phase because both consumers import from here**; defining the shape twice is the two-lists defect T009 warns about, one file apart. (FR-004)
  Verified in the tree: `revisionCountSchema` declared and `revisions: revisionCountSchema` on
  `connectionAckSchema.payload` — **required**, which is right for a frame the platform builds and
  is the inverse of chapter 3.24's `outboxEventSchema` mistake. It turned three fixtures red on the
  spot, which is the compiler naming every construction site.

- [X] T012 [US1] Add `channel_revisions` to `internalSessionResponseSchema` in `relay-platform/packages/protocol/src/internal.ts`, **importing `revisionCountSchema` from `./frames.js`** rather than spelling the record shape again — that import direction already exists for `messageSchema` and `MESSAGE_TEXT_MAX`. Give it `.default({})`, following `banned`'s precedent in this same schema: an api built before this feature still satisfies it during a rolling deploy, and the gateway then behaves as it does today. (FR-004, FR-014)
  On `internalSessionResponseSchema` at `internal.ts:204`, importing `revisionCountSchema` rather
  than respelling the record, with `.default({})`. **Not** on `internalMembershipsResponseSchema` —
  that route is a backstop answering "is this user still a member", and a count there would be a
  second place for the same number to be read from and disagree.

- [X] T012a [US1] Build the protocol package — `pnpm --filter @relay/protocol build` — **before anything consumes the new fields**. `packages/protocol/package.json` exports `./dist/index.d.ts` and `./dist/index.js` with no tsconfig path mapping to source, so T011 and T012's schema changes are **invisible to the api and the gateway until this runs**, and the three tasks below would fail for a reason that is not theirs. Then `tsc --noEmit` in both consumers: the compiler's list of call sites is the inventory, not a grep. (FR-004, FR-014)
  `packages/protocol/dist/frames.js` carries the schema, so the api and the gateway can see it.
  This task exists because the package exports `./dist` with no path mapping to source, and the
  second analysis pass found three tasks that would otherwise have failed for a reason that was
  not theirs.

- [X] T013 [US1] Fill `channel_revisions` in `relay-platform/services/api/src/internal/session.controller.ts`, at the `channel_ids:` field, from T009's rows. **Cited by field and not by line**: T009 changes `channelsForUser`'s return shape in an earlier phase, so a line number recorded now is stale before this task runs — feature 043 had a task name the wrong line and it would have caused a defect. `channel_ids` keeps its shape: eleven chapters publish that field and widening it into objects would edit all of them for a field they do not read. (FR-004)
  Filled from the hoisted `memberships` array, which is the same rows `channel_ids` maps — one
  query feeding two fields, because at 10,000 connections a second call here is 10,000 extra reads.

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

- [X] T020 [US2] Handle the channel joined during the absence in `relay-platform/services/gateway/src/session.ts`. **This is FR-007's third absence** and the reason FR-007 was rewritten: the earlier "treated as presenting zero" signalled a repair here. (FR-007, FR-007a)

  **NO CODE. The case cannot arise, and that is the outcome rather than the excuse.** This task
  was written against the draft in which the gateway compared the client's counts with its own;
  a channel absent from the client's list read as zero, zero is lower than any revised channel,
  and the client was sent to repair something it held nothing of. The gateway now compares
  nothing, so there is no branch that could get this wrong and none was added. **A design in
  which a case does not exist beats a branch that handles it** — the branch is a thing that can
  rot, and the third absence is exactly the one no test was asserting when the wording was wrong.

  Verified twice rather than reasoned about once: `resume.itest.ts` asserts that the counts are
  reported WHOLE and never scoped to the presented cursor, and T021's fixture joins a channel
  mid-absence and finds it reported with the revision that happened before the client arrived.

  **And the one way FR-007a could still be violated was checked at its source.** If the api's
  `channel_revisions` could omit a channel that `channel_ids` names, a client would get no
  baseline for it. Both are built from the same `memberships` array in `session.controller.ts` —
  one query, two `.map`s — so the key sets are identical by construction and not by agreement.

- [X] T021 [US2] Write the boundedness tests in `relay-platform/services/gateway/src/session.itest.ts`: revisions in one channel of several raise only that channel's count; three revisions produce a difference of exactly three; a newly joined channel signals no repair. Same credential rules as T017. (SC-002, SC-003)

  **A ONE-CHANNEL FIXTURE CAN STATE BOUNDEDNESS AND CANNOT FAIL IT.** "Only the revised channel
  rose" is trivially true when there is one channel, and a gateway that raised every channel's
  count would pass. So `boot` now returns a seeding handle and the test makes its own second and
  third channels, rather than adding channels to a fixture twenty-nine other tests would then be
  connecting through for no reason of their own.

  All three claims in one test, because they share an expensive setup: `+3` on the revised
  channel, unchanged on the quiet one, and the channel joined mid-absence reported at `1` —
  carrying a revision that happened before this client could ever have seen it, with no count
  held to compare it against.

  **THE FIRST TWO ATTEMPTS TO FORCE IT RED WERE INVALID, AND THE SECOND ONE EXPLAINS WHY.**
  Boundedness rests on `.where(eq(channels.id, channelId))`, so a probe has to widen that
  predicate — and both a dropped `WHERE` and a deliberately inverted one came back **500**, which
  says nothing about boundedness. Asked directly, the database answered:

      global-operation guard: this statement modified sentinel row public.channels …
      which belongs to no test — the bait planted by packages/test-harness/src/guard.itest.ts

  **The platform already refuses the defect this probe was trying to introduce.** A wrongly-scoped
  bump on `channels` is not merely untested here, it is caught by the bait — which is a stronger
  guarantee than the assertion, and the reason the assertion could not be made to fail that way.

  The exactly-three claim was then forced properly, by bumping the counter by two: `expected 6 to
  be 3`, with the end-to-end test's `expected 6 to be 5` behind it. Restored, rebuilt, 30 green.

- [X] T022 [US2] Append amendment hunks to `relay-tutorial/fences/post-series.md` for anything this phase changed, and re-run `check:fences`. (FR-015)

  **None needed, and the reason is measured rather than assumed.** This phase changed exactly one
  file, `session.itest.ts`, which is published only as `title="… (excerpt)"` — one of thirteen
  such files repository-wide. `check:fences` skips those titles by name, so an edit to it is
  invisible to the gate and carries no hunk. Re-run anyway and green at 240 files: **a task that
  reports "nothing to do" without running the checker is a task that has not checked.**

  Worth keeping in view for close-out: this is the same property that makes `session.itest.ts`
  the least-guarded file this feature touched. It now holds the only end-to-end proof that the
  column, the api and the ack are connected, and no gate would notice if it drifted.

**Checkpoint**: US2 is independent of US3.

---

## Phase 5: User Story 3 — a client developer can find the obligation (Priority: P3)

**Goal**: the contract is published, not inferred.

- [X] T023 [US3] Document the count in `docs/05-sad.md` §5.2, the runtime view that already carries `connection.ack {resume_ok}` in its sequence diagram. **There is no public protocol reference to put this in** — the implementation review lists one as absent and it is Part 4's — so §5.2 is the nearest published home, and this task records that choice rather than leaving a reader to wonder why it is in the SAD. (FR-012)

  The sequence diagram's ack line became `connection.ack {resume_ok, revisions}`, and the prose
  after it states the limit, the field, the comparison table, and the two things the platform
  deliberately does not do. `check:figures` green at 264 figures — **a mermaid block is prose to
  every checker here**, so the diagram edit was verified by running the figure check rather than
  by assuming a diagram is inert.

- [X] T024 [US3] Amend the clauses in `docs/04-srs.md` to name the signal, so the documented limit and the documented remedy sit together. Add revision **1.10** to Appendix D, appended below 1.9 — `check-revision-order.mjs` fails on a descent. (FR-013, SC-007)

  **THE TASK NAMED CLAUSES THAT DO NOT EXIST IN THIS DOCUMENT.** It said "SRS FR-016a (3.23) and SRS
  FR-016b (3.23)", and so does the spec's FR-013 and the quickstart's scenario 7. Those are **chapter
  3.23's specification ids**, defined in `specs/041-chapter-3-23/spec.md`; the SRS carried that
  limit in revision 1.6's narrative and in `FR-RTM-03`'s silence, and the only place in `docs/`
  that spells `FR-016a (3.23)` is a quoted ADR passage inside the SAD. Grepping the identifier returned
  one hit and no clause. **Reading the clauses found three to amend where the task expected two:**

  | Clause | Why it was wrong before |
  |---|---|
  | `EIR-WS-03` | it enumerates the ack's contents — identity and cursor — and the enumeration was incomplete |
  | `FR-RTM-03` | it describes what resume delivers and said nothing about what it cannot |
  | `FR-RTM-05` | it lists edit and deletion among the events emitted, without saying they reach only clients connected at the time |

  Revision **1.10** appended, and `check-revision-order` reads 11 revisions ascending 1.0 to 1.10
  — worth confirming rather than assuming, because a string comparison would have put 1.10 below
  1.9. `check:srs` green at 245 clause rows, 245 unique identifiers.

- [X] T025 [US3] Verify `quickstart.md` scenario 7, and **read the amended §5.2 and the clauses as somebody who has not seen this feature** — SC-006 asks whether the repair can be implemented from the published text alone. Then re-run `check:docs`: `docs/04-srs.md` and `docs/05-sad.md` are both mirrored into `relay-tutorial/content/docs/`, so `pnpm sync:docs` must run or the drift check fails.

  **THE READING PASS FOUND A REQUIREMENT THE PUBLISHED TEXT DID NOT SATISFY.** With the spec and
  the source closed, the published text answered which field, what shape, which channels appear,
  what to compare against, what to do when the count is higher or equal, and when to store — and
  **had no instruction at all for a count that is lower than the one the client holds.** What it
  said was that the *platform* refuses nothing over such a count, which is the platform's half of
  FR-008 and not the client's. A developer whose local number is stale, restored from a backup, or
  simply wrong had nothing to follow. Two smaller gaps came out of the same pass: the history
  re-read named no endpoint, and "the difference is how many" never said how many *of what* —
  three revisions may be three edits of one message. §5.2 now carries a three-row table and both
  clarifications.

  **This does not discharge SC-006, and saying it did would be the easy lie.** The exercise finds
  information that is ABSENT. It cannot find information that is present and unclear, because the
  person running it wrote the feature and cannot unknow the answer. SC-006 asks whether somebody
  who does not already know can implement from the text, and no instrument in these repositories
  answers that — six Python checkers, and every one of them compares bytes. It needs a person:
  `specs/036-chapter-3-18/reader-protocol.md`, 45 minutes, six questions. Chapters 3.14 through
  3.24 have each named this gap and none has closed it; this feature does not close it either,
  and it goes to `gaps.md` re-measured rather than carried.

  `sync:docs` run, `check:docs` green — drift check and revision order both — and `check:srs`
  green. Quickstart scenario 7 rewritten to name the clauses that exist, and scenario 7a added
  for the reading pass itself.

**Checkpoint**: all three stories complete.

---

## Phase 6: Polish and close-out

- [X] T026 Run the coverage lane with the pinned variables and read `coverage/coverage-summary.json`, **not the text table** — the text reporter omits a file at 100% on all four metrics, which is the set this feature needs to see.

  **exit 0, 447 s, 99 files, 1,396 tests** — against chapter 3.24's 455 s, 97 files, 1,357 tests,
  and the two durations are **not comparable**: `consumer.itest.ts` alone has ranged from 101 s to
  484 s depending on how full the broker was. The lane was cleared first (`reset-lane.mjs`:
  DELIVERIES 40 -> 0, EVENTS 96 -> 0, 0 orphaned durables, 7,515 stale webhook rows), and the
  state it was NOT cleared to is in `baseline.txt` too — 76,980 environments and 791,520 outbox
  rows that `reset-lane.mjs` does not touch by design.

  Totals: **93.18% statements, 87.84% branches, 92.61% functions, 94.43% lines** over 104 measured
  files. The ten files this feature changed are tabulated in `baseline.txt`. Read from the JSON,
  and the JSON was the right call: `frames.ts`, `auth.ts` and `memberships.controller.ts` are all
  at 100 on all four and the text reporter would have shown none of them.

- [X] T027 Re-pin the changed files in `relay-platform/vitest.coverage.config.mts`, and **prove the pins are live**: a per-file threshold whose key matches no file is ignored silently and protects nothing. Demand 101% of a file at 100% and confirm vitest names the key.

  43 pinned keys -> **48**. Four of this feature's files were already pinned and all four still
  meet their floors; five had no pin and now do, at values measured rather than rounded.

  **BOTH HALVES OF THE PROBE RAN IN ONE RUN, AND BOTH ANSWERED:**

      "services/gateway/src/auth.ts"  statements: 101
        -> ERROR: Coverage for statements (100%) does not meet
           "services/gateway/src/auth.ts" threshold (101%)          THE PIN IS LIVE

      "services/gateway/src/this-file-does-not-exist.ts"  everything: 101
        -> nothing. No error, no warning, no mention.               SILENT, AS WARNED

  **AND THE PROBE RUN FOUND SOMETHING NOBODY WAS LOOKING FOR.** It failed a second threshold:
  `session.ts` functions measured **85.36%** where the run twenty minutes earlier measured
  **87.80%** — on identical code, with the other three metrics moving by a third of a point and
  every other pinned file byte-identical across both runs. A 2.44-point swing is about one
  function of forty, so something in that suite is timing-dependent.

  A floor at the measured value would have gone red on the next run for no change to the code,
  and the fix would then have been to lower it — **a ratchet that teaches people to lower
  ratchets**. `session.ts` is pinned below the lower observation by roughly the observed swing,
  with both numbers in the config so the next feature does not rediscover them. The instability
  is filed as a `C7` case.

  **`services/api/src/db/schema.ts` is deliberately left unpinned**, and the reason is in the
  config rather than in its absence: 59.15% statements and 40.81% functions look alarming and are
  drizzle table declarations whose "functions" are index-building callbacks that run only when a
  query touches that table. A floor there would ratchet on which tables the suite happens to
  query.

  Final run: **exit 0**, no threshold errors, 99 files, 1,396 tests.

- [X] T028 [P] Read every new test's title against its assertion, one at a time, in `relay-platform/services/api/src/db/repository.itest.ts`, `relay-platform/packages/protocol/src/frames.test.ts`, `relay-platform/services/gateway/src/session.itest.ts` and `relay-platform/services/gateway/src/resume.itest.ts`. **Expect the count to be wrong.** **Strip any task id from a title** — requirement ids belong there, task ids do not. (SC-003)

  **THREE FILES NAMED, FOUR IN THE TREE, FIFTEEN TITLES.** The fourth is `resume.itest.ts`,
  which the task could not have known about because T017 moved the cursor cases there after this
  task was written. Fourth feature running to name the wrong file count.

  **FOUR TITLES OVERCLAIMED, AND THE WORST ONE WAS MINE FROM AN HOUR EARLIER:**

  | Title | What it claimed | What it asserted |
  |---|---|---|
  | `describe(… FR-004, FR-007, FR-009)` in `frames.test.ts` | FR-004, that a client is told the count for every channel | a schema file cannot see a client. **FR-004 stripped** |
  | `carries the count on channelsForUser, for both of that query's callers (FR-014)` | both callers, and FR-014's no-extra-query rule | one call to the repository. **Both claims dropped** |
  | `refuses a negative count and a fractional one` | two cases | three — it also refuses a string. **Retitled** |
  | `exports the count schema on its own, so the internal hop validates the same rule` | that the internal hop uses it | that the export parses. **The "so" clause dropped** |

  **AND FR-003 WAS CITED BY TWO TITLES AND ASSERTED BY NEITHER.** The audit's own remedy was a
  test called `does not rise for a revision that was REFUSED (FR-003)` — delete a message, edit
  it, confirm the count did not move. It passed. **It also proves nothing about FR-003**: the
  edit path refuses a deleted message twice, on the read and on the compare-and-set, and *both
  refusals happen before the counter's statement*. The bump never executes, so the test passes
  identically with the bump outside the transaction — which is the one thing FR-003 forbids.
  A vacuous test written by the pass that exists to find vacuous tests, caught by reading the
  repository rather than the test.

  Two changes came out of it: the behavioural test keeps its real property under an honest title
  (`does not rise for an edit refused before it is applied`), and FR-003 gets a source-reading
  test — the instrument `main.test.ts` already uses for producers nothing else can see. It scans
  `repository.ts` for both `revisionSequence` bumps and asserts each runs on `tx` and not on
  `this.db`. **Forced red**: moving one bump onto the pool gives
  `the bump at 200649 must run on the transaction`. 68 tests green after restore.

  **Seven task ids survive in test titles across four files elsewhere in the tree**, in suites this
  feature does not touch, left from chapters whose audits reached only their own files. Measured
  and tabulated as item 044-2 in `gaps.md` — **and the ids themselves are not repeated here**,
  because `check-refs.py` holds that a task id inside `tasks.md` must mean a task in `tasks.md`,
  which is the rule that stops a renumber silently re-pointing a citation. The instrument said so
  when this record first spelled them out.

- [X] T029 [P] Run the credential scan over this feature's diff across **all three repositories**, and record every pattern searched and every hit classified in `baseline.txt`. Never report only "clean".

  Sixteen patterns over 5,092 added lines. Eight distinct hits, every one classified in
  `baseline.txt`: four are the lane's pinned local development values carried unchanged from
  feature 043, three are variable names whose values are those four, and three are false
  positives where a source path with no dots or dashes is 40+ characters of the base64 alphabet.
  Nothing new introduced.

  **THE FIRST RUN LIED, AND THE REASON IS THE FINDING.** `grep` on this machine is **ugrep
  7.8.4**, and under it `(postgres|redis)://[^:/@]+:[^@/]+@` matches nothing while the same
  pattern without the group matches — so the DSN pattern reported **0 hits on a corpus
  containing that DSN twice**. A second pattern reported 0 because it required a closing quote
  the material does not have. Two of sixteen silently clean on material that was present.

  The re-run gives **every pattern a positive control** and reports a pattern that fails its own
  example as BROKEN rather than as zero. That is what makes a 0 a claim about the corpus instead
  of a claim about the tool — and it is the third instrument this feature caught overstating its
  reach, after `check-fence-chain`'s ambiguous pre-image and a test that could not fail.

- [X] T030 Write `specs/044-revision-watermark/gaps.md`, carrying feature 043's items **re-measured against the tree rather than copied** — three of 043's closed on re-measurement without anyone working on them. Close nothing that this feature did not close.

  **CLOSED BY THIS FEATURE: NONE**, stated plainly rather than left to be inferred from a short
  list. Two things it fixed were its own defects, not carried gaps, and they are recorded against
  the tasks that found them.

  **The re-measurement earned its cost three times:**

  - **3.23-4 nearly closed on a lookalike.** `packages/test-harness/src/lists-agree.test.ts`
    exists and asserts two exemption lists agree — and the pair it asserts is
    `DRAIN_EXEMPT_TESTS`, not the `DRIVER_EXEMPT_TESTS` the item is about, which still has no
    agreement test. A filename-level check would have closed it. Reading the assertions kept it
    open, and found that the template for the fix is one `describe` away from the list needing it.
  - **C3 measured fifteen and is thirteen.** Two titles carry a prose suffix and both base files
    are chained elsewhere. This count has been wrong four times out of five and every error was in
    parsing the title, never in the tree.
  - **C6 re-confirmed at zero** rather than carried, because a closed item that quietly reopens is
    what a ledger is for.

  **Two new items**, both found by this feature and neither about the feature: `grep` on this
  machine is ugrep and disagrees with GNU grep on a construct a credential scan used (044-1), and
  six task ids survive in test titles in files no audit has reached (044-2). C8 is open for the
  eighth feature and the unnumbered one for the thirteenth.

- [X] T031 Run the twenty-run battery of `pnpm test:integration` from a cleared lane with the sequencer caches removed — including the **root** `node_modules/.vite/vitest`, which a `packages/*` and `services/*` glob misses. **Nothing else runs on the machine.**

  **20 OF 20 GREEN.** Mean 225.45 s, stdev 1.15, min 225, max 230, budget 240. The exit column is
  twenty Gs and there is **not one alternation**.

  Chapter 3.24 measured **9 of 20**, and its exit column alternated fifteen times consecutively —
  one chance in eight thousand if the runs were independent, which was the evidence that they were
  not. That was one defect: `harness.ts` SIGTERMed its children and slept 200 ms without awaiting
  `exit`, and the vitest sequencer reordered the files each run so the victim moved.

  **Feature 043 fixed it, and 043's own battery was also 20 of 20** — mean 225.35 s, stdev 0.99.
  So this is the **second** clean battery. A first draft of this record called it the first, and
  `CLAUDE.md`'s header said otherwise in four lines directly above the block being edited.

  The credit is 043's; what 044 adds is that the fix held across a second twenty runs, on a lane
  carrying 77,000 more environments. **The two means are 0.10 s apart**, which is the useful part:
  they are the first pair of batteries in this project that can be compared at all.

  The task's warning about the root cache was worth its line: seven caches exist and
  `./node_modules/.vite/vitest` is one of them.

- [X] T032 Re-measure SC-004 and SC-005 against T002's baselines and record both in `baseline.txt`. **If either moved more than 10%, record which of three was chosen and why.** Do not let the baseline quietly become whatever the lane now costs.

  **Both MET.** SC-004 −2.33% (1402.00 → 1369.33/s, band 1262–1542), with **30,000 of 30,000
  connections surviving** across three runs, zero failed, and the subscription law unchanged at
  11,000 subjects. SC-005 +2.75% on the edit and +2.99% on the delete — one UPDATE on a row the
  transaction already holds, and the delete moves more because it does less work to begin with,
  which is the direction T002 predicted.

  **T002 ASKED A QUESTION AND THE ANSWER INVERTS ITS OWN PROPOSED FIX.** T002 recorded that a 10%
  criterion against a measurement whose noise is 11% cannot tell a regression from a Tuesday, and
  proposed moving to p50 or raising the run count. Six runs a side say:

      edit    mean cv 12.9%      p50 cv 17.3%
      delete  mean cv 13.5%      p50 cv 20.6%

  **p50 is the noisier statistic here, on both paths.** A median of 200 samples with a long tail
  wanders inside a crowded middle while the mean is anchored by the whole sample. The instinct
  that a median is the robust choice is right about outliers and wrong about this.

  At the measured variance, resolving a 10% shift needs **~26 runs per side** on the mean and ~47
  on p50. Six resolves about 21%, so SC-005 as written cannot see a 10% regression — and did not
  see one here either; it saw +2.75% inside a band of ±21%.

  **Chosen: the first of the three — accept with the measurement attached**, because nothing
  moved. The criterion stays at 10% and its resolution limit is written down, rather than the
  number being adjusted to whatever the lane now costs.

- [X] T033 Run all fourteen gates last — `pnpm typecheck`, `pnpm lint`, `pnpm build` in `relay-platform`; `pnpm check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` in `relay-tutorial`; and the six instruments in `specs/044-revision-watermark/` — with every exit code written to a file **outside any pipeline**.

  **14 gates, 0 red** — and the first run of them was **2 red**, both caused by this phase's own
  work, which is the argument for running them last rather than trusting the phase.

  | Gate | First run | Cause |
  |---|---|---|
  | `pnpm typecheck` | **2** | `import.meta` in `repository.itest.ts`. The api builds to CommonJS, where that is a hard compile error — and `migrations.test.ts`, three files away, carries `__dirname` with the reason in a comment. The convention was already written down; it just was not read. |
  | `check:fences` | **1** | three fenced files changed in Phase 6 — `frames.test.ts` (title audit), `repository.itest.ts` (the FR-003 test) and `vitest.coverage.config.mts` (the new pins). The plan predicted the config would be the sixteenth file at close-out, the way it made 3.23's 33 become 34. |

  All three amended at `-U6`, unique first try. Green at 240 fenced files.

  **AND THE SIX INSTRUMENTS FOUND SIX MORE THINGS AFTER THAT** — in documents written in the same
  session, which is what `gaps.md` C8 means when it says the cost is demonstrated every time:

  - `check-refs.py` refused the seven foreign task ids in `gaps.md`'s 044-2 table until they were
    **declared as `(file, id)` pairs**. `('gaps.md', 'T031')` is precisely the collision that
    design exists for: `T031` is also a real local task, and an id-only allowlist would have
    accepted a bare `T031` anywhere.
  - It then refused the same ids inside `tasks.md`, where **no allowlist is consulted at all** —
    the rule being that a task id in the task list must mean a task in the task list, so a
    renumber cannot silently re-point a citation. The record now names the `gaps.md` item instead
    of repeating the ids. The right fix was to delete the allowlist entries I had just added:
    an allowlist for something no longer present is a lie waiting to be believed.
  - It refused `FR-016a (3.23)` and `FR-016b (3.23)` when they were written without the chapter
    suffix, correctly — an unsuffixed id claims to be *this* feature's requirement. **It then
    refused this very bullet**, which had spelled them bare while explaining that bare ones are
    refused. A checker that exempts the sentence describing it would be a checker with a hole
    the shape of its own documentation.
  - It refused a `T028` record that named no file path, and two prose citations of local task ids.
  - `check-checklist.py` refused the checklist for not mentioning `docs/04-srs.md`, which the spec
    started naming only after FR-013 stopped naming two identifiers that do not exist.

- [X] T034 Commit the close-out records, then trim `CLAUDE.md` and update the `SPECKIT` block to point past this feature.

  `CLAUDE.md` 239 -> 307 lines, and **trimmed on the way**: the coverage-key lesson was stated
  twice and is now stated once with both halves measured; the port-band and `reset-lane` stories
  are compressed to their transferable rules now that two consecutive clean batteries have closed
  them; the two fence-chain sections are merged.

  **AND ITS OWN HEADER CAUGHT A FALSE CLAIM IN THIS RECORD.** T031 was first written as "the
  first clean battery". `CLAUDE.md`'s existing header said 043 was **also 20 of 20**, at mean
  225.35 s — four lines above the block being edited. Corrected in both `baseline.txt` and T031:
  this is the second, and the two means being 0.10 s apart is the more useful fact, because they
  are the first pair of batteries in this project that can be compared at all.

  Two other numbers were stale and are now re-measured rather than carried: the lane's Postgres
  accumulation (12,000 environments recorded, 76,980 measured) and the carried-ledger paragraph,
  which now says 044 closed **none** of the twenty-eight.

  `SPECKIT` block: **no active feature.**


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
