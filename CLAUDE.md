**FEATURE 044 IS CLOSED.** Its record is `specs/044-revision-watermark/` — `gaps.md` first
(**28 carried and re-measured, 3 new, 2 closed AFTER the close-out**), then `baseline.txt`,
`traceability.md` and `tasks.md`. It publishes no chapter, so every platform change carries an
amendment hunk in `relay-tutorial/fences/post-series.md`.

**PART 3 IS CLOSED AND 3.24 WAS ITS LAST CHAPTER.** Everything deferred is Part 4's: hosted
media (`media_not_available`) is 4.5 and 4.6, the queryable attempt log is 4.2, FR-MOD-03's
audit log is 4.7.

<!-- SPECKIT START -->
**ACTIVE FEATURE:** `specs/045-part-3-rework/` — Part 3's 24 chapters regrouped into eight
contiguous subject movements and renumbered to 25, English prose only. Plan:
`specs/045-part-3-rework/plan.md`. **56 tasks, 8 phases, four analysis passes, one critical each.**

**EVERY CRITICAL WAS SOMETHING THE GATES DO NOT LOOK AT.** That is the whole lesson of this feature
so far, and it is in `plan.md`'s Testing section as a table because `check:fences` is almost its only
test:

    untitled fences        99 per locale — the mirror matches `title="…"` and skips them   pass 4
    anything outside a fence   133 metadata paths, an 810-line chapter registry            passes 1, 4
    the 13 excerpt-only files  99 ordinals among ten of them                               from the start
    prose                      whether a paragraph still describes the diff beneath it     from the start

**Pass 1** — `lib/tutorial.ts`, 810 hand-maintained lines declaring all 41 chapters, read by the
sitemap and six components, guarded by nothing.
**Pass 2** — the plan's own mechanism falsified: filtering the final file by line attribution gives
**52 parse errors on `repository.ts`, 59 on `session.ts`**. Three-way merge gives 56 states, 0
failures.
**Pass 3** — the chain does not end at the last chapter: `fences/post-series.md` amends 49 paths, 21
of them order-changing with 48 hunks the reorder can break.
**Pass 4** — SC-006 delegated to a mirror blind to 99 of the 722 fences it was meant to protect, in
the one task that replaces everything which is not a fence.

**AND A CORRECTION APPLIED TO ONE NUMBER AND NOT ITS NEIGHBOUR SURVIVED TWO PASSES.** The reference
count went 985 → 1,429 when the pattern gained a capital `C`; the FILE count came from that same
pattern and stayed at 166 until pass 3 — it is **183**, union **184**. **State the pattern and the
corpus with every count.**
<!-- SPECKIT END -->

    044 "the revision watermark"
                                            17 platform files, 20 net new tests in 5 files
                                            20 of 20 battery runs green
    mean 225.45 s, stdev 1.15, budget 240 · headroom 14.55 s
    coverage 99 files / 1,396 tests / 447 s, exit 0 · 240 fenced files, 41 chapters
    SC-004 -2.33% · SC-005 edit +2.75% delete +2.99% · both MET

**WHAT IT BUILT.** One column, `channels.revision_sequence`, raised by exactly one per edit or
deletion inside the transaction that applies it, never by a send. Reported on every
`connection.ack` as `revisions: {channel_id: count}`, for every channel the user belongs to,
zeros included. **The platform reports and never compares.**

**THE DESIGN CHANGED MID-BUILD AND THE REVERSAL IS THE LESSON.** A draft had the client present
its counts on the upgrade URL so the gateway could answer with the stale channels. It was built,
then removed. **A parameter the server parses and never acts on is a contract it can never
remove**; one the server acts on hands the client a number the platform makes decisions with,
which is how a fabricated count becomes a denial of service the client controls. Removing it also
deleted three FR-007 edge cases rather than handling them — **a design in which a case cannot
arise beats a branch that handles it**, because the branch is the thing that rots.

## THE INSTRUMENTS LIED THREE TIMES IN ONE FEATURE, EACH IN A DIFFERENT WAY

**`grep` ON THIS MACHINE IS ugrep 7.8.4, NOT GNU grep** (`/usr/bin/grep` is GNU 3.12; PATH
resolves elsewhere). A grouped alternation followed by two negated classes matches **nothing**
under it and matches under GNU grep:

    (postgres|redis)://[^:/@]+:[^@/]+@    ugrep 0    GNU 1
    postgres://[^:/@]+:[^@/]+@            ugrep 1    GNU 1

The credential scan filed that zero as evidence over a corpus containing the string twice. **Give
every pattern a positive control** and report a pattern that fails its own example as BROKEN
rather than as zero — that is what turns a `0` into a claim about the corpus. One shipped gate
uses the construct (`check-srs-ids.sh:49`); it was run under both engines and agrees.

**A PER-FILE COVERAGE THRESHOLD WHOSE KEY MATCHES NO FILE IS SILENT.** Demanding 101% of
`this-file-does-not-exist.ts` produced no error, no warning, nothing. Demanding 101% of a real
file names the key. **Run both halves of that probe every time the ratchet is re-pinned.**

**AND A TEST WRITTEN BY THE AUDIT THAT FINDS VACUOUS TESTS WAS VACUOUS.** FR-003 was cited by two
titles and asserted by neither, so the audit added `does not rise for a revision that was
REFUSED`. It passes — and passes identically with the counter moved outside the transaction,
because the edit path refuses a deleted message *before* the counter's statement is reached. The
bump never runs. **Ask what would have to be false for this to fail, and then read the code it
calls**, not the test. FR-003 now has a source-reading test that goes red when a bump moves onto
`this.db`.

## COVERAGE IS NOT REPRODUCIBLE RUN TO RUN, AND THE RATCHET HAS TO ALLOW FOR IT

`session.ts` functions measured **87.80%** and **85.36%** on identical code twenty minutes apart —
about one function of forty — while every other pinned file was byte-identical across both runs.
A floor at the measured value goes red on the next run for no change to the code, and the fix is
then to lower it: **a ratchet that teaches people to lower ratchets.** Pin below the lower
observation by the observed swing and put both numbers in the config.

**AND A p50 IS NOT AUTOMATICALLY THE ROBUST STATISTIC.** SC-005's baseline proposed moving to p50
if the noise swamped the 10% threshold. Six runs a side: edit mean cv **12.9%**, edit p50
**17.3%**; delete mean 13.5%, p50 20.6%. **p50 was noisier on both paths** — a median of 200
samples with a long tail wanders inside a crowded middle while the mean is anchored by the whole
sample. Resolving a 10% shift at that variance needs ~26 runs per side. The criterion was kept at
10% with its resolution limit recorded, rather than adjusted to whatever the lane now costs.

## READ THE CLAUSES, NOT THE IDENTIFIERS — AND THEN RUN THE TASK

**FOUR DOCUMENTS AGREED ON TWO CLAUSES THAT DO NOT EXIST.** The spec, the plan, the tasks and the
quickstart all said this feature would amend "SRS FR-016a and SRS FR-016b". Those are **chapter
3.23's specification ids**; they appear nowhere in `docs/04-srs.md`. Three analysis passes read
those artifacts against each other and saw agreement, because they agreed with each other and not
with the tree. What found it was **opening the SRS to make the edit**. Reading the clauses then
gave **three** to amend — `EIR-WS-03`, `FR-RTM-03`, `FR-RTM-05` — where the requirement named two.

**A TASK'S FILE COUNT IS WRONG IN ONE DIRECTION, EVERY TIME.** T018 named five fenced files and
thirteen needed hunks. T028 named three test files and there were four. The plan said 12, then 15,
then 17. **A plan counts the fix and not what the fix drags with it.**

## THE ONE THAT KEEPS EARNING ITS PLACE

**AN ARGUMENT THAT IS RIGHT ABOUT THE PRODUCER CAN INVERT ABOUT THE READER.** Chapter 3.24
made `messageSchema.attachments` required, which is correct for a schema the platform
BUILDS — required is what makes the compiler name every construction site. The same sentence
carried into `outboxEventSchema`, which READS off a durable queue, meant every in-flight
`message.created` written by the previous binary was answered with `message.term()`.

**Feature 043 was told to do it again and did not.** The task for the message-length bound
named `frames.ts:34` — `messageSchema`, the outbound message read off stored rows. The socket
door with no bound was fifty lines below. Bounding the reader would have been the same defect
with a different field, and there is now a test asserting `messageSchema` stays unbounded
*deliberately*, because the task pointed at it by line number.

**Required is a claim about what you write. A reader of anything durable cannot require a
field its writer did not have.**

## MEASURE THE CARRIED LEDGER; DO NOT COPY IT

Four of 043's twenty-three carried items were wrong when re-measured, and **three closed with
nobody working on them** — the `stdio: "ignore"` class went because retiring the port bands
REQUIRED reading each child's `listening` line, and a child whose output is discarded cannot
report one. **The diagnostic argument had been made for years; the mechanical need is what did
it.**

**044 RE-MEASURED ALL TWENTY-EIGHT AND CLOSED NONE DURING THE FEATURE, WHICH IS ALSO A RESULT** —
said plainly in `gaps.md` rather than implied by a short list. **Two were then closed afterwards
as work of their own**, taken against the ledger rather than against a task list, and both paid
back the re-measurement that kept them open:

**A LOOKALIKE NEARLY CLOSED AN OPEN ITEM.** `packages/test-harness/src/lists-agree.test.ts`
exists and asserts two exemption lists name the same files — and the pair it asserts is
`DRAIN_EXEMPT_TESTS`, **not** the `DRIVER_EXEMPT_TESTS` the item was about. A filename-level check
would have closed it. **Read the assertion, not the filename.**

**AND THE ITEM'S OWN PREMISE WAS WRONG.** It said the driver list and "the harness's own list"
agree by somebody remembering. **There is no second list**; what the driver list must agree with
is the TREE. That made the real defect sharper than the one filed: **the linter checks one
direction only.** An unlisted file importing `pg` fails loudly; a listed file importing nothing
restricted passes forever, so the list can only grow and a stale entry holds a standing exemption
over a file that no longer needs one. Both directions are now asserted, with the restricted module
names read from the rule rather than restated.

**A TASK ID IN A TEST TITLE OUTLIVES THE TASK, AND A TITLE IS THE PART READ DETACHED FROM ITS
FILE** — a CI summary has no repository to grep. Seven such ids are gone. Two could not be removed
alone: one had a comment fifty lines away pointing AT the title by its id, and one was being
printed to **stdout**. Ids anywhere in test files still number **330 across 46 files**; that is a
separate, much weaker item (comments are read by somebody who already has the file open) and is
filed rather than swept.

## TWO CLOSED STORIES, KEPT FOR THEIR RULES

**A HAND-MAINTAINED TABLE CANNOT BE CHECKED.** Nine api ports came from hand-allocated bands
across eight files. **Two bands contained a service the lane itself runs** — 5432 inside
`membership`'s 5400-5599, 4222 inside `limits`' 4100-4299 — and that was chapter 3.24's
eleventh red, the one its record called unexplainable. The failure is silent both ways: the
child cannot bind, and the health check gets its answer from whatever *does* hold the port.
All nine now use `PORT=0` with the port read from the child's own log line, and the map is
deleted rather than corrected. **Two consecutive 20-of-20 batteries say it held.**

**A TEST OF A SCRIPT MUST ASSERT WHAT THE SCRIPT DID, NOT WHAT THE TABLE HOLDS.**
`reset-lane.itest.ts` was wrong twice the same way: it counted rows "due now", which a run
that just finished violates legitimately, and it counted staleness against `now()` re-evaluated
~115 ms after the script's own. **Pin one instant before the script runs.**

## OTHER THINGS 043 PAID FOR

**A RED PROBE WRITES TO THE LANE.** Reverting the avatar rule to check the tests could see its
absence left two `javascript:alert(1)` rows stored, accepted with a 200 — and the next
measurement read them as pre-existing data contradicting the plan. The probe demonstrated the
defect more sharply than the test did, and it has to be cleaned up before anything is counted.

**AN ASSERTION SCOPED WIDER THAN THE THING IT TESTS FAILS FOR SOMEBODY ELSE'S REASON.**
`presence.itest.ts` asserted `select count(*) from outbox` was unchanged while vitest ran
`membership.itest.ts` in parallel — `expected 614255 to be 614250`, nothing in it suggesting
a neighbour. `limits.itest.ts` asserted a total inside a wall-clock minute bucket
(`floor(now / 60_000)`), so ten sends across the boundary wrote two keys and read one:
`expected 7 to be 10`, which reads exactly like a limiter dropping increments. **The first
fix there was worse than the fault** — sleeping to the next boundary blew the test's 5-second
timeout the moment the guard fired.

**WHEN MEASUREMENT FALSIFIES A CLAUSE, AMEND IT.** Done three times: FR-RTM-09 and FR-RTM-10
in the SRS (revision 1.8), and **this feature's own FR-016**, which said to refuse a type "the
platform does not emit" and would have refused 838 stored subscriptions to a declared,
published, unbuilt event type. The governance clause requires amendment rather than silent
divergence, and that applies to a feature's own specification.

**A PLAN COUNTS THE FIX AND NOT THE VERIFICATION.** 17 files estimated, 58 changed, and every
unplanned one came from RUNNING something rather than reading it. None of that is visible to a
plan; all of it is visible to twenty runs.

## THE LANE, AND WHAT IT STILL CANNOT TELL YOU

**The test lane is the instrument closest to hand and the least representative thing here.**
Ordering by `max(messages.created_at)` costs 0.87 ms on the lane and 159 ms at a million
rows — 145x from an indexed column — and the lane's largest membership set is FIVE channels,
so it cannot see any of that.

**It costs per SUITE, not per test** (`--concurrency=1`), and it can cost more every week:
`consumer.itest.ts` took 484 s on a dirty broker and 101 s on a clean one. 3.23's 228.80 s and
3.24's 233.08 s are **not comparable** to anything.

**BUT 043 AND 044 ARE — 225.35 s and 225.45 s, 0.10 s apart on a 240 s budget.** That is the
first pair in this project that can be compared at all, and the reason is the port fix: a lane
that is not fighting itself gives a duration that means something. The old rule was "no two
batteries are comparable"; the rule now is **"two batteries are comparable once the lane stops
colliding with itself, and you find out by measuring, not by assuming either way."**

**The broker no longer accumulates, and part of that is circular.** `reset-lane.itest.ts` runs
the real script and `@relay/test-harness` sorts first, so every run begins by purging. That is
"the lane self-cleans", not "the fix stopped the accumulation" — and it is safe only because
`--concurrency=1`. **Postgres rows still accumulate and `reset-lane.mjs` does not touch them by
design** — it purges lane debris, not data. Measured at 044's close-out: 76,980 environments,
791,520 outbox rows, 392,517 messages, 93,319 channels. Record the row counts beside any
close-out timing, because they are part of the instrument.

**A FILE AT 100% BRANCHES IS NOT A FILE WHOSE EVERY ARM HAS RUN.** v8 records a `binary-expr`
arm as covered when the operand was EVALUATED, not when it went both ways. Constitution VI's
100%-branch clause is stated in that number.

**AN ARGUMENT COSTS 545 WORDS IF IT IS MADE OF PROSE AND ABOUT 280 IF IT IS MADE OF
ARTIFACTS.** Say which kind each argument is when the estimate is written.

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository — or the broker, or the database — a question with a yes-or-no
   answer.** `curl localhost:8222/jsz?consumers=1` answered in one command what two hypotheses
   could not. 043's decisive numbers were all queries: 838 subscriptions, 0 avatar rows, 15
   SQL files against 8 snapshots, 0.2 rows per second.
2. **Read the clauses, not the identifiers.**
3. **Check a task's premise before executing it**, and run the command a task tells someone to
   run. 043 found four tasks whose premise was wrong, including one that would have caused a
   defect.

**AND WHEN A MECHANISM IS PROPOSED, FORCE IT.** Eight gateway-suite runs at 35 s each found
two flakes in five minutes that a 78-minute battery would have found once.

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

Write the class list explicitly and make the checker **fail on an unknown member**. Then test
it red, three ways.

- **`check-revision-order.mjs`** (new): fails on a descent, an unparseable version, and a
  renamed heading — and `1.10` correctly sorts above `1.9`, which string comparison does not.
- **`check-error-codes.mjs`** now compares `CLOSE_CODES` in both directions. A renamed code
  fires both at once.
- **`check-fence-chain.mjs` can retire a file now.** `replay` has understood `(deleted)` since
  3.2; the appendix loop never did, so after Part 3 closed nothing could retire a published
  file.
- **`check:errors` reads the BUILT `dist`.** Build before believing it.
- **A checker reports the FIRST failure per file.**
- **No checker reads prose**, and a `mermaid` block is prose.
- **AN UNTITLED FENCE IS NEVER COMPARED TO ANYTHING.** `check-fence-chain.mjs:77` collects a
  fence only when it matches `title="…"`. **146 of 904 — 16% — are outside every gate.** This
  is one step further out than the excerpt-only class, which is skipped *by* a title somebody
  wrote. Nobody decided this one. `gaps.md` 043-1 opens it.
- **FOURTEEN GATES, NOT ELEVEN**, and capture every exit code OUTSIDE a pipeline. `fail=1`
  inside `for … | sort` runs in a subshell and dies with it. **043 reproduced that mistake
  three times**, once in a task whose own text warns about it.

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

## THE CYCLE THIS PROJECT USES

`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (repeatedly) →
`/speckit-implement` (once per phase). 3.24 ran twenty-one analyze passes, 3.23 eleven, 043
fourteen, 044 three. **Do not stop on falling yield** — and note two things no number of passes
finds: a defect in code no lane runs, and **four artifacts that agree with each other and not
with the tree** (044's three passes all read "SRS FR-016a" without checking the SRS had one).
**The third pass was the one that ran the premise** rather than reading it, and that is the
pass that found the most.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**Pin the lane environment where the tasks can see it** (`baseline.txt`), and bring the stack
up with `RELAY_POSTGRES_PORT=15432` — this machine's own Postgres holds 5432.
**Nothing else runs on the machine during a timing battery.**

**USE A PERSON.** Chapters 3.14 through 3.24 each named this gap; 044 is the thirteenth record
to name it and not close it. **And 044 has the sharpest evidence for why the substitute fails**:
reading the published text with the spec and source closed found a real hole — FR-008's client
half was missing — because that exercise finds information that is ABSENT. It cannot find
information that is present and unclear, since the person running it wrote the sentence. `specs/036-chapter-3-18/reader-protocol.md`: 45 minutes,
six questions, one person who has not read the work.

Every check in these three repositories compares bytes. Six Python instruments, five `check:*`
scripts, and a compile-time assertion added this week — and not one can say whether a
paragraph is understandable to somebody who does not already know the answer. Each says so in
its own last line:

    check-refs: ids only — this says nothing about whether the prose around them is true
    sweep: this says nothing about whether the prose is TRUE
    check-checklist: presence only — it cannot tell whether a ticked box is true

**An instrument that is easy to run tells you what it measures, not what you wanted to know.**
