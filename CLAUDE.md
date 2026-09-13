**FEATURE 045 IS CLOSED.** Its record is `specs/045-part-3-rework/` — `gaps.md` first
(**82 entries; 74 through 82 are the lane rework**), then `baseline.txt`, `carry-log.md`,
`traceability.md` and `tasks.md`. 044's is `specs/044-revision-watermark/`, 043's is
`specs/043-fix-review-findings/`.

**PART 3 IS 26 CHAPTERS, REGROUPED INTO EIGHT CONTIGUOUS SUBJECT MOVEMENTS AND RENUMBERED.**
**Twenty-one of the twenty-six numbers mean a different chapter than they did**, and four
numbers exist before and after pointing at different content — so **name a chapter, never
number it**. `specs/045-part-3-rework/chapter-map.json` is the one record; the mapping page
`relay-tutorial/app/(en)/part-3/whats-moved` publishes it and carries the fresh-start
database instruction. Everything deferred is still Part 4's: hosted media
(`media_not_available`) is 4.5 and 4.6, the queryable attempt log is 4.2, FR-MOD-03's audit
log is 4.7.

**THE REBUILT CHAIN IS `main` NOW.** 228 commits replaced by 230, diverging at the end of
Part 2; the old history is tagged `backup/pre-main-move-20260911` in all three repositories.
One annotated tag per chapter (`rework/part3-chN`, unpadded) with `rework/base-convention` as
chapter 1's base — **not `rework/part3-base`, which does not exist and which a gate silently
passed on twenty-six times**. `pnpm check:fences` runs for real against it and reports **109**,
the number the patched checker reported throughout the rebuild.

**AND IT IS PUSHED.** `relay-platform`'s `main` was force-pushed over 227 commits of published
history; the replaced history is preserved on the remote as the tag
`backup/pre-main-move-20260911` in all three repositories, alongside the 27 `rework/*` chapter
tags. **Anyone holding an older clone of `relay-platform` must reset rather than pull.**

<!-- SPECKIT START -->
**ACTIVE: 046 — CHAPTER 4.1, "the question the counters can't answer".** Plan:
`specs/046-chapter-4-1/plan.md`. Part 4 is **24 chapters in seven movements**, renamed
**"Everywhere the data went"**; the structure record is `docs/12-part-4-structure.md` and it is
newer than `docs/07-tutorial-plan.md` wherever they disagree.

**THE PLANNED CHAPTER COULD NOT BE WRITTEN.** `docs/07` said *"run the metering query against
Postgres under write load"* and **there is no metering query** — `quotas/credit.ts` is two pure
functions and the module holds no aggregate at all. The real premise is a shape mismatch:
`messages` carries no `environment_id` and nothing indexes `created_at`, so FR-ANL-05's daily
question is a join and a scan, against a ClickHouse table ordered by exactly those two columns.
**The chapter's argument is not that the query is slow — it is that the index which fixes it
taxes every write for a question no write asks.**

**TWO RESEARCH ASSUMPTIONS WERE WRONG AND BOTH ARE KEPT IN `research.md`.** The bot exemption
was searched for in `quotas/` and `messages/` and lives in `repository.ts:assertWithinQuota` —
`docs/10` §0 had already run that exact check, and reading it would have been cheaper than four
greps. And "write load" is capped at **ten sends per second** by `DEFAULT_LIMITS.send`, so the
chapter measures **latency, not throughput**, and says so.

**THE CHAPTER SHIPS NO PRODUCT CODE.** Three scripts in `scripts/scale/` and four numbers. The
counterfactual column and index are applied to a throwaway copy and **must never become a
migration** (045-69). Two gates Part 4 needs before its first split — a standing `check:redirects`
and a gate refusing chapter ordinals in platform source — do not exist; all six Python
instruments live in `specs/045-part-3-rework/` and are wired to nothing.

**AND THE CHAPTER CANNOT BE TAGGED YET.** `part3-ch18` (`54b2cd53`) and `rework/part3-ch18`
(`3732d6cf`) both exist and resolve to different commits, so a reader following a published SKIP
AHEAD box lands on the wrong chapter. Deciding Part 4's tag convention is not this chapter's work
and blocks only tagging, not authoring.
<!-- SPECKIT END -->

    045 "part 3 rework"           24 chapters -> 26, eight movements, English prose only
                                  296 -> 110 fence-chain problems · 26 of 26 tags typecheck
    SC-007  403.76 s -> 232.05 s, 20 of 20 green, stdev 0.51, cv 0.22%
            inside the 202.91-248.00 s window it had been failing at +79%
    peak memory 5,180 MB mean · 913 tests and 0 leaked processes every run

**WHAT IT COST TO MAKE THE LANE FAST, AND WHERE THE TIME ACTUALLY WAS.** `fileParallelism:
false` had been serialising the api and gateway lanes since the outbox chapter, for a real
error — two suites issuing `CREATE TYPE` against one schema. **The reason died eight chapters
later** when `globalSetup` began migrating once before any file starts, and the setting
stayed, justified in a comment written in the very chapter that closed the race.

**EIGHT PLACES HELD THE LANES APART, THE ESTIMATE SAID THREE, AND THREE OF THE EIGHT ARE NOT
ASSERTIONS AT ALL** — a fixture planting rows no broker will accept, two forged frames a
required field three chapters later invalidated, and a count that could never have failed for
its own reason. Six were found one failure at a time over six runs; **the last two came from
asking the tree in one pass**, which is `check-lane-scope.py`. When a count keeps growing,
stop counting failures and go ask the repository.

**AND THE WORKER COUNT IS A BILL, NOT A SETTING.** Vitest defaults to about one worker per
core — here eighteen NestJS apps against one Postgres, which killed two battery attempts
before anything was measured. Every second of the api lane's saving is in **one worker to
two** (177 s -> 102 s for 87 MB); a ninth buys nothing and costs 1.2 GB. The gateway's knee is
**four**, not two. **The right worker count is per-lane and measured; a default is a number
about the machine, chosen by something that has never seen the workload.**

    044 "the revision watermark"  one column, `channels.revision_sequence`, raised inside the
                                  transaction that edits or deletes, never by a send
    reported on every `connection.ack` as `revisions: {channel_id: count}`, zeros included
    **the platform reports and never compares**
    mean 225.45 s, stdev 1.15 · SC-004 -2.33% · SC-005 edit +2.75% delete +2.99% · both MET

**044'S REVERSAL IS THE LESSON THAT OUTLIVED IT.** A draft had the client present its counts
on the upgrade URL. It was built, then removed. **A parameter the server parses and never acts
on is a contract it can never remove**; one it acts on hands the client a number the platform
decides with, which is how a fabricated count becomes a denial of service the client controls.
Removing it also deleted three edge cases rather than handling them — **a design in which a
case cannot arise beats a branch that handles it**, because the branch is the thing that rots.

## AN INSTRUMENT THAT REPORTS ZERO HAS TO PROVE IT LOOKED

Four lies in two features, each in a different way, and the rule is the same every time:
**a zero from an instrument is a claim about the corpus only if the instrument can be shown
to have read it.**

**`grep` ON THIS MACHINE IS ugrep 7.8.4, NOT GNU grep** (`/usr/bin/grep` is GNU 3.12; PATH
resolves elsewhere). A grouped alternation followed by two negated classes matches nothing
under it and matches under GNU — `(postgres|redis)://[^:/@]+:[^@/]+@` gives ugrep 0, GNU 1,
over a corpus holding the string twice. **Give every pattern a positive control**, and report
a pattern that fails its own example as BROKEN rather than as zero. One shipped gate uses the
construct (`check-srs-ids.sh:49`); it agrees under both engines.

**A PER-FILE COVERAGE THRESHOLD WHOSE KEY MATCHES NO FILE IS SILENT.** Demanding 101% of
`this-file-does-not-exist.ts` produces no error, no warning, nothing. **Run both halves of
that probe every time the ratchet is re-pinned.**

**A CHECKER HANDED A REF THAT DOES NOT RESOLVE COMPARED NOTHING AND EXITED 0** — twenty-six
times, printing `12 fences, 0 compared, 0 problem(s)`. **The zero that means "clean" and the
zero that means "never looked" printed the same line**, and four real problems sat behind it.
A checker must refuse its arguments rather than trust them, and refuse a run that compares
nothing (045-81).

**AND A TEST WRITTEN BY THE AUDIT THAT FINDS VACUOUS TESTS WAS VACUOUS.** It passed
identically with the counter moved outside the transaction, because the path refuses earlier
and the bump never runs. **Ask what would have to be false for this to fail, and then read the
code it calls**, not the test.

## COVERAGE IS NOT REPRODUCIBLE RUN TO RUN, AND THE RATCHET HAS TO ALLOW FOR IT

`session.ts` functions measured **87.80%** and **85.36%** on identical code twenty minutes
apart — about one function of forty — while every other pinned file was byte-identical across
both runs. A floor at the measured value goes red for no change to the code, and the fix is
then to lower it: **a ratchet that teaches people to lower ratchets.** Pin below the lower
observation by the observed swing and put both numbers in the config.

**AND A p50 IS NOT AUTOMATICALLY THE ROBUST STATISTIC.** Six runs a side: edit mean cv 12.9%,
edit p50 **17.3%**; delete mean 13.5%, p50 **20.6%**. **p50 was noisier on both paths** — a
median of 200 samples with a long tail wanders inside a crowded middle while the mean is
anchored by the whole sample. Resolving a 10% shift at that variance needs ~26 runs per side;
the criterion was kept with its resolution limit recorded rather than adjusted to fit.

## READ THE CLAUSES, NOT THE IDENTIFIERS — AND THEN RUN THE TASK

**FOUR DOCUMENTS AGREED ON TWO CLAUSES THAT DO NOT EXIST.** Spec, plan, tasks and quickstart all
said 044 would amend "SRS FR-016a and FR-016b" — chapter ids, absent from `docs/04-srs.md`.
Three analysis passes saw agreement because the artifacts agreed with EACH OTHER and not with
the tree. What found it was **opening the SRS to make the edit**, and reading the clauses gave
**three** to amend where the requirement named two. 045 hit the same shape from the other side:
a sweep passed `rework/part3-base` twenty-six times and there is no such tag.

## THE ONE THAT KEEPS EARNING ITS PLACE

**AN ARGUMENT THAT IS RIGHT ABOUT THE PRODUCER CAN INVERT ABOUT THE READER.** Making
`messageSchema.attachments` required is correct for a schema the platform BUILDS — required is
what makes the compiler name every construction site. The same sentence carried into
`outboxEventSchema`, which READS off a durable queue, answered every in-flight `message.created`
written by the previous binary with `message.term()`. **043 was told to do it again by a task
citing a line number, and did not.**

**Required is a claim about what you write. A reader of anything durable cannot require a field
its writer did not have.** 045 paid the test-side of this: adding a required `revisions` to the
ack invalidated two forged sample frames three chapters away, and the tests asserting the wrong
refusal stayed green.

## MEASURE THE CARRIED LEDGER; DO NOT COPY IT — AND THAT GOES FOR COMMITS

Four of 043's twenty-three carried items were wrong when re-measured, and **three closed with
nobody working on them**. 044 re-measured all twenty-eight and closed none DURING the feature,
said plainly rather than implied by a short list; two were then closed afterwards as work of
their own. **A lookalike nearly closed one** — a test file asserting the right shape about the
wrong pair of lists. **Read the assertion, not the filename.** And that item's own premise was
wrong: there was no second list, and the real defect was sharper than the one filed, because
the linter checked one direction only.

**045 CARRIED COMMITS RATHER THAN ITEMS, AND THE FAILURE MODE IS THE SAME ONE LEVEL DOWN.**
Twenty-four commits from two closed features. Four of the first rows were decided wrong, in
opposite directions, for one reason: **a commit was classified by one of the things it does.**
One did two things and was skipped for the half already present — its subject named both
halves. One was accepted as complete because its file count was right.

**THE `test(` / `fix(` PAIRING IS THE SPECIFIC TRAP, AND IT CAUGHT THIS PROJECT THREE TIMES IN
ONE CARRY.** A tombstone test, a race test and a teardown assertion were each taken without the
`fix(` commit they were written to prove, and every time the symptom was a suite that failed
some or all of the time and read as flaky. **A red test is the visible half, so it gets carried
first and alone.** Before taking a `test(` commit, find the fix it exists to demonstrate.

**AND FOUR OF SIX SKIPS WERE RIGHT FOR A BETTER REASON THAN EXPECTED** — the work was already
in the chain, arrived at independently, and in three cases in a STRONGER form: the lane reset
plants the row it asserts on, the port map is deleted rather than extended, the exemption list
is read from the rule rather than restated. **Cherry-picking blindly would have downgraded the
chain in every one of those three.**

**A TASK ID IN A TEST TITLE OUTLIVES THE TASK, AND A TITLE IS THE PART READ DETACHED FROM ITS
FILE** — a CI summary has no repository to grep. Seven are gone; two could not be removed alone,
one having a comment fifty lines away pointing AT the title by its id, one printing to stdout.
Ids anywhere in test files still number **330 across 46 files**, filed rather than swept.

## TWO CLOSED STORIES, KEPT FOR THEIR RULES

**A HAND-MAINTAINED TABLE CANNOT BE CHECKED.** Nine api ports came from hand-allocated bands
across eight files, and **two bands contained a service the lane itself runs** — 5432 inside
`membership`'s range, 4222 inside `limits`'. The failure is silent both ways: the child cannot
bind, and the health check gets its answer from whatever *does* hold the port. All nine now use
`PORT=0` with the port read from the child's own log line, and the map is **deleted rather than
corrected**.

**A TEST OF A SCRIPT MUST ASSERT WHAT THE SCRIPT DID, NOT WHAT THE TABLE HOLDS.** `reset-lane`
counted rows "due now", which a run that just finished violates legitimately, and counted
staleness against a `now()` re-evaluated ~115 ms after the script's own. **Pin one instant
before the script runs** — the same pin 045 needed to keep that suite's whole-table count honest
under a lane that no longer serialises.

## OTHER THINGS 043 PAID FOR

**A RED PROBE WRITES TO THE LANE.** Reverting the avatar rule to check the tests could see its
absence left two `javascript:alert(1)` rows stored, accepted with a 200 — and the next
measurement read them as pre-existing data contradicting the plan. **Clean up a probe before
anything is counted.**

**AN ASSERTION SCOPED WIDER THAN THE THING IT TESTS FAILS FOR SOMEBODY ELSE'S REASON.** 043
found two — a whole-table `outbox` count and a wall-clock minute bucket — and **the first fix
was worse than the fault**, sleeping to the next boundary and blowing the test's timeout. 045
found six more and made the class checkable; see the lane section below.

**WHEN MEASUREMENT FALSIFIES A CLAUSE, AMEND IT.** Done three times: FR-RTM-09 and FR-RTM-10 in
the SRS (revision 1.8), and **043's own FR-016**, which would have refused 838 stored
subscriptions to a declared, published, unbuilt event type. The governance clause requires
amendment rather than silent divergence, and that applies to a feature's own specification.

**A PLAN COUNTS THE FIX AND NOT THE VERIFICATION.** 17 files estimated, 58 changed, and every
unplanned one came from RUNNING something rather than reading it. 045 said three and found
eight, the same way. **The error is in one direction, every time.**

## THE LANE, AND WHAT IT STILL CANNOT TELL YOU

**The test lane is the instrument closest to hand and the least representative thing here.**
Ordering by `max(messages.created_at)` costs 0.87 ms on the lane and 159 ms at a million
rows — 145x from an indexed column — and the lane's largest membership set is FIVE channels,
so it cannot see any of that.

**IT NO LONGER COSTS PER SUITE.** The api lane runs two files at a time and the gateway four,
both bounds measured rather than inherited (045-79); `vitest.coverage.config.mts` and the e2e
lane still serialise. That changes what a duration means: a suite's own time is now overlapped
with a neighbour's, so **a slower suite does not always show up in the total**, and the lane is
correspondingly less useful as a per-suite stopwatch than it was.

**AND IT MAKES EVERY WHOLE-TABLE ASSERTION A NEIGHBOUR'S PROBLEM.** Eight of them were found
this way (045-74). `check-lane-scope.py` asks the question directly — which queries read a
shared table without a predicate naming this test's own rows — and reports zero. **Run it after
adding an integration test**, because the alternative is finding out once, in the fifteenth run
of a battery.

**BATTERIES ARE COMPARABLE NOW, AND THE PAIRS SAY SO.** 043 and 044 came in 0.10 s apart on a
240 s budget. 045 measured its own lane either side of one change, twenty runs a side:
**403.76 s -> 232.05 s, stdev 0.50 and 0.51, cv 0.22% both.** The old rule was "no two batteries
are comparable"; the rule now is **"two batteries are comparable once the lane stops colliding
with itself, and you find out by measuring, not by assuming either way."** 3.23's 228.80 s and
3.24's 233.08 s are still not comparable to anything.

**A FLAKE DOES NOT SHOW UP IN THE DISTRIBUTION.** cv 0.22% across twenty runs, and one of them
red — a frame that had not arrived, not a slow run. **Twenty runs is a sample of the lane's
timing and a very thin sample of its failure modes**; three green runs is weaker still, and
045 offered exactly that as evidence before the fourth run falsified it.

**Postgres rows still accumulate and `reset-lane.mjs` does not touch them by design** — it
purges lane debris, not data. Measured at 045's close-out: **31,215 environments, 481,251
outbox rows (5,253 pending), 300,719 messages, 45,567 channels.** Record the row counts beside
any close-out timing, because they are part of the instrument.

**A FILE AT 100% BRANCHES IS NOT A FILE WHOSE EVERY ARM HAS RUN.** v8 records a `binary-expr`
arm as covered when the operand was EVALUATED, not when it went both ways. Constitution VI's
100%-branch clause is stated in that number.

**AN ARGUMENT COSTS 545 WORDS IF IT IS MADE OF PROSE AND ABOUT 280 IF IT IS MADE OF
ARTIFACTS.** Say which kind each argument is when the estimate is written.

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository — or the broker, or the database — a question with a yes-or-no
   answer.** `curl localhost:8222/jsz?consumers=1` answered in one command what two hypotheses
   could not. 043's decisive numbers were all queries. **045's were too, and one of them ended a
   hunt**: `3,200 pending outbox rows in 16 subjects are unroutable, every one of them a test
   fixture's bait, and nothing else in the backlog is` — which explained two failures of
   different shapes at once, `NatsError: 503` and `expected 41 to be 700`.
2. **Read the clauses, not the identifiers.**
3. **Check a task's premise before executing it**, and run the command a task tells someone to
   run. 043 found four tasks whose premise was wrong, including one that would have caused a
   defect.

**AND WHEN A MECHANISM IS PROPOSED, FORCE IT — BUT FORCE IT UNDER THE CONDITION IT FAILED IN.**
Eight gateway-suite runs at 35 s found two flakes in five minutes that a 78-minute battery found
once. **The same trick then failed**: a flake from a twenty-run battery would not reproduce in
eight runs of that lane alone, because it needs the api lane loading the machine beside it.
Amplifying the wrong variable proves nothing; **8 of 8 green was not evidence the flake was
gone, and reading it that way would have closed the item.** Raising the worker count until the
failure returned is what gave a probe to fix against.

**AND A SWEEP BEATS A BATTERY FOR FINDING A CLASS.** Six instances of one fault were found one
failure at a time across six runs; the last two came from one pass of an instrument that asked
the tree directly. **When the count of a class keeps growing, stop counting failures.**

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

Write the class list explicitly and make the checker **fail on an unknown member**. Then test it
red, three ways — `check-revision-order.mjs` fails on a descent, an unparseable version and a
renamed heading; `check-error-codes.mjs` compares `CLOSE_CODES` in both directions;
`check-lane-scope.py` carries ten controls including two that pin its own earlier mistakes.

- **`check:errors` reads the BUILT `dist`.** Build before believing it — and before RUNNING a
  tag, because the harness spawns `dist` too.
- **A checker reports the FIRST failure per file.**
- **No checker reads prose**, and a `mermaid` block is prose.
- **A checker that cannot resolve its arguments must refuse**, not compare nothing and exit 0.
- **AN UNTITLED FENCE IS NEVER COMPARED TO ANYTHING.** `check-fence-chain.mjs:77` collects a
  fence only when it matches `title="…"`. **146 of 904 — 16% — are outside every gate**, one
  step further out than the excerpt-only class, which is at least skipped BY a title somebody
  wrote. Nobody decided this one; `gaps.md` 043-1 opens it and 045 did not close it.
- **FOURTEEN GATES, NOT ELEVEN**, and capture every exit code OUTSIDE a pipeline. `fail=1`
  inside `for … | sort` runs in a subshell and dies with it. **043 reproduced that mistake three
  times**, once in a task whose own text warns about it.
- **AND AN INSTRUMENT'S FALSE NEGATIVE IS WORSE THAN ITS FALSE POSITIVE.** `check-lane-scope`
  went through two wrong designs: one reported three correctly-scoped queries, the next MISSED a
  real one because the surrounding JavaScript happened to contain a scope word. **The first
  wastes an afternoon; the second reports a clean sweep over a file you already know is dirty.**

## TESTS THAT PASS WHILE PROVING NOTHING

Ask, of every test on a failure path: **what would have to be false for this to fail?**

- **A health check that has never passed.** `membership` and `presence` probed `/health`; this
  api serves `/healthz`. Both loops ran 100 failed probes and returned the URL anyway — a flat
  ten-second sleep reporting success. **Neither fault could surface while the other was there
  to absorb it.**
- **`webhooks.itest.ts` asserted status and message text** and passed while the body said
  `internal_error`. Only the code could have caught it, which is why it survived from 3.5.
- **A repository test proves a check exists; only a route test proves it fires.**
- **A conditional assertion is an assertion that may not run.**
- **Two 204s prove nothing.** Idempotence is about what the second call DID.
- **A title that overclaims is the same defect.** 043's audit caught two of its own: one
  claimed a derivation nothing in the body can observe, one said "every refusal" while leaving
  one asserted by status alone.
- **An assertion that can only fail for somebody else's reason.** Signup's invariant 7 counted
  every `organisations` row before and after an unauthenticated request that is refused before it
  reaches a handler — **no code path existed that could move the number**, and it moved anyway.
  Replaced by the structural claim its own comment already made and nothing was checking:
  `provisionOrganisation` has exactly one non-test importer.
- **A flat sleep before an assertion is a bet that the lane is idle.** `await settle(700)`, then
  count the frames. **Arrival is a condition and absence is not**: poll to a deadline for what
  must arrive, and keep a quiet window only for what must not — taken AFTER the arrival wait,
  never instead of it. One red in twenty full runs, in two different tests of one file.
- **And a fixture is a test too.** Drain bait planted on a subject no stream accepts, carrying no
  envelope id, broke two invariants of a suite that never mentions it. **A fixture imitating a
  thing must be usable everywhere the thing is**, or it is a landmine rather than bait.

## THE FENCE CHAIN

1. **`-U6` IS A DEFAULT, NOT A RULE.** Regenerate wider when the pre-image matches twice.
   `resume.itest.ts` carries eight session stubs byte-identical far past six lines; `-U10` made
   all nine hunks unique and **`-U8` was worse — `[1, 1, 3]`** — because widening context merges
   adjacent hunks and a merged hunk spans more repetition than either half did. **Verify the
   hunks apply clean before pasting, not after.**
1a. **GENERATE HUNKS FROM THE CHECKER'S OWN REPLAY.** Copy `check-fence-chain.mjs`, truncate it
   at the HEAD comparison, make it dump its 240-file end state, diff that against the working
   tree, delete the copy. A generator that replays differently from the checker produces hunks
   the checker rejects for reasons neither of them explains.
2. **The predecessor is a commit, not a tag.**
3. **A `diff` hunk says A way to get from one file to another, not THE way.**
4. **An appendix hunk anchored on a file's last line forbids any chapter from appending**,
   and a diff body inside a ```ts fence is read as a whole file — the appendix takes `diff`.
5. **An excerpt-only file is never verified — THIRTEEN of them**, re-measured at 044's
   close-out. A naive count says fifteen: two titles carry a prose suffix and both base files
   are chained elsewhere, so **normalise the title before comparing.** This count has been
   wrong four times out of five and every error was in parsing the title.
   `services/gateway/src/session.itest.ts` is one of the thirteen and now holds the **only**
   end-to-end proof that 044's column, api and ack are connected.
6. **Run `check:fences` after ANY source edit**, not only the ratchet.

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown
and a JSX expression in MDX.

**A FOUNDATION FENCE IS NOT A THING TO REGENERATE.** Chapter 1 fences several files as WHOLE
BODIES, and every later diff in every later chapter is anchored on those bytes. Bringing one up
to date satisfies the per-chapter checker and takes the cumulative chain from **111 problems to
203**, unanchoring ninety-two downstream hunks. Where the two checkers disagree there, the chain
is the one carrying the readers — and the change belongs in the appendix, which applies after
every chapter and is where anything no chapter can own goes (045-81).

**AND REBUILD BEFORE RUNNING A TAG, NOT ONLY BEFORE TYPECHECKING ONE.** The stale-`dist` trap has
a runtime form: the harness SPAWNS `services/api/dist`, so a `dist` built at the tip against an
older tag's database gives 38 identical `42703 column ... does not exist` errors that read like a
broken chain. It cost a wrong published conclusion before it was found (045-77).

## THE CYCLE THIS PROJECT USES

`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (repeatedly) →
`/speckit-implement` (once per phase). 3.24 ran twenty-one analyze passes, 3.23 eleven, 043
fourteen, 044 three, 045 five. **Do not stop on falling yield** — and note two things no number
of passes finds: a defect in code no lane runs, and **artifacts that agree with each other and
not with the tree**. **The pass that RUNS the premise finds the most.**

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**Pin the lane environment where the tasks can see it** (`baseline.txt`), and bring the stack up
with `RELAY_POSTGRES_PORT=15432` — this machine's own Postgres holds 5432.

**NOTHING ELSE RUNS ON THE MACHINE DURING A TIMING BATTERY, AND NOTHING TOUCHES THE REPOSITORY
EITHER** — a few hundred `git show` calls in a sibling worktree cost one run 768 seconds while
its per-suite times stayed identical, which is how you tell interference from a defect. Two 045
batteries were also killed by the host's own memory supervisor at ~20 s in, with 12 GB free;
detaching the driver is what let the twenty runs finish.

**USE A PERSON.** Chapters 3.14 onward each named this gap and 045 is the fourteenth record to
name it and not close it. **044 has the sharpest evidence for why the substitute fails**:
reading the published text with the spec and source closed found a real hole — FR-008's client
half was missing — because that exercise finds information that is ABSENT. It cannot find
information that is present and unclear, since the person running it wrote the sentence.
`specs/036-chapter-3-18/reader-protocol.md`: 45 minutes, six questions, one person who has not
read the work.

Every check in these three repositories compares bytes. Twelve Python instruments and five
`check:*` scripts — and not one can say whether a paragraph is understandable to somebody who
does not already know the answer. Each says so in its own last line:

    check-refs: ids only — this says nothing about whether the prose around them is true
    check-chapter: bytes only — it cannot say whether the PROSE describes the diff
    check-lane-scope: SQL text only — a scope applied in JavaScript is invisible to it

**An instrument that is easy to run tells you what it measures, not what you wanted to know.**
