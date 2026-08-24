<!-- SPECKIT START -->
**CHAPTERS 3.15 AND 3.16 ARE CLOSED.** One feature, two published chapters, 251 tasks,
checklist 16/16, both locales, **`pnpm check:fences` clean — 211 fenced files across 33
chapters, all 33 translated.** Its record is `specs/034-chapter-3-15/` — read
`chapter-notes.md` first (the plan against what shipped, and the phases that went badly),
then `gaps.md` (eight open things, each with an owner), `traceability.md` (58 requirements
and 12 clauses, both directions) and `baseline.txt` for every measurement.

    3.15 "the channel a customer controls"   20 files taught, 2,947 words, 20 fences
    3.16 "what a user sees"                  26 files taught, 3,800 words, 38 fences
                                             + 11 files fenced and NOT taught
    550 tests, 20/20 green, 192-197 s, mean 193.55, stdev 1.54
    coverage 920 tests, every ratchet met; repository.ts branches 89.51% -> 92.11%

## THE FILE COUNT WAS TWO COUNTS, and it took eight revisions to notice

    25  the SRS clause list
    29  the task list
    34  "which chapter fences this file?"        -> app.module.ts, in NO task, 8 routes need it
    36  writing out the send call graph
    38  counting the paths the tasks name
    40  git diff --name-only vs check:fences     -> 2 files in no bucket, 1 never touched
    41  implementation hitting a defect          -> api-client.ts, unpredictable by any count
    43  git diff again, at the end               -> THE COUNT WAS TWO COUNTS

**What a chapter TEACHES is not what it must FENCE.** Eleven files changed by exactly one word
— a corrected citation, zero substantive lines — and the chain does not care why a file changed:
a claimed path's state must equal the repository's. Eleven **fences with no subject**. Three
phases earlier T091 found the inverse: `tenant-scope.itest.ts` is a **subject with no fence**,
because the catalogue moved 22 -> 23 tables and the file did not change by one character.

**Not one revision came from re-reading the document that held the previous number.** Six came
from asking a new question, one from re-deriving an old answer, one from a defect. The word
estimate corrected by 3.15's measured 8% shortfall predicted 3,830 for 3.16 and it landed at
3,800; **the nominal rate said the chapter could not be written.**

## THE THREE MECHANISMS THAT FOUND THINGS, RANKED BY YIELD

1. **Ask the repository a question with a yes-or-no answer.** Does this verb have a handler?
   (`GET /v1/channels/:channelId` did not, and three artifacts assumed it did.) Which chapter
   fences this file? (`app.module.ts` — in no task; without it eight routes do not mount.) What
   did `git diff` actually change? (Two revisions of the count, including the one that split it.)
2. **Make an artifact more precise and watch a contradiction fall out.** Five passes of
   artifact-vs-artifact reading produced only arithmetic errors. Changing "all three verbs" to
   "all four verbs SC-001 names" put send's refusal in contact with the indistinguishability
   criterion, and two defects fell out at once.
3. **Check a task's premise before executing it.** T187a said the appendix amends `sentinel.sql`;
   it mentions it inside another file's fence and never titles it. T153 named two answers for
   what a ban does to an open socket and the answer was a third, already built. T108 asked that a
   rename not move a column and **the platform has no rename.** T124 asked to delete a message
   and **nothing writes a tombstone.** T087 asked for a subscribe frame and **the union has one
   inbound member.** Five task premises wrong, all five found by looking for the thing.

## WHAT THE INSTRUMENTS CAUGHT THAT READING DID NOT

- **The derived target list failed on the build that added each of six routes**, five separate
  times, before anyone classified them. This is the single highest-yield check in the repository.
- **`codes.test.ts` asserts the exact close-code set** and failed when 4003 was added — which is
  what made a fifth code a decision rather than an accident.
- **The coverage ratchet failed at lines 98.92% against a pin of 99, and the fix was to DELETE a
  redundant throw**, not to test it. Second time it has removed code rather than covered it
  (chapter 3.12 removed `addMember`'s `rowCount ?? 0`).
- **`check:figures` did not exist, and fifteen figures in four published chapters rendered a
  caption over nothing.** `Figure` takes `caption` and `code`; 3.11-3.14 passed `chart={…}` and
  this chapter's draft passed `src={…}`. MDX props are not type-checked, so all three build green
  and hand the diagram `undefined`. Chapter 9 emits four mermaid sources; chapter 13 emitted zero.
  Found by comparing the two locales' props. **The checker's own first version reported 122
  problems in 193 figures** — all false, because early chapters write `<Figure>` across three
  lines. A checker that cries wolf on a healthy tree is how a real problem hides.

## MEASUREMENTS WORTH NOT RE-TAKING

**The test lane is the instrument closest to hand and the least representative thing here.**

    ordering by max(messages.created_at)     0.87 ms on the lane   159 ms at 1,000,000
                                             -> Seq Scan over every message, every listing
    an indexed channels.last_activity_at     1.1 ms                145x apart
    the unread count, 50 channels @ 1M msgs  count rows 9.8-13.4   cached counter 1.2-2.1
                                             the subtraction 1.1-4.5 -> counter is NOT faster
    the listing's plan, by memberships       1k 0.46ms  5k 2.22ms  20k 10.62ms  50k 9.06ms
                                             the FIRST page is the most expensive (keyset)
                                             at 50k the planner drops the Sort and gets faster
    users vs channels on the lane            94,144 vs 27,337 = 3.4:1, why 4 KB not 8 KB
    the lane's largest membership set         FIVE channels — it cannot see any of this

**And the lane costs per SUITE, not per test.** 407 tests -> 550 moved the mean 193.0 -> 193.55 s
across twenty runs. A prediction of 230-250 s assumed cost scales with test count; it scales with
api boots, because the lane is `--concurrency=1`. 240 s budget, 43 s headroom at the worst run.

**Twenty green rejects a per-run failure rate above 13.91% at 95% confidence and nothing finer.**
A 5% flake survives it 35.85% of the time; rejecting one needs 59 runs. Chapter 3.11 ran twenty
green and an eleven-chapter-old flake surfaced on run 21.

## THE FENCE CHAIN, FIVE MORE LESSONS

1. **Three lines of context suffice when uniqueness is CHECKED.** 3.12's "eight lines" rule was a
   proxy for not being able to tell. All 19 diffs in 3.15 and all 30 in 3.16 are at three lines,
   verified by simulating what the checker does — apply each hunk to the evolving text and count
   the pre-image. No hunk needed widening.
2. **A chapter cannot do the appendix's work either.** 3.12 learned a chapter cannot amend a state
   post-series builds; this is the same rule reversed. A diff generated straight to HEAD performs
   the appendix's edit itself, and the appendix's hunk then matches **0 times**. The target for
   such a path is *HEAD with the appendix's edits undone*.
3. **A `diff` hunk says A way to get from one file to another, not THE way.** `@@ -360,0 +441,186
   @@` was read three wrong ways: the 186 lines were two blocks (61 the appendix's), `pre[:360]`
   dropped the predecessor's tail, and diff's offset was not the semantic insertion point. When a
   second tool applies its own hunks to your result, which way you chose is the whole question.
4. **An appendix hunk anchored on a file's last line forbids any chapter from appending to it.**
   `credentials.itest.ts`'s hunk ended on the outer `});`, which is exactly where a new `describe`
   must go. Re-anchor on the lines before the block.
5. **An excerpt-only file is never verified against the repository at all.** `sentinel.ts`,
   `sentinel.sql` and `guard.itest.ts` are outside the chain permanently; `sentinel.ts` grew 32
   lines here and nothing compared a character of it.

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown and
a JSX expression in MDX. `Could not parse expression with acorn`, line 3134 of a 4,400-line page.

## FIVE TASKS WHOSE TESTS PASSED WHILE PROVING NOTHING

Each was green, and each was fixed by asking what would have to be false for it to fail:

- **T126** sent a message, acknowledged it, then asserted the count was zero — proving only that
  `setReadPosition` works. The assertion that matters is the one *before* the acknowledgement, and
  the spec's assumption ("a user's own message is read by them") is **false**.
- **T086** could have recorded "nothing was masked" as a success. The finding is *why*: Phase 7
  **replaced** `channelExists` rather than adding beneath it, so there is no outer check left to
  mask an inner one. Added underneath — the obvious way — that removal comes back green.
- **T044's first attempt** changed `notFound()`, which both halves of every pair use, so both moved
  together and the oracle saw nothing.
- **The send path's repository test** passed for six analysis passes while its controller supplied
  no caller. **A repository test proves a check exists; only a route test proves it fires.**
- **T134** awaited a `message.created` frame in a suite where none has ever arrived, which is
  chapter 3.12's own recorded finding written into a test against it.

## WHAT THE NEXT FEATURE SHOULD DO DIFFERENTLY

1. **Separate the two file counts in the plan.** One column for what a chapter teaches (drives the
   word estimate) and one for what it must fence (drives the chain). Conflating them cost eight
   revisions and made a ceiling look comfortable when it was binding.
2. **Grep the claim in BOTH repositories.** The citation classification searched `relay-platform`
   and missed a 48th citation living inside a `relay-tutorial` fence body. A search scoped to one
   repository cannot find a claim about that repository written in another.
3. **Check every task's premise as its first step.** Five were wrong here, and each cost a wrong
   attempt: an operation the platform lacks, an amendment that does not exist, a refusal code that
   is the leak it warns about (T117 asked for 400, and 400 requires the lookup that distinguishes
   "exists elsewhere" from "exists nowhere").
4. **Use a person.** Chapter 3.14 named this gap; this feature has it too. Two chapters, 6,747
   prose words, and every check applied to them compares bytes. **An instrument that is easy to
   run tells you what it measures, not what you wanted to know** — which is the same sentence as
   the 145× measurement, one level up.

## THE CHAPTER CYCLE THIS PROJECT USES

`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` (repeatedly) ->
`/speckit-implement` (once per phase). This feature ran **fifteen analyze passes for 8 CRITICALs**;
3.12 ran fourteen for 6. Seven of the eight CRITICALs were the same shape: **something every
comparable case in the repository has that no task provided** — a module registration, a handler, a
credential class, a repository parameter.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice in 3.12.
**And nothing else runs on the machine during a twenty-run battery** — 3.12's attempt one failed at
run 11 to two Next.js dev servers, with no port held and no `EADDRINUSE`; the wall-clock timeline
was the only evidence that told interference from defect.
<!-- SPECKIT END -->
