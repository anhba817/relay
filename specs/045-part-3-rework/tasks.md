# Tasks: Part 3, reorganised by subject

**Feature**: `specs/045-part-3-rework/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**Format**: `- [ ] TNNN [P?] [USn?] description with a file path`. `[P]` means parallelisable —
different files, no dependency on an incomplete task. Story labels appear only in story phases.

**THE STORY ORDER AND THE EXECUTION ORDER DIFFER, ON PURPOSE.** US3 is P2 and runs before the two
P1 stories. Once no source comment names an ordinal, moving a chapter cannot invalidate one — so
doing the references first keeps two large changes separately verifiable. The other order entangles
them, and no gate could then say which one broke a chapter. Stated here rather than left for somebody
to discover by reading the phase numbers.

**Tests are the fence chain.** This feature writes no test code. `check:fences` replays 240 fenced
files byte-exact across 42 chapters after the split — 41 today — and is the acceptance test for almost every task below. The two
places it cannot see are named where they occur: the thirteen excerpt-only files, and prose that
walks through a diff.

---

## Phase 1: Setup — and proving the instrument before trusting it

- [ ] T001 Pin the starting state in `specs/045-part-3-rework/baseline.txt`: all fourteen gates with each exit code captured **outside any pipeline**, plus the numbers this feature is measured against — 24 chapters, 447,394 words, 242 fenced files, 904 fences, 1,429 source references, and the battery's 225.45 s mean with stdev 1.15. **`fail=1` inside a `for … | sort` runs in a subshell and dies with it**, which has printed "ALL GATES: GREEN" over a red one three times in feature 043. (SC-007)
- [ ] T002 Build the snapshot tool at `specs/045-part-3-rework/snapshot.mjs`: replay the published chain and dump each path's state **after every chapter and again after `relay-tutorial/fences/post-series.md`**. **The appendix is part of the chain and the first tooling forgot it** — the omission showed as 70 reference-bearing lines present in the platform file and in no snapshot, concentrated in `eslint.config.mjs` and `vitest.coverage.config.mts`. (FR-016) **Copy `check-fence-chain.mjs` and truncate it rather than reimplementing the replay** — a generator that replays differently from the checker produces output the checker rejects for reasons neither explains.
- [ ] T003 Build the replay tool at `specs/045-part-3-rework/replay.mjs`: for each path, commit the snapshots as a git history, cherry-pick them onto the new order, and emit each resulting state plus the fence between consecutive states. Conflicts stop and are reported by path, for hand resolution in T021.

  **THIS IS NOT THE MECHANISM THE PLAN FIRST SPECIFIED, AND THE REPLACEMENT WAS MEASURED.** The first
  design filtered the final file by line attribution — *the final file minus every line owned by a
  later cluster*. Analysis pass 2 built it: **52 parse errors on `repository.ts`, 59 on `session.ts`,
  4 on `schema.ts`**, because line-level ownership cuts through syntax. Three-way merge instead gives
  **56 intermediate states with 0 parse failures**. A merge of two real files is a real file; a
  filtered subset of one is not.

  **AND THE TARGET IS NOT ALWAYS THE PLATFORM FILE.** For the **21** order-changing paths the
  appendix also amends, a chapter fence must land on the state the appendix then amends — targeting
  the platform file overshoots by exactly those hunks, and `check:fences` reports the failure at the
  wrong place. (FR-016)
- [ ] T004 **The control, and the reason Phase 1 exists.** Run `replay.mjs --order current` and require byte-exact reproduction of today's `app/(en)/part-3` fences. **A generator that cannot rebuild what already exists cannot be trusted to build what does not**, and every later phase reads its output. **This control has already caught one mechanism**: the attribution design reproduced **17 of 96** states under it, which is how T003's approach came to be replaced before a line of the book moved. (SC-005)
- [ ] T005 Prove T004's control can fail: perturb one fence body in a Part 3 `page.mdx`, confirm the comparison names that file and that fence, restore. **A control that has never been red is a control nobody has tested** — feature 044 shipped two probes that could not fail, one of them written by the audit that exists to find them.

**Checkpoint**: the tool reproduces the present. Nothing has moved.

---

## Phase 2: Foundational — the three tables

**Blocking.** Every later phase reads one of these.

- [ ] T006 Write the subject-name table at `specs/045-part-3-rework/subjects.json`: one entry per Part 3 chapter, keyed by slug, giving the phrase a source comment should use — `webhooks-that-survive-the-customer` → "the webhook dispatcher chapter". **Keyed by slug and not by number**, because the number is the thing being retired.
- [ ] T007 Write the chapter map at `specs/045-part-3-rework/chapter-map.json` from `contracts/chapter-map.md`. **One record, two consumers** — the published mapping page and the redirects. A hand-maintained pair is the defect the port bands taught this project, and it cost chapter 3.24 an unexplainable eleventh red. (FR-014, SC-008)
- [ ] T008 [P] Write `specs/045-part-3-rework/classify-refs.py`: emit every one of the 1,429 source references with its file, line, class and proposed rewrite. Three classes, measured in research R5 — 416 beside a requirement id, 923 plain subject references, 90 positional claims. **Report the pattern and the corpus with every count**: 1,429 is all `.ts` under `services/` and `packages/`, 1,298 is the subset inside the 183 fenced paths, and the 985 this feature planned against came from a pattern missing a capital `C`. **Give the pattern a positive control and report a pattern that fails its own example as BROKEN rather than as zero**: `grep` here is ugrep 7.8.4, and a grouped alternation followed by two negated classes matches nothing under it. (FR-008, SC-002)
- [ ] T009a [P] Write `specs/045-part-3-rework/check-registry.py`: `relay-tutorial/lib/tutorial.ts` declares every chapter's number, path, title, `titleVi` and reading time **by hand**, and the sitemap plus six components read it — the sidebar, the chapter shell's previous and next links, the site header, the landing page and the language switcher. Compare it against the filesystem **in both directions** and test it red each way. **Nothing checks this file today**, and it agrees at 41 and 41, which is what makes silent drift possible rather than unlikely. (FR-015, SC-009)
- [ ] T009b [P] Write `specs/045-part-3-rework/check-fence-parity.py`: count **every** fence in each chapter, titled and untitled, and require the English and Vietnamese pages to agree per chapter. **`check:fences` cannot do this** — `check-fence-chain.mjs:77` collects a fence only when it matches `title="…"`, so it compares 623 per locale in Part 3 and never sees the other **99**. Test it red by deleting one untitled fence from a Vietnamese page. (FR-010, SC-006)
- [ ] T009 [P] Write `specs/045-part-3-rework/check-map.py`: the map is a bijection over 24 old and 25 new chapters, every slug exists on disk, and **every new ordinal is used exactly once**. Test it red on a duplicate and on a missing slug. (FR-007, FR-014)

**Checkpoint**: the three tables exist and disagree with nothing.

---

## Phase 3: User Story 3 — a chapter can move without ageing a reference (Priority: P2, runs first)

**Goal**: no source comment names a Part 3 ordinal.

**Independent test**: count Part-3 chapter-number references in `relay-platform`. 1,429 today; zero in fenced files after.

- [ ] T010 [US3] Rewrite the 416 references that sit beside a requirement id, across the `.ts` files of `relay-platform`: **delete the ordinal and keep the id**. `(chapter 3.21, FR-RTM-08)` becomes `(FR-RTM-08)`. This class loses nothing at all — the durable reference was already there. (FR-008)
- [ ] T011 [US3] Rewrite the plain subject references in `relay-platform/packages/` from `subjects.json`, and record the count done against the count found. (FR-008)
- [ ] T011a [US3] Rewrite them in `relay-platform/services/api/src/db/` — `repository.ts` alone holds 129 references, the largest concentration in the tree. (FR-008)
- [ ] T011b [US3] Rewrite them in the rest of `relay-platform/services/api/`, outside `src/db/repository.ts`, located with `grep -rn`. (FR-008)
- [ ] T011c [US3] Rewrite them in `relay-platform/services/gateway/` and `services/dispatcher/`, located with `grep -rn`. (FR-008)

  **923 references split four ways, because one task of that size cannot be told part-done from
  done.** Each batch reports found against rewritten. **Read each one; do not run a blind
  substitution** — the table gives the phrase and the sentence decides whether it fits.
- [ ] T012 [US3] Rewrite the 90 positional claims by hand, located by `classify-refs.py` across `relay-platform`. These name a chapter to say *when* something happened, so a subject name does not substitute — the sentence has to be rewritten to state the fact instead of pointing at where it was established. (FR-008)
- [ ] T013 [P] [US3] Rewrite the 210 references in the 49 **unfenced** `.ts` files under `relay-platform`. Parallel with T010–T012 only if the file sets are confirmed disjoint first — check, do not assume. (FR-008)
- [ ] T014 [US3] Regenerate the fences for the **183** fenced files whose comments changed, and append amendment hunks to `relay-tutorial/fences/post-series.md`. **`-U6` is a default, not a rule**: regenerate wider when a pre-image matches twice, and verify the hunks apply clean before pasting, not after. `-U8` was worse than `-U6` once and `-U10` fixed it, because widening context merges adjacent hunks. (FR-006, FR-013)

  **THE PROPAGATION WAS MEASURED AND IT IS MECHANICAL.** Of 1,221 reference-bearing lines in fenced
  source, **94% are byte-identical from the chapter that introduced them to the final file and 0%
  changed between chapters** — so rewriting a comment is a replace across snapshots rather than 1,429
  separate decisions. The remaining **5% appear in no chapter snapshot at all**: those are the
  appendix's, and they are T021a's. **This premise was untested until analysis pass 3**, and it is the
  one headline check in this feature that passed.
- [ ] T015 [US3] Verify: zero ordinals in fenced source, `check:fences` green at 240 files, and `pnpm typecheck`, `lint`, `build` green in `relay-platform`. **A comment edit that breaks a build is still a broken build.** (SC-002, FR-013)
- [ ] T016 [US3] Check the **ten excerpt-only platform files** separately with `check-excerpt-files.py` — they carry **99 ordinals**, 43 of them in `session.itest.ts` alone. The other three of the thirteen are `docs/04-srs.md`, `docs/05-sad.md` and a predecessor's `baseline.txt`, which are not `relay-platform` source and so fall outside FR-008. **`check:fences` compares them to nothing**, so T015's green says nothing about them — and one of them, `session.itest.ts`, holds the only end-to-end proof of feature 044's signal.
- [ ] T017 [US3] Commit all three repositories. `git checkout` on a file with uncommitted work has destroyed it twice in this project.

**Checkpoint**: US3 is independently shippable. Nothing has moved, and nothing can be aged by moving it.

---

## Phase 4: User Story 1 — a reader follows one subject to its end (Priority: P1) 🎯 MVP

**Goal**: eight of eight subject clusters contiguous.

**Independent test**: group every chapter by subject, confirm each group occupies consecutive positions.

- [ ] T018 [US1] Split the milestone chapter per `contracts/chapter-map.md`: the error-registry half becomes new 3.3 under its own slug, the outsider half becomes new 3.25 keeping `errors-that-resolve-and-an-outsider`. **Its 21 fences divide 14 to the registry and 7 to the outsider**, at the chapter's own `## The outsider` heading on line 961 of 1,565 — nothing straddles it, and the assignment is in `contracts/chapter-map.md` because the scope estimate turns on it. **This is the only chapter whose prose is divided**, and the division is where FR-009's "prose is preserved" is most at risk. (FR-005, FR-007)
- [ ] T019 [US1] Rename the 24 English chapter directories under `relay-tutorial/app/(en)/part-3/` per `chapter-map.json`. **The slug travels with the chapter; only the numeric segment moves.** (FR-007)
- [ ] T020 [US1] Update `metadata.alternates.canonical` and the `languages` pair in each moved **English** `page.mdx` — **61 hard-coded chapter paths** across the 24 — which name their own path and do not follow a directory rename.
- [ ] T021 [US1] Run `replay.mjs --order new` for the **42** order-changing paths, **resolve the 31 merge conflicts by hand**, and write the **289** regenerated fences into their chapters. **Give the 5 paths that merge cleanly onto a *different* file their own reading** — they pass every mechanical check until the final byte comparison, which is the worst way for this to fail. **These counts moved during analysis**: 39 and 278 assumed the milestone chapter moved whole, and the answer is 39/278 if its fences land early against 44/300 if late. The split is now decided fence by fence in `contracts/chapter-map.md`. **3 of 39 would replay from the old deltas and 36 would not** — 31 conflict and 5 land on a different file, which is the outcome that passes every check but the last. (FR-006, SC-005)
- [ ] T021a [US1] Re-verify the **48 existing appendix hunks** on the 21 order-changing paths they amend, in `relay-tutorial/fences/post-series.md`, and regenerate any whose pre-image no longer matches. **They were generated against today's chain end state**, and R2 measured 5 paths where reordering lands on a different file — where that intersects these 21, the appendix's own pre-images stop matching. T014 only *appends* new hunks and would leave these silently stale. (FR-016, SC-010)
- [ ] T021b [US1] Confirm the chain **including the appendix** lands byte-exact on `relay-platform` with `pnpm check:fences`. **The chain does not end at the last chapter**, and a tool that stops there reaches a state that is not the platform's. (SC-010)
- [ ] T022 [US1] Rewrite the 54 forward references in Part 3 prose, across the English `page.mdx` files. A sentence that says "chapter 3.19 will build this" is wrong when 3.19 now precedes it; some become backward references and some become nothing.
- [ ] T023 [US1] Read every moved chapter's prose against its regenerated diffs. **This is the task no gate can do.** A chapter that walks a reader through a hunk now shows a different hunk, and `check:fences` is satisfied either way. Budget for it: 289 fences across 42 paths, concentrated in `repository.ts` (23 fences), `schema.ts` and `session.ts` (16 each). (FR-009)
- [ ] T023a [US1] Rewrite the 24 Part 3 entries in `relay-tutorial/lib/tutorial.ts` from `chapter-map.json` — number, path and order — and add the 25th for the split chapter, deriving its `readerMinutes` and `readerProduces` from the halves. **No requirement named this file until analysis went looking for what else knows a chapter number**, and skipping it leaves every gate green with a broken sitemap, a broken sidebar and dead previous-and-next links on all 25 chapters. (FR-015)
- [ ] T023b [US1] Run `check-registry.py` and confirm both directions agree at 42 chapters. (SC-009)
- [ ] T024 [US1] Verify SC-001 with `check-movements.py`: eight of eight, against five of eight today. Then `check:fences` green at 240 files across **42** chapters — 41 today, plus the one the split adds. (FR-001, SC-001, FR-013)
- [ ] T025 [US1] Commit all three repositories with `git commit`, `relay-tutorial` and `relay-platform` before the root pointer.

**Checkpoint**: Part 3 reads as eight movements. This is the MVP — the defect is closed.

---

## Phase 5: User Story 2 — a reader is never asked to build for an absence (Priority: P1)

**Goal**: nothing is taught before the thing it operates on exists.

**Independent test**: every synthesised intermediate state compiles, and every webhook event type has a producer in an earlier chapter.

**This phase is mostly verification of Phase 4's arrangement**, and saying so is honest: FR-002 is satisfied by the order chosen in `contracts/chapter-map.md`, not by code written here. What this phase adds is the proof, and the proof can fail.

- [ ] T026 [US2] Typecheck every intermediate state: `replay.mjs --order new --typecheck-each`. **A state that does not compile is a finding about the order, not a bug in the tool** — it means a chapter teaches code calling something a later chapter introduces. Record which pair and move one of them. (FR-002, FR-003, SC-004)
- [ ] T027 [US2] Trace each **emitted** event type in `relay-platform/services/api/src/outbox/event.ts` to a producer in an earlier chapter — **five of the eight declared**, measured from the `emitted` flags. Record the other three, `channel.created`, `user.connected` and `user.disconnected`, as declared and unbuilt. Feature 043 measured **838 stored subscriptions to types the platform does not emit**; this feature builds none of them, which is why SC-003 is scoped to the emitted set rather than to all eight. (FR-002, SC-003)
- [ ] T028 [US2] Confirm the isolation milestone at new 3.24 attacks every route built before it, from `relay-platform/services/api/src/isolation/gauntlet.itest.ts`, using its own derived target list rather than a hand-written one. The list extends itself from the running router, so this is a check that the derivation still runs, not that somebody remembered to add rows. (FR-004)
- [ ] T029 [US2] Confirm the outsider milestone at new 3.25 has nothing after it — no later `page.mdx` under Part 3 — and that the SRS Phase 2 exit criterion it renders a verdict on is still the last word in Part 3. (FR-004)
- [ ] T030 [US2] Commit all three repositories with `git commit`, root pointer last.

**Checkpoint**: both P1 stories are done and proved.

---

## Phase 6: The Vietnamese placeholders

- [ ] T031 Rename the 24 Vietnamese directories under `relay-tutorial/app/(vi)/vi/part-3/chapter-NN/` per `chapter-map.json`, and split the milestone chapter to match, giving **25**. (FR-010)
- [ ] T032 Replace the prose in each `relay-tutorial/app/(vi)/vi/part-3/chapter-NN/*/page.mdx` with a placeholder, **keeping every import, every `metadata` field, every figure, every JSX box — `<Why>`, `<Trap>`, `<SkipAhead>`, `<ForwardRef>`, `<Checkpoint>` — and every code fence byte-identical to its English counterpart**.

  **THE MIRROR PROTECTS ONLY 623 OF THE 722 FENCES.** It compares titled fences and is blind to the
  **99 untitled** ones per locale, which hold console transcripts and worked diagrams. Dropping them
  passes every gate and deletes real content from 24 published pages. `check-fence-parity.py` is what
  catches it.

  **AND 41 OF THE 623 SIT INSIDE A JSX BOX.** Strip the prose without keeping the wrapper and the MDX
  stops balancing — which fails at `pnpm build`, not at a gate, so it surfaces after the work rather
  than during it. (FR-010, FR-011, SC-006) (FR-010, SC-006)
- [ ] T032a Update `metadata.alternates.canonical` and the `languages` pair in each Vietnamese `page.mdx` — **72 hard-coded chapter paths** across the 24, more than the English side because each names both locales. **No task owned these until analysis pass 4**: T020 sits in the English reorder phase and Phase 6 never mentioned metadata. **The mirror cannot see metadata at all**, so wrong canonicals ship green — and they are what `hreflang` and the sitemap resolve against. (FR-007, SC-008)
- [ ] T033 Mark each Vietnamese `page.mdx` placeholder visibly as awaiting translation, so a reader is never shown a page that looks translated and is not (FR-011). (FR-011)
- [ ] T034 Verify the mirror with `pnpm check:fences` **and count the pages** under `relay-tutorial/app/(vi)/vi/part-3/` — **25**, one per English chapter. A deleted Vietnamese page passes `check:fences` silently, because the checker skips chapters that do not exist — so absence is invisible to the gate that is supposed to catch it. (SC-006)
- [ ] T035 Commit `relay-tutorial` with `git -C relay-tutorial commit`, then the root repository's submodule pointer.

---

## Phase 7: The published surfaces

- [ ] T036 Amend Part 3's rows in `docs/07-tutorial-plan.md` to the new structure, and **derive the chapter count from the rows rather than carrying it in the heading**. That heading said seven, then sixteen, then twenty-one through three chapters that each added a row without moving it — in a paragraph whose own last sentence says the count comes from the rows. (FR-012)
- [ ] T037 [P] Publish the mapping page from `chapter-map.json` as its own route under `relay-tutorial/app/`, naming all 24 old numbers, and link it from the series sidebar in `components/reading/series-sidebar.tsx`. **There is no Part 3 index page** — an earlier draft of this task assumed one; navigation is rendered from the registry. **Four chapters keep their number and change meaning** — 3.13, 3.14, 3.15 and 3.16 all exist before and after and name different chapters, which is the sharpest thing a returning reader needs told. (FR-014, SC-008)
- [ ] T038 [P] Generate the 48 redirects into `relay-tutorial/next.config.ts` from the same `chapter-map.json`, permanent rather than temporary. The split chapter's old URL has to choose a target; `contracts/chapter-map.md` records that it goes to the outsider half and why. (FR-014, SC-008)
- [ ] T039 Rewrite the references into Part 3 found in every `page.mdx` outside Part 3, English and Vietnamese, with `grep -rn` over `relay-tutorial`. Those parts are not reordered, so their own ordinals are stable — but a Part 2 chapter that says "chapter 3.18 builds this" is now wrong.
- [ ] T040 Verify every old URL resolves: `pnpm build` then `check-redirects.py`, 48 redirects each landing on one of the 50 pages that exist. **Check `app/sitemap.ts` in the same pass** — it is the map's third consumer, it is generated from the registry, and the plan called it two consumers until analysis counted them. **And check the 133 metadata paths**, 61 English and 72 Vietnamese: nothing in the gate set reads them. (SC-008)

---

## Phase 8: Polish and close-out

- [ ] T041 [P] Run the coverage lane as a **control**. The platform's behaviour does not change in this feature, so coverage should not move; read `coverage/coverage-summary.json` rather than the text table, which omits any file at 100% on all four metrics. Re-pin nothing unless a number moved, and if one did, find out why before pinning it.
- [ ] T042 [P] Run the credential scan over this feature's diff across all three repositories, recording every pattern searched and every hit classified in `baseline.txt`. **Never report only "clean"** — and give each pattern a positive control, because two of sixteen silently reported zero on material that was present the last time this was run.
- [ ] T043 Run the twenty-run battery of `pnpm test:integration` from a cleared lane with all seven sequencer caches removed, **including the root `node_modules/.vite/vitest`** which a `packages/*` and `services/*` glob misses. SC-007 is a tripwire: 225.45 s ± 10%, and a moved duration means the platform changed when it was not supposed to. (SC-007)
- [ ] T044 Write `specs/045-part-3-rework/gaps.md`, carrying feature 044's ledger **re-measured against the tree rather than copied**. Two items — 044-2 and 3.23-4 — were closed after 044's close-out and must not be re-opened by a copy. Note whether this feature closes `043-1`: renumbering touches every chapter, so the 146 untitled fences are as findable now as they will ever be.
- [ ] T045 Run all fourteen gates last — `pnpm typecheck`, `pnpm lint`, `pnpm build` in `relay-platform`; `pnpm check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` in `relay-tutorial`; and the six instruments in `specs/045-part-3-rework/` — with every exit code written to a file outside any pipeline. (FR-013)
- [ ] T046 Commit the close-out records, then trim `CLAUDE.md` and point the `SPECKIT` block past this feature.

---

## Dependencies

    Phase 1 (T001-T005)  ──▶ Phase 2 (T006-T009)  ──▶ Phase 3 / US3 (T010-T017)
                                                            │
                                                            ▼
                                              Phase 4 / US1 (T018-T025)  P1, MVP
                                                            │
                                                            ▼
                                              Phase 5 / US2 (T026-T030)  P1
                                                            │
                                       ┌────────────────────┼────────────────────┐
                                       ▼                    ▼                    ▼
                              Phase 6 (T031-T035)   Phase 7 (T036-T040)          │
                                       └────────────────────┴──────────▶ Phase 8 (T041-T046)

**US3 blocks US1, which is the inversion worth reading twice.** A P2 story runs before a P1 one
because doing it second would mean rewriting references the reorder had already invalidated, twice.

**US2 depends on US1** and cannot be tested before it: it verifies the arrangement US1 builds. This is
the one story pair that is not independent, and saying so is better than claiming an independence the
tasks do not have.

**Phases 6 and 7 are independent of each other** and both depend on US1's numbering being final.

## Parallel opportunities

- **T008 and T009** are different files and different questions.
- **T013** parallelises with T010–T012 **only after** the file sets are confirmed disjoint. Check it;
  an assumption of disjointness is how two edits land on one file.
- **T037 and T038** read the same map and write different files.
- **T041 and T042** are a lane run and a text scan.
- **Within Phase 3 and Phase 4, almost nothing is parallel.** T014 depends on every comment edit
  before it, and T021 depends on the directory renames. The chain is the bottleneck by design.

## Implementation strategy

**MVP is Phase 1 + Phase 2 + Phase 3 + Phase 4.** That is the defect closed: Part 3 reads as eight
movements and no reference ages when a chapter moves. Phase 5 proves it, Phases 6 and 7 publish it.

**Phase 1 is not optional and not setup.** It is the control. If `replay.mjs` cannot rebuild today's
chain byte-exact, every fence it writes later is unverifiable, and the feature has no test at all.
**The control has already rejected one mechanism at 17 of 96 states**, which is the argument for
running it before anything moves rather than after.

**Commit each phase.**

**Expect the file count to be wrong.** The plan estimates **184** fenced files and 289 fences across 42 paths. It has already read 169/39/278, then 169/42/289, and now 184 — the last move because a pattern correction was applied to the reference count and not to the file count beside it. Feature 043
estimated 17 files and changed 58; feature 044 estimated 12, then 15, then 17. Every unplanned file in
043 came from **running** something rather than reading it, and T023 — reading prose against
regenerated diffs — is the task most likely to find work no instrument here can see.
