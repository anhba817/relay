# Tasks: Tutorial Chapter 3.7 — "Commit and publish are two instants"

**Feature**: `specs/028-chapter-3-7` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: a correctness fix worth four lines, a chapter that explains why
those four lines were missing for four chapters, and a renumbering that leaves no
reference naming the wrong thing.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story from spec.md this task serves
- Setup, Verification, Publication and Close-out tasks carry no story label

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to
`relay-tutorial/`, spec paths to `specs/028-chapter-3-7/`.

---

## Phase 1: Setup & baseline

- [X] T001 Record provenance in `specs/028-chapter-3-7/baseline.txt`: the submodule commits and tags this chapter starts from, confirming `relay-platform` is at `part3-ch6` and both pins match their HEADs
- [X] T002 Record the pre-change baseline in `specs/028-chapter-3-7/baseline.txt` — unit and integration counts per package, the four coverage figures, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output
- [X] T003 [P] Record the site baseline in `specs/028-chapter-3-7/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the fence count and locale count the chain reports
- [X] T004 **Measure the flake rate before fixing it** — run `pnpm test:integration` twenty times per quickstart V0, record every exit code and the text of every failure in `specs/028-chapter-3-7/baseline.txt`. Roughly three hours of wall clock, and the only honest way to state a rate (SC-001)
- [X] T005 If twenty runs produce no failure, say so in `baseline.txt` and record what that means: the rate is lower than chapter 3.6's one-in-six, and the deterministic test from T006 is carrying the whole proof rather than sharing it

**Checkpoint**: the starting numbers exist, including a rate rather than an anecdote.

---

## Phase 2: User Story 1 — A reconnecting client is never shown a message twice (Priority: P1) 🎯 MVP

**Goal**: the platform stops delivering a message a resuming client has already
been given.

**Independent test**: publish a frame the backfill already delivered, after the
resume has completed; the client receives it once.

- [X] T006 [US1] Write the failing test in `relay-platform/services/gateway/src/resume.itest.ts`: a fourth quadrant beside the three that exist — backfill returns `frame(42)`, the resume completes, then `publishFromElsewhere(frame(42))`, and the timeline must be `[42]`. One number apart from the test above it (research R2, R4)
- [X] T007 [US1] **Watch T006 fail** (SC-002) and paste the failure into `specs/028-chapter-3-7/captured-output.md`. A regression test nobody has seen fail is a regression test nobody has checked — chapter 3.5 shipped an assertion that could not fail and chapter 3.6 a mutation that could not compile
- [X] T008 [US1] Add two pure functions to `relay-platform/services/gateway/src/resume.ts` beside `flushable`: the suppression predicate — given marks and a frame, is this a duplicate? `<=`, not `<`, for the reason `flushable`'s own comment gives — and the scoping that drops any channel the presented cursors did not name. **Both belong in this file rather than in `session.ts`**: it is the module that is deliberately pure, `scopeCursors` is the same shape of filter one screen above, and a scoping written inline in `session.ts` could not be reached by the unit test in T009 (contracts/resume.md § suppression, FR-001, FR-007)
- [X] T009 [P] [US1] Extend `relay-platform/services/gateway/src/resume.test.ts` with the predicate's cases: at the mark, below it, above it, a channel with no mark, and two channels where only one is suppressed; that the mark set never exceeds the cursor set even when the backfill answers with a channel nobody asked about; and that a cursor far above anything the channel holds seeds a mark rather than being clamped, which is the documented consequence rather than a defect (FR-001, FR-002, FR-004, FR-007)
- [X] T010 [US1] Add `marks` to `Connection` in `relay-platform/services/gateway/src/registry.ts` — nullable, per data-model.md, with the three distinguishable states written down
- [X] T011 [US1] Set the field in `relay-platform/services/gateway/src/session.ts` when a resume succeeds, from the `marks` that `highWaterMarks` already computes and that the code currently discards, passed through T008's scoping helper — `highWaterMarks` also adds a key for every channel the backfill returned, and the 200 bound has to be the gateway's own rather than inherited from the api's response shape (FR-007)
- [X] T012 [US1] Clear the field on every degrade path in `session.ts`, beside the existing `connection.buffer = []`. A client told to page history must not also be denied frames (FR-005, contract invariant 5)
- [X] T013 [US1] Consult the field in `deliver()` in `session.ts` before sending, and **rewrite the comment on `Connection.phase`** that says delivery "reads this field and nothing else" — that sentence is the defect stated as a design principle (research R1)
- [X] T014 [US1] Confirm T006 now passes and the three tests that were already in `resume.itest.ts` still pass unchanged in substance (FR-002, SC-003)
- [X] T015 [P] [US1] Extend `relay-platform/services/gateway/src/session.test.ts`: a live frame at or below the mark is not sent, one above it is, and a connection that never resumed suppresses nothing (FR-003, FR-006)
- [X] T016 [US1] Add the out-of-order case to `resume.itest.ts` — publish sequence 5 then sequence 4, both at or below the mark, after the resume — which is the case that made the spec's original retirement rule unsafe (FR-007a, FR-008, contract invariant 8, research R3, quickstart V5)
- [X] T017 [US1] Add the degraded-resume case to `resume.itest.ts`: force a degrade, publish a low sequence, and confirm it arrives (FR-005, quickstart V4)
- [ ] T018 [US1] Run `pnpm coverage` and **raise** `services/gateway/src/resume.ts`'s branch pin in `relay-platform/vitest.coverage.config.mts` to what the work achieves — it is already pinned at 93, and a ratchet left at its old number is a ratchet that has stopped ratcheting. Checked here rather than at the end, because 3.5 deferred it and found four thresholds red with the chapter otherwise finished

**Checkpoint**: the duplicate is gone, deterministically, and nothing is lost.

---

## Phase 3: Verification

- [ ] T019 Run the sabotage battery per `specs/028-chapter-3-7/quickstart.md` V6 — five mutations, each reverted and the file verified byte-identical by `md5sum`, recording which test failed for each. The fifth ADDS retirement rather than removing a mechanism, and it is the only check that V5 can catch a regression in this chapter's central decision (SC-005, FR-007a)
- [ ] T020 **Commit before running the battery.** Its revert step is `git checkout --`, which silently discarded an uncommitted correction during chapter 3.6 and failed the byte-identical check against the previous run's hashes
- [ ] T021 Run `pnpm test:integration` twenty consecutive times and record every exit code in `specs/028-chapter-3-7/baseline.txt` beside T004's pre-fix count (SC-001)
- [ ] T022 Run both lanes and coverage, confirm every pre-existing suite passes unchanged in substance, and record the chapter-end counts (SC-003, SC-004)
- [ ] T023 Capture every transcript the chapter will quote into `specs/028-chapter-3-7/captured-output.md`: T007's failure, the passing deterministic test, the e2e assertion text from chapter 3.6's baseline, the battery, and the coverage summary (FR-010, FR-016)

**Checkpoint**: the fix is proven twice — once deterministically, once by rate.

---

## Phase 4: User Story 3 — Part 3's numbering leaves no lies behind (Priority: P3)

**Goal**: no document, page or source comment cites a chapter number that does not
name what it claims to name.

**Independent test**: quickstart V9's sweep finds no wrong reference.

**Ordered before the chapter on purpose.** The source-comment corrections must be
fenced in this chapter, so they have to exist before the chapter's fences are
generated. Everything else in this phase could run at any point.

- [ ] T024 [US3] Rewrite the three chapter-number comments to name the subject rather than the ordinal — `relay-platform/services/api/src/db/schema.ts` lines 375 and 596, and `relay-platform/scripts/webhook-walk.mjs` line 453 (FR-019, research R6)
- [ ] T025 [US3] Confirm the `schema.ts:375` correction fixes a reference that was **already stale** — it says "chapter 3.7's cross-tenant gauntlet" and the gauntlet became 3.8 when chapter 3.6 was inserted — and record that in `specs/028-chapter-3-7/chapter-notes.md`
- [ ] T026 [P] [US3] Sweep prose cross-references in published pages that name a moved chapter, in every locale — `relay-tutorial/app/(en)/part-0/chapter-04/**/page.mdx`, `relay-tutorial/app/(en)/part-3/chapter-05/**/page.mdx`, `relay-tutorial/app/(en)/part-3/chapter-06/**/page.mdx` and their `app/(vi)/vi/…` twins. Prose only — the same sentences inside fenced source belong to T024 (FR-018)
- [ ] T027 [US3] Confirm `docs/07-tutorial-plan.md` and `relay-tutorial/lib/tutorial.ts` agree with each other and with the published pages: quotas 3.8, gauntlet 3.9 (FR-017, already done during `/speckit-specify`)
- [ ] T028 [US3] Run quickstart V9's sweep across `docs/`, both locales' pages, and the platform's source, and confirm every hit names what it claims to name (SC-007)

**Checkpoint**: the renumbering is complete and the source stops citing ordinals.

---

## Phase 5: User Story 2 — The chapter, in English (Priority: P2)

**Goal**: a reader who finished chapter 2.7 believing the race was closed learns
what the proof did not cover, and why.

**Independent test**: the chapter states the two instants, shows the failing
timeline from a real run, and names the case chapter 2.7's own reasoning omits.

- [ ] T029 [US2] Write the English chapter at `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx`: the two instants, the gateway's send path, and where the dedup window closes (FR-009)
- [ ] T030 [US2] Add the section to `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx` that quotes chapter 2.7's own reasoning — "in the backfill, in the buffer, or both" — and shows the fourth case it does not enumerate, without rewriting or blaming that chapter (FR-011, SC-008)
- [ ] T031 [US2] Add the quadrant table to `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx`: when published against sequence versus mark, three tests and one empty cell, one number apart (research R2)
- [ ] T032 [US2] Add the section to `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx` connecting the seam to 3.3's outbox, 3.5's post-then-report and 3.6's publish-after-commit — four instances, four different correct answers (FR-012)
- [ ] T033 [US2] Add the section to `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx` on how it was found: an intermittent failure in a lane already red for three unrelated reasons, and what that cost (FR-013)
- [ ] T034 [US2] Add the section to `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx` on the retirement rule the spec proposed and research overturned, including the out-of-order publication that makes it unsafe (research R3)
- [ ] T035 [US2] Add the section on chapter numbers inside fenced source code to `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx` — why a comment citing an ordinal goes stale on every insertion, and why the mechanism guaranteeing the book matches the code is the same one that makes the correction cost a fence. **Without this section the corrected files cannot be fenced here** (research R6, FR-020)
- [ ] T036 [P] [US2] Write `relay-tutorial/app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/figures.ts` — the two instants on a timeline, the four quadrants, and where the mark now lives
- [ ] T037 [US2] Generate every fence from the real files rather than typing them — **including diff fences for `relay-platform/services/api/src/db/schema.ts` and `relay-platform/scripts/webhook-walk.mjs`**, whose chains end in chapter 3.6 and whose HEAD check fails until this chapter amends them — and confirm `pnpm check:fences` replays the chain onto `relay-platform` (FR-015, FR-020)
- [ ] T038 [US2] Measure the battery on the published page and record it in `specs/028-chapter-3-7/battery.txt`, with the prose word count against the 2,000–4,000 bound and the SKIP AHEAD naming `part3-ch7`
- [ ] T039 [US2] Traceability: confirm every `FR-*`/`NFR-*`/`ADR-*` the chapter cites resolves in `docs/` or the constitution — chapter 3.6 leaked fourteen feature-local identifiers a reader cannot look up

---

## Phase 6: Publication in both locales

- [ ] T040 Translate the chapter to `relay-tutorial/app/(vi)/vi/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx`, splitting prose from fences mechanically before translating anything and leaving every fence byte-identical (FR-014, translate-mdx §2.4)
- [ ] T041 [P] Translate `relay-tutorial/app/(vi)/vi/part-3/chapter-07/commit-and-publish-are-two-instants/figures.ts` — mermaid labels only; identifiers, field names and file paths stay English
- [ ] T042 Verify the translated page's JSX box tags balance in both locales before building — chapter 3.6's translation dropped a `<Why>` opening tag and the build error named a line 200 lines away
- [ ] T043 Set 3.7 published in `relay-tutorial/lib/tutorial.ts` with `translatedIn: ["vi"]`
- [ ] T044 Verify publication of both routes: 200, the reading shell present, and the figures rendering as **SVG in a headless browser** (SC-006) — a page that returns 200 is not a page that is laid out, and 3.5 shipped three blank diagrams past a passing build
- [ ] T045 Run `pnpm check:fences` and confirm the Vietnamese fences mirror the English byte for byte and the locale count has risen

---

## Phase 7: Close-out

- [ ] T046 Run quickstart V0–V9 end to end from `specs/028-chapter-3-7/quickstart.md`, reading exit codes rather than grepping output
- [ ] T047 Scan `specs/028-chapter-3-7/captured-output.md` and both published pages for leaked credentials, recording the patterns searched rather than the conclusion alone
- [ ] T048 Write `specs/028-chapter-3-7/chapter-notes.md` from what happened rather than what was planned, including the pre-fix and post-fix flake counts and anything the battery contradicted
- [ ] T049 Fix forward any defect this chapter exposes in an earlier chapter, in every locale that chapter has, and record it in `specs/028-chapter-3-7/chapter-notes.md`
- [ ] T050 Amend `docs/07-tutorial-plan.md` if this chapter's scope moved, and confirm the Part 3 numbering it carries still matches `relay-tutorial/lib/tutorial.ts`
- [ ] T051 Tag `relay-platform` as `part3-ch7` at the chapter-end commit, because the chapter's SKIP AHEAD tells readers that tag exists — 3.5 published that claim before the tag was created

---

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1 → Phase 2**: the flake rate is measured before the fix, or the twenty post-fix runs mean nothing
- **T006 → T007 → T008**: the test is written, watched to fail, and only then made to pass. Reversing that order produces a test that has never been checked
- **Phase 2 → Phase 3**: sabotage needs a mechanism to remove
- **Phase 4 → Phase 5**: the source-comment corrections must be fenced in this chapter, so they land before the chapter's fences are generated
- **Phase 5 → Phase 6**: the translation mirrors an English page that must be final

### The phase order deviates from priority order, on purpose

US3 is P3 and runs before US2, which is P2. The reason is mechanical rather than a
re-prioritisation: US3 changes source files whose fences this chapter generates, so
doing it afterwards would mean regenerating them. Everything else about US3 —
the prose sweep, the plan and registry check — could run at any point and is marked
`[P]` where it can.

### User story dependencies

US1 stands alone and is the whole correctness fix. US2 depends on US1 having
happened and on Phase 3's transcripts existing. US3 is independent of both in
substance and ordered before US2 for the fence reason above.

### Parallel opportunities

- **Phase 1**: T003 is the tutorial's lane and independent of T002's
- **Phase 2**: T009 and T015 are unit tests in files nothing else in the phase touches
- **Phase 4**: T026 touches only tutorial prose and is independent of T024's source edits
- **Phase 5**: T036 (figures) is independent of the prose tasks
- **Phase 6**: T041 (figures) is independent of T040 (page)

---

## Implementation Strategy

**MVP is Phase 2 alone.** With Phases 1 and 2, the platform stops delivering a
duplicate to a resuming client and there is a test that proves it deterministically.
That is the entire correctness content of this chapter; everything after it is
evidence, explanation and bookkeeping.

The chapter is what makes it a chapter rather than a patch, and it is genuinely
optional in the sense that the fix ships without it — which is exactly why the plan
records that the alternative considered was a post-series fence with no chapter at
all, and rejected it.

---

## Notes

**On T004's three hours.** Twenty serialised lane runs is the expensive task in
this feature and it produces one number. It is worth it because SC-001 asks for
twenty consecutive passes afterwards, and "twenty passes" is meaningless without
knowing that twenty runs used to fail. If the budget has to be cut, cut the
post-fix runs to ten and say so in the notes — but keep the pre-fix measurement,
because that is the one that establishes the defect was real and not a story about
a flaky suite.

**On the fourth quadrant.** T006 is one number different from a test that has been
passing since chapter 2.7. That is the finding, not a coincidence: a suite written
from a three-case model has three tests, and the matrix has four cells. The chapter
should show the table rather than describe it.

**On the failure mode.** Every other chapter in Part 3 risks a duplicate. This one
risks a GAP, which constitution II ranks worse. T012, T017 and the fourth sabotage
mutation all exist for that single reason, and a reviewer who wants to attack this
chapter should attack there first.
