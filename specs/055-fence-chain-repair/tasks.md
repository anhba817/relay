# Tasks: repair the fence chain — 110 to 0

**Feature**: `specs/055-fence-chain-repair` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) — read it first, it corrects two of the
specification's own assumptions.

**Read before executing any task**: every target below was measured on 2026-09-17 and the chain
moves whenever a chapter or the platform does. T001 re-measures before anything is repaired, and
a task that names a count is quoting that measurement rather than asserting it.

**The loop, after every target**: `pnpm check:fences | tail -1`. A repair that lowers the count
by fewer problems than the target holds means some were shadows; **one that raises it unanchored
something downstream** and is reverted or finished inside that target, with both numbers recorded.

---

## Phase 1: Setup — the inventory, re-measured

**Goal**: know what the 110 are today, not what they were when the plan was written.

- [ ] T001 Run `pnpm check:fences` from `relay-tutorial` and record the total, APPLY and HEAD in `specs/055-fence-chain-repair/baseline.txt`. Expected 110 — APPLY 74, HEAD 36. **Any divergence from that is the first finding** (FR-013), not a rounding.
- [ ] T002 [P] Classify all problems into the four classes and record each count in `baseline.txt`: `matched 0 times`, `no earlier fence to amend`, `differs at line`, `does not exist in relay-platform`. Expected 42 / 32 / 25 / 11.
- [ ] T003 [P] Record where each problem lives — `app/(en)`, `app/(vi)`, `fences/post-series.md` — and confirm **zero are reported against `relay-platform`**. Expected 36 HEAD en · 30 APPLY en · 30 APPLY vi · 14 APPLY appendix.
- [ ] T004 [P] Attribute every problem to the target it is about, by the message where it names one and by the fence's title where it does not, and record the per-target counts in `baseline.txt`. Expected **47 targets** — 36 platform files, 11 phrases — with the top eleven holding 64 of the 110.
- [ ] T005 [P] Confirm the en/vi mirror: every vi problem has an en twin at the same chapter slug, same line, same message, and **zero are vi-only**. This is what makes the diagnosis half the size of the count, so it is checked rather than assumed.
- [ ] T006 [P] Record `MIRROR` at **0** in `baseline.txt`. It is the check that every locale repair is a faithful copy, and it must read 0 at every later measurement.
- [ ] T007 [P] Measure the unread-fence population and record it: opening fences, titled, untitled-with-a-language, and titles already carrying `(excerpt)`. Expected 2,109 / 1,749 / 360 / 222. **`gaps.md` 043-1's "146 of 904" is a 2026-08 figure** and this is the number SC-008 is measured against.
- [ ] T008 Resolve or record the **109 → 110** discrepancy (FR-014): `specs/045-part-3-rework/gaps.md:3327` reports 109 — APPLY 74, HEAD 35, and feature 046's T062 measured 110 — APPLY 74, HEAD 36 and reported it as *"a delta of 0"* against its own opening. One HEAD problem appeared in between. Name the file if the per-file lists can be recovered from either feature's record; record the mechanism either way, because **the delta-of-0 convention is what kept it invisible for nine chapters**.
- [ ] T009 Commit phase 1.

**Checkpoint**: the 110 are inventoried by class, locale and target, and the numbers this feature will be judged against are written down rather than carried.

---

## Phase 2: Foundational — the instrument every repair depends on

**Goal**: hunks are generated from the same replay that checks them. **Blocks phases 4, 5 and 6.**

- [ ] T010 Add a `--dump <dir>` flag to `relay-tutorial/scripts/check-fence-chain.mjs` that writes each path's final replayed state to `<dir>/<path>` and prints how many it wrote. It changes no threshold, exempts no class and alters no exit code — **an output mode, not a loosening** (FR-002), and the contract says so where a reviewer will read it.
- [ ] T011 Prove the dump is the same replay the check uses: dump twice and `diff -r` the trees; run `pnpm check:fences` with and without the flag and confirm the same count. **A generator that replays differently produces hunks the checker rejects for reasons neither of them explains.**
- [ ] T012 Confirm the dump covers every chained path: `find <dir> -type f | wc -l` against the count `--dump` prints for itself. Expected **285 now**.
  **DO NOT COMPARE IT AGAINST THE CHECKER'S OWN `N fenced files replay onto relay-platform` LINE, WHICH DOES NOT EXIST YET.** That line is printed only on the success path, **after** the `process.exit(1)` the 110 problems take, so at any count above zero it never appears. The cross-check against it belongs in phase 7 (T086), where the line is available because the count is 0.
  **And 285 is a pre-phase-3 figure.** The eleven prose-titled fences are in `en.state` today — measured: one declaration moved HEAD from 36 to 35 — so declaring them removes eleven entries and the dump becomes **274**. A re-dump in phase 4 or later that reports 285 means phase 3 did not land.
- [ ] T013 Dump the state for `vitest.coverage.config.mts` and record in `baseline.txt` that it is **318 lines against the tree's 1,182 and contains no `env` block**, together with the dump's own file count at this point (285, before phase 3 takes it to 274). This is the measurement that explains nine of that file's fifteen bad hunks, and it is the instrument's own positive control — if the dump does not show it, the dump is wrong.
- [ ] T014 Run lint and `pnpm build` in `relay-tutorial`; commit phase 2.

**Checkpoint**: the chain's own state is readable on demand, and it has been shown to agree with the checker.

---

## Phase 3: The eleven that name no file (US1) 🎯 first, and it is the loop's control

**Goal**: FR-008 — every listing is either a verified whole-file claim or a declared not-file. **Expected 110 → 99.**

All eleven are ` ```text ` command output. The repair is `(excerpt)` in the title, which
`NOT_A_FILE` at `check-fence-chain.mjs:42` already skips in both loops, and which **222 titles in
this series already carry**. The English title and its Vietnamese twin change together or
`MIRROR` unpairs them.

- [ ] T015 [P] [US1] Declare `the ladder against the registry` in `app/(en)/part-3/chapter-03/errors-that-resolve/page.mdx` and its `app/(vi)/vi/` twin. Body unchanged.
- [ ] T016 [P] [US1] Declare `who builds a docs_url` in `app/(en)/part-3/chapter-03/errors-that-resolve/page.mdx` and its vi twin.
- [ ] T017 [P] [US1] Declare `the typo, now` in `app/(en)/part-3/chapter-03/errors-that-resolve/page.mdx` and its vi twin.
- [ ] T018 [P] [US1] Declare `the derivation, reporting itself` in `app/(en)/part-3/chapter-04/the-isolation-harness/page.mdx` and its vi twin.
- [ ] T019 [P] [US1] Declare `what the schema looks like from here` in `app/(en)/part-3/chapter-04/the-isolation-harness/page.mdx` and its vi twin.
- [ ] T020 [P] [US1] Declare `the structural check, on the first table added after it` in `app/(en)/part-3/chapter-05/the-outbox/page.mdx` and its vi twin.
- [ ] T021 [P] [US1] Declare `the same error, from inside one package` in `app/(en)/part-3/chapter-05/the-outbox/page.mdx` and its vi twin.
- [ ] T022 [P] [US1] Declare `the check, on the consumer's table` in `app/(en)/part-3/chapter-06/jetstream-and-the-first-consumer/page.mdx` and its vi twin.
- [ ] T023 [P] [US1] Declare `42P01` in `app/(en)/part-3/chapter-06/jetstream-and-the-first-consumer/page.mdx` and its vi twin.
- [ ] T024 [P] [US1] Declare `run 11 of 20` in `app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/page.mdx` and its vi twin.
- [ ] T025 [P] [US1] Declare `the build that added the module` in `app/(en)/part-3/chapter-08/the-endpoints-and-the-instruments/page.mdx` and its vi twin.
- [ ] T026 [US1] **Read each of the eleven bodies before declaring it, and record that you did.** The criterion is that the block is not a file's contents — all eleven are command output today, and a twelfth that looked like a listing would not be this class. A declaration nobody checked is the exemption FR-002 forbids, wearing a different hat.
- [ ] T027 [US1] Run `pnpm check:fences` and confirm **exactly 99 — APPLY 74, HEAD 25**, with `MIRROR` still 0. **This is the measurement loop's positive control**: eleven declarations have no cascade risk, so if the count moves by anything other than 11 the instrument is wrong before anything expensive has been attempted. Record both numbers in `baseline.txt`.
  **`MIRROR` IS THE PRIMARY SIGNAL HERE AND THE TOTAL IS NOT — MEASURED.** One fence declared in English only gives **`110 — APPLY 74, HEAD 35, MIRROR 1`**: HEAD falls by one and MIRROR rises by one, so **the total does not move at all.** Declared in both locales it gives `109 — APPLY 74, HEAD 35`. `MIRROR` compares the chapter's **joined title list first** and `continue`s on mismatch (`check-fence-chain.mjs:307`), so a chapter whose Vietnamese titles were not renamed produces **one** problem however many of its fences were declared — and chapter 3.3 holds three of the eleven, so **one missed chapter can hold three declarations back while the number looks untouched.**
  So read `MIRROR` first: it must be **0**. A total of 110 after this phase does not mean nothing happened; it means a locale pair was broken. **An earlier draft of this task predicted "100 rather than 99" and the probe says otherwise** — the total under-moves by one per affected chapter, not per fence.
- [ ] T028 Run `pnpm build`; commit phase 3.

**Checkpoint**: 99, by a repair that could not have cascaded — and the loop has been shown to work before it is trusted with the rest.

---

## Phase 4: The twelve files whose hunks cannot anchor (US1)

**Goal**: FR-006 — 42 problems, regenerated against the dumped chain state, first failure per file first. **Expected 99 → 57.**

Every hunk here is `@@` bodies only; a `--- a/` header is read as body text and fails. Widen the
context when a pre-image matches twice and **verify before pasting** — `-U8` can be worse than
`-U10`, because widening merges adjacent hunks.

**EVERY REPAIR IN THIS PHASE IS A LOCALE PAIR** (FR-011): 3 of `turbo.json`'s 6 bad hunks are
Vietnamese, and so are half of `app.module.ts`'s, `codes.ts`'s and `eslint.config.mjs`'s. The
English fence is where the hunk is regenerated and the Vietnamese twin takes a byte-identical
copy.

- [ ] T029 [US1] `vitest.coverage.config.mts` — **15 of the 42**, and the largest single target in the feature. Repair the **first** failing hunk only (the appendix hunk that creates the `env` block, `fences/post-series.md`), then re-measure before touching the other fourteen: nine of them are anchored inside that block and should repair themselves. Chapters: 3.17, 3.22, 3.23, plus 9 appendix hunks.
- [ ] T030 [US1] `vitest.coverage.config.mts` — repair whatever of the fifteen survives T029, in chapter order, re-measuring after each. Record how many were shadows, because **that ratio is the feature's headline finding about what a count of 110 means**.
- [ ] T031 [US1] `turbo.json` — 6 bad hunks across 3.22, 3.23, 3.24 (3 en + 3 vi). Fenced by 10 chapters plus 1 appendix hunk, so regenerate rather than republish.
- [ ] T032 [US1] `services/api/src/app.module.ts` — 4 bad hunks across 3.22 and 3.23. Fenced by 11 chapters.
- [ ] T033 [US1] `packages/protocol/src/codes.ts` — 4 bad hunks across 3.23 and 3.24. Fenced by 12 chapters, the most-chained file in the series.
- [ ] T034 [US1] `eslint.config.mjs` — 3 bad hunks in 3.25 and the appendix. `gaps.md` 047-1 recorded this file as unable to take a fence at all; that entry is re-measured here and closed or re-stated with today's numbers.
- [ ] T035 [P] [US1] `services/api/src/webhooks/test-event.itest.ts` — 2 bad hunks in 3.22.
- [ ] T036 [P] [US1] `packages/test-harness/src/sentinel.sql` — 2 bad hunks in 3.23.
- [ ] T037 [P] [US1] `packages/e2e/src/harness.ts` — 2 bad hunks in 3.22.
- [ ] T038 [P] [US1] `package.json` — 1 bad hunk in the appendix. Chapter 4.9 edited this hunk's `+` side; the pre-image failure predates that.
- [ ] T039 [P] [US1] `services/api/package.json` — 1 bad hunk in the appendix.
- [ ] T040 [P] [US1] `services/api/src/auth/credentials.itest.ts` — 1 bad hunk in the appendix.
- [ ] T041 [P] [US1] `services/gateway/src/presence.itest.ts` — 1 bad hunk in the appendix.
- [ ] T042 [US1] Re-measure and record after every file above, in `baseline.txt`: **the total, APPLY, HEAD and `MIRROR`**, with the file that preceded each number and **the command that regenerated its hunks** (FR-003, FR-011, SC-004, SC-009). A recorded command is what makes the repair reproducible; chapter 4.2 published one nobody ran through five analysis passes.
  **Expect movement in both directions**: repairing a hunk changes the state every later hunk for that file anchors on, and feature 045 measured one regeneration taking the chain from 111 to 203. **A file that raises the count is reverted or finished before the next file is started** (FR-004), with both numbers recorded — not carried forward as a deficit to fix later.
- [ ] T043 Run `pnpm build`; commit phase 4.

**Checkpoint**: no hunk in the series is written against a state that does not exist.

---

## Phase 5: The nine files the chain never sees whole (US1, US3)

**Goal**: FR-005 — 32 problems over 9 files. **Expected 57 → 25.**

**This is the phase that can repair the checker and damage the chapter.** Up to 1,956 lines of
listing land in published chapters, and the content must come from a tag rather than the working
tree, which is up to twenty chapters ahead. **`fences/post-series.md` is not available**: it
applies after every chapter and can never supply a predecessor state (R2).

**THE TAG IS DECIDED BY THE DESIGN, AND GETTING IT WRONG FAILS ON CONTACT.** The rule is one
sentence — **the body is the file at the tag of the chapter that publishes it** — and it resolves
differently for T044's two designs:

    replace chapter N's diff with a body at N     →  rework/part3-chN
    add a body at an earlier chapter M            →  rework/part3-chM   (usually N-1)

Measured, and this is why the rule is stated rather than assumed: chapter 3.3's existing hunk for
`session.itest.ts` **applies to `rework/part3-ch2` (281 lines) and does not apply to
`rework/part3-ch3` (287 lines)**, because ch3 already contains what the hunk adds. Taking the
wrong one produces `hunk pre-image matched 0 times` **after** the introduction has landed, which
reads like the defect this phase is fixing rather than the one it just caused.

Both candidates are measured per file below. **T044 decides the design before any body is
taken.**

**EVERY REPAIR IN THIS PHASE IS A LOCALE PAIR** (FR-011): the English fence and its Vietnamese
twin, byte-identical, changed together.

- [ ] T044 [US3] **Decide, per file, between the two designs and record the decision, its reason AND THE TAG IT IMPLIES**, before any body is taken: replace the first `diff` with a whole body at that chapter (`rework/part3-chN`), or add the body to an earlier chapter that introduces the file (`rework/part3-chM`). Nine judgements about published prose; research could not settle them by measurement. **This task blocks T045 through T053** — it is not a task to do beside them.
- [ ] T045 [US1] `services/gateway/src/session.itest.ts` — first amended in 3.3 and again in 3.5, 3.9, 3.17, 3.22. Ten problems, the second-largest target. **`rework/part3-ch2` 281 lines · `rework/part3-ch3` 287 · today 1,626.** Measured: chapter 3.3's existing hunk applies to ch2 and not to ch3.
- [ ] T046 [P] [US1] `services/api/src/outbox/event.test.ts` — amended in 3.11 and 3.17. 4 problems. **ch10 93 lines · ch11 122 · today 524.**
- [ ] T047 [P] [US1] `packages/test-harness/src/driver-exempt.test.ts` — amended in 3.11 and 3.22. 4 problems. **ch10 92 lines · ch11 104 · today 127.**
- [ ] T048 [P] [US1] `packages/protocol/src/internal.test.ts` — amended in 3.20 and 3.24. 4 problems. **ch19 49 lines · ch20 114 · today 253** — the widest gap between the two candidates in the phase, so the design decision costs 65 lines here.
- [ ] T049 [P] [US1] `services/api/src/messages/history.itest.ts` — amended in 3.11. 2 problems. **ch10 102 lines · ch11 150 · today 150.**
- [ ] T050 [P] [US1] `services/api/src/messages/idempotency.itest.ts` — amended in 3.11. 2 problems. **ch10 136 lines · ch11 144 · today 224.**
- [ ] T051 [P] [US1] `services/api/src/fanout/fanout.itest.ts` — amended in 3.17. 2 problems. **ch16 558 lines · ch17 559 · today 561** — the two candidates differ by one line, and it is still the largest body in the phase.
- [ ] T052 [P] [US1] `packages/test-harness/src/guard.itest.ts` — amended in 3.23. 2 problems. **ch22 333 lines · ch23 427 · today 442.**
- [ ] T053 [P] [US1] `services/dispatcher/vitest.integration.config.mts` — amended in 3.23. 2 problems, and the cheapest file in the phase. **ch22 14 lines · ch23 49 · today 49.**
- [ ] T054 [US1] After each introduction, confirm **every existing amendment for that path still applies** — by running the checker, not by reading. An introduction whose content is right for the reader and wrong by one line leaves the later hunks anchored on bytes that do not exist.
- [ ] T054a [US1] Re-measure and record after **every file** in this phase, in `baseline.txt`: the total, APPLY, HEAD and `MIRROR`, with the file that preceded each number and the tag the body came from (FR-003, FR-011, SC-004, SC-009). **Phase 5 had no measurement task until analysis found it missing** — phases 4 and 6 had one and this one did not, which is the shape this feature is about: a check that exists in one place and not its twin. A file that raises the count is reverted or finished before the next is started (FR-004).
- [ ] T055 [US3] **Read each repaired chapter's prose beside its new listing** and confirm the prose describes what the fence shows. Record the count of chapters read. Feature 045's sentence is the standard: *"putting those into the last chapter that happened to fence the file would make that chapter show a reader code it never discusses."*
- [ ] T056 [US3] Where no chapter honestly introduces a file, **record the exception under FR-012 with what it would cost** and turn that file's fences into excerpts instead. The count improving is not the test; whether a reader can still follow the chapter is. **Record how many fences this converts**, because T090 asserts the declared-`(excerpt)` population and would otherwise fail for this task's reason.
- [ ] T057 Run `pnpm build`; commit phase 5.

**Checkpoint**: every file the chapters amend has been shown to the reader at least once, or the exception is written down with its price.

---

## Phase 6: The twenty-five divergences (US1)

**Goal**: FR-007 — the replayed end state equals the repository. **Expected 25 → 0.**

**Appended, never regenerated.** `codes.ts` is fenced by 12 chapters, `app.module.ts` by 11,
`vitest.coverage.config.mts` by 11 plus 9 appendix hunks, and one early-fence regeneration took
the chain from 111 problems to 203. The home for an appended hunk is `fences/post-series.md`
unless a chapter genuinely discusses the change.

**A hunk appended in the appendix has no Vietnamese twin** — `fences/post-series.md` is one file
for both locales. A hunk appended **in a chapter** is a locale pair like every other (FR-011),
and T084 checks `MIRROR` after each.

- [ ] T058 [US1] Re-measure all 25 divergences **after phases 4 and 5**, because a divergence is whatever is left once every hunk has applied. The two largest — `vitest.coverage.config.mts` at 867 differing lines and `eslint.config.mjs` at 540 — were measured against a chain state those phases change, so **their real size is not yet known** and the plan says so rather than guessing.
- [ ] T059 [US1] `vitest.coverage.config.mts` — append in `fences/post-series.md`. Chapter 4.9 could not publish its own two-line edit to this file for exactly this reason and described it in prose instead; that prose is replaced by the hunk here.
- [ ] T060 [US1] `eslint.config.mjs` — append in `fences/post-series.md`. 206 chain lines against 451.
- [ ] T061 [P] [US1] `packages/protocol/src/codes.ts` — 157 differing lines.
- [ ] T062 [P] [US1] `services/api/src/isolation/targets.ts` — 119 differing lines.
- [ ] T063 [P] [US1] `services/api/src/auth/credential.guard.ts` — 102 differing lines.
- [ ] T064 [P] [US1] `services/api/src/auth/credentials.itest.ts` — 86 differing lines.
- [ ] T065 [P] [US1] `packages/protocol/src/codes.test.ts` — 79 differing lines.
- [ ] T066 [P] [US1] `packages/test-harness/src/sentinel.sql` — 57 differing lines. **And record separately that the published fence carries `END $;` where the repository has `END $$;`** (FR-016): a reader copying that listing gets a syntax error, and the count never said so.
- [ ] T067 [P] [US1] `services/api/src/app.module.ts` — 54 differing lines.
- [ ] T068 [P] [US1] `packages/test-harness/src/bound-port.test.ts` — 53 differing lines.
- [ ] T069 [P] [US1] `services/gateway/src/presence.itest.ts` — 49 differing lines.
- [ ] T070 [P] [US1] `services/api/src/outbox/event.ts` — 38 differing lines.
- [ ] T071 [P] [US1] `services/gateway/src/main.test.ts` — 36 differing lines.
- [ ] T072 [P] [US1] `services/api/src/internal/dispatch.controller.ts` — 21 differing lines.
- [ ] T073 [P] [US1] `services/api/src/internal/usage.controller.ts` — 20 differing lines.
- [ ] T074 [P] [US1] `services/api/src/isolation/targets.itest.ts` — 18 differing lines.
- [ ] T075 [P] [US1] `services/api/src/isolation/fixtures.ts` — 18 differing lines.
- [ ] T076 [P] [US1] `packages/test-harness/src/sentinel.ts` — 18 differing lines.
- [ ] T077 [P] [US1] `services/api/src/auth/authenticate.middleware.ts` — 16 differing lines.
- [ ] T078 [P] [US1] `services/api/src/webhooks/test-event.itest.ts` — 8 differing lines.
- [ ] T079 [P] [US1] `services/api/src/db/catalogue.ts` — 7 differing lines.
- [ ] T080 [P] [US1] `package.json` — 7 differing lines, and it is `test:integration` at line 15, which chapter 4.9 pointed at `scripts/integration-gate.mjs`.
- [ ] T081 [P] [US1] `services/gateway/src/typing.itest.ts` — 5 differing lines, from chapter 4.9's presence-payload repair.
- [ ] T082 [P] [US1] `services/api/package.json` — 4 differing lines.
- [ ] T083 [P] [US1] `.gitignore` — 2 differing lines, and the checker's message prints `<eof>` on **both** sides, so the difference is invisible in the report. **Diff the dumped state against the tree with `diff` and `cat -A` before writing anything**: if the difference is whitespace or a trailing newline, **a `@@` hunk may not be able to express it at all**, and the honest outcome is an FR-012 exception with the bytes shown, not a hunk that looks right and changes nothing. This is the one target in the phase whose repair might not exist.
- [ ] T084 [US1] Re-measure after each file and record the total, APPLY, HEAD and `MIRROR` with the file that preceded each number, and the command that generated its hunk (FR-003, FR-011, SC-004, SC-009). A file that raises the count is reverted or finished before the next is started (FR-004).
- [ ] T085 Run `pnpm build`; commit phase 6.

**Checkpoint**: every titled fence in the series replays onto the repository.

---

## Phase 7: Zero, and what zero does not mean (US2)

**Goal**: FR-001 — the count is 0 and the run exits 0, with the checker unchanged in what it accepts.

- [ ] T086 [US2] Run `pnpm check:fences` on a clean tree and confirm **0 problems** (SC-001), recorded beside T001's opening. **Assert the success LINE, not the exit code**: `check-fence-chain: N fenced files replay onto relay-platform across M chapters (…)`, with N equal to the dump's count.
  **Exit 0 is not evidence the checker looked.** `scripts/check-fence-chain.sh:10-13` prints `relay-platform not found — skipping` and **exits 0** when the platform repository is absent, so a standalone clone satisfies "0 problems, exit 0" having replayed nothing. That is feature 045's own lesson (045-81) arriving in this feature's own success criterion, and the success line is the only output that distinguishes the two zeroes. Record the line verbatim.
- [ ] T087 [US2] **Plant a regression and run it red** (SC-003): change one line in a fenced platform file with no chapter hunk, confirm the run exits non-zero and names that file, then restore. Run red rather than reasoned about — the same probe chapter 4.9 used on the reconciler.
- [ ] T088 [US2] Confirm `MIRROR` is 0 (SC-004) and that the four classes are each 0 (SC-005), reported separately rather than as one total.
- [ ] T089 [US2] Confirm no file under `relay-platform/` was edited by this feature: `git diff --stat part4-ch9` in that repository is empty (SC-010). **A requirement, not an observation** — the cheapest repair for 25 of the 110 would have been to edit the platform.
- [ ] T090 [US2] Re-measure the unread-fence population (SC-008) and confirm untitled is unchanged at 360 and declared `(excerpt)` has risen to **233 plus whatever T056 recorded** — 11 from phase 3 and one per fence any FR-012 exception converted. **An assertion of "exactly 11" would fail for T056's reason rather than its own**, which is the defect class this project keeps finding. Nothing that names a real file may have become unverified **without a recorded exception**.
- [ ] T091 [US2] Confirm the count never exceeded 110 at any measured point (SC-006), from `baseline.txt`'s per-target record. If it did, the excursion is reported with the file that caused it and the number it reached.
- [ ] T092 [US2] Run every other gate in the tutorial job: `pnpm lint`, `pnpm build`, `check:docs`, `check:srs`, `check:figures`, `check:errors`. **Build `relay-platform` first** — `check:errors` reads the built `dist`.
- [ ] T093 Commit phase 7.

**Checkpoint**: the gate can go red for its own reason, and has been shown doing it.

---

## Phase 8: The record

**Goal**: what was repaired, what was declared, what was recorded as unrepairable, and what zero does not claim.

- [ ] T094 Write **ADR-29** in `docs/05-sad.md` and `docs/06-adr-deep-dives.md`: the `--dump` flag and the `(excerpt)` declarations as one decision about what a fence claims, with the rejected alternatives — teaching the checker that `lang=text` is never a file, retitling to the real path, removing the titles — and a reversal condition. Constitution VII, and the plan flagged it as owed.
- [ ] T095 Write `specs/055-fence-chain-repair/gaps.md`. **Re-measure the carried items this feature touches** rather than copying them: 043-1 (untitled fences, re-measured at 360 of 2,109), 047-1 (`eslint.config.mjs` could not take a fence), 048-3 (`vitest.coverage.config.mts` diverged at line 29), 050-3 (the vi chain is never compared to the tree), 050-4 (the 11 prose titles), 054-1 (the red workflow, closed by this feature).
- [ ] T096 In `gaps.md`, record **what zero does not mean**: not that the chapters are readable, not that the listings are pedagogically right, not that the 360 untitled fences mean anything. One property — every titled fence replays onto the repository.
- [ ] T097 In `gaps.md`, record the cascade arithmetic (FR-015): how many of the 110 were single defects and how many were shadows of an earlier failure in the same file, so the next reader of a fence-chain number knows what it counts.
- [ ] T098 Write `specs/055-fence-chain-repair/traceability.md` mapping every FR and SC to the tasks and artifacts that discharged it, and **record any discharged in a weaker form than their words suggest**.
- [ ] T099 Update `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T100 Consider whether zero should be **guarded** rather than merely reached — the checker already exits non-zero above 0, so the open question is what holds the number between chapters. Adjacent to `gaps.md` 048-5 and 054-4; record the decision either way rather than leaving the next chapter to discover it.
- [ ] T101 Commit phase 8 and push all three repositories.
- [ ] T102 [US2] Discharge **SC-002**: after the push, confirm the **tutorial job in CI succeeds** — the first push in nine chapters whose result reflects that push. **This is the only success criterion that cannot be verified locally**, and it had no task until analysis found it: T092 runs the same gates on this machine, which is not the same claim. If the job fails for a reason this feature did not cause, record it rather than repairing it here.

**Checkpoint**: 110 to 0, with the arithmetic that says which of the 110 were defects and which were shadows.

---

## Dependencies

    Phase 1  ─────────────────────────────────────────► everything
    Phase 2  ─────► Phases 4, 5, 6 (every hunk is generated against the dump)
    Phase 3  ─────► independent of everything, and it is the loop's positive control
    Phase 4  ─────► Phase 6 (a divergence is what remains after the hunks apply)
    Phase 5  ─────► Phase 6 (same reason)
    Phases 3-6 ───► Phase 7 (zero needs all four classes at zero)
    T044     ─────► T045-T053 (the design decides which tag the body comes from)
    T101     ─────► T102      (SC-002 is only observable after a push)

**US1 is delivered incrementally and US2 is not.** Each repaired target is a listing a reader can
trust, so phases 3 through 6 each deliver value on their own. The build's colour changes only at
0 — at one problem the step is as red as at 110 — so US2 is a single step at the end rather than
a slice.

**US3 is a constraint on phase 5 rather than a phase.** It is where a repair can improve the
checker's number and make a chapter worse, and T055 is the only task in the feature whose test is
reading.

## Parallel opportunities

- **Phase 1**: T002 through T007 are six reads of the same report.
- **Phase 3**: all eleven declarations are independent — different chapters, no chain state.
- **Phase 4**: T035 through T041 are seven single-hunk files in different chapters. T029 through
  T034 are sequential because each one's later hunks depend on its own first repair.
- **Phase 5**: T046 through T053 are eight independent files. T045 is alone because
  `session.itest.ts` spans five chapters.
- **Phase 6**: T061 through T083 are twenty-three independent appended hunks.

## Implementation strategy

**The MVP is phase 3.** Eleven declarations, no cascade risk, 110 → 99, and it proves the
measurement loop before anything expensive is attempted. If the count moves by anything other
than 11, stop and fix the instrument.

**Then the order the mechanics force**: hunks before divergences within a file, first failure
before the rest within a file, introductions before the hunks that depend on them, English before
Vietnamese within a fence.

**The riskiest phase is 5, not 4.** Phase 4 can raise the count and the checker says so
immediately. Phase 5 can leave the count falling while a chapter quietly acquires 559 lines of
test file it never discusses, and only a person reading it notices.
