**CHAPTER 3.22 IS CLOSED**, tagged `part3-ch22` in all three repositories. Its record is
`specs/040-chapter-3-22/` — `chapter-notes.md` first, then `gaps.md` (**eight items**, each
with an owner and each reference carrying its chapter), then `traceability.md` and
`baseline.txt`.

    3.22 "the sixth connection, and where the count lives"
                                            2,914 words, 12 fenced, 4 figures
                                            14 platform files, 40 new tests
    17 of 20 battery runs green · mean 228.65 s, stdev 0.64, budget 240 — 11.35 s spare
    45 files, 748 tests · coverage 95 files / 1,213 tests / 448.31 s, exit 0
    connections.ts 100/100/100/100 · 237 fenced files, 39 chapters, 39 translated

**ALL THREE BATTERY FAILURES WERE OTHER CHAPTERS' FILES**, and a red run is SHORT because
turbo abandons the remaining packages — runs 1 and 17 stopped at ~104 s with the gateway
suite never running, so a red run's duration says where the failure was and not how long the
lane takes. The mean above is over the seventeen green runs.

**READING BEAT DERIVING, AND IT BEAT IT BY A DAY.** Three of this chapter's four design
decisions were already written in the tree — the refusal's shape at `session.ts:715`, the
close-code test at `codes.ts:10`, the two intervals in `presence.ts:41`. The hand-off said
the chapter's first job was a decision; the decision had been published in the document the
chapter was about to implement. **Ask the repository before deriving an answer.**

**A FALSIFICATION CAN ONLY SEE THE TESTS THAT EXIST.** Replacing `SET NX` with a
check-then-act left all sixteen tests green, and the honest-looking reading — *the ordering
is not observable, assert the invariant instead* — is a statement about the suite. Twelve
simultaneous connections tell the two apart every time: five admitted against twelve. Write
the test that could see it before concluding nothing can.

**A TASK'S PREMISE INHERITED FROM A PREDECESSOR'S RECORD AND NEVER RE-RUN** was this
chapter's single most common defect — three times. `limits.itest.ts` is fenced by chapter 13
and not 08; `sync-docs.sh` publishes **seven** documents and not eight, and its own comment
says at length why `07-tutorial-plan.md` is excluded; and `IFEQ` → `XX` turns two tests red,
not the one the task named. Every one was settled by one `grep`.

**THE LOG LINE IS THE ONLY EVIDENCE A FAIL-OPEN PATH HAS.** Delete
`connection.cap_unenforced` and eighteen of twenty integration tests stay green, including
the one that opens six connections against an unreachable registry. From outside, *accepted
with the cap unenforced* and *accepted because the user was under it* are the same event.
And an absence is not a distinction: telling the two apart needs a positive field on the
accept line (`cap_enforced`) and a connection id to join the two lines on.

**A FLAKY TEST WAS A PRODUCT DEFECT, AND ITS MESSAGE THREW THE EVIDENCE AWAY.** 2 runs in 6,
reported as `no connection.ack within 5s` — true, and true of a socket refused 4004 half a
second earlier. `releaseAll` tombstones all five places at once and the walk stepped over
every one, so a client reconnecting after a deploy was refused with a close code whose
remedy it cannot perform. **A sleep in the test would have hidden it**, and a sleep in the
unit test for the same property had been hiding it for two phases.

**A CHAPTER CAN TEACH A FILE IT IS NOT ALLOWED TO FENCE.** `eslint.config.mjs` reaches 73
lines after every chapter has run; the repository's is 472, and `DRIVER_EXEMPT_TESTS` is not
in the 73. A hunk anchored on a line the appendix has not added yet matches **zero** times.
Chapter 3.19 hit this first and wrote the rule into `fences/post-series.md`; 3.22 is the
second. **A titled fence that names no file is also a fence** — `check-fence-chain.mjs:43`
skips exactly `(excerpt)` and `.naive.`, so a ```text block titled with a description is
read as a claim about a file that does not exist.

**AND THE RATCHET REMOVED CODE FOR THE FOURTH TIME.** `connections.ts` first read
96.15/82.60/100/97.67, and three of its four uncovered arms were unreachable rather than
untested: a second "could not ask" path needing Redis to die between two commands, a
re-wrapping of outcomes that already meant the same thing, and an `instanceof Error` ternary
whose other half nothing can produce. One test for the fourth.

**CHAPTER 3.21 IS CLOSED**, tagged `part3-ch21` — fence predecessor `0ecb21f`, which is
`git rev-parse part3-ch21^{commit}` and not the tag. Record: `specs/039-chapter-3-21/`.

    3.21 "the frame nobody may send"        2,306 words, 18 fenced, 3 figures
    19 of 20 battery runs green · mean 228.63 s, stdev 0.68, budget 240

**COVERAGE CANNOT SEE AN OMISSION.** `**/main.ts` is excluded from the ratchet
(`vitest.coverage.config.mts:97`) and that is where 3.21's worst defect lived — a module
built, its `close()` awaited, never passed to `attachSessions`. The feature was inert while
1,174 coverage tests and 174 gateway integration tests were green. **Including `main.ts`
would not have caught it**: every line executed; the defect was an argument that was not
there. `packages/outsider/src/integrate.itest.ts` is the only instrument that boots the
shipped binary, and it is what found it. **A chapter that adds an argument to
`attachSessions` owes an outsider test** — and 3.22's `main.test.ts` checks that every
module is CLOSED, which is not the same check.

**VERIFY BY EXIT CODE, NEVER BY ABSENCE OF OUTPUT.** Three ways a check reads green without
running: `pnpm -s` in the wrong repo returns 254 silently; a pipeline ending in `tail` makes
`$?` read `tail` (hit again in 3.22); and `[ -z "$(git -C relay-platform status)" ]` prints
"clean" when the path does not resolve. **The nine pinned lane variables apply to
`pnpm coverage`, not just `test:integration`.**

**`.resume()` IS A THIRD WAY TO THROW THE EVIDENCE AWAY** and the most deceptive, because it
looks handled. It cost 3.21 its own battery failure — run 8, `no ack within 5s`, **zero
`"service":"gateway"` lines in the whole log**, cause undeterminable. **Five files still
discard**: `isolation`, `limits`, `public-surface` pipe and read nothing; `membership` and
`presence` use `stdio: "ignore"`. 3.22 measured the cost of fixing them — twelve regenerated
diffs across four chapters' fences — and recorded the decision not to. `gaps.md` item 6.

**A TEST'S TITLE IS NOT CHECKED AGAINST ITS ASSERTION.** 3.21's late pass found four of its
own; 3.22 found three more, all in the same direction — *"is a no-op"* and *"releases
nothing"* describe the keys while `resolves.toBeUndefined()` describes the promise, and one
title carried a task id that will outlive the task. Grep the titles for a requirement id and
read the assertion under each.

**CHAPTER 3.20 IS CLOSED**, tagged `part3-ch20`, record in `specs/038-chapter-3-20/`.

    3.20 "the membership that changed under a live socket"   2,999 words, 27 fenced
    two twenty-run batteries: 17/20 and 16/20 green

**FORTY RUNS, SEVEN FAILURES — AND "TWENTY GREEN" WOULD HAVE BEEN LUCK.** The observed
per-run failure rate is **17.5%**, which twenty green runs reject at 95% confidence. Two
mechanisms, neither in that chapter's code: the rate limiter's fixed window is aligned to the
wall clock, and a gateway api fixture that never answers `/health`. **The reason four are
still open is that the evidence is thrown away.**

**TWO TASKS SPECIFIED AN ORDERING AS THE REQUIREMENT AND NEITHER WAS OBSERVABLE.** A task
claiming "the ordering is the requirement" is claiming an observable difference, and that
claim needs falsifying before the test is written — **and 3.22 added the other half: the
falsification is only as good as the tests that exist to run it against.**

**A PUBLISHED SENTENCE STOPPED BEING TRUE AND NO CHECKER COULD SEE IT.** Found by grepping
for a **claim** rather than a symbol. `git diff` finds a changed sentence; nothing finds one
that stopped being true because the code moved underneath it. 3.22 corrected three such
claims in two published chapters.

**A ROUTE CAN BE THOROUGHLY TESTED AND COMPLETELY UNCOVERED.** `GET /internal/memberships`
had five integration tests and read **28.57% statements, 0% branches** — that suite runs in
the gateway package and the api's coverage is measured in the api package.

**I DISTURBED MY OWN MEASUREMENT.** 3.20's first battery counted 700 tests in run 1 and 701
in the rest, because a test was written into a file while it was running. Nothing else runs
on the machine, and that includes your own tooling.

## THE TWO FILE COUNTS ARE A PRACTICE, AND 3.22 NEEDED THREE

    10   what the chapter teaches      -> drove the word estimate
    11   what the chapter must fence   -> drove the chain
    13   files changed, re-derived from `git diff` at the end (14 after the pin)

The three differ for reasons worth stating: two changed files are `(excerpt)`-only, so their
edits are free at the chain **and unverified by it**; one is fenced and barely taught.
`git diff --name-only` against `check:fences` at the very end is what settles it.

**But the word RATE is not an estimator, and neither is the per-argument rate.** 3.15 and
3.16 agreed on 153.5 and 154.3 words per taught file; 3.17 came in at 84.7. Estimating from
*arguments* instead, 3.21 wrote 436 words each and 3.22 wrote 583 — because three of 3.22's
five argue against something already published, and disagreeing costs more than deciding.

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository a question with a yes-or-no answer.** Does this verb have a handler?
   Which chapter fences this file? How many documents does `sync-docs.sh` publish? What did
   `git diff` actually change?
2. **Read the clauses, not the identifiers.** Enumerating ids answers *is this number free*;
   it never answers *does a clause already say this*. `check:srs` says in its own comment
   that it does not read meaning.
3. **Check a task's premise before executing it, and run the command a task tells someone to
   run, in the pass that writes it.** A generalisation needs its own verification step.

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

Write the class list explicitly and make the checker **fail on an unknown member**. Then test
it red, three ways. `check:figures`'s first version reported 122 problems in 193 figures, all
false; a checker that cries wolf on a healthy tree is how a real problem hides — and 3.22's
`check-refs.py` did exactly that for the second time, rejecting a correctly-qualified
citation split across a line wrap.

- **The derived target list fails on the build that adds a route** — still the single
  highest-yield check in the repository.
- **`codes.test.ts` asserts the exact close-code set and the exact code count**, which is
  what makes a new code a decision rather than an accident. 3.22's one new code moved **four**
  pinned places in that file; the task that specified it found two.
- **`check:errors` reads `packages/protocol/dist/codes.js`** — the BUILT artifact. Build
  before believing it.
- **No checker reads prose.**

## TESTS THAT PASS WHILE PROVING NOTHING

Ask, of every test on a failure path: **what would have to be false for this to fail?**

- **A repository test proves a check exists; only a route test proves it fires.**
- **A test can pass with half its subject applied.**
- **Removing a check can come back green** if an earlier phase *replaced* rather than nested.
- **A green package is not evidence a race is fixed** — 3.7 demoted its own criterion in
  writing and moved the proof to tests that force the race.
- **An unbounded wait turns a red test into a forty-second one.** 3.22 measured 40,192 ms
  and 40,172 ms on a lane with eleven seconds of headroom; both became a one-line diff.
  `Promise.race` is the wrong fix — the loser's rejection has nobody waiting on it.

## MEASUREMENTS WORTH NOT RE-TAKING

**The test lane is the instrument closest to hand and the least representative thing here.**

    ordering by max(messages.created_at)     0.87 ms on the lane   159 ms at 1,000,000
    an indexed channels.last_activity_at     1.1 ms                145x apart
    the listing's plan, by memberships       the FIRST page is the most expensive (keyset)
    the lane's largest membership set        FIVE channels — it cannot see any of this

**The lane costs per SUITE, not per test** — `--concurrency=1`, so cost scales with api
boots. 240 s budget.

**Twenty green rejects a per-run failure rate above 13.91% at 95% confidence and nothing
finer.** A 5% flake survives it 35.85% of the time; rejecting one needs 59 runs.

## THE FENCE CHAIN

1. **Three lines of context suffice when uniqueness is CHECKED.**
2. **The predecessor is a commit, not a tag.**
3. **A chapter cannot do the appendix's work, and vice versa.** The target is *HEAD with the
   appendix's edits undone* — and **generate against the working tree, not `HEAD`**, or a
   fence shows a line the repository no longer has.
4. **A `diff` hunk says A way to get from one file to another, not THE way.**
5. **An appendix hunk anchored on a file's last line forbids any chapter from appending.**
6. **A diff body inside a ```ts fence is read as a whole file.**
7. **An excerpt-only file is never verified against the repository at all** — now two files,
   `limits.itest.ts` and `session.itest.ts`. `gaps.md` item 3.
8. **A file whose chain lives entirely in the appendix cannot be fenced by a chapter.**

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown
and a JSX expression in MDX.

## THE CHAPTER CYCLE THIS PROJECT USES

`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` (repeatedly) ->
`/speckit-implement` (once per phase). 3.22 ran **fifteen** analyze passes, 3.17 sixteen for
20 CRITICALs. **Do not stop on falling yield** — 3.16's pass 12 recommended stopping and
passes 13, 14 and 15 each found a CRITICAL.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**A phase that adds raw SQL must run the suite that executes it.**
**Pin the lane environment where the tasks can see it** (`baseline.txt`).
**Nothing else runs on the machine during a timing battery.**

**USE A PERSON.** Chapters 3.14 through 3.22 have each named this gap and none has closed it.
`specs/036-chapter-3-18/reader-protocol.md`, 45 minutes, six questions. Every check in this
repository compares bytes. **An instrument that is easy to run tells you what it measures,
not what you wanted to know.**
