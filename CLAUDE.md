**CHAPTER 3.24 IS CLOSED**, tagged `part3-ch24` in all three repositories. Its record is
`specs/042-chapter-3-24/` — `chapter-notes.md` first, then `gaps.md` (**five items plus
seventeen carried, each re-measured**), then `traceability.md` and `baseline.txt`.

**3.24 IS THE LAST CHAPTER OF PART 3.** Everything it deferred is Part 4's: hosted media
(`media_not_available`) is 4.5 and 4.6, the queryable attempt log is 4.2, FR-MOD-03's audit log
is 4.7.

    3.24 "the message that is not only text"
                                            2,776 words, 30 fenced, 5 figures
                                            37 platform files, 61 net new tests in 22 files
    9 of 20 battery runs green · mean 233.08 s over the GREEN runs, stdev 1.75, budget 240
    coverage 97 files / 1,357 tests / 455 s, exit 0 · 241 fenced files, 41 chapters

**AN ARGUMENT THAT IS RIGHT ABOUT THE PRODUCER CAN INVERT ABOUT THE READER.** This chapter's
thesis is *make the field required, not optional* — correct for `messageSchema`, which the
platform BUILDS, because required is what makes the compiler name every construction site. The
same sentence was carried into `outboxEventSchema`, which the consumer READS off a durable
queue, and there it means every in-flight `message.created` written by the previous binary is
answered with `message.term()` — destroyed, not retried. **Required is a claim about what you
write. A reader of anything durable cannot require a field its writer did not have.**

**IT TOOK THE CLOSE-OUT COVERAGE LANE TO FIND IT**, after twenty-one analysis passes and eleven
phases, and `event.ts`'s own header says why: the api's suite runs `RELAY_EVENT_CONSUMER=off`,
so nothing in it exercises the consumer. What caught it are two fixtures nobody updated —
`consumer.itest.ts:46` and `scripts/consumer-walk.mjs:75` — which between them are the only
place in the repository that still spells a pre-3.24 event. **Do not "fix" a fixture that is red
because it describes the past.**

## THE BATTERY: 9 OF 20, AND THE FRACTION IS THE LEAST OF IT

**"CARRY THE INTERVAL, NOT THE FRACTION" IS NOT ENOUGH — THE INTERVAL CARRIES AN ASSUMPTION.**
11 red of 20 gives a Clopper-Pearson 95% interval of [31.53%, 76.94%], which assumes twenty
independent trials. Read the exit column down: from run 3 to run 17 it alternates without a
break, G R G R G R G R G R G R G R G. Fifteen alternations is one chance in eight thousand.
**A battery whose runs share state is not a sample of anything. Carry the mechanism.**

**TEN OF THE ELEVEN REDS ARE ONE DEFECT, ISOLATED BY FORCING THE FILE ORDER.** `harness.ts:534`
SIGTERMs its children and sleeps a flat 200 ms without awaiting `exit`; `tuan.itest.ts:45` is
the only suite that boots two gateways, so it needs longer. Three runs:

    quotas -> tuan -> webhooks     webhooks 3rd   RED      rules out nothing yet
    quotas -> webhooks -> tuan     webhooks 2nd   GREEN    rules out "the third fails"
    tuan -> quotas -> webhooks     quotas   2nd   RED      rules out "webhooks is broken"

**The victim is whoever boots next after `tuan` stops — this run or the next one.** And the
health check cannot tell the child it started from the child it is replacing: `waitForHealth`
polls a URL, the dying predecessor answers 200, and every red run prints `api up on 4100`
exactly like a green one. The `EADDRINUSE` goes to an unread pipe.

**THE ALTERNATION IS THE TEST RUNNER.** `node_modules/.vite/vitest/<hash>/results.json` stores
`{duration, failed}` per file; the sequencer runs previously-failed files first, which pushes
`tuan` into the last slot, which makes the next run green, which restores duration order.
**The lane's failure rate is a function of a JSON file in `node_modules`** — and the state it
was left in after run 20 predicted the next failure before it ran.

**THE ELEVENTH RED IS THE ONE NOBODY CAN EXPLAIN**, and for the recorded reason:
`limits.itest.ts` said *"api never became healthy"* and the child wrote why to `stdio: "ignore"`.
Same family as chapter 3.23's two.

## A LANE THAT ACCUMULATES ANSWERS A DIFFERENT QUESTION EVERY WEEK

**AN IDENTICAL FAILURE ON A CLEANED ENVIRONMENT IS NOT THE ENVIRONMENT.** The first coverage run
went red with fifteen failures and one hypothesis explained all of them: 56,193 messages and 216
durable consumers on `DELIVERIES`. Clearing it fixed the nine dispatcher failures and reproduced
the six consumer ones **exactly** — 484189 ms against 484245 ms. Two causes, and the cheap one
was tested rather than believed.

**THE LANE FILLS UP UNTIL IT CANNOT PASS AND REPORTS IT AS AN ASSERTION FAILURE.**
`dispatcher-deliver` pinned at `MAX_ACK_PENDING` on rows long deleted; 215 `itest-deliver-*`
durables each replaying 56,000 messages, because `main.ts:86` uses `DeliverPolicy.All`; and
`publishDue()` calls the PRODUCTION relay, so purging the stream refills it from stale rows. The
test says `expected 0 to be greater than 0`. **Ask the broker** — `scripts/stream-info.mjs` reads
exactly this and no failure message mentions it. Twenty battery runs added 4,717 environments,
60,953 outbox rows and 19 orphaned durables. **Clear it before a close-out measurement**, or the
number is taken on a different instrument than the last chapter used.

## MEASUREMENTS WORTH NOT RE-TAKING

**The test lane is the instrument closest to hand and the least representative thing here.**

    ordering by max(messages.created_at)     0.87 ms on the lane   159 ms at 1,000,000
    an indexed channels.last_activity_at     1.1 ms                145x apart
    the lane's largest membership set        FIVE channels — it cannot see any of this

**The lane costs per SUITE, not per test** — `--concurrency=1`, so cost scales with api boots.
**And it costs more every week**: `consumer.itest.ts` took 484 s on a dirty broker and 101 s on
a clean one. Chapter 3.23's 228.80 s mean and this chapter's 233.08 s are **not comparable**,
and neither will be to the next.

**A FILE AT 100% BRANCHES IS NOT A FILE WHOSE EVERY ARM HAS RUN.** v8 records a `binary-expr`
arm as covered when the operand was EVALUATED, not when it went both ways:
`typeof value.text === "string" && value.text.length > 0` measures `[7, 7]` and the `typeof`
check has never once been false. Constitution VI's 100%-branch clause is stated in that number.

**AN ARGUMENT COSTS 545 WORDS IF IT IS MADE OF PROSE AND ABOUT 280 IF IT IS MADE OF ARTIFACTS.**
Three chapters at a flat 545: +21%, -9%, **+77%**. 3.22 and 3.23 argued from published documents
and from reasoning; 3.24's evidence is compiler output, a diff and a test name, and a reader who
can see the list does not need the paragraph describing it. **Say which kind each argument is
when the estimate is written.**

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository — or the broker, or the database — a question with a yes-or-no answer.**
   `curl localhost:8222/jsz?consumers=1` answered in one command what two hypotheses could not.
2. **Read the clauses, not the identifiers.** Enumerating ids answers *is this number free*; it
   never answers *does a clause already say this*.
3. **Check a task's premise before executing it**, and run the command a task tells someone to
   run, in the pass that writes it.

**AND WHEN A MECHANISM IS PROPOSED, FORCE IT.** Three runs with a hand-written sequencer cache
cost eight minutes and turned "probably the ports" into a demonstrated cause with two rival
explanations eliminated. **A confounded experiment is worth recording too**: the first attempt
ran seconds after its predecessor and failed for the reason the experiment was about.

## OTHER THINGS THAT COST A CHAPTER TO LEARN

**TWO SCHEMAS THAT MUST DIFFER CANNOT SHARE A REFERENCE AT ALL.** `editMessageBodySchema.text`
was `sendMessageBodySchema.shape.text`; relaxing the send's `.min(1)` silently relaxed the
edit's, and an edit has no attachments field to restore its floor. The compiler cannot see it —
the types are identical either way.

**THREE CARRIED GAP ITEMS WERE WRONG ON THE DAY THEY WERE WRITTEN.** Seventeen re-measured, three
misses, none a regression: the drizzle snapshot was six behind and is seven, because the chapter
measured before adding its OWN migration; excerpt-only fence chains were two and are ten;
children discarding their output were nine and are eleven. **Two was the gateway's count, not the
repository's, twice, one item apart.** A measurement taken mid-chapter is stale by close-out.

**A NUMBER IN A HEADING IS CARRIED; A NUMBER DERIVED FROM ROWS HAS TO BE RE-DERIVED BY SOMEBODY.**
`docs/07-tutorial-plan.md` said Part 3 had 21 chapters over a table of 24, through 3.22, 3.23 and
3.24 — in a paragraph whose own last sentence says the count comes from the rows.

**A TASK ID IN A TEST TITLE OUTLIVES THE TASK.** 3.22 wrote one, 3.23 fifty-two, 3.24 thirty-three
and its own audit stripped them. Requirement ids belong there; task ids do not.

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

Write the class list explicitly and make the checker **fail on an unknown member**. Then test it
red, three ways.

- **The derived target list fails on the build that adds a route** — still the highest-yield
  check here.
- **`codes.test.ts` asserts the exact close-code set and the exact count.**
- **`check:errors` reads the BUILT `dist`.** Build before believing it.
- **A checker that overstates its reach is a checker that lies.** `check-refs.py` walks `*.md`
  only; `baseline.txt` is `.txt`.
- **A checker reports the FIRST failure per file.** `check-fence-chain`'s "3 problems" was three
  files, not three lines.
- **No checker reads prose**, and a `mermaid` block is prose.

## TESTS THAT PASS WHILE PROVING NOTHING

Ask, of every test on a failure path: **what would have to be false for this to fail?**

- **A repository test proves a check exists; only a route test proves it fires.**
- **A conditional assertion is an assertion that may not run.** A test guarded by
  `if (status === 200)` against a route that answers 404 asserted nothing for a phase — and
  `GET /v1/channels` is not a route.
- **An indistinguishability pair can pass because both halves changed together.**
- **`?? null` cannot tell an absent key from a null one.**
- **An unbounded wait turns a red test into a forty-second one.**
- **Two 204s prove nothing.** Idempotence is about what the second call DID; the assertion that
  carries it is the outbox row count.

## THE FENCE CHAIN

1. **Three lines of context suffice when uniqueness is CHECKED** — and `event.ts`'s two
   deliberately identical branches fail that check at `-U3`. Regenerate at `-U6`.
2. **The predecessor is a commit, not a tag.**
3. **A chapter cannot do the appendix's work, and vice versa.** Generate against the working
   tree, not `HEAD`.
4. **A `diff` hunk says A way to get from one file to another, not THE way.**
5. **An appendix hunk anchored on a file's last line forbids any chapter from appending.**
6. **A diff body inside a ```ts fence is read as a whole file.**
7. **An excerpt-only file is never verified against the repository at all** — TEN of them, not
   two. This chapter edited three.
8. **A file whose chain lives entirely in the appendix cannot be fenced by a chapter.**
9. **The generator is not idempotent unless it excludes the chapter's own pages.**
10. **Run `check:fences` after ANY source edit in phase 12, not only the ratchet.** The title
    audit invalidated three fences and the outbox fix a fourth. **A line-for-line patch of a
    fence body is not enough when the change alters the hunk's line counts.**

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown
and a JSX expression in MDX.

## THE CHAPTER CYCLE THIS PROJECT USES

`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` (repeatedly) ->
`/speckit-implement` (once per phase). 3.24 ran **twenty-one** analyze passes, 3.23 eleven, 3.22
fifteen. **Do not stop on falling yield** — and note that twenty-one passes did not find the
outbox reader, because no pass runs the consumer.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**A phase that adds raw SQL must run the suite that executes it.**
**Pin the lane environment where the tasks can see it** (`baseline.txt`).
**Nothing else runs on the machine during a timing battery.**

**USE A PERSON.** Chapters 3.14 through 3.24 have each named this gap and none has closed it.
`specs/036-chapter-3-18/reader-protocol.md`, 45 minutes, six questions. Every check in this
repository compares bytes — six Python instruments now, and not one can answer whether a
paragraph is understandable to somebody who does not already know the answer. **An instrument
that is easy to run tells you what it measures, not what you wanted to know.**
