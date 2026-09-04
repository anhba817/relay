**CHAPTER 3.23 IS CLOSED**, tagged `part3-ch23` in all three repositories. Its record is
`specs/041-chapter-3-23/` — `chapter-notes.md` first, then `gaps.md` (**nine items plus eight
carried from 3.22, each re-measured**), then `traceability.md` and `baseline.txt`.

    3.23 "the words somebody wants back"
                                            3,269 words, 34 fenced, 4 figures
                                            37 platform files, 84 new tests in 14 files
    18 of 20 battery runs green · mean 228.80 s over the GREEN runs, stdev 0.72,
    budget 240 — and both reds are the SAME five tests, cause undeterminable
    coverage 96 files / 1,296 tests / 462 s, exit 0 · 240 fenced files, 40 chapters
    messages.controller.ts branches 87 -> 92 (achieved 92.85), lines 100 -> 97

**BOTH BATTERY FAILURES ARE THE SAME FIVE TESTS AND NOBODY CAN SAY WHY.** `session.itest.ts`'s
delivery describe, its api child gone mid-describe — `ECONNREFUSED …:4502` in run 2 and `:4410`
in run 20, both inside that file's own 4400-4599 range. **796 api log lines survive in each red
log and not one is from the child that died**, because that file pipes its child's output and
reads it only to build the health-check failure message. `EADDRINUSE` greps to zero and **that
zero proves nothing** — such a line would sit in an unread pipe. An identical failure twice is
not what a flake looks like.

**"EIGHTEEN OF TWENTY" IS A MEASUREMENT WITH A CONFIDENCE INTERVAL, NOT A QUALITY BAR.**
2 of 20 gives a 95% Clopper-Pearson interval of **[1.23%, 31.70%]**. A true 5% rate produces
two or more failures in twenty runs 26.4% of the time, and a true 10% rate produces zero 12.2%
of the time — so **twenty runs cannot separate a 5% lane from a 10% one.** Chapter 3.20 needed
forty to put 17.5% on the record. Carry the interval, not the fraction.

**A DOCUMENT THAT CLAIMS TO QUOTE A PUBLISHED SOURCE AND DOES NOT.** `data-model.md` gave
`message_edits` a surrogate `id UUID PRIMARY KEY` and said, in the sentence above it, *"Its
shape is the SAD's, not this chapter's."* The SAD publishes three columns and a composite key.
Eleven analysis passes went past it, and the reason is the general one: **every checker here
compares identifiers, and this was a clause.** The table's name was in the plan, the tasks and
the data model; nothing read the DDL underneath it.

**THE FALSIFICATION THAT CAME BACK GREEN IS THE ONE WORTH THE PHASE.** Removing
`channelVisibleTo` from the edit path broke nothing — the foreign-versus-missing pair test
compared two bodies that read identically either way, so it passed while proving nothing. The
case only that predicate answers is a private channel of the same tenant, where the caller was
otherwise refused for **authorship** and so learned that a message exists in a channel they may
not read. Nineteen falsifications ran; eighteen went red for the stated reason and this one
bought a test.

**A CHECK THAT MATCHED THE EXAMPLES IN FRONT OF IT.** `db/catalogue.ts` asks whether every
table's rows trace to one tenant, and it accepted a foreign-key path of **length one**. That
covered every table that existed. `message_edits` is two links out, so the highest-yield
instrument in the repository refused a correct table in 4 ms and offered three remedies, all
wrong. **Reachability is not adjacency** — and "this is not a weakening" is a claim, so it was
falsified twice against the live database.

**SIX TASK PREMISES WERE WRONG, AND EACH COST LESS TO CHECK THAN TO EXECUTE.**

- **Tests that could not be written where the plan put them.** `resume.itest.ts` boots the
  gateway against a *stubbed* api and has no rows to edit; FR-016 is about what the backfill
  returns, so five of six tests moved to `backfill.itest.ts`.
- **A gate asked to fail on a true sentence.** `public-surface.itest.ts`'s list is what that
  test CALLS, not an inventory of the public surface. The `check-prose.py` entry was deleted
  rather than satisfied: a checker crying wolf on a healthy tree is how a real problem hides.
- **An audit scheduled over work nobody did.** The title-audit task lists
  `packages/outsider/src/integrate.itest.ts` among the files this chapter adds tests to, and
  no task wrote one. It is the only instrument that boots the shipped binary.
- **A phase ordering defect.** The idempotence test counts an outbox event the task list
  created three phases later — and ADR-06 puts that insert **inside** the transaction, so it
  could not wait.
- **A contract whose argument was false.** It specified 404 for editing a tombstone because
  *"a 410 on a message a caller may not edit would confirm the message exists"* — but nobody
  who may not edit it reaches that refusal, because authorship is checked first. A 404 there
  is chapter 2.8's verb-disagreement defect inside one resource.
- **A stale figure count**, the fourth number in this chapter inherited from a predecessor's
  record and wrong. It survived only because the task said "rises from" rather than "is".

**TWO 204s PROVE NOTHING.** Idempotence is about what the second call DID, and the status is
the same either way. The assertion that carries it is the outbox row count. The edit's answer
is the opposite and both are right: every edit emits, because the platform does not compare
message texts to decide whether an edit happened.

**A TASK ID IN A TEST TITLE OUTLIVES THE TASK — 52 OF THEM.** Chapter 3.22 corrected one and
wrote the rule down; this chapter wrote fifty-two `T0xx:` prefixes before its own title audit
stripped them. Requirement ids in titles are right and task ids are not. Six more titles said
something the assertion did not: *"reports no edited_at"* where the assertion was
`toHaveProperty("edited_at", null)`, and *"sends every kind"* where the test greps source text.

**A GENERATOR THAT READS ITS OWN OUTPUT IS NOT IDEMPOTENT.** The fence generator decides
whole-file versus diff by asking "does any chapter already fence this path?" — and on a second
run the answer includes its own first run, so a file it fenced whole comes back as a diff of
the file against itself. Hit twice: writing the Vietnamese mirror, and regenerating after a
late edit. **Exclude the chapter's own pages from that question.**

**AN ARGUMENT COSTS ABOUT 545 WORDS, WHATEVER IT ARGUES AGAINST.** 3.22 estimated from
arguments and came in 21% over at 583 each; 3.23 estimated 420 each on the theory that arguing
against published material costs more, and came in at 545 — a 9% drop where the model predicted
28%. **Estimate at 545 per argument and stop adjusting.**

**RUN THE GENERATED MIGRATION THROUGH A REVIEW, NOT THROUGH THE RUNNER.** `drizzle-kit
generate` produced `0008_message_edits.sql` against an existing `0008_limit_policy.sql`, with
six whole tables and fourteen alters replayed from migrations its snapshot cannot see. Its
meta has been six migrations behind since chapter 3.9, so **every generation since has been
wrong** and only ADR-16's review has kept it harmless. `gaps.md` item 6.

**A `.test.ts` IN THE DOCKER-FREE LANE NEEDS A RUNNING REDIS.** `connections.test.ts` talks to
a real broker at six call sites. Found when the compose stack went down mid-session and
`pnpm test` came back with twelve failures that were correct behaviour. **The lane's exit code
no longer answers the question it was built to answer.** `gaps.md` item 9.

**THREE WRONG THINGS IN ONE SEQUENCE DIAGRAM**, published since the SAD's first draft: a route
that does not exist, an `INSERT` into a table that does not exist, and a paragraph counting a
consumer that is not built. **No checker reads prose, and a `mermaid` block is prose.**

## CHAPTER 3.22'S DURABLE LESSONS, STILL LOAD-BEARING

**READING BEAT DERIVING.** Three of 3.23's design decisions were published before it opened —
`prior_text TEXT NOT NULL`, `messages.metadata`, and the four read paths. **Ask the repository
before deriving an answer.**

**A FALSIFICATION CAN ONLY SEE THE TESTS THAT EXIST.** Write the test that could see it before
concluding nothing can.

**THE LOG LINE IS THE ONLY EVIDENCE A FAIL-OPEN PATH HAS**, and an absence is not a
distinction.

**VERIFY BY EXIT CODE, NEVER BY ABSENCE OF OUTPUT.** A pipeline ending in `tail` makes `$?` read
`tail`; `pnpm -s` in the wrong repo returns 254 silently.

**A CHAPTER CAN TEACH A FILE IT IS NOT ALLOWED TO FENCE**, and a titled fence naming no file is
still a fence.

**THE RATCHET REMOVES CODE.** Fifth time in 3.23: a `?? "unknown"` that was unreachable *and*
would have put that word on the wire as somebody's name, plus three copies of the same two
context fallbacks collapsed into one function.

## THE TWO FILE COUNTS ARE A PRACTICE

    9    what the chapter teaches      -> drove the word estimate
    34   what the chapter must fence   -> drove the chain
    37   files changed, re-derived from `git diff` at the very end

**33 became 34 during close-out**, because the coverage ratchet edited a fenced file. Phase 12's
own header warns about exactly that, which is why it cost one command instead of a surprise.

**Three changed files stay unfenced** — no chapter has ever fenced them and this one does not
teach them. Fencing them would add 2,251 lines the chapter never discusses.

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository a question with a yes-or-no answer.**
2. **Read the clauses, not the identifiers.** Enumerating ids answers *is this number free*; it
   never answers *does a clause already say this*. 3.23's worst finding was a DDL nobody read
   under a table name everybody checked.
3. **Check a task's premise before executing it**, and run the command a task tells someone to
   run, in the pass that writes it.

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

Write the class list explicitly and make the checker **fail on an unknown member**. Then test it
red, three ways.

- **The derived target list fails on the build that adds a route** — still the highest-yield
  check here, and 3.23 fired it in both directions at once.
- **`codes.test.ts` asserts the exact close-code set and the exact count.** 3.23 added two error
  codes where its plan expected one.
- **`check:errors` reads the BUILT `dist`.** Build before believing it.
- **A checker that overstates its reach is a checker that lies.** `check-refs.py` walks `*.md`
  only and printed "no undeclared task ids outside tasks.md"; `baseline.txt` is `.txt`.
- **No checker reads prose.**

## TESTS THAT PASS WHILE PROVING NOTHING

Ask, of every test on a failure path: **what would have to be false for this to fail?**

- **A repository test proves a check exists; only a route test proves it fires.**
- **A test can pass with half its subject applied.**
- **An indistinguishability pair can pass because both halves changed together.** 3.23's
  foreign-versus-missing pair matched whichever check produced it.
- **`?? null` cannot tell an absent key from a null one.** A control test was green before its
  field existed.
- **An unbounded wait turns a red test into a forty-second one.**

## MEASUREMENTS WORTH NOT RE-TAKING

**The test lane is the instrument closest to hand and the least representative thing here.**

    ordering by max(messages.created_at)     0.87 ms on the lane   159 ms at 1,000,000
    an indexed channels.last_activity_at     1.1 ms                145x apart
    the lane's largest membership set        FIVE channels — it cannot see any of this
    121,250 senderless rows                  no write path can produce one any more

**The lane costs per SUITE, not per test** — `--concurrency=1`, so cost scales with api boots.
240 s budget. **Twenty green rejects a per-run failure rate above 13.91% at 95% and nothing
finer.**

## THE FENCE CHAIN

1. **Three lines of context suffice when uniqueness is CHECKED.**
2. **The predecessor is a commit, not a tag.**
3. **A chapter cannot do the appendix's work, and vice versa.** Generate against the working
   tree, not `HEAD`.
4. **A `diff` hunk says A way to get from one file to another, not THE way.**
5. **An appendix hunk anchored on a file's last line forbids any chapter from appending.**
6. **A diff body inside a ```ts fence is read as a whole file.**
7. **An excerpt-only file is never verified against the repository at all** — still two.
8. **A file whose chain lives entirely in the appendix cannot be fenced by a chapter.**
9. **The generator is not idempotent unless it excludes the chapter's own pages.**

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown
and a JSX expression in MDX.

## THE CHAPTER CYCLE THIS PROJECT USES

`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` (repeatedly) ->
`/speckit-implement` (once per phase). 3.23 ran **eleven** analyze passes, 3.22 fifteen, 3.17
sixteen. **Do not stop on falling yield** — and note that eleven passes did not read one DDL.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**A phase that adds raw SQL must run the suite that executes it** — and the suite that
executes 3.23's new SQL was the tenancy catalogue, not the one the task named.
**Pin the lane environment where the tasks can see it** (`baseline.txt`).
**Nothing else runs on the machine during a timing battery.**

**USE A PERSON.** Chapters 3.14 through 3.23 have each named this gap and none has closed it.
`specs/036-chapter-3-18/reader-protocol.md`, 45 minutes, six questions. Every check in this
repository compares bytes. **An instrument that is easy to run tells you what it measures, not
what you wanted to know.**
