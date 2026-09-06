**FEATURE 043 IS CLOSED.** Its record is `specs/043-fix-review-findings/` — `gaps.md` first
(**24 items: 23 carried and re-measured, 1 new**), then `baseline.txt`, `traceability.md`
and `tasks.md`. It publishes no chapter, so every platform change carries an amendment hunk
in `relay-tutorial/fences/post-series.md`.

**PART 3 IS CLOSED AND 3.24 WAS ITS LAST CHAPTER.** Everything deferred is Part 4's: hosted
media (`media_not_available`) is 4.5 and 4.6, the queryable attempt log is 4.2, FR-MOD-03's
audit log is 4.7.

<!-- SPECKIT START -->
**ACTIVE FEATURE:** `specs/044-revision-watermark/` — a per-channel revision counter so a
reconnecting client can tell which of its channels hold edits or deletions it never saw. Plan:
`specs/044-revision-watermark/plan.md`.

FR-016a already says the stale copy is repairable by re-reading history and FR-016b says the
limit must be documented; **nothing tells a client to perform the repair**. The window is
routine rather than exotic — a rolling restart leaves the last client to reconnect 3m20s
behind, because `DEFAULT_LIMITS.connect` is 3,000/min against a gateway that accepts 1,125-1,675
per second (`docs/11-scalability-measurement-2026-09-06.md`).

It publishes no chapter, so every changed platform file that a chapter fences carries an
amendment hunk in `relay-tutorial/fences/post-series.md`.
<!-- SPECKIT END -->

    043 "fix the review's findings"
                                            58 files (47 platform, 11 tutorial)
                                            20 of 20 battery runs green
    mean 225.35 s, stdev 0.99, budget 240 · headroom 14.65 s
    coverage 99 files / 1,379 tests / 439 s, exit 0 · 240 fenced files, 41 chapters
    unit lane 512 tests / 56 files with every container stopped

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

Four of 043's twenty-three carried gap items were wrong when re-measured — files discarding a
child's output was recorded as ELEVEN and measured ZERO, excerpt-only chains TEN and measured
THIRTEEN — and **three closed without anyone working on them**. The `stdio: "ignore"` class
went because retiring the port bands REQUIRED reading each child's `listening` line, and a
child whose output is discarded cannot report one. **The diagnostic argument had been made for
years; the mechanical need is what did it.** Detail in `specs/043-fix-review-findings/gaps.md`.

## A HAND-MAINTAINED TABLE CANNOT BE CHECKED

Nine api ports were drawn from hand-allocated bands across eight files, listed in a map at the
top of `limits.itest.ts`. **Two bands contained a service the lane itself runs** — 5432
(Postgres) inside `membership`'s 5400-5599, and 4222 (NATS) inside `limits`' 4100-4299.

The failure is silent both ways: the child cannot bind, `stdio: "ignore"` eats the
`EADDRINUSE`, and the health check gets its answer from whatever *does* hold the port. Every
test in the file then fails against Postgres with `other side closed` and no port named
anywhere.

**That is chapter 3.24's eleventh red, the one its record called unexplainable.** It was
`limits.itest.ts` saying "api never became healthy". 4222 is in its band.

All nine retired for `PORT=0`, with the port read back from the child's own log line. The map
is deleted rather than corrected — it had to avoid every other band and every service port on
every contributor's machine, and stay right as both moved.

## A TEST OF A SCRIPT MUST ASSERT WHAT THE SCRIPT DID

`reset-lane.itest.ts` was wrong twice, the same way both times, and both were assertions about
the TABLE rather than about the script's effect:

- it counted rows "due now", which a run that just finished violates legitimately;
- it counted staleness against `now()`, re-evaluated ~115 ms after the script's own `now()`.
  Rows aging across the 30-minute mark in between failed runs 16 and 20 of a battery. Measured
  live: 0.2 rows crossed per second.

**The window did not exist until the lane had been up longer than `STALE_AFTER`**, so the
first seven runs were structurally safe and it read as a late-onset flake. Pinning one instant
before the script runs fixes it; a planted row that crosses 400 ms out counts 0 against the
pinned instant and 1 against a re-evaluated one.

## OTHER THINGS 043 PAID FOR

**EXIT 0 DOES NOT PROVE A PER-FILE THRESHOLD MATCHED.** A coverage pin whose key matches no
file is ignored silently — it passes forever and protects nothing. Demanding 101% of a file at
100% is what proves the key resolves; vitest then names it.

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

**It costs per SUITE, not per test** (`--concurrency=1`), and **it costs more every week**:
`consumer.itest.ts` took 484 s on a dirty broker and 101 s on a clean one. 3.23's 228.80 s,
3.24's 233.08 s and 043's 225.35 s are **not comparable**, and neither will be to the next.

**The broker no longer accumulates, and part of that is circular.** `reset-lane.itest.ts` runs
the real script and `@relay/test-harness` sorts first, so every run begins by purging. That is
"the lane self-cleans", not "the fix stopped the accumulation" — and it is safe only because
`--concurrency=1`. Postgres rows still accumulate: 12,000 environments and 160,000 outbox rows
in twenty runs.

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

1. **Three lines of context suffice when uniqueness is CHECKED.** Regenerate at `-U6` when the
   pre-image matches twice — 043 hit this once.
2. **The predecessor is a commit, not a tag.**
3. **A `diff` hunk says A way to get from one file to another, not THE way.**
4. **An appendix hunk anchored on a file's last line forbids any chapter from appending**,
   and a diff body inside a ```ts fence is read as a whole file — the appendix takes `diff`.
5. **An excerpt-only file is never verified — THIRTEEN of them.** 043 edited three, and no
   gate could see any of those edits.
6. **Run `check:fences` after ANY source edit**, not only the ratchet.

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown
and a JSX expression in MDX.

## THE CYCLE THIS PROJECT USES

`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (repeatedly) →
`/speckit-implement` (once per phase). 3.24 ran twenty-one analyze passes, 3.23 eleven, 043
fourteen. **Do not stop on falling yield** — and note that no number of passes finds a defect
in code no lane runs.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**Pin the lane environment where the tasks can see it** (`baseline.txt`), and bring the stack
up with `RELAY_POSTGRES_PORT=15432` — this machine's own Postgres holds 5432.
**Nothing else runs on the machine during a timing battery.**

**USE A PERSON.** Chapters 3.14 through 3.24 each named this gap, and 043 is the twelfth
record to name it and not close it. `specs/036-chapter-3-18/reader-protocol.md`: 45 minutes,
six questions, one person who has not read the work.

Every check in these three repositories compares bytes. Six Python instruments, five `check:*`
scripts, and a compile-time assertion added this week — and not one can say whether a
paragraph is understandable to somebody who does not already know the answer. Each says so in
its own last line:

    check-refs: ids only — this says nothing about whether the prose around them is true
    sweep: this says nothing about whether the prose is TRUE
    check-checklist: presence only — it cannot tell whether a ticked box is true

**An instrument that is easy to run tells you what it measures, not what you wanted to know.**
