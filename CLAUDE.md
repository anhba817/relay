<!-- SPECKIT START -->
**CHAPTER 3.22 IS IN PLANNING** — `specs/040-chapter-3-22/`, FR-RTM-09's five-connection
cap. Read `plan.md`, then `research.md`. **The hand-off it was given was wrong in a new
way: it assigned a decision that had already been published**, and the decision it did not
name was the larger one.

**THREE OF FOUR DESIGN DECISIONS WERE ALREADY WRITTEN IN THE TREE.** Reading beat deriving,
which is this file's mechanism 2 with a number on it. Where the refusal happens: chapter
3.11 settled it at `session.ts:715` for the closest analogue — *"the argument for the HTTP
shape evaporates with it, and the shape that is left reaches a browser where a failed
upgrade's body does not"*. **A browser cannot read a failed upgrade's body**, so refusing at
the upgrade seam gives a browser a bare connection failure. Whether it needs a sixth close
code: `codes.ts:10` states the test — *"a client that cannot tell them apart retries the
wrong one for ever"* — and all four reuses fail it. The two intervals: three refreshes per
window, from `presence.ts:41`.

**AND THE FOURTH CONTRADICTS A PUBLISHED DOCUMENT.** `docs/05-sad.md:574` prescribes a
sorted set pruned with `ZREMRANGEBYSCORE`, which needs Lua for FR-013's atomicity —
and **Constitution VII requires "a superseding ADR with profiling evidence" for a second
language, which this lane cannot produce** (largest fixture: five channels; NFR-SCL-01 asks
about ten thousand connections). `grep` for `.eval(`, `defineCommand` and `.multi(` returns
ZERO hits: this platform has never issued a multi-command Redis operation. So the design is
**five slot keys claimed with `SET NX PX`** — presence's own primitive — which makes the TTL
per member by construction rather than working around it, and needs an ADR plus the SAD
amendment.

**THE SAD DESCRIBES `conn:{env}:{user}` TWICE, IN TWO SHAPES AND TWO TENSES.** Line 167 says
the gateway *"registers the connection in Redis (`conn:{env}:{user}` → instance ID,
TTL-refreshed)"* — present tense, single value, describing something that does not exist.
Line 574 says *set* of instance IDs and *"Not built"*. `conn:` appears in exactly one place
in the platform: a comment saying presence does not need it.

**`policy.ts` DIVIDES BY FIVE AND SHIPS A DIFFERENT NUMBER.** `10_000 / 5 = 2_000`; the
constant is `connect: 3_000`, and `policy.test.ts:54` pins it while its comment says *"the
chapter states the derivation and this asserts the result"*. The limiter counts
establishments, so the figure for its stated goal is 10,000 — three numbers. **Until this
chapter, five was enforced nowhere, so the division was sizing against a hypothetical.**
Not this chapter's to fix; `gaps.md` gets the arithmetic.

**AN ELIMINATED HYPOTHESIS WAS ELIMINATED BY THE WRONG TEST.** `presence.itest.ts` takes
`4700 + %200` = 4700–4899; `meter.itest.ts`'s api takes `4710 + %60` = 4710–4769. **The
unregistered range strictly contains a registered one**, and the gateway's integration
config sets no `fileParallelism`, so both run at once. Chapter 3.20 eliminated "a port
collision" because *"the failing ports are in each file's own range"* — a test that cannot
see this, because the colliding port IS in each file's own range. P = 1/200 per run, which
is a contributor and not a cause. These are the two files with open battery failures.

**CHAPTER 3.21 IS CLOSED**, tagged `part3-ch21` in all three repositories — fence
predecessor `0ecb21f`, which is `git rev-parse part3-ch21^{commit}` and not the tag. Its
record is `specs/039-chapter-3-21/` — `chapter-notes.md` first, then `gaps.md` (**nine new
items**, twenty-five carried), then `traceability.md` and `baseline.txt`.

    3.21 "the frame nobody may send"        2,306 words, 18 fenced, 3 figures
                                            18 platform files (+2,559 -26), 13 tutorial
    19 of 20 battery runs green · mean 228.63 s, stdev 0.68, budget 240 — 11.37 s spare
    44 files, 727 tests · coverage 93 files / 1174 tests / 436.45 s, exit 0
    both new production files 100/100/100/100 · 234 fenced files, 38 chapters translated

**A FABRIC OWNS ITS SUBJECT GRAMMAR, and a kind that cannot share a payload type cannot
share a subject.** Three chapters reached this independently, so it is a rule. ADR-19's
"three typed points" undercounted: the grep returns eight lines over seven places.

**COVERAGE CANNOT SEE AN OMISSION.** `**/main.ts` is excluded from the ratchet
(`vitest.coverage.config.mts:97`) and that is where 3.21's worst defect lived — the module
was built, its `close()` awaited, and it was never passed to `attachSessions`. The feature
was inert in the product while 1,174 coverage tests and 174 gateway integration tests were
green. **Including `main.ts` would not have caught it either**: every line executed; the
defect was an argument that was not there. `packages/outsider/src/integrate.itest.ts` is the
only instrument that boots the shipped binary, and it is what found it. **A chapter that adds
an argument to `attachSessions` owes an outsider test.** `gaps.md` item 8.

**VERIFY BY EXIT CODE, NEVER BY ABSENCE OF OUTPUT.** Three ways a check reads green without
running, all hit in one close-out: `pnpm -s` in the wrong repo returns 254 silently; a
pipeline ending in `tail` makes `&&` read `tail`'s status (this committed over a RED
checker); and `[ -z "$(git -C relay-platform status)" ]` prints "clean" when the path does
not resolve. **And the nine pinned lane variables apply to `pnpm coverage`, not just
`test:integration`** — two full lane runs were spent learning that, one of them predicted
verbatim by `quickstart.md`.

**`.resume()` IS A THIRD WAY TO THROW THE EVIDENCE AWAY** and the most deceptive, because it
looks handled: `stdio: "ignore"` never creates the output, an unread pipe leaves it in a
kernel buffer, `.resume()` reads it and discards it. It cost 3.21 its own battery failure —
run 8, `no ack within 5s`, **zero `"service":"gateway"` lines in the whole log**, with the
429 and `auth_degraded` theories both eliminated against green runs and the cause
undeterminable. **Five files still discard**: `isolation`, `limits`, `public-surface` pipe
and read nothing; `membership` and `presence` use `stdio: "ignore"`. Two of the five are the
files behind the open battery failures. `gaps.md` item 9.

**TWO PATTERNS IN ONE FILE DISAGREED ABOUT WHAT AN ID IS, AND THE CHECKER WAS THE WRONG
ONE.** `check-refs.py`'s `TASK` accepted `T\d{3}[a-z]?` and its `REF` refused the letter, so
it printed "no undeclared task ids" while `gaps.md` cited `T107a` two paragraphs above.
Widening it by one optional letter surfaced **six live citations in one run**. The sixth
instrument in that chapter to match the examples in front of it rather than the set the rule
names — and the first to under-report rather than cry wolf, which is worse.

**A TEST'S TITLE IS NOT CHECKED AGAINST ITS ASSERTION**, and 3.21's T098 found four of its
own: "logs it once" over a body proving five connection failures and zero publish ones,
"exactly the three names" asserting two, an `expect(true).toBe(true)`, and one test with no
`expect` at all.

**CHAPTER 3.20 IS CLOSED**, tagged `part3-ch20` in all three repositories. Its record is
`specs/038-chapter-3-20/` — read `chapter-notes.md` first, then `gaps.md` (**25 items**,
each with an owner and each reference carrying its chapter, because the numbers collide),
then `traceability.md` and `baseline.txt`.

    3.20 "the membership that changed under a live socket"
                                            9 files taught, 2,999 words, 27 fenced
                                            (18 the chain demanded + 9 new)
                                            31 files changed, re-derived from git diff
    two twenty-run batteries: 17/20 and 16/20 green
    lane mean 228.50 / 228.77, stdev 1.25 / 0.50, budget 240 — 11.2 s headroom
    43 files, 701 tests · gateway package 45.50 / 45.48
    coverage: all four new production files 100/100/100/100
    229 fenced files across 37 chapters, 37 translated · predecessor `d38f415`

**The fence predecessor for 3.21 is `git rev-parse part3-ch20^{commit}`, not the tag** —
it is annotated. And **nothing is pushed**: all three repositories are ahead of
`origin/main`, so the tag exists on one machine until somebody pushes it with the branches,
submodules first.

**FORTY RUNS, SEVEN FAILURES — AND "TWENTY GREEN" WOULD HAVE BEEN LUCK.** The observed
per-run failure rate is **17.5%**, which twenty green runs reject at 95% confidence. So
3.19's 18/20 and 3.17's 25/26 are consistent with this same rate and none of the three
batteries could tell them apart. Two mechanisms, neither in this chapter's code:

- **the rate limiter's fixed window is aligned to the wall clock.** `windowStart =
  Math.floor(now / windowMs) * windowMs`, and two tests in `limits.itest.ts` send three
  requests expecting the third to be refused. A boundary between the second and third
  resets the counter. Chapter 3.17 recorded this class with the mechanism unidentified; it
  is identified now. `gaps.md` item 19.
- **a gateway api fixture fails; one of the five is chapter 3.19's known case and four are
  not explained.** Run 19 repeated 3.19's run 10 exactly — `isolation.itest.ts`, the same
  `beforeAll`, `Hook timed out in 90000ms`, gateway package 101.21 s against that chapter's
  101.02. 3.19 named it: several files each spawn an api, vitest runs them in parallel, one
  api takes over ninety seconds to answer `/health`. **This chapter added the seventh
  spawning file and then recorded the failure as unexplained.**

  The other four — `session.itest.ts` ×3 with `ECONNREFUSED`, `presence.itest.ts` ×1 with
  `fetch failed` — have **three hypotheses measured and eliminated**: Postgres connection
  exhaustion (peak 50 of 100), a port collision (the failing ports are in each file's own
  range), and an undrained stdout pipe (Node buffers a full pipe in memory; an api spawned
  that way answered 4,000 requests). "Contention" was written into this file as the cause
  before any of that was checked. `gaps.md` item 19a.

  **The reason four are still open is that the evidence is thrown away**: all seven files
  either spawn with `stdio: "ignore"` or pipe and never read, so every failing api has
  already said why and nobody was listening.

- **AND A GREEN e2e PACKAGE IS NOT EVIDENCE THE RESUME SEAM HOLDS.** Chapter 3.6's flake 4
  was a real duplicate there — `expected [ 1, 2, 3, 4, 4 ]`, the backfill and the live
  flush both delivering sequence 4. Chapter 3.7 ran twenty clean and refused to call that a
  fix: the race needs a backfill to land between an api commit and a Redis publish, that gap
  widens under load, and 3.6's lane was slow only because 4,068 pending deliveries were
  being retried. **The defect did not get rarer; the conditions that exposed it went away.**
  3.7 demoted its own criterion in writing and moved the proof to tests that force the race.
  Deleting `suppressed(connection.marks, message)` still turns two of them red in ten
  seconds. `gaps.md` item 19c.

**TWO TASKS SPECIFIED AN ORDERING AS THE REQUIREMENT AND NEITHER WAS OBSERVABLE.** Both
asked for the proof that it bites — remove the ordering, watch a test fail — and neither
failed. Send-before-cut is unobservable because the notice goes to a socket reference the
function already holds; subscribe-before-insert because `subscribersOf` returning a
connection changes nothing while the instance is not subscribed. What FR-008 actually
forbids is deriving the audience **after** the mutation, which fails the first test in five
seconds. **A task claiming "the ordering is the requirement" is claiming an observable
difference, and that claim needs falsifying before the test is written.**

**A PUBLISHED SENTENCE STOPPED BEING TRUE AND NO CHECKER COULD SEE IT.** ADR-07's deep dive
says a lost pub/sub frame "is indistinguishable from a lost WiFi packet, and both heal
identically" — true of every payload that fabric carried when it was written, false of a
revocation, which has no sequence and no cursor. Found by grepping for a **claim** rather
than a symbol. `git diff` finds a changed sentence; nothing finds one that stopped being
true because the code moved underneath it.

**A ROUTE CAN BE THOROUGHLY TESTED AND COMPLETELY UNCOVERED.**
`GET /internal/memberships` had five integration tests and read **28.57% statements, 0%
branches** — that suite runs in the gateway package and the api's coverage is measured in
the api package. Ask where a route's coverage is measured, not just whether it is tested.

**AND THREE OF FOUR NEW FILES HIT 100/100/100/100 ON THE FIRST RUN**, because the phase
that built them listed the arms before writing them. Chapter 3.19 met its equivalents at
close-out and paid seven tests, a deleted branch and a re-measured battery.

**I DISTURBED MY OWN MEASUREMENT.** The first battery's run 1 counted 700 tests and the
rest 701, because a test was written into `outbox.itest.ts` while it was running. The rule
is that nothing else runs on the machine; editing a source file is worse than a stray
container, and the rule did not say so because nobody had done it.

**CHAPTER 3.19 IS CLOSED**, tagged `part3-ch19` in all three repositories. Its record is
`specs/037-chapter-3-19/` — read `chapter-notes.md` first (its close-out names the fence
predecessor and what the two red battery runs were), then `gaps.md` (**seventeen** items,
each with an owner and each reference carrying its chapter, because the numbers collide:
3.17's item 1 is a flake and 3.18's item 1 is the idempotency keys). Then
`traceability.md` and `baseline.txt`.

    3.19 "presence, and who is allowed to see it"  10 files taught, 2,445 words, 9 fences
                                                   11 files changed in the platform,
                                                   re-derived from git diff
    645 integration tests across 42 files, 18 of 20 full-lane runs green
    mean 228.18 s, stdev 1.41, budget 240 — 11.8 s of headroom
    coverage: gateway/presence.ts and protocol/presence.ts both 100/100/100/100
    221 fenced files across 36 chapters, 36 translated · fence predecessor `d38f415`

**The fence predecessor for 3.20 is commit `d38f415`, not the tag** — `part3-ch19` is
annotated, so `git rev-parse part3-ch19` returns the tag object and `^{commit}` returns the
commit. And **nothing is pushed**: all three repositories are ahead of `origin/main`, so the
tag exists on one machine until somebody pushes it with the branches.

**Four items in `gaps.md` are addressed to the next chapter rather than to nobody.** Item 2
is FR-RTM-10, now unmet on three paths — socket sends, REST sends and presence — and one
membership re-read in the session layer closes all three. Item 5 is nine translated chapters
absent from the sitemap, nine one-line edits. Item 8 is this feature's two checkers, which
die like 3.18's `sweep.py` unless somebody decides. Item 17 is six of the gateway's eight
integration files each spawning their own api, which is the mechanism behind the battery's
run 10.

**USE A PERSON is on its sixth chapter.** 3.18 made it runnable —
`specs/036-chapter-3-18/reader-protocol.md`, 45 minutes, six questions — and nobody ran it.
3.19's two most expensive findings were both prose: four published claims about presence that
nine analysis passes of tooling went past, and a test whose title claimed an arm it never
touched. Every check here compares bytes.

**A TEST'S TITLE IS NOT CHECKED AGAINST ITS ASSERTION.** *"logs presence.invalid_payload for
a payload that is not a transition"* asserted `toEqual([])` — a good test under a false name —
and both rejection arms of the module read zero coverage while it was green, through six
analysis passes and four phases. The coverage ratchet found it, and only because the pin was
100. Grep the test names for a requirement id and read the assertion under each.

**THREE 30-SECOND NUMBERS ARE THREE QUANTITIES**, and this is now shipped code rather than a
research note. `PING_INTERVAL_MS`, FR-RTM-06's grace period and the SAD's key TTL are all
30_000; a TTL equal to its refresh interval expires a connected user, so presence refreshes
at 10_000. And a fix can be worse than its bug: arming the grace check at exactly `graceMs`
puts two deadlines on one instant reached by two clocks, and the losing side strands a user
online for ever.

**CHAPTER 3.18 IS CLOSED**, tagged `part3-ch18`. Its record is `specs/036-chapter-3-18/`, and
3.19's `gaps.md` carries its items 1, 2, 3, 5 and 9 forward with their status re-checked —
its 4, 6 and 8 were 3.19's and closed or moved there.

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
