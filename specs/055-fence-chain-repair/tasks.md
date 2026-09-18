# Tasks: repair the fence chain — 110 to 0

**Feature**: `specs/055-fence-chain-repair` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) — read it first, it corrects two of the
specification's own assumptions.

**Read before executing any task**: every target below was measured on 2026-09-17 and the chain
moves whenever a chapter or the platform does. T001 re-measures before anything is repaired, and
a task that names a count is quoting that measurement rather than asserting it.

**The loop, after every target**: `pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'`.
**NOT `| tail -1`, WHICH NEVER SHOWS THE COUNT.** Every problem line and the summary go to
**stderr**, and above zero pnpm exits 1 and writes its own `ELIFECYCLE Command failed with exit
code 1.` last — so `| tail -1` prints that, and `2>&1 | tail -1` prints it too. Measured. The
command an earlier draft prescribed **about fifty times** works only once the repair is finished,
which is the same shape as T012's note that the success line exists only on the success path.
A repair that lowers the count
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
  **AND RECORD WHAT A NON-ZERO `MIRROR` COSTS, BECAUSE IT IS NOT ONE FENCE.** The loop joins each chapter's `lang title` list, and on a mismatch it pushes **one** problem and `continue`s — **past every body comparison in that chapter** (`check-fence-chain.mjs:307-314`). So `MIRROR 1` does not mean one fence is wrong; it means **that chapter's fences were not compared at all**. The eleven declarations sit in **6 chapters holding 128 titled fences**, the largest of them 40, so a half-applied pair in `the-endpoints-and-the-instruments` reports 1 and leaves 40 bodies unchecked.
  **The total will not show it**: the declaration removes a HEAD problem as it adds the MIRROR one, so the count stays at 110. Analysis pass 2 measured exactly that flat total and read it as *"the total does not move"*; this is its other half. **Any measurement taken while `MIRROR > 0` covers fewer fences than the one before it**, and phase 5 adds fences to chapters as well, so the window is not phase 3's alone.
- [ ] T007 [P] Measure the unread-fence population and record it: opening fences, titled, untitled-with-a-language, and titles already carrying `(excerpt)`. Expected 2,109 / 1,749 / 360 / 222. **`gaps.md` 043-1's "146 of 904" is a 2026-08 figure** and this is the number SC-008 is measured against.
  **RECORD THE LOCALE SPLIT, BECAUSE EVERY ONE OF THESE IS A TWO-LOCALE NUMBER.** Measured: `app/(en)` 1,071 fences · `app/(vi)` 1,005 · `fences/` 33, and the 222 is **111 en and 111 vi**. A count of this population taken on one side is half of it, which is the arithmetic T090 got wrong until analysis pass 5.
  **And `(excerpt)` is not the whole of what the checker skips.** `NOT_A_FILE` is `(excerpt) || .naive.`, and `.naive.` carries **one more pair** — so the population the checker refuses to read is **224**, of which 222 are `(excerpt)`. Record both numbers; a task that asks for "the declared population" and gets one of them cannot say which.
- [ ] T008 Resolve or record the **109 → 110** discrepancy (FR-014): `specs/045-part-3-rework/gaps.md:3327` reports 109 — APPLY 74, HEAD 35, and feature 046's T062 measured 110 — APPLY 74, HEAD 36 and reported it as *"a delta of 0"* against its own opening. One HEAD problem appeared in between. Name the file if the per-file lists can be recovered from either feature's record; record the mechanism either way, because **the delta-of-0 convention is what kept it invisible for nine chapters**.
- [ ] T009 Commit phase 1.

**Checkpoint**: the 110 are inventoried by class, locale and target, and the numbers this feature will be judged against are written down rather than carried.

---

## Phase 2: Foundational — the instrument every repair depends on

**Goal**: hunks are generated from the same replay that checks them. **Blocks phases 4, 5 and 6.**

- [ ] T010 Add a `--dump <dir> [--at <page>]` flag to `relay-tutorial/scripts/check-fence-chain.mjs`. Plain `--dump` writes each path's state after every chapter and the appendix; `--at <page>` writes the state **as that page is reached, before its own fences apply**. Both print how many paths they wrote, **and which chain they wrote**. The bytes are what the checker compares, **trailing newline included**. It changes no threshold, exempts no class and alters no exit code — **an output mode, not a loosening** (FR-002), and the contract says so where a reviewer will read it.
  **BOTH MODES, BECAUSE ONE CANNOT SERVE THE CHAPTER HUNKS — MEASURED.** `turbo.json` replays to **62 lines at chapter 3.22** and **74 after the appendix**; a hunk generated against the final state carries twelve lines of context that do not exist at 3.22. A final-state dump serves the **14 appendix hunks** and the **25 divergences** and cannot serve the **28 chapter hunks**. An earlier draft of this task specified the final-state mode alone, which would have produced hunks that fail exactly like the ones they replace — chapter 4.8's *"check which state a hunk is written against before blaming the hunk"*, arriving inside the instrument written to prevent it.
  **AND THERE IS NO `--locale` FLAG, BECAUSE THE PAGE PATH IS ALREADY THE LOCALE.** Every problem line begins with `app/(en)/…` or `app/(vi)/vi/…`, so `--at` derives the chain from the argument it was given and a flag could only disagree with it. **The plain `--dump` mode writes the English chain, and must say so in its own output.** Measured by class and locale:

    class                  en   vi  appendix   total   served by
    hunk pre-image         14   14        14      42   --at for 28 · --dump for 14
    no earlier fence       16   16         0      32   a tag, not a dump (R2)
    differs at line        25    0         0      25   --dump
    does not exist         11    0         0      11   a title edit, no dump

  **All 39 consumers of the final-state mode are English** — the HEAD comparison iterates `en.state`, and `fences/post-series.md` is one file for both locales — and **all 30 Vietnamese problems are chapter problems**, so every one is served by `--at` on an `app/(vi)/vi/…` page. Half of the 28 chapter hunks are Vietnamese, and an earlier draft of this task left the chain a bare `--dump` reads unnamed: **pass 1's throwaway dumper silently read `en.state`**, which is right for 39 of the 110 and wrong for 28 of them.
- [ ] T011 Prove the dump is the same replay the check uses: dump twice and `diff -r` the trees; run `pnpm check:fences` with and without the flag and confirm the same count. **A generator that replays differently produces hunks the checker rejects for reasons neither of them explains.**
  **AND ADD THE POSITIVE CONTROL, BECAUSE DETERMINISM IS NOT CORRECTNESS.** Dumping twice proves the dump is stable; **a dump that is consistently wrong passes that check.** So: take a chapter hunk that **works today**, dump with `--at` at its chapter, and confirm the hunk applies against that state. It must. Then confirm the same hunk does **not** apply against the plain `--dump` state, which is what proves the two modes are different states rather than the same one twice.
  **RUN THAT CONTROL ON A VIETNAMESE PAGE TOO**, because half the chapter hunks are vi and a dumper that reads `en.state` for every argument passes the English half of this check. The discriminator needs no arithmetic: `services/api/src/metering/reconcile.ts` is chained in en 4.9 and in **no vi chapter**, so `--at` on a vi page must not write it and `--at` on en 4.9 must. Ten paths are in that position, all in en 4.5 through 4.9.
  **And check the trailing newline**: dump a path with no HEAD divergence and diff it against the tree — zero output. Pass 3's own probe dropped the final newline and made `turbo.json` read one line short of the tree, which looked like a divergence that does not exist.
- [ ] T012 Confirm the dump covers every chained path: `find <dir> -type f | wc -l` against the count `--dump` prints for itself. Expected **285 now** for the English final-state mode; the vi chain holds **276**. **`--at <page>` writes fewer** — only the paths the chain has seen by that page, which for an early chapter is a small fraction of 285 — so its count is recorded per chapter rather than compared against a fixed number.
  **DO NOT COMPARE IT AGAINST THE CHECKER'S OWN `N fenced files replay onto relay-platform` LINE, WHICH DOES NOT EXIST YET.** That line is printed only on the success path, **after** the `process.exit(1)` the 110 problems take, so at any count above zero it never appears. The cross-check against it belongs in phase 7 (T086), where the line is available because the count is 0.
  **And the 285/276 gap is 9 where the title count says 10** — ten paths are titled in en chapters and in no vi chapter (all in 4.5 through 4.9), so one of them never reaches the state. **Name it rather than averaging the two numbers**; a path that is titled and unchained is one of 043-1's population arriving inside this feature's own instrument check.
  **And 285 is a pre-phase-3 figure.** The eleven prose-titled fences are in `en.state` today — measured: one declaration moved HEAD from 36 to 35 — so declaring them removes eleven entries and the dump becomes **274**. A re-dump in phase 4 or later that reports 285 means phase 3 did not land.
- [ ] T013 Dump the state for `vitest.coverage.config.mts` and record in `baseline.txt` that it is **318 lines against the tree's 1,182 and contains no `env` block**, together with the dump's own file count at this point (285, before phase 3 takes it to 274). This is the measurement that explains nine of that file's fifteen bad hunks, and it is the instrument's own positive control — if the dump does not show it, the dump is wrong.
- [ ] T014 Run lint and `pnpm build` in `relay-tutorial`; commit phase 2.

**Checkpoint**: the chain's own state is readable on demand, and it has been shown to agree with the checker.

---

## Phase 3: The eleven that name no file (US1) 🎯 first, and it is the loop's control

**Goal**: FR-008 — every listing is either a verified whole-file claim or a declared not-file. **Expected 110 → 99**, and the declared-`(excerpt)` population **222 → 244**, because eleven titles are **22 fences**.

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

## Phase 4: The twelve files whose hunks cannot anchor (US1, US3)

**Goal**: FR-006 — 42 problems, regenerated against the dumped chain state, first failure per file first. **Expected 99 → 57.**

Every hunk here is `@@` bodies only; a `--- a/` header is read as body text and fails. Widen the
context when a pre-image matches twice and **verify before pasting** — `-U8` can be worse than
`-U10`, because widening merges adjacent hunks.

**EVERY REPAIR IN THIS PHASE IS A LOCALE PAIR** (FR-011): 3 of `turbo.json`'s 6 bad hunks are
Vietnamese, and so are half of `app.module.ts`'s, `codes.ts`'s and `eslint.config.mjs`'s. The
English fence is where the hunk is regenerated and the Vietnamese twin takes a byte-identical
copy.

- [ ] T029 [US1] `vitest.coverage.config.mts` — **15 of the 42**, and the largest single target in the feature. Repair the **first** failing hunk only, then re-measure before touching the other fourteen. **The first is `app/(en)/part-3/chapter-17/the-words-somebody-wants-back/page.mdx:6703`**, measured in replay order:

    en 3.17:6703 · en 3.22:5589 · en 3.23:1997 · APPENDIX ×9 (from :1501) · vi 3.17 · vi 3.22 · vi 3.23

  **An earlier draft of this task named the appendix hunk at `:1501` as the first, and it is the fourth.** Chapters replay before the appendix, so three chapter hunks fail ahead of it — and whether `:1501` can anchor at all depends on the state those three leave behind. The claim that nine appendix hunks are shadows of `:1501` is R3's and stands; **which hunk is the root does not follow from it**, and only re-measuring after 3.17 says.
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
- [ ] T042a [US3] **Read the prose beside every hunk this phase regenerated in a chapter** — the 28 of the 42 that are not in `fences/post-series.md` — and confirm it still describes what the fence now shows; record the count of chapters read (SC-007). **A regenerated hunk is not the hunk it replaced.** It is `diff(chain state at that chapter, the file at rework/part3-chN)`, so it absorbs whatever divergence the chain was carrying for that path — which means it can be **larger** than the hunk it replaces and can show the reader lines that chapter never discusses. Record every case where a regenerated hunk grew, with the line counts before and after: that is the phase's prose risk and it has a mechanism behind it rather than being a general caution.
  **SC-007 had one task and three phases that edit chapters.** It lived in phase 5 only (T055) while this phase rewrites 28 listings a reader sees and phase 6 appends into however many chapters the appendix is not the honest home for. Analysis pass 1 recorded the gap as *"partial"* in a coverage table and never raised it as a numbered finding, so nothing fixed it — **a finding filed in a table rather than a line does not get repaired**, which is the same shape as the check that exists in one config and not its twin.
- [ ] T043 Run `pnpm build`; commit phase 4.

**Checkpoint**: no hunk in the series is written against a state that does not exist, and the prose beside each regenerated one has been read.

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

- [ ] T044 [US3] **Decide, per file, between the three designs and record the decision, its reason AND THE TAG IT IMPLIES**, before any body is taken: replace the first `diff` with a whole body at that chapter (`rework/part3-chN`), add the body to an earlier chapter that introduces the file (`rework/part3-chM`), or **declare the file's fences excerpts and record the exception under FR-012** (T056's route, taken as a decision rather than reached as a failure). Nine judgements about published prose; research could not settle them by measurement. **This task blocks T045 through T053** — it is not a task to do beside them.
  **THE THIRD DESIGN IS ALREADY THE PRACTICE FOR SEVEN OF THE NINE.** Measured: `session.itest.ts` carries **5 failing `diff` fences and 2 `(excerpt)` ones**, and `fanout.itest.ts`, `driver-exempt.test.ts`, `idempotency.itest.ts` and `guard.itest.ts` each carry at least one excerpt beside their diffs. So the chapters already show these files in excerpt form, and converting the diffs is a smaller edit with a precedent in the same page — which is why it belongs in this decision rather than in T056's fallback.
  **Record both numbers per file, because the price runs the other way too.** `session.itest.ts` is 287 lines published against 5 amendments left unverified, and `CLAUDE.md` records it as holding **the only end-to-end proof that 044's column, api and ack are connected** — an excerpt is never compared to anything, so that proof stops being checked. The decision is which of the two costs a chapter should pay, stated as lines against amendments rather than as a preference.
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
- [ ] T055 [US3] **Read each repaired chapter's prose beside its new listing** and confirm the prose describes what the fence shows. Record the count of chapters read. **One of SC-007's three read-throughs** — T042a covers the regenerated hunks and T084a the appended ones; this one covers the introductions, which are the largest listings the feature publishes and the only ones a chapter has never shown before. Feature 045's sentence is the standard: *"putting those into the last chapter that happened to fence the file would make that chapter show a reader code it never discusses."*
- [ ] T056 [US3] Where no chapter honestly introduces a file, **convert AND record under FR-012**: turn that file's fences into excerpts — which is what takes the problem out of the count — and write down the reason, the measurement and what a real repair would cost. **Recording alone leaves the count non-zero**, because nothing reads `gaps.md` and the checker cannot tell a documented problem from any other. The count improving is not the test; whether a reader can still follow the chapter is. **Record how many fence PAIRS this converts** — the unit is the pair, so each one moves T090's population by **two** — because T090 asserts the declared-`(excerpt)` population and would otherwise fail for this task's reason. **T044 now offers this route as a design rather than a fallback**, so what reaches this task is a file for which all three designs were costed and none was honest, not a file nobody decided about.
- [ ] T057 Run `pnpm build`; commit phase 5.

**Checkpoint**: every file the chapters amend has been shown to the reader at least once, or the exception is written down with its price.

---

## Phase 6: The twenty-five divergences (US1, US3)

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
- [ ] T083 [P] [US1] `.gitignore` — **one differing line, and it is a pure append: the cheapest target in the phase.** Measured: the chain state is **7 lines**, the tree holds **8**, the state is a **strict prefix**, and the line the tree has is `corpus.json` — a file the corpus scripts write and no chapter teaches, so `fences/post-series.md` is its home for the reason the appendix exists. Still diff the dumped state against the tree with `diff` and `cat -A` before writing, because whitespace is the one difference a `@@` hunk cannot always express.
  **AND THE TASK HAD THIS EXACTLY BACKWARDS UNTIL ANALYSIS PASS 6 RAN IT.** It read *"2 differing lines … the one target in the phase whose repair might not exist"*, because `differs at line 0` with `<eof>` on both sides reads like no difference at all. It is `findIndex` returning −1 — **the signature of a chain state that is a prefix of the tree** — and it is the only one of the 25 that prints it. **A message that reads like "nothing to see" cost this target its diagnosis**, which is 047's *"a check that cannot fail for the reason you care about"* in the reporting rather than the checking.
- [ ] T084 [US1] Re-measure after each file and record the total, APPLY, HEAD and `MIRROR` with the file that preceded each number, and the command that generated its hunk (FR-003, FR-011, SC-004, SC-009). A file that raises the count is reverted or finished before the next is started (FR-004).
- [ ] T084a [US3] **Read the prose beside every hunk this phase appended in a chapter** and confirm it still describes the listing; record the count of chapters read (SC-007). Hunks that landed in `fences/post-series.md` are exempt by construction — the appendix exists so that a change no chapter teaches is not put in front of a reader, which is the checker's own header comment and the reason FR-007 prefers it. **So record the split: how many of the 25 went to the appendix and how many into a chapter**, because the second number is the only part of this phase a reader sees.
- [ ] T085 Run `pnpm build`; commit phase 6.

**Checkpoint**: every titled fence in the series replays onto the repository, and every hunk that landed in a chapter rather than the appendix has been read beside its prose.

---

## Phase 7: Zero, and what zero does not mean (US2)

**Goal**: FR-001 — the count is 0 and the run exits 0, with the checker unchanged in what it accepts.

- [ ] T086 [US2] Run `pnpm check:fences` on a clean tree and confirm **0 problems** (SC-001), recorded beside T001's opening. **Assert the success LINE, not the exit code**: `check-fence-chain: N fenced files replay onto relay-platform across M chapters (…)`, with the line expected whole: **283 fenced files across 52 chapters (46 translated, 2 retired, plus post-series amendments)**.
  **NOT "N equal to the dump's count", WHICH IS A TAUTOLOGY.** The dump writes one file per entry in `en.state` and the success line prints `en.state.size`; both come from the same map in the same run, so the comparison can only fail on a filesystem error. **283 is derived from the work instead**: 285 at T012, **minus 11** for phase 3's declarations, **plus 9** for phase 5's introductions — measured, **0 of those 9 files are in `en.state` today**, because a path whose only fences are failing diffs never enters it. Adjust by whatever T056 converts, and record the adjustment rather than the adjusted number alone.
  **AND 52 IS NOT 47.** `app/(en)` holds a **`part-0` of five chapters** that no artifact in this feature mentions and that carries **zero titled fences** in either locale, so the success line counts five pages that verify nothing — 46 translated for the same reason, and `2 retired` from the two `(deleted)` titles. Probed from a correctly-sited copy of the checker: `en.state=285 en.chapters=52 en.deleted=2 · vi.state=276 vi.chapters=46`.
  **Exit 0 is not evidence the checker looked.** `scripts/check-fence-chain.sh:10-13` prints `relay-platform not found — skipping` and **exits 0** when the platform repository is absent, so a standalone clone satisfies "0 problems, exit 0" having replayed nothing. That is feature 045's own lesson (045-81) arriving in this feature's own success criterion, and the success line is the only output that distinguishes the two zeroes. Record the line verbatim.
- [ ] T087 [US2] **Plant a regression and run it red** (SC-003): change one line in a fenced platform file with no chapter hunk, confirm the run exits non-zero and names that file, then restore. Run red rather than reasoned about — the same probe chapter 4.9 used on the reconciler.
- [ ] T088 [US2] Confirm `MIRROR` is 0 (SC-004) and that the four classes are each 0 (SC-005), reported separately rather than as one total. **`MIRROR` at 0 is the only reading of it that means what it says** — see T006: at any other value, the chapters it names had no body comparison at all, so the number is a count of chapters skipped rather than of fences wrong.
- [ ] T089 [US2] Confirm no file under `relay-platform/` was edited by this feature: `git diff --stat part4-ch9` in that repository is empty (SC-010). **A requirement, not an observation** — the cheapest repair for 25 of the 110 would have been to edit the platform.
- [ ] T090 [US2] Re-measure the unread-fence population (SC-008) and confirm untitled is unchanged at 360 and declared `(excerpt)` has risen from **222 to 244, plus two per fence-pair T056 recorded** — **22** from phase 3, because the eleven prose titles are eleven English fences and eleven Vietnamese ones, and phase 3 declares both. **An assertion of "exactly 11" would fail for T056's reason rather than its own**, which is the defect class this project keeps finding. Nothing that names a real file may have become unverified **without a recorded exception**.
  **AND THIS TASK HELD THE ERROR IT WAS WRITTEN TO PREVENT.** It read *"233 … 11 from phase 3"* until analysis pass 5 counted the fences: the eleven titles occur **exactly twice each, once per locale**, 22 in all. Every repair task in this feature carries *"EVERY REPAIR IN THIS PHASE IS A LOCALE PAIR"*; **the counting tasks did not**, and the same omission is why pass 4 found the dump reading `en.state` for both chains. **A feature's own rule has to reach the tasks that measure, not only the tasks that edit.**
  **Report `(excerpt)` and `NOT_A_FILE` separately** — 244 and 246 at the close, the two apart being the `.naive.` pair, which nothing in this feature touches.
- [ ] T091 [US2] Confirm the count never exceeded 110 at any measured point (SC-006), from `baseline.txt`'s per-target record. If it did, the excursion is reported with the file that caused it and the number it reached.
  **And confirm every FR-012 exception was converted, not only recorded** — each one appears in `gaps.md` **and** as a declared `(excerpt)` in T090's population. An exception that exists only in prose is a problem the checker is still counting, so FR-001's zero and FR-012's escape hatch can only both hold if the two lists agree. Report the count of exceptions and check it from both sides.
- [ ] T092 [US2] Run every other gate in the tutorial job: `pnpm lint`, `pnpm build`, `check:docs`, `check:srs`, `check:figures`, `check:errors`. **Build `relay-platform` first** — `check:errors` reads the built `dist`.
- [ ] T093 Commit phase 7.

**Checkpoint**: the gate can go red for its own reason, and has been shown doing it.

---

## Phase 8: The record

**Goal**: what was repaired, what was declared, what was recorded as unrepairable, and what zero does not claim.

- [ ] T094 Write **ADR-29** in `docs/05-sad.md` and `docs/06-adr-deep-dives.md`: the `--dump` flag and the `(excerpt)` declarations as one decision about what a fence claims, with the rejected alternatives — teaching the checker that `lang=text` is never a file, retitling to the real path, removing the titles — and a reversal condition. Constitution VII, and the plan flagged it as owed.
- [ ] T095 Write `specs/055-fence-chain-repair/gaps.md`. **Re-measure the carried items this feature touches** rather than copying them: 043-1 (untitled fences, re-measured at 360 of 2,109), 047-1 (`eslint.config.mjs` could not take a fence), 048-3 (`vitest.coverage.config.mts` diverged at line 29), 050-3 (the vi chain is never compared to the tree — **carry the measurement, not the sentence**: the appendix loop mutates `en.state` only and `const vi = replay("vi", …)` runs at `check-fence-chain.mjs:300`, after both the appendix and the HEAD comparison, so the two chains' end states differ by **9 paths** and `turbo.json` ends at **en 75 · vi 62**. That is the mechanism the entry describes in prose, and this feature can state it in numbers because phase 2 built the instrument that reads it), 050-4 (the 11 prose titles), 054-1 (the red workflow, closed by this feature).
- [ ] T096 In `gaps.md`, record **what zero does not mean**: not that the chapters are readable, not that the listings are pedagogically right, not that the 360 untitled fences mean anything. One property — every titled fence replays onto the repository.
  **And that the success line's chapter count is pages on disk, not pages checked.** It reads 52 where `part-0`'s five carry no titled fence at all, so "across 52 chapters" is a claim about what the walker found, not about what was verified. The number that means something is the 283.
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
    T042a, T055, T084a        each follows its own phase's repairs — SC-007's three read-throughs
    T101     ─────► T102      (SC-002 is only observable after a push)

**US1 is delivered incrementally and US2 is not.** Each repaired target is a listing a reader can
trust, so phases 3 through 6 each deliver value on their own. The build's colour changes only at
0 — at one problem the step is as red as at 110 — so US2 is a single step at the end rather than
a slice.

**US3 IS A CONSTRAINT ON PHASES 4, 5 AND 6, AND THIS PARAGRAPH SAID PHASE 5 ALONE.** Every phase
that edits a chapter can improve the checker's number and make the chapter worse: phase 4
regenerates 42 listings, phase 5 publishes up to 1,956 lines of new ones, phase 6 appends into a
chapter wherever the appendix is not the honest home. **Three tasks have reading as their test —
T042a, T055 and T084a** — and the count of chapters read is recorded in each, because SC-007 says
*every* repaired chapter and a criterion checked in one of three phases is checked nowhere the
other two matter.

**Phase 5 is still where the judgement is**, which is why T044 blocks nine tasks and the other two
read-throughs block nothing: a regenerated or appended hunk can be shown to be wrong for the
reader, while a missing introduction has to be *placed*, and no measurement settles where.

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
