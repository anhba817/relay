<!-- SPECKIT START -->
**CHAPTER 3.18 IS IN PLANNING** — `specs/036-chapter-3-18/`, the message that never arrived.
A message sent over REST commits, returns `201`, and reaches no live socket: the only publisher
to the fan-out is the gateway's own send handler. Chapter 3.14 recorded it as a verdict, 3.17
left it as `gaps.md` item 3, and `docs/05-sad.md:138` has drawn the missing edge all along.
Read `plan.md`, then `research.md` — R10 is why the api writes its own publisher instead of
reusing the gateway's, and R5 is the risk the plan could not close by reading.
**There is no SRS amendment. Principle VI is satisfied by citation** (FR-RTM-01 is the unmet
clause, not FR-RTM-05 as the tutorial plan's row says) — and a reader arriving from 3.17, where
the amendment *was* the gate, will look for one.

**CHAPTER 3.17 IS CLOSED**, tagged `part3-ch17` in all three repositories. Its record is
`specs/035-chapter-3-17/` — read `chapter-notes.md` first, then `gaps.md` (nine items, each with
an owner; item 3 is what 3.18 does), `traceability.md` and `baseline.txt` for every measurement.

    3.17 "the sender a message never had"    16 files taught, 2,962 words, 27 fences
                                             + 7 files changed and claimed by no chapter
    589 integration tests, 25 of 26 full-lane runs green, mean 193.55 s, stdev 0.99
    coverage: repository.ts branches 91 -> 92, functions 100% (115/115)
    212 fenced files across 34 chapters, 34 translated · 212 figures · 91 static pages

## THE TWO FILE COUNTS ARE NOW A PRACTICE, AND IT WORKED

3.15/3.16 revised one conflated count eight times. 3.17 kept two columns from T080 to T085 and
**neither number was ever asked to do the other's job**:

    16   what the chapter teaches      -> drove the word estimate
    27   what the chapter must fence   -> drove the chain
    35   files changed, re-derived from `git diff` at the end — agreed with T080's prediction

Do this in every plan. `git diff --name-only` against `check:fences` at the very end is what
settles it; a first count is expected to be wrong.

**But the word RATE is not an estimator.** 3.15 and 3.16 agreed on 153.5 and 154.3 words per
taught file, to within 1%, and 3.17 came in at 84.7 — 45% below. Prose tracks the number of
*arguments* a chapter makes, not the number of paths it touches. 3.17 taught 16 files to make one
argument. Estimate from arguments, and say which.

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository a question with a yes-or-no answer.** Does this verb have a handler?
   Which chapter fences this file? Does this client have an `error` listener? (`createFanout` does
   not, while both rate limiters do and both explain why — found in one grep, and it is 3.18's
   R10.) What did `git diff` actually change?
2. **Read the clauses, not the identifiers.** Two of 3.17's three most expensive findings were a
   governing document saying something the feature assumed it did not say. Enumerating ids answers
   *is this number free*; it never answers *does a clause already say this*. `check:srs` enforces
   uniqueness and says in its own comment that it does not read meaning.
3. **Check a task's premise before executing it, and run the command a task tells someone to
   run, in the pass that writes it.** 3.15/3.16 had five wrong premises; 3.17 had five more and
   three that surfaced only during implementation. Pass 6 wrote a `grep` into T012a and pass 7
   ran it: seven hits, three dead, two do-not-touch, and one that would have deleted a capability
   3.15 shipped. A generalisation needs its own verification step.

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

**Five instruments in 3.17 were wrong the same way: a pattern matching the examples in front of me
rather than the set the rule names.** `check:srs` shipped covering 192 of 243 clause rows and
printed "192 clause rows" as though that were the document — the regex matched three-part ids, so
`DR-01`, `CON-06` and all 22 `EIR-*` were invisible. Also a `[P]` collision check that omitted
`.txt`, a prose matcher with 9 false positives, `grep -c sendMessage(` reading 100 for 27, and
`grep -c "path:"` reading 41 for 38.

Write the class list explicitly and make the checker **fail on an unknown member**. Then test it
red, three ways. `check:figures`'s first version reported 122 problems in 193 figures, all false;
a checker that cries wolf on a healthy tree is how a real problem hides.

## WHAT THE INSTRUMENTS CAUGHT THAT READING DID NOT

- **The derived target list fails on the build that adds a route** — five times over two features,
  and still the single highest-yield check in the repository.
- **`codes.test.ts` asserts the exact close-code set and the exact code count** (16 -> 17), which
  is what makes a new code a decision rather than an accident.
- **The coverage ratchet has now removed code three times rather than covered it.** 3.17: 98.95%
  against a pin of 99, and the file's own comment had predicted 98.92 for that exact mistake.
  Deleted an unreachable throw; statements 2555 -> 2552.
- **`check:errors` reads `packages/protocol/dist/codes.js`** — the BUILT artifact. A stale `dist`
  makes it green for the wrong reason. Build before believing it.
- **No checker reads prose.** A published Trap contradicting 3.17's own chapter survived fifteen
  analysis passes. `gaps.md` item 8.

## TESTS THAT PASS WHILE PROVING NOTHING

Ask, of every test on a failure path: **what would have to be false for this to fail?**

- **A repository test proves a check exists; only a route test proves it fires.** The send path's
  repository test passed for six analysis passes while its controller supplied no caller.
- **A test can pass with half its subject applied.** 3.17's T047c used a quota ceiling of 1, so
  the second person was over the limit either way — proven by removing the `kind` filter and
  watching 26 tests stay green.
- **Removing a check can come back green** if an earlier phase *replaced* rather than nested
  (T086). And changing a shared helper moves both halves of a pair, so the oracle sees nothing
  (T044).
- **3.18's live instance:** the fan-out's `publish` swallows its own errors and resolves. So "the
  send returned 201 while Redis was down" is true of a publisher that does nothing at all. The
  assertion that carries the requirement is the **log line**.

## MEASUREMENTS WORTH NOT RE-TAKING

**The test lane is the instrument closest to hand and the least representative thing here.**

    ordering by max(messages.created_at)     0.87 ms on the lane   159 ms at 1,000,000
    an indexed channels.last_activity_at     1.1 ms                145x apart
    the unread count, 50 channels @ 1M msgs  count rows 9.8-13.4   cached counter 1.2-2.1
                                             the subtraction 1.1-4.5 -> counter is NOT faster
    the listing's plan, by memberships       1k 0.46ms  5k 2.22ms  20k 10.62ms  50k 9.06ms
                                             the FIRST page is the most expensive (keyset)
    the lane's largest membership set        FIVE channels — it cannot see any of this

**The lane costs per SUITE, not per test** — it is `--concurrency=1`, so cost scales with api
boots. 407 -> 550 -> 589 tests moved the mean 193.0 -> 193.55 s. 240 s budget.

**Twenty green rejects a per-run failure rate above 13.91% at 95% confidence and nothing finer.**
A 5% flake survives it 35.85% of the time; rejecting one needs 59 runs. 3.17 ran twenty-six and
failed once, mechanism unidentified — `gaps.md` item 1, deliberately unfixed.

## THE FENCE CHAIN

1. **Three lines of context suffice when uniqueness is CHECKED** — verified by simulating what the
   checker does. 3.12's "eight lines" was a proxy for not being able to tell.
2. **The predecessor is a commit, not a tag.** A feature's tail can amend a platform file after
   tagging.
3. **A chapter cannot do the appendix's work, and vice versa.** A diff generated straight to HEAD
   performs the appendix's edit itself, and the appendix's hunk then matches 0 times. The target is
   *HEAD with the appendix's edits undone*.
4. **A `diff` hunk says A way to get from one file to another, not THE way** — and when a second
   tool applies its own hunks to your result, which way you chose is the whole question.
5. **An appendix hunk anchored on a file's last line forbids any chapter from appending to it.**
6. **A diff body inside a ```ts fence is read as a whole file.** And prose fences are not the
   chain's requirement — 3.16 needed 20 more paths fenced than it taught.
7. **An excerpt-only file is never verified against the repository at all** — `sentinel.ts`,
   `sentinel.sql`, `guard.itest.ts`. `gaps.md` item 7.

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown and
a JSX expression in MDX. `Could not parse expression with acorn`, line 3134 of a 4,400-line page.

## THE CHAPTER CYCLE THIS PROJECT USES

`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` (repeatedly) ->
`/speckit-implement` (once per phase). 3.17 ran **sixteen analyze passes for 20 CRITICALs**; 3.16
ran fifteen for 8; 3.12 fourteen for 6. **Do not stop on falling yield** — 3.16's pass 12
recommended stopping and passes 13, 14 and 15 each found a CRITICAL. Yield measures the questions
asked, not the defects present.

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice in 3.12.
**A phase that adds raw SQL must run the suite that executes it** — 3.17's phase 2 committed two
broken tests that typechecked, because a raw `sql` template is just a string.
**Pin the lane environment where the tasks can see it** (`baseline.txt`): four variables and one
stopped compose profile stood between a red lane and a green one.
**Nothing else runs on the machine during a timing battery** — 3.12's attempt one failed at run 11
to two Next.js dev servers, with no port held and no `EADDRINUSE`.

**USE A PERSON.** Chapters 3.14, 3.15, 3.16 and 3.17 have each named this gap and none has closed
it. The sealed outsider had been wrong about the API for two chapters because nobody ran it. Every
check in this repository compares bytes. **An instrument that is easy to run tells you what it
measures, not what you wanted to know** — the same sentence as the 145x measurement, one level up.
<!-- SPECKIT END -->
