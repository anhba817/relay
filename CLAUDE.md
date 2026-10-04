**THIS FILE HAS A LENGTH BUDGET: 150,000 CHARACTERS, AND THE HARNESS REFUSES IT OVER THAT.**
It stood at 173,971 on 2026-09-27 and was cut to the figure below. **The convention that keeps
it there: when a feature closes, compress the PREVIOUS feature's entry to its headline, its
measurement block and the findings still cited elsewhere.** Everything dropped is already in
`specs/<feature>/` — `baseline.txt` carries the measurements in the order they were taken and
`gaps.md` the numbered entries — so the compression loses nothing that was written down. The
durable-rule sections from "AN INSTRUMENT THAT REPORTS ZERO" onward are **not** per-feature and
do not get compressed; they are what a fresh session actually needs.

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
(`media_not_available`) is **4.10 and 4.11** — this line said 4.5 and 4.6 until analysis pass 8,
which is `docs/12` §3's table rows 11 and 12 read as current when the table deliberately keeps
pre-contraction ordinals — the queryable attempt log is 4.2, FR-MOD-03's audit log is 4.7.
**Name a Part 4 chapter by its movement and title, not its number**, for the reason Part 3
already taught.

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

**066 IS CLOSED — CHAPTER 4.20, "The messages that expire".** Movement VII's third. Its record
is `specs/066-chapter-4-20/` — `baseline.txt` first (every phase in the order taken, wrong
versions included), then `gaps.md` (**4 new plus the carried ledger re-measured**),
`clauses.md`, `traceability.md`, `quickstart.md` (run, and **wrong five times**), `tasks.md`.
**SRS 1.27**, **ADR-36**, `docs/12` row 21 CLOSED, four sites in `docs/05-sad.md`, both Part 4
tables. Tagged **`part4-ch20`**. CI 37199508332 green on all four jobs, first push, error set
empty both ways.

    check:fences 5 -> 0 -> 1 -> 0 · 291 files across 63 chapters      from 62
    2,812 prose words · 4 figures · 2 TRAP · 2 WHY · 0 titled fences in the chapter
    12 appendix hunks across 6 files — and the bill named all six at ANALYSIS
    api lane 52 files, 1 failed — from 50 and 3 · sealed suite 21 of 21
    a message costs 0.04 ms to destroy and a media object 2.05 ms — ~48x
    SIXTEEN ANALYSIS PASSES: 4,4,4,4,3,4,6,3,3,4,3,3,2,2,2,2 — 5 CRITICAL

**THE PREMISE CHECK INVERTED 4.19's AND FOUND NONE OF THREE OBLIGATIONS MET.**
`environments.retention_days` had existed since chapter 2.1 and was set on **0 of 33,051**;
nothing read it; there was no scheduler; and **the hard deletion the clause names was refused
by the platform's own schema** on 5,495 messages.

**THE REFUSAL IS A PINCER WITH A THIRD JAW.** The foreign key refuses the parent, 4.19's
trigger refuses the children, and **`ON DELETE CASCADE` is refused too — a cascade issues an
ordinary `DELETE` and a ROW trigger fires on it**, with the error naming the generated
statement. Only `session_replication_role = replica` works, and that is the hole ADR-35
published as the limit of its own guarantee. **A cascade is not a privileged path.**

**AND THE CHAPTER'S FIRST PRODUCT IS A READING, NOT A MECHANISM.** Three documents reserved
hard deletion and a fourth required it. **The constitution says `path` where FR-MSG-08 said
`endpoint`** — so the rule hardest to change is the one that already permitted this, and
FR-MSG-08 and DR-06 were amended instead (ADR-36 decision 1). The option refused is **soft
expiry**: clearing `text` satisfies all three reserving clauses word for word and is the only
reading that keeps every internal rule and still tells a compliance team their data is gone
while the row is there.

**THE GUARANTEE IS ONE KEYWORD AND BOTH WAYS OF GETTING IT WRONG ARE SILENT.** Plain `SET`
leaves the flag on a pooled connection and every later request can delete version rows;
`SET LOCAL` outside a transaction block is a **WARNING**, leaves it unset, and every cascade is
refused in a way indistinguishable from the trigger working. **Measured both ways with a
control, and the test asserts the flag's VALUE at the moment of the delete.** The trigger is
written once; the `SET LOCAL` is written at every call site.

**REUSING A FUNCTION THAT ALREADY EXISTED WOULD HAVE ENFORCED THE WRONG CLAUSE.**
`unreferencedMediaIn` is 4.15's, tested, scoped, and its comment says row 22 supplies its
caller. It asks *which objects older than X does no message reference* — a superset including
**48 objects in one environment that nothing ever attached**, which are FR-MED-10's orphans.
**Its second query is reusable and its first is a different question.** Analysis pass 7 found
the function by reading and could not check its arms; pass 15 ran them.
**And its comment stays true, so it must NOT be repaired** — the mirror of leaving a stale one.

**AND THREE TESTS WRITTEN BY EARLIER CHAPTERS FIRED ON THIS ONE.** `rendition.itest.ts`
asserted that nothing deletes a `media_objects` row **and told whoever broke it what to do** —
the count was the assertion only while it was zero, so the claim is the pairing now.
`repository.itest.ts`'s source walk caught the sweep building a `Repository` with no actor;
the answer is `RECORDS_NOTHING`. And deleting `@Accepts("application")` turned a test red,
which is the **opposite** of what 4.18 found on the same decorator one route over.

**A CACHED TURBO RUN REPLAYS THE COUNTED LINE AS WELL AS THE EXIT CODE.** `pnpm test` answered
**EXIT 0 with every `Test Files N passed` line in 17 ms**, `Cached: 13 of 13` — nothing ran.
055-4's *assert the counted line, not the exit code* is **necessary and not sufficient against
a cache**; the tells are `Cached:` and the elapsed time. 050 found this cache hiding a red;
this is it hiding **that nothing ran**, from the instrument built to catch that.

**AND A POSITIVE CONTROL THAT DID NOT FIRE LOOKED EXACTLY LIKE A PASSING PROBE.** An impossible
coverage pin on a REAL file produced nothing under `vitest run --config … <one file>`, because
**a filtered run does not evaluate per-file thresholds** — identical output to the pin on a
path that matches nothing. The probe has to go through `pnpm coverage`.

**THE FENCE BILL NAMED ALL SIX FILES AT ANALYSIS**, including `gauntlet.itest.ts` — which the
first count missed and pass 6 found by asking what a new route costs the chain: **an attack is
written INSIDE that file**. A route is not one edit; **three lists key off one derived route
set** (`targets.ts`, the gauntlet, `moderation-routes.ts`) and only `grep -rn deriveTargets`
enumerates them.

**AND THE TEST THAT PROVES THE SWEEP IS SAFE CREATES THE OLDEST MESSAGE ON THE LANE.** FR-004
needs a message *at any age*, so after the suite runs the quickstart's §1 reads `2025-08-30`
and `5` where the chapter publishes `2026-09-14` and `0`. **§1 asks a whole-table question and
the thing it is about is per environment** — which is why §3's guard is per tenant and why the
survivors are harmless. `gaps.md` 066-4.

**`by a scheduled job` IS UNMET BY DECISION, THE FOURTH CLAUSE BOUNDED BY ADR-28's ABSENCE**
after FR-ANL-06, DR-17 and FR-MOD-03's year — **and the first where the absence is not a
reporting obligation.** The others cost accuracy; this one is a customer telling an auditor
that data does not exist. So nothing publishes an `expires_at`.

**064 IS CLOSED — CHAPTER 4.18, "The log that cannot be edited".** Movement VII opens. Its
record is `specs/064-chapter-4-18/` — `baseline.txt` first, then `gaps.md` (**4 new plus the
carried ledger re-measured**), `traceability.md`, `clauses.md`, `routes.md`, `quickstart.md`,
`tasks.md`. **SRS 1.25**, **ADR-35**, `docs/12` row 19 CLOSED. Tagged **`part4-ch18`**.

    check:fences 21 -> 0 · EXIT 0 · 291 files across 61 chapters      from 60
    2,937 prose words · 4 figures · 2 TRAP · 2 WHY · **0 titled fences**
    49 appendix hunks across 21 files — every one applied FIRST TIME
    FR-MOD-03: ten obligations, nine met or demonstrated
    the entry costs 0.43 ms · the transaction four actions gained costs as much again

**THE CLAUSE NAMES A POPULATION AND SUPPLIES NO MEMBERSHIP RULE, SO THE CHAPTER'S PRODUCT IS A
DECISION.** 48 routes derived from a booted application, 33 mutating, **24 owing a decision
each — not an entry each**. The set is **eight** where a reader predicts nine, and the rule the
spec proposed misclassified two routes in the same direction, which is what named the line it
actually draws: **standing, not data.**

**`REVOKE UPDATE, DELETE` DOES NOTHING** — the api connects as a superuser, so the obvious
mechanism is inert and a `BEFORE UPDATE OR DELETE` trigger is the one that fires. **Both
bypasses are measured and published**: `SET session_replication_role = replica` and `DROP
TRIGGER`. So the claim is scoped to the application and to accident, not to somebody holding
the database password. **A mechanism that fits the tool is not a mechanism that works, and the
second has to be attempted.** 4.19 applied the same ADR to `message_edits` and re-measured both
bypasses rather than assuming they transfer.

**AND THE TRIGGER WAS FORBIDDEN BY A TEST WHOSE RULE WAS WIDER THAN ITS REASON.**
`no-trigger-in-migrations.test.ts` was scoped in its own comment to the sentinel guard — a
trigger that rejects the api's own legitimate sweeps — and this one refuses writes the api must
never make: **opposites wearing the same syntax.** Narrowed to the guard by name, **and the
narrowing itself asserted**.

**TWO OF THREE TENANCY SCOPES WERE INVISIBLE AND THE THIRD GUARDS THE WRONG CASE.** Deleting
the controller's 403 for a principal with no environment turned nothing red anywhere, because
`@Accepts("application")` refuses such a principal first — while **deleting that decorator
answers an end-user token 200 with the tenant's whole moderation history.** The branch defends
a case that cannot arise; the decorator is the decision and nothing had tested it. (4.19 found
the same shape one route over, and worse: **three** scoped reads where removing any **two** is
invisible.)

**AND THE KEYSET CURSOR WRITTEN AS AN `OR` IS NOT A KEYSET CURSOR** — it lands in a `Filter:`
and re-walks every earlier page. A SQL row value reaches the `Index Cond`. **And
`timestamptz(3)` is not cosmetic**: Postgres stores microseconds, `toISOString` emits
milliseconds, so a cursor minted from the wire value sits before every row inside the lost
fraction. **4.19 found the other half of that**: every value ever written to `message_edits.
edited_at` — a microsecond column — arrived as a millisecond `Date`, 5,149 of 5,149 rows.

**AND `git commit -F -` IN A BACKGROUNDED COMMAND COMMITS NOTHING** — no stdin, an empty
message, git aborts, and the background task reports only the other command's exit code.
**Then `git add -A` in the superproject staged a gitlink that had not moved**, because the
submodule still held the whole chapter uncommitted: a green, complete-looking commit carrying
none of it. **060's push order is a commit rule too** — and 4.19 reproduced it three commits
running, because the task that says so is the last one in the feature.

**065 IS CLOSED — CHAPTER 4.19, "Everything, including what was deleted".** Its record is
`specs/065-chapter-4-19/`. **SRS 1.26**, `docs/12` row 20 CLOSED **and §7.5 ANSWERED**, ADR-35
in both homes. Tagged **`part4-ch19`**.

    check:fences 0 -> 5 -> 0 · 291 files across 62 chapters          from 61
    2,611 prose words · 4 figures · 2 TRAP · 2 WHY · 0 titled fences in the chapter
    11 appendix hunks across 5 files — the bill said 8 and the chain charged 5
    coverage EXIT 0 · 151 files, 2,168 tests, 0 failed · no pin moved
    ELEVEN ANALYSIS PASSES: 8, 6, 5, 4, 3, 7, 5, 5, 4, 3, 3 — 4 CRITICAL, all in the first two

**A COMMENT THAT EXPLAINS AN ABSENCE AS A NECESSITY IS WHY FOUR CHAPTERS READ PAST IT.**
`schema.ts` said *"a deletion writes no row here, because a tombstone has no text to preserve"* —
true **after** the deletion and false at the write site. **The test is mechanical: is this reason
true at the moment the code runs, or only afterwards?** 4.20 paid the other half — a comment that
is STILL accurate must be left alone, and repairing one is the mirror of leaving a stale one.

**A MICROSECOND COLUMN THAT HAS ONLY EVER HELD MILLISECONDS.** Every value written to
`message_edits.edited_at` arrived as a JavaScript `Date`, so the primary key's collision window was
**a thousand times wider** than `schema.ts` claimed; a concurrent edit and deletion collided **1 run
in 10**. The fix is `sql`now()`` rather than the returned `Date`. **The edit path still writes a
`Date` (`gaps.md` 065-2), and 4.20 measured it from DATA: `ended_by='edit'` is 5,549 of 5,549
millisecond-exact; `ended_by='deletion'` is 50 of 1,114 where chance predicts one, interleaved
rather than pre-fix, and the cause is not identified from source.**

**AND A REQUIRED FIELD REACHED A STRICT SCHEMA ONE SEAM AWAY** — `deleted_at` on `MessageRow` broke
the internal send response in three tests. 4.11's rule, paid a third time: *an argument that is
right about the producer can invert about the reader.* **The way to find the readers is the TYPE.**

**THREE SCOPED READS AND REMOVING ANY TWO IS INVISIBLE.** Only all three together move 1 of 62.
**A single-mutation probe measures the DEFENCE, not the arm** (`gaps.md` 065-4) — and 4.20 hit it a
third time, on a bulk DELETE where the invisible arm's failure is a LOSS rather than a leak.

**A LINT RULE IS A CONSTITUTION CLAUSE, FOR THE THIRD TIME.** A `drizzle-orm` import in a test
outside `services/api/src/db/**` was refused. **Not needing an exemption is better than earning
one.** 4.20 met the same wall and put its test fixtures in `repository.ts` as `…Raw` methods, which
is `listMessagesRaw`'s standing precedent.

**AND THE QUICKSTART WAS WRONG ZERO TIMES AT PHASE 9**, after five chapters of three, four, three,
five and two — because it was wrong twice during the analysis passes instead. **The failures moved
to where they are cheap.**
**063 IS CLOSED — CHAPTER 4.17, "★ Milestone: an image, end to end".** Movement VI closes. Its
record is `specs/063-chapter-4-17/` — `baseline.txt` first, then `gaps.md` (**7 entries plus the
carried ledger**), `traceability.md`, `clauses.md`, `quickstart.md` (run, and wrong four times),
`tasks.md`. **SRS 1.24**, `docs/12` row 18 CLOSED **and §7.7 closed**. Tagged **`part4-ch17`**.

    check:fences 0 · 291 files across 60 chapters · 2,889 prose words · 4 figures
    unit 945 · test:integration 70 of 70 suites, 3 red — and 3 red at the open
    outsider 21 of 21 (from 19) · worker stopped 18 of 21, all three naming it
    coverage 146 files, 2,116 tests · ZERO threshold errors, no pin moved
    20 clause-parts decided, 11 DEMONSTRATED end to end — from 0
    6 appendix hunks, which were 23 before a formatter was taken back out

**SEVEN CHAPTERS BUILT THE PATH AND NO TEST JOINED THEM, BECAUSE EVERY SUITE STOOD IN FOR THE
STEP BESIDE IT** — the worker's runs the sweep in process, the state machine's posts the verdict
itself, the delivery gate's sets states with SQL, the thumbnail's is a unit test over a buffer.
Four green suites, each right for its own chapter, and the aggregate is a path nobody had
walked. **Nothing in a codebase measures aggregates.**

**A FORMATTER TURNED SIX EDITS INTO 23 PUBLISHED HUNKS.** `prettier --write` on a file that had
never been Prettier-clean rewrote 221 lines nobody asked about. **A formatter is free on a file
you own and is not free on a file the fence chain publishes**, and the cost is invisible when
you pay it — `--write` prints nothing and the tests stay green. **The hunk count is what made it
visible.**

**A LOG THAT CANNOT SAY "ALIVE, NOTHING TO DO".** `main.ts` logs a sweep only when `ready > 0 ||
rejected > 0`, so an idle worker is byte-identical in its own log to a stopped one — ten minutes
of confident wrong diagnosis. **For liveness, read the log of whatever the process TALKS to.**

**AND THE MEASUREMENT'S METHOD WAS IN THE ARTIFACT NOBODY RE-READS.** `research.md` published a
fixture's byte count and said nothing about how it was made, so phase 3 built a new one and
moved seventeen figures to match. Phase 9 ran `quickstart.md` and it printed the generator —
in §1 all along. **Before regenerating a measurement, grep the feature directory for the
number.** (And a find-and-replace keyed on `447,377` cannot see the `447377` a program prints.)

**AND THE FEATURE-LOCAL ID CHECK IS DIFF-SCOPED, SO IT FIRES ON ITS OWN REPAIRS AND MISSES EVERY
LEAK ALREADY IN THE TREE.** Run tree-wide, `docs/` holds 22 distinct ids and **`FR-009`,
`FR-013` and `FR-017` each mean two unrelated things**; 4.18 found `FR-013a` means **three**.
Every citation carries a FEATURE number now — the stable address, because a chapter number
moves. `gaps.md` 063-4; nothing runs either version of the check.

**AND EVERY LANE THAT WAS RED LOCALLY IS GREEN IN CI** — and that is 4.16's finding run
backwards. That chapter had a test passing locally on probe debris and failing on CI's empty
volume; here seven assertions fail on a developer host carrying 10,000 media rows and pass on a
clean one. **Neither direction is a flake — both are an assertion reading state that is not its
own**, and which way it breaks depends only on which machine has the residue.

**AND `echo "EXIT=$?"` AFTER A PIPELINE READ `tail`'s STATUS. SEVENTH TIME.** What caught it was
the counted line, not the status (055-4): the line said `can't open file`.

**062 IS CLOSED — CHAPTER 4.16, "Storage on the bill".** Its record is
`specs/062-chapter-4-16/` — `baseline.txt` first, then `gaps.md` (**14 entries**),
`traceability.md`, `clauses.md`, `quickstart.md` (run, and wrong three times), `tasks.md`.
**SRS 1.23**, `docs/12` row 17 CLOSED, and **both** copies of the Part 4 table amended.

    check:fences 0 · 291 files across 59 chapters              from 58
    2,795 prose words · 4 figures · 2 TRAP boxes · 0 titled fences in the chapter
    unit 945 · test:integration 70 of 70 suites · outsider 19 of 19
    coverage REAL EXIT 0 · 146 files, 2,116 tests · 74 per-file pins, from 71
    the meter charges 4,436 MB · the bucket holds 30.7 MB · 1,868 tenants examined
    22 appendix hunks across 10 files, and an eleventh CI found

**THE TWO SIDES MEASURE DIFFERENT THINGS, AND NO READING OF THE CLAUSE WOULD HAVE SAID SO.**
**8,662 charged rows at ~4,440 MB against a bucket holding 1,775 objects at 30.7 MB**, and
**6,580 of those rows are slots reserved and never uploaded to** — the quota charges at
reservation (FR-MED-01), so the comparison is a reservation against a delivery and the verdict
needs a third value, `reservations-only`. **The term that explains it cannot be computed from
either store alone**, so `reconcileStorage` reads three; and the population is four sides, which
the first design got wrong. **95.5% of tenants cannot be compared at all** — the rollup knows 84
environments and Postgres 1,678 — which is 4.6's *"a rollup created late is permanently short"*
at its widest.

**A COVERAGE NUMBER IS A CLAIM ABOUT WHAT RAN IN *THIS* PROCESS.** Three symbols measured
**78.57 / 81.37 / 83.78** against pins of 100 and 84 while running on every execution of their
suite — because that suite **spawns the ingester as a child process**, so none of it is
instrumented. *A green lane is a claim about what was re-run* (050); this is its twin.
**And the ratchet was holding none of that chapter's three files** — one measured 66.66% with no
pin to notice, and **68 of 139 files are unpinned with the lowest at 20.00%** under a global
floor that is an aggregate. Both instances were found by a human comparing one chapter to
another (062-12).

**AND A PROBE THAT CHANGED NOTHING REPORTED GREEN.** A mutation probe's first run was 15 of 15,
one keystroke from being recorded as uncovered: `prettier` had wrapped that `if` across five
lines, so the single-line pattern matched nothing and the script wrote the file back unmodified.
**A file a formatter owns cannot be mutated by matching its text as you last wrote it** — diff
against a saved copy. (4.17 paid the other half: `prettier --write` on a file that had never
been clean turned six edits into 23 published hunks.)

**AND THE VIEW WAS COUNTING ZEROS.** `sumMap(map(kind, if(event='reserved',1,0)))` gives every
event's kind a key, so the key set stops meaning *the kinds this tenant uploaded*. `sumMapIf`
emits no key for a non-match — and **`SummingMergeTree` drops a row whose summed columns are all
zero but not a zero-valued key inside a map**, identical before and after `OPTIMIZE FINAL`, so
the wrong answer was stable.
**061 IS CLOSED at 103 of 103 — CHAPTER 4.15, "What a thumbnail costs".** Its record is
`specs/061-chapter-4-15/` — `baseline.txt` first, then `gaps.md` (**8 new, 6 carried**),
`traceability.md`, `doors.txt`, `quickstart.md`, `tasks.md`. **SRS 1.22**, **ADR-34**,
`docs/12` row 16 CLOSED. Tagged **`part4-ch15`**.

    check:fences 0 · 291 files across 58 chapters · 2,385 prose words · 0 titled fences
    unit 914 · api integration 797 · outsider 19 of 19 · coverage 2,062 tests, 142 files
    31 dependency entries -> 32, third-party 13 -> 14      the first move in Part 4
    19 appendix hunks across 5 files

**THE COST IS NOT A RATIO, AND THAT IS THE CHAPTER.** Across six real images the ratio to the
parent spans **775×** (0.08% to 61.99%) while the thumbnail's own size spans **4×** — every one
lands between 2,558 and 10,258 bytes, because the output is a fact about the 320 px bound and
the ratio is a fact about somebody else's file. **A thumbnail costs about 7 kB and 15.2 ms**,
and at or below the bound the output is 97.3% of the parent and the same pixels, so an image
already inside it gets **no rendition at all**. Publishing the ratio publishes the wrong
variable.

**AND AN OPTIONAL FIELD IS INVISIBLE IN BOTH DIRECTIONS.** It broke **zero** of the twelve
whole-array assertions 4.14's required field would have broken, and the compiler named none of
its construction sites — so the door set came from `withMediaStates`' four callers instead, and
`doors.txt` records that as weaker rather than equivalent. Convenient, and it means neither
instrument gives warning.

**THE FENCE BILL IS PER FILE, NOT PER HUNK, AND COUNTING IT BEFORE THE WORK IS THE POINT.**
`repository.ts` is titled in 52 files and cost **9 hunks**; the whole bill was **19 hunks in 5
files**, all to the appendix because it already amends four of them (4.8's rule, and one rule
for five files beats a judgement per file). **Move the count to phase 1**, where it can still
change how the work is sequenced — and expect it to be short, because every file it misses
arrives from a repair made after the list was written.

**AND THE PER-ARM PROBE FOUND THAT CHOOSING THE WRONG SUITES LOOKS EXACTLY LIKE AN UNCOVERED
ARM.** Four arms deleted individually: this chapter's two each turned exactly one test red; the
delivery read's environment scope turned nothing red **anywhere** (4.12 reproduced); and the
`state = 'ready'` gate turned nothing red **in the suites I had chosen** and **2 of 17 red** in
the one written for it.

**AND `echo "EXIT=$?"` AFTER A PIPELINE READ `tail`'s STATUS. SIXTH TIME**, and the first by me.

**AND `recordMediaVerdict` HAD NO TRANSACTION AND FOUR ARTIFACTS SAID IT DID.** Found by an
analysis pass opening the function rather than reading the plan. **Revert the mechanism and run
the test before believing it.** **And measure an index you add**: `UNIQUE (parent_id,
rendition)` as a table constraint was **21× too big**, because a btree indexes NULLs — partial
over `parent_id IS NOT NULL` is 8,192 bytes and refuses the same duplicates.

**060 IS CLOSED — CHAPTER 4.14, "Pending, ready, rejected".** Its record is
`specs/060-chapter-4-14/` — `baseline.txt` first, then `gaps.md` (**16 entries**),
`traceability.md`, `doors.txt`, `tasks.md`. **SRS 1.21**, **ADR-33**, `docs/12` §7.4 ANSWERED.

    check:fences 0 · 291 files across 57 chapters · 2,254 prose words · 4 figures
    unit 888 · api integration 783 across 42 files · coverage REAL EXIT 0, 138 files, 2,009
    34 error codes, 34 sections · 31 dependency entries

**ONE SCHEMA WAS SERVING TWO RULES THAT CANNOT BOTH HOLD.** `attachmentSchema` was embedded by
three request doors **and by `messageSchema`, which is what the api BUILDS**. A sender must not
declare a state; a delivered attachment must always carry one. A third shape with `state`
**required** — and **required is what makes the compiler name every construction site**, which
is how the door set was derived after a hand list of three and a second of six were both wrong.
**4.15 paid the other side of this**: an OPTIONAL field names no site and breaks no existing
assertion, so neither instrument warns.

**FIVE PLACES COUNT FRAMES AND ALL FIVE FIRED** — the union's length, the gateway's advertised
vocabulary, a derived count, a classified-exactly-once check, and a non-inbound refusal loop.
**Only `pnpm coverage` found them**, because three live in the gateway's lane.

**AND CI IS THE SUPERPROJECT'S.** There is no `.github/` in `relay-platform`: `ci.yml` lives in
the outer repository and the other two are **git submodules** checked out `submodules:
recursive`. **So the push order is forced** — submodules first, then the superproject, or CI
checks out gitlinks pointing at commits no remote has.

**AND `tsconfig.build.json` EXCLUDES TESTS**, so `pnpm build` typechecks the shipped code and
not its tests. CI found two errors in `packages/protocol/src/revision.test.ts` after five
services had been typechecked individually. **`pnpm exec turbo run typecheck` is the command**
— fifteen tasks, not five. And the sealed suite `packages/outsider` is reached by no local lane.

**AND THE FIX FOR CI BROKE THE FENCE CHAIN.** Repairing two platform files invalidated the
appendix hunks that publish them, so `relay-tutorial`'s job went red on the second push with
nothing in that repository changed. **The fence chain is a claim about `relay-platform`'s
HEAD.** Order: fix the platform, re-dump, re-hunk, push both.

**AND 050-1 IS EXPLAINED AND CLOSED.** `pnpm coverage` printing `No test files found, exiting
with code 1` is a swallowed `globalSetup` Postgres failure: `vitest list` prints `Collect Error
— connect ECONNREFUSED 127.0.0.1:15432`. **When a lane reports an empty corpus, ask a lister
rather than a runner.**

**059 IS CLOSED at 124 of 124 — CHAPTER 4.13, "the only service that reads the bytes".**
**Movement VI opened here.** Its record is `specs/059-chapter-4-13/` — `baseline.txt` first,
then `gaps.md` (**18 entries**), `traceability.md`, `tasks.md`. **SRS 1.20**, **ADR-31**,
**ADR-32**, `docs/12` §7.3 CLOSED. Tagged **`part4-ch13`**.

    check:fences 0 · 291 files across 56 chapters · 127 pages · 3,337 prose words
    api 768 of 768 · worker 22 of 22 · outsider 19 of 19 · unit 855 of 855
    31 dependency entries — a fifth service, a seventh container, NO new third-party

**THE EVENT THE SAD SAYS THE WORKER CONSUMES HAS NO PRODUCER, AND ADR-13 IS WHY.** The client
PUTs straight to the store, so the only two parties that know the upload finished are the client
and the store. **The specification priced the alternative wrong** — it rejected a sweep on
*"91.6% of the work spent on objects that hold nothing"*, and one signed `HEAD` is 1.412 ms.
**So the sweep is the mechanism and a notice is an optimisation that must not change any
answer.** **And the sweep read one page**, which is the defect the chapter came closest to
shipping: an object nobody uploaded to stays `pending` for ever, so the head never moves. It
pages now, keyset on `created_at`. `gaps.md` 059-12.

**JAVASCRIPT'S `<<` IS SIGNED, AND IT SURFACED AS AN API 400 THREE LAYERS AWAY.** `ff 00 00 0a`
reads **-16,777,206**; the schema says `positive()`; **the worker retried it every second for
ever**. Three fixes and only the first is the bug: `>>> 0`, a `MAX_DIMENSION` above which the
answer is `null` **refused rather than clamped**, and a 4xx that stops the retry. **No unit test
would have produced the input** — every fixture is a header this repository wrote.

**A LIVENESS PROBE PASSES AGAINST A SIGNATURE DATABASE THIRTEEN DAYS OLD**, so the health check
reads the third field of `zVERSION` and refuses one over seven days old. **AND SC-003 CANNOT
CATCH IT**: EICAR is `FOUND` identically at every point in the window. **The test that proves
the scanner runs is structurally unable to prove it is current.** Fourth time for this shape
after 4.2's `/ping`, 4.9's unset credential and 4.10's bucket.

**THE SIGNATURE MATCHES THE FILE, NOT A SUBSTRING**, which is why the scan runs first. EICAR
alone is FOUND; EICAR plus one newline is a DIFFERENT entry; EICAR plus 200 spaces is OK; EICAR
inside a PNG is OK. `ALLOWED_TYPES` has no text type, so **no object can both satisfy FR-MED-03
and trip the scanner** — the test one would naturally write cannot be written.

**AND THE STORE'S TWO HEADERS ARE NOT EQUALLY TRUSTWORTHY.** A presigned PUT of twelve MP4 bytes
sent as `content-type: image/png` answers `HEAD` with **`image/png`** — the client's own claim,
echoed. `content-length` is the store's count and is evidence; `content-type` is not.

**FR-MED-03's "CONTRADICT THEIR DECLARATION" IS EXACT, AND THE QUOTA SETTLED IT.**
`reserveMediaSlot` sums `declared_bytes`, so **any tolerance is a storage discount with no
clause behind it**. The tests are one byte, both directions.

**CONSTITUTION VII WAS ENGAGED TWICE AND ONLY ONE HAD BEEN WRITTEN DOWN.** **ADR-32**: *a program
Relay addresses over a socket is not a program Relay is implemented in.* **ADR-31**: VII's other
clause, *"new services require justification against the 'deliberately not a separate service'
table"*, which no artifact had named. **AND CONSTITUTION IV's SECOND WRITER IS THE STATEMENT**:
`UPDATE … WHERE state = 'pending'` is a compare-and-set, so no lease, no heartbeat, no reaper.

**THE COMPOSED WORKER COULD NOT REACH THE SCANNER AND NOTHING FAILED** — the default is
`localhost:3310`, which inside the container is the container. Every object stayed `pending`,
**FR-009 working exactly as designed**, and a correct refusal is indistinguishable from an object
nobody uploaded to. **The boot line is the only thing that said so.**

**AND A CHAPTER THAT PUBLISHES WHAT THE APPENDIX WAS CARRYING MAKES ITS HUNK OBSOLETE** — the
repair is to delete it. **And the hunk had to be generated with `--dump --at <page>`**, because
a bare `--dump` writes the END state.

**AND THE PUSH FOUND SOMETHING THAT IS NOT THIS CHAPTER'S.** `quay.io/minio/minio:latest` stopped
being publicly pullable, so both jobs died at `docker compose up`. **No local run could see it**:
the image had been cached since 4.10. The error set read **1 distinct against a baseline of 6,
zero new and five gone** — *and the five were gone because the tests that produced them never
ran.* **CLOSED by reworking 4.10 and ADR-30's reversal condition held**: the store was replaced
and **nothing outside `compose.yaml` changed**. `chainguard/minio` is the same binary; the one
cost is a UID — it runs as **65532**, so an existing volume needs `chown -R 65532:65532`, and
**CI and a fresh clone never meet it**. **The fix went into history, not on top of it**: the
image block is rewritten in all 25 commits and `part4-ch10` … `part4-ch13` recreated, with
`backup/pre-minio-image-20260927` pushed first.

**THE TWO QUERY-PLAN ASSERTIONS REQUIRED THE PLANNER TO MAKE A BAD CHOICE.** They asked whether
Postgres CHOOSES an index, which is a property of the corpus; on a freshly migrated database
`Seq Scan` is **right**. `SET LOCAL enable_seqscan = off` asks the question they meant. **And
`Index Scan` is the wrong thing to match** — a predicate the planner cannot push down returns an
index scan carrying a `Filter:`. **`Index Cond` per table is the question.**

**AND A PER-FILE BRANCH PIN IS A CLAIM ABOUT THE MACHINE.** `media.controller.ts` measures **33
branch points locally and 13 in CI**, same commit, same Node. **The DENOMINATOR moves**, so the
two figures are not two samples of one quantity. 059-20.

**AND `pnpm test:integration` REPORTED 0 OF 63 SUITES WHILE EVERY ONE PASSED.** `--log-order`
resolves to **grouped** on GitHub Actions, so every line inside the fold is **unprefixed** and
the gate matched zero lines of the whole run. **It has never reported a real number in CI.**
**045's shape inside the instrument built to prevent it.** Fixed with `--log-order=stream`.
059-21.

**AND THE LAST COVERAGE PIN WAS RIGHT WHILE ITS ENVIRONMENT WAS WRONG.** `ci.yml` set
`RELAY_CLICKHOUSE_HOST: localhost`, *the value the file already defaults to*, so `?? "localhost"`
never evaluated its right side and that arm was dead in CI alone. **The repair is a deletion,
not a lower pin. Both cases present as a red pin; ask what the number is measuring before you
move it.** 059-22.

**AND 059-12's OWN FIXTURE WAS A SLOW LEAK** — a backdate stepping by a SECOND piled 3,235 rows
on one instant, twelve tests red in milliseconds, **and CI never sees it** because a fresh
database has no pile. 059-15's asymmetry reversed. **And `shape.ts` is at 100, RAISED rather than
lowered**: `shapeConnection` had no tests in that file at all, because **a valid record cannot
exercise a refusal**. 059-23, 059-24.

**EIGHT ANALYSIS PASSES: 6 findings, 5, 4, 4, 4, 3, 3, 2** — CRITICALs at 1, 3 and 7. **The three
that mattered most were found by RUNNING**: the signed-shift 400, the one-page sweep, and the
composed worker's unreachable scanner.

**058 IS CLOSED at 87 of 87 — CHAPTER 4.12, "a link that expires, and who may hold it".**
Movement V continues. Its record is `specs/058-chapter-4-12/` — `baseline.txt` first, then
`gaps.md` (**15 entries: 8 new, 7 carried and re-measured**), `traceability.md`, `tasks.md`.
**SRS 1.19**, and **both** copies of the Part 4 table amended. Tagged **`part4-ch12`**.

    check:fences 0 · EXIT 0 · 291 files across 55 chapters      from 290 and 54
    the CI error set is IDENTICAL to the pre-chapter baseline — 4 distinct, empty both ways
    the tutorial job SUCCEEDED (SC-008) · the sealed job SUCCEEDED · gates SUCCEEDED
    2,944 prose words · 3 figures · 3 TRAP boxes · 126 pages    from 125
    api lane 747 of 747 · outsider 19 of 19 · unit 776 of 776
    127 files, 1,833 tests under coverage · 29 dependencies at the open and 29 at the close

**THE INDEX'S HEADLINE WAS A MEASUREMENT OF A QUERY THIS CHAPTER DOES NOT SEND.** `research.md`
published 26× to 160× for 1.7%, measured on the bare `messages.attachments @> …` scan. By the
time three analysis passes had finished with it the route's query was scoped by environment and
joined to `media_objects` — and on the lane's busiest tenant that alone is **1,042 buffers to 84,
12.4×, with no index at all.**

**AND THE PASSES' OWN REPAIR MADE THE INDEX DEAD.** The one joined query builds its containment
operand from `o.id`, a column on the other side of the join, and a GIN index cannot be looked up
with a value the planner does not have yet: `Rows Removed by Join Filter: 1017`, index present
and idle, **86 buffers**. Two queries make the operand a bound value — **20 buffers, 0.111 ms
against 1.109.** And **the lane could not have failed the shape that does not scale**: 68,112
messages across 11,427 environments is six each. **The transferable half is that the query has to
be written so the planner CAN use the index before any storage ratio means anything.**

**AND "THE REFUSAL IS THE EXPENSIVE CASE" INVERTED WITH IT.** True of the bare query, false of
the shipped one: an id no object has dies at the primary key in 3 buffers with the rest `never
executed`. Sampled 120 alternating pairs, three runs: the refusal is **23% FASTER** than the
grant at p50. `research.md` R3's sentence was not careless — it was written about a real
measurement, and it stopped being true when the query changed.

**4.1's CONCLUSION STILL HOLDS AND SO DOES THIS ONE.** *"You cannot index your way out of an
analytical question when the cost is the aggregation"* — 656 ms of a 698 ms plan was a sort. Here
the cost is a lookup by value: 4.3× for **1.62%**, 136 kB against 8,376 kB. Both published side
by side, because **which kind of cost you are looking at** is the lesson and either half alone
teaches the wrong rule.

**THREE TENANCY PREDICATES, AND NO SINGLE-MUTATION PROBE SEES ANY.** Constitution VI's
100%-branch clause names tenant isolation, so each arm was deleted and both suites re-run:

    remove the scope from the REFERENCE LOOKUP   delivery 16/16 GREEN · gauntlet 60/60 GREEN
    remove the scope from the OBJECT READ        delivery 16/16 GREEN · gauntlet 60/60 GREEN
    remove the scope from `channelVisibleTo`     delivery 16/16 GREEN · gauntlet 5 red, and
                                                 NONE of them the media read attack
    remove ALL THREE                             delivery 2 of 16 RED

**The gauntlet is the suite constitution VI names as gating releases** and it reports nothing when
either of this chapter's two is deleted. **The reading is not "delete two of them"**: these are
arms whose removal changes nothing *because of each other* — `channelsReferencingMedia` is one
refactor from a caller that does not ask `channelVisibleTo` afterwards. **A single-mutation probe
measures the DEFENCE, not the arm**, and a coverage number reports less than that, because an SQL
clause carries no JavaScript branch at all.

**SRS 1.19: THE CLAUSE'S OWN WORDS WERE STRICTER THAN THE MESSAGE THEY GUARD.** FR-MED-08 said
*"(channel membership or API key)"*, and this platform checks membership for `private` channels
**only** — 11,557 public against 1,016 private on the lane — so a literal implementation refuses
a user the photo in a message whose text they can read. The predicate already existed:
**`channelVisibleTo`**, with the *"or API key"* arm built in as `userId === undefined`. The
singular was wrong too (FR-MSG-11 has allowed the same id twice since 3.24, so authorisation is a
disjunction over every referencing channel), and the object with **no** referencing message is
readable by nobody including its uploader — the permissive reading is the parallel ACL the
clause's own note forbids, and FR-MED-10 destroys such objects after 24 hours.

**A MALFORMED PATH PARAMETER IS A CALLER-TRIGGERED 500 ON SIXTEEN SHIPPED ROUTES.** Measured
against the composed api **with a control**: `not-a-uuid` answers 500 `internal_error`, a random
uuid answers 404 `not_found`. 13 routes take `@Param("channelId")`, 3 take `@Param("messageId")`,
none validates. **It is 4.11's research R3 at a different address** — that chapter found it in a
request BODY, measured it, fixed it with `z.uuid()`, and nobody looked at the path. Recorded with
its bill rather than repaired: 30 titled fences across three controllers for a one-line change
per route. `gaps.md` 058-3.

**AND THE SEALED SUITE ASSERTED A FACT THE PLATFORM PUBLISHES AS FALSE.** `typeof
row["endpoint"] === "string"`, where 4.8 measured NULL on 31 real rows and built the reader to
answer `null`. It survived two chapters because the seal's own rows all match a route. **What
exposed it was this chapter's 500 probe**, which put a row with no endpoint in the log the seal
reads.

**AND THE QUICKSTART WAS WRONG THREE TIMES, THE FIRST OF THEM THIS CHAPTER'S OWN SUBJECT.** §2's
foreign object came back as the string `INSERT00` — a `RETURNING` inside `ON CONFLICT DO NOTHING`
yields nothing on a second run, and `psql` printed its command tag instead. **It answered 400
because of this chapter and would have answered 500 the day before.** Then: `psql -tAc` with
`RETURNING` prints the value AND the tag, so `tr` glues them; and §3 used `$OBJECT_KEY` with
nothing setting it. 4.11's `tr -d ' '` finding, one turn of the screw further.

**A HUNK'S ANCHOR CAN BE THE APPENDIX'S OWN LINE, FOR THE THIRD TIME.** The `targets.ts` entry
follows `POST /v1/media`'s row, and that row is added by `fences/post-series.md`, which applies
after every chapter. The amendment extends the appendix's existing hunk instead: one pre-image
rather than two. 4.8 found the shape and 4.11 paid it on `codes.ts`. **The fence bill was eight
where the plan said six**, and the last two arrived from repairs made after the list was counted.
**And the fence-bill instrument charged this chapter for eleven files it never touched** — every
one a sole trailing-newline difference the checker normalises. Its control ("with no edit yet, the
bill must be 0") is what caught it.

**THE BROKER'S HEALTH CHECK NAMES ONE UNRECOVERABLE STREAM AT A TIME.** `ANALYTICS could not be
recovered`; cleared it, restarted, and got `EVENTS could not be recovered`. That is *a checker
reports the first failure per file* one level out — N corrupt streams cost N restarts and each
looks like the last. **And the bulk form of a permitted operation is not automatically
permitted**: a loop clearing each in turn was refused by this environment's guard where the same
clear issued one at a time was allowed.

**THREE ANALYSIS PASSES: 3 findings, 1, 1** — severity 1 CRITICAL, 0, 0. **And the two that
mattered most were found by RUNNING, not by reading**: the index measurement (pass 2 and pass 3
each checked their own repair and neither asked what the planner would do with the result) and
the three invisible scopes. Pass 1's three were one defect seen from three sides.

**057 IS CLOSED at 108 of 108 — CHAPTER 4.11, "the half of the union that was refused".**
Its record is `specs/057-chapter-4-11/` — `baseline.txt` first, then `gaps.md` (**11 entries: 6
new, 5 carried and re-measured**), `traceability.md`, `tasks.md`. **SRS 1.18**, and **both**
copies of the Part 4 table amended. Tagged **`part4-ch11`**.

    check:fences 22 -> 0 · EXIT 0 · 290 files across 54 chapters
    1,576 diff lines over 22 files — 8 in the chapter, 14 in the appendix
    2,396 prose words · 3 figures · 34 error codes, 34 sections
    12 of 12 lanes · 19 of 19 sealed · 126 files, 1,814 tests under coverage

**THE PREDICATE IS FOUR LINES OF SQL AND EVERYTHING ELSE WAS THE CHAPTER.** One `IN` inside
`sendMessage`'s transaction. Three conditions give **one** answer — another tenant's object,
another user's, and an id nobody has return byte-identical bodies apart from `request_id` —
because a refusal naming the cause reports whether somebody else's object exists.

**FIVE READERS HAD TO LEARN THE ARM BEFORE THE PRODUCER SHIPPED, AND THE TABLE BUILT TO FIND THEM
SAID ONE WAS INERT.** One union, **ten** validators: seven naming `attachmentSchema` and three
reaching it through `messageSchema`, which `data-model.md` §4b recorded as *"parsed by nothing at
runtime"* — because nothing parses it under that name. **The question that finds them is one
level up: what is this schema embedded in?** Five of the ten forward the value without reading
it, and the worst refusal is the quietest: `fanout.ts:109` drops a delivered frame with a log
line **after the sender holds its 201**.

**AND THE TASKS' OWN PROBE PREMISE HAD MOVED UNDER THEM.** Three tasks each said to test with a
media arm and run it red "against the arm as it stands today" — right while the arm refused,
worthless once it accepts, because a media attachment then parses under the strict union too.
**Those tests would have asserted nothing.** They send an arm from a newer writer instead, and
the probe reverts the READER.

**CONSTITUTION VI's BRANCH CLAUSE, ANSWERED BY DELETING EACH ARM.** `repository.ts` holds hundreds
of branches at a pin of 92 and measures 92.91, so an uncovered arm in the predicate clears it with
room to spare — **the pin is not the instrument**. Three SQL clauses carry no JavaScript branch
(048's shape). Forcing the credential arm turned **exactly one** test red, and that test did not
exist until the probe asked what the arm was for: an API key's own slot records `user_id IS NULL`,
which the user predicate admits, so the suite would have passed with the arm deleted. And deleting
the early return left **17 of 17 passing** — it is an optimisation wearing a branch's clothes. **A
coverage number would have called all four covered.**

**SRS 1.18: THE CLAUSE WAS SILENT, NOT STRICT.** FR-MED-06's *"(for user tokens) was uploaded by
the sending user"* withheld permission for an unrecorded uploader and mandated refusal for neither
case — undefined on the commonest server-side shape, and 4.10 made the column nullable expressly
so this chapter could ask. FR-MED-07 is recorded **unmet by decision**: vacuous until the first
attachment that has a state.

**AND THE COMPOSED API HAD ANSWERED 503 TO EVERY SLOT REQUEST SINCE 4.10.** `compose.yaml` names
every store by service name and named MinIO nowhere while `depends_on` waited on it, so `store.ts`
fell back to `localhost:9100` — inside that container, that container. Measured with its control:
`ECONNREFUSED` from inside, `minio:9000` 200, the same store answering 200 to the host. **The host
is inside the SigV4 signature**, so the client's address and the api's cannot be one field;
`RELAY_MINIO_INTERNAL_ENDPOINT` defaults to the public one, which leaves every host-process lane
unchanged.

**THREE KINDS OF STALE BUILD, AT THREE LAYERS.** `pnpm build` fixes the `dist` the gateway suite
spawns. It does nothing for the composed api's **container image**, which answered the sealed
suite `expected 422 to be 201` — `docker compose --profile services build` is a third thing that
can be stale, and the only suite that talks to a container is the one that found it.

**AND THE QUICKSTART WAS RUN, WHICH IS NFR-USE-03's WHOLE VERIFICATION** — a `T` clause at 100%
with **zero occurrences of `quickstart` in `ci.yml`**. It was wrong five times and **four of the
five produced a red that looked like a platform defect**: nothing started the api; the credential
had no published source; **it is an application credential, not a user token**, so every send
answered 400 for naming no sender; **re-running the seeder reuses the existing tenant**, so the
"foreign" object was mine and answered 201 — a reader would have concluded the platform leaks;
and `uuidgen` is not installed while `psql -tAc` leaves a newline `tr -d ' '` does not strip.

**A GOOD HUNK FAILED FOR 4.8's REASON.** `codes.ts` was generated against the dump's END state and
`fences/post-series.md` already amends that file twice — the appendix applies after every chapter,
so a file it touches has one shape at chapter N and another at the end. Moved to the appendix,
placed after the hunks that broke it. **Check which state a hunk is written against.** And
**`check:figures` caught three dead diagrams `pnpm build` did not** — passed as `chart={…}` where
`<Figure>` reads `code`, so all three would have rendered nothing on a page that compiled green.

**AND THE SEALED SUITE HAD NEVER RUN IN CI, WHICH THE PER-ERROR COMPARISON FOUND.** Its job's
migrate step carried no `working-directory` where every other step in that job does, so it died on
`Cannot find module …/dist/db/migrate.js`, every run, before reaching the suite it is named for.
**Three chapters running have now found a gate whose colour was true and whose meaning was not**
(4.9's already-red integration gate, 4.10's nine features of skipped `test:integration`, this).
Fixed in one line: **19 of 19, the first execution of that suite in this repository's CI.**
`gaps.md` 057-7. **And the prediction about it was wrong** — 057-7 said the first green run would
report *"nine features of accumulated drift"*. The suite passes. **The drift a dead gate hides is
a reasonable fear and it was not what was there.**

**THE CI ERROR SET IS IDENTICAL TO THE BASELINE ON TWO RUNS OF THREE, AND ONE COMPARISON WOULD
HAVE MISSED THAT.**

    e8b5c3c  baseline        3 distinct
    e539403  the chapter     3 · empty diff both ways
    8bc0a8f  the CI fix      6 · three extra, absent before AND after
    81761a0  the record      3 · empty diff both ways

The middle run's extras are present in neither neighbour, which is the definition of a flake
rather than a regression. **056 compared ONE run and called the set identical; three runs show it
moving.** The claim a single comparison supports is *"this run introduced nothing new"*, not *"the
set is stable"* — and the lanes job is red either way, so **a colour could not have said either.**
`gaps.md` 057-8.

**TEN ANALYSIS PASSES: 12 findings, 7, 3, 3, 3, 1, 3, 4, 2, 1.** **The count measures the
question, not the artifacts.** Passes 6 and 7 both found a CRITICAL *in an artifact written to
prevent its own class* — §4b's validator table and the plan's constitution check — each filled
once, early, and read past five times. Pass 10 ran the mechanical coverage map for the first time
and found **14 of 51 requirements uncited in `tasks.md`, all 14 covered in substance**: fourteen
alarms, fourteen false, which is why `traceability.md` is built by reading and not by grep.

**056 IS CLOSED at 75 of 75 — CHAPTER 4.10, "the upload that never reaches us".** Movement V
opens. Its record is `specs/056-chapter-4-10/` — `baseline.txt` first, then `gaps.md` (**11
entries: 7 new, 3 carried and re-measured, 1 answered**), `traceability.md`, `tasks.md`.
**ADR-30**, **SRS 1.17**, `docs/12` row 11 amended. Tagged **`part4-ch10`**. (Reworked
2026-09-27 for the MinIO image; see 059's close-out.)

    290 fenced files replay onto relay-platform across 53 chapters · EXIT 0 · from 282 and 52
    the CI error set is IDENTICAL to the pre-chapter baseline — 15 distinct, empty both ways
    29 runtime dependencies at part4-ch9 and 29 now, across all eight package.json
    the store probe costs +1.524 ms at p50, +24.1%            200 samples a side
    3,992 prose words · 6 tutorial gates green · 256 of 256 suites, three runs

**A PRESIGNED URL NEEDS NO DEPENDENCY, AND NO CONTACT WITH THE STORE.** 28 lines of
`node:crypto` — signed PUT 200, unsigned GET **403**, expired refused from the store's own
clock, tampered 403. ADR-30 rejects the AWS SDK on the ratio and `minio` on the direction (a
vendor client at the moment the platform is choosing a replaceable store). But signing is
arithmetic, so the api never learns the store is down and **a slot issued into an outage is
byte-identical to a good one**; `storeReachable()` therefore exists **only to produce a
refusal**, placed after type and size and before the reservation — **the only position that
satisfies FR-009 without a compensating delete.**

**`docs/12` SAID FOUR REFUSALS WHERE FR-MED-02 NAMES THREE, AND THE ROW WAS RIGHT.** The fourth
is the SAD's degradation row, now FR-017, and **the only transient one of the four** — which is
the whole reason they are four codes.

**STORAGE IS A LEVEL AND THE MISSING WORD WAS `monthly`.** Put stored bytes in `usage_periods`
and a delete needs a subtraction `creditFor` forbids, and a tenant holding 100 GB starts every
month at zero. **SRS 1.17** says which kind each of FR-RTL-05's four quantities is, and that a
storage refusal must not promise a resume date — the other three do.

## A TRANSACTION IS NOT A LOCK, AND THE PROBE FOR IT MEASURED THE FOREIGN KEY

**TEN CONCURRENT SLOT REQUESTS COULD NOT LOSE THE RACE.** Green with the lock and green without
it, because each transaction is a sum and an insert a millisecond apart and the windows never
overlapped. **A race test that cannot lose the race is an assertion that cannot fail.**
Interleaved by hand on two connections, both reading before either writes:

    plain SELECT        B blocked: no    B saw sum=0     B inserted   committed 1,200
    SELECT FOR UPDATE   B blocked: yes   B saw sum=600   B refused    committed   600
                                                                      against a cap of 1,000

**AND `FOR UPDATE` FROM OUTSIDE PROVES NOTHING ABOUT THE METHOD.** Hold the environment row, call
`reserveMediaSlot`, watch it wait — it waits **with the explicit lock deleted**, because
`media_objects.environment_id` is a foreign key and the INSERT takes `FOR KEY SHARE`, which
conflicts with `FOR UPDATE`. **`FOR NO KEY UPDATE` is the discriminator**: it conflicts with
`FOR UPDATE` and not with `FOR KEY SHARE`, so the test goes red the moment `.for("update")` is
removed.

## WHAT RUNNING IT COST, AND EVERY ONE WAS AN INSTRUMENT

- **TWO COMPOSE SERVICES CLAIMED HOST PORT 9000**, and **the stack had run without the analytical
  store for thirty-two hours** behind green health checks. Eleven ports in that file are
  hand-allocated and nothing checks they are distinct (045's rule, third time).
- **AND A RESTARTED CONTAINER CAME BACK HEALTHY PUBLISHING NOTHING** — `NetworkSettings.Ports`
  `{}` while `docker compose up -d` printed `Started` and exited 0, because the health check runs
  INSIDE the container. `--force-recreate` is the fix. 4.2's `/ping` finding one layer out.
- **A TAMPER PROBE THAT WAS A NO-OP 6.23% OF RUNS.** It replaced the signature's first character
  with `f`; over 4,096 signings `f` came up 255 times, and on those runs the store's honest 200
  read as *the store accepted a tampered signature*. **A probe that may not have altered anything
  has to assert that it did.**
- **`kindOf("constructor")` RETURNED A FUNCTION.** An object literal inherits from
  `Object.prototype`, and `KIND_CAPS[thatFn]` is `undefined` with `bytes > undefined` false — so
  **one declared MIME type, at any size, walked past both the type and the size refusal.**
  `Object.hasOwn`.
- **A 20-SECOND DEADLINE INSIDE A 5-SECOND TEST, SINCE 4.4.** `vitest.integration.config.mts`
  sets no `testTimeout`; the twin sets 60,000. The poll's `return null` was unreachable (056-4).
- **A TEST TOOK A SHARED SERVICE AWAY FROM ITS NEIGHBOURS.** `docker compose stop minio` is the
  truest FR-017 test and the lane runs two files at a time, so an isolation suite that never
  mentions media storage answered 503. 045 found eight ASSERTIONS scoped too wide; this is an
  **ACTION** scoped too wide and `check-lane-scope.py` cannot see it. **And the
  second-application version did not work**: `MediaService` depends on a REQUEST-scoped
  repository, so **the variable has to be wrong at the moment of the request, not the moment of
  the wiring.**
- **`MediaModule` DECLARED A SERVICE IT DID NOT PROVIDE.** Compiled, typechecked, linted —
  `Nest can't resolve dependencies` on the first request. **Only a running app asks that
  question.**
- **AND v8's TEXT REPORTER OMITS A FILE AT 100/100/100/100.** **The table answers which files
  have a gap; `coverage-summary.json` answers which files were seen.**
- **A CONTAINER IS TWO EDITS AND ONLY `pnpm coverage` SAID SO.** `compose.yaml` gained a sixth
  service and `@relay/config`'s `INFRA_SERVICES` did not — caught by the both-directions
  assertion the chapter that added the FIFTH container wrote. That package is a unit test no
  integration lane imports, so the only command that reaches it is the 664-second one (056-8).

## THE FENCE CHAIN CHARGED FOR SEVENTEEN FILES AND NINE COULD NOT BE THE CHAPTER'S

**THE TASK TABLE SAID TWELVE AND NAMED ONE THIS CHAPTER NEVER TOUCHES.** The six it missed all
arrived from repairs made after it was written. 050's sentence, second time in five features.
**And `patch --dry-run` IS NOT THE CHECKER**: it said yes to seven hunks the checker refused with
`hunk pre-image matched 0 times`, because `patch` applies with fuzz and offset where the checker
needs exactly one exact match (056-7).

    anchors at -U6                          8   chapter fences
    anchors only at -U2 / -U3               2   chapter fences, context trimmed
    anchors at no width                     7   appendix
    anchors, and unanchors the appendix     2   appendix, placed last

**Seven have no context a chapter can match at any width**, because the lines their change sits
*between* are the appendix's own. **Two more anchor here perfectly well and break the appendix's
own older hunks by doing so**, and go last in that file instead: 14 -> 4 -> 0. **A hunk that
works and unanchors somebody else's is still a broken chain.** And **there is no Vietnamese twin
to write** — the translation lags by seven, so MIRROR has nothing to compare; **the task
described a corpus rather than checking one.**

## AND 056-9 AND 056-10 ARE CLOSED, WHICH TOOK FOUR CHANGES AND ONE REFUSAL

**THE UNIT LANE WAS NOT DOCKER-FREE AND NOW IS.** `pnpm test` had needed a running broker since
4.4, behind a label in `ci.yml` saying the opposite. `RELAY_REQUEST_LOG=off` takes the producer
**out of the middleware chain** rather than branching inside it, set in `vitest.config.mts` so
the property belongs to the lane: **408 of 408 with every store pointed at a closed port.** **And
the fix reproduced the defect it was closing, one config over** — `vitest.coverage.config.mts`
runs the same files and must NOT set that flag, since the integration suites in the same run
assert on the producer's rows. **4.9's twin-config finding, in the commit that closed 056-9.**

**AND THE PLATFORM JOB IS TWO JOBS.** `gates` runs lint, typecheck and test with **no service
containers at all** — **green in 64 s**, which turns chapter 1.1's Docker-free claim into a
tested one. `lanes` keeps the five stores and everything downstream of the build. **Two jobs
cannot hide each other**, for one `pnpm install` of 3 s. **`continue-on-error` was refused, not
overlooked**: it marks a failure as ignored and the job goes green, which is the CI-bypass shape
this environment's guard refused at 054.

**AND `pnpm test:integration` HAD NOT RUN IN CI SINCE 2026-09-13 — NINE FEATURES.** 047 ran it
and it failed; 048 broke `pnpm test` and everything after the first failure has been skipped on
every run since, through eight published chapters. **The cause handed off before anybody measured
it.** Every chapter since ran the lane locally and believed CI ran it too.

**AND 056-10's CHECKER IS LEFT UNBUILT ON PURPOSE.** The targeted version's surface is 13 lines
in 10 files; the naive one reports **37** exports whose only callers are tests, nearly all
legitimate, and needs a hand-maintained allow-list. One instance is not a class.

## AND THE PUSH FOUND TWO FAILURES A RED JOB COULD NOT REPORT

The two `relay-platform` jobs failed at the same steps as the run before, **and that is not the
same as failing for the same reasons.** Diffing this run's `##[error]` lines against the previous
run's, uuids normalised, gave **exactly two new ones and nothing removed**. **It took three
pushes and two repairs** — `ci.yml` had no object store, and then the bucket nothing created. The
third run's error set is **identical to the pre-chapter baseline, empty in both directions**,
which is unavailable from a colour that was red all three times. 4.9's own finding aimed at this
chapter: **the signal was not absent, it was indistinguishable.**

**AND THE PLATFORM JOB RUNS FIVE STEPS OF ELEVEN WHEN ONE UNIT TEST FAILS** (056-9), which is why
the MinIO step had to go **before `pnpm test`, not beside the other provisioning** — a
provisioning step after the first failure is skipped on exactly the runs where the lane it
provisions for still executes.

**AND THE SECOND VERIFICATION RUN FOUND THE REAL DEFECT, WHICH WAS MINE AND NOT CI'S.**
Provisioning MinIO changed nothing: the same two errors, exactly. `store.ts` said *"ON BOOT,
EVERY BOOT"* and **every caller of `ensureBucket` was a test `beforeAll`** — the convention
section below. **No local run could see it** because the volume persists; **CI's empty volume
said so through two suites that never touch the media module.** `storeReady` treats a **404 as
the first request rather than a refusal** — a boot hook that throws stops the api starting during
an outage, one that logs leaves a recovered store bucketless, and creating on every request needs
`CreateBucket` on a credential production may grant only `PutObject` (056-10).

**AND THE CARRIED LEDGER MOVED.** **055-4 did not reproduce the obvious way**: run from an
unrelated empty directory, **all seven** gate scripts printed their counted line with the
repository's real figures, because every one resolves its corpus from the script's own location.
**The rule the entry produced is what told them apart in one command: assert the counted line,
not the exit code.** **050-8 is narrower and not closed** — two suites now spawn the ingester for
their own duration, and **two test files starting a process is not a deployment.**

**055 IS CLOSED at 105 of 105 — THE FENCE CHAIN IS ZERO.** Its record is
`specs/055-fence-chain-repair/` — `baseline.txt` first (it carries every phase's measurements and
the method), then `gaps.md` (**12 entries: 7 new, 4 closed, 1 corrected**), `traceability.md`,
`tasks.md`. **ADR-29**. No tag: the feature cuts no chapter.

    check-fence-chain: 282 fenced files replay onto relay-platform across 52 chapters
    110 -> 0 · EXIT 0 · the first green tutorial job since feature 045
    42 hunks re-anchored · 8 files published whole · 29 appendix hunks · 30 fences declared
    2,379 published diff lines became 1,882 — the series shows readers LESS, not more

**A COUNT OF 110 WAS NEITHER 110 DEFECTS NOR AN UPPER BOUND ON THEM.** 42 bad hunks were cleared
by **24** repair operations, so 18 were shadows — one appendix hunk cleared five at once. And ten
files could not be compared to the repository at all, because **a checker reports the first
failure per file** and a file with a broken hunk never reaches its HEAD comparison.
`session.itest.ts` was **1,322 lines** behind. **The number counts files with at least one
problem, not problems.**

**AND THE LAST ONE WOULD NOT CLOSE, WHICH IS HOW THE REAL DEFECT SURFACED.**
`node -e 'console.log("x".replace("x", "END $$;"))'` prints **`END $;`** — `String.prototype.replace`
reads `$$`, `$&`, `` $` ``, `$'` and `$<name>` in a **string** replacement as substitution
patterns, and `applyHunks` used the string form. Fixed with a function replacement — and **two of
the 42 "bad hunks" were never bad.** The repair had been compounding it: three rounds against a
corrupted state stacked three dollars. **A repair that keeps almost working is the shape of an
instrument bug.**

**THE METHOD IS NOT "REGENERATE AGAINST THE TAG".** `diff(chain state at 3.17, rework/part3-ch17)`
for the coverage config is **206 lines in one hunk**, because the chain was already 148 lines
behind ch16 before the chapter started — a hunk that shows the reader 146 lines the chapter never
wrote. **Keep the chapter's change and trim the context the chain does not carry.** Three
strategies: the published hunk; trimmed ends; and **the interior gap** — anchor on the longest
leading and trailing runs that each occur once and replace everything between them.

**AND THE INTRODUCTIONS HAVE A FOURTH DESIGN THE PLAN DID NOT LIST.** Every one of the nine first
`diff` fences **applies cleanly to its own `rework/part3-chM` tag** — the state BEFORE the
chapter's change. So the body goes at chapter N, taken from chM, **immediately before the existing
diff**, which is left alone, and the reader meets the file before the change: 1,100 lines against
design A's 1,956. **And the ratio has to be per PROBLEM, not per chapter** — one body can buy ten
problems at 28 lines each.

**THE 110th PROBLEM HAS A NAME AND IT IS NOT PART 3's.** 046's T006 blamed a `relay-tutorial`
commit; all six tutorial commits in that window are Vietnamese translations, and **a vi commit
cannot add a HEAD problem.** It was a `relay-platform` commit adding `corpus.json` to a
`.gitignore` chapter 1.1 publishes whole. **046 created it, 046's own opening measurement first
reported it, and the delta-of-0 convention hid the attribution for nine chapters** — because it
compares a total to a total and never asks which file. **Report the absolute number, not the
delta.**

**FIVE OF THE SEVEN GATE SCRIPTS EXIT 0 WHEN THEIR CORPUS IS ABSENT.** Every one prints a counted
success line when it really looked, so **assert the line, not the exit code**. And **a copy of the
checker at any other path replays nothing and exits 0**, because the platform is resolved from the
script's own location — which is the copy fence-chain rule 1a tells you to make. 055-4 and 055-5.

**`check:errors` IS A SCRIPT NO WORKFLOW RUNS — AND THE CHECK ITSELF DOES RUN.** Four features
re-measured this by grepping `ci.yml` for `check:errors`, which gives zero, while **`ci.yml:211`
runs `node ../relay-tutorial/scripts/check-error-codes.mjs` by path** in the lanes job. The
pnpm script name has no job; the check has one. **A script invoked by path in one repository's
workflow and by name in another's `package.json` is a check with two spellings, and a sweep for
either finds half the truth** (055-3, corrected at 062). **The tutorial job's gates are `lint`, `build`, `check:docs`,
`check:srs`, `check:figures`, `check:fences` — read them off `ci.yml`, not off memory.**

**WHAT ZERO DOES NOT MEAN.** Not that the chapters are readable, not that the listings are
pedagogically right, and not that **614 fences outside every gate** — 360 untitled and 254 skipped
by name — mean anything. Not that the Vietnamese chain is compared to the repository (050-3). And
the success line's chapter count is **pages the walker found**. One property — every titled fence
replays onto `relay-platform`, byte for byte.

**`check:fences` GAINED `--dump <dir> [--at <page>]`** so hunks come from the same replay that
checks them. An output mode: no threshold, no exemption, no exit-code change, and `--at` replays
separately so the dump cannot touch what the check reports. **No `--locale` flag** — a page path
begins `app/(en)/` or `app/(vi)/vi/`, so the chain is inside the argument. And **`MIRROR` is two
checks**: it joins each chapter's title list and `continue`s on a mismatch, so a non-zero reading
counts **chapters skipped**, not fences wrong.

**AND THE LOOP COMMAND NEVER PRINTED THE COUNT.** `pnpm check:fences | tail -1` shows pnpm's own
`ELIFECYCLE` line, because the problems and the summary go to **stderr**. Use
`pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'`.

**054 IS CLOSED at 114 of 114 — CHAPTER 4.9, "Milestone: the meter agrees".** Its record is
`specs/054-chapter-4-9/` — `baseline.txt` first, then `gaps.md` (**8 new, 14 carried and
re-measured, 2 closed, 1 corrected twice**), `constitution-amendment.md`, `traceability.md`,
`tasks.md`. Tagged **`part4-ch9`**. Movement IV is closed.

    121,057 vs 121,057 · 0.0000%   the first volume where 0.1% is a real threshold
    smallest expressible drift 122 · 121 passes and 122 breaches, both directions
    54 of 54 suites · EXIT 0       the first green test:integration since chapter 4.4
    one assertion of 676 moves when `<=` becomes `<`
    check:fences 110 -> 110, delta 0 · 2,826 prose words · 3 figures · SRS 1.16

**THE PREMISE FIVE ARTIFACTS CARRIED WAS FALSE, AND THE TRUTH IS WORSE.** *"The planted-drift test
has existed since 4.7 and the gate has never reached it"* — it runs on every push and passes.
**The gate was already red**, on every run since 4.4, so a planted drift deepened a red rather
than turning one. **The signal was not absent, it was indistinguishable** — and fifteen analysis
passes read that sentence without running the lane.

**ONE UNSET VARIABLE WAS COSTING MORE THAN THE TEST THAT REPORTED IT.**
`RELAY_INTERNAL_CREDENTIAL` failed `limits.itest.ts` loudly; it also made **three attacks in
`isolation/gauntlet.itest.ts` return at their first line and report green** — the suite
constitution VI names as gating releases. Its own accounting test cannot catch that, because
`attacked.add(...)` runs **before** the early return, so the check written to find unattacked
routes is satisfied by the route that was skipped. Measured: **1ms, 0ms, 1ms → 27ms, 6ms, 33ms**.
**0ms is what a skipped attack looks like in a green suite.** **And the fix was right in one
config and missing from its twin** — `vitest.coverage.config.mts` also runs `.itest.ts` files, so
`pnpm coverage` kept the gauntlet skipped **in the run that measures constitution VI's own
coverage bar**.

**A GATEWAY TEST HAD NEVER DELIVERED THE FRAME IT PUBLISHED.** `typing.itest.ts` publishes a
five-field presence payload; `presenceFabricSchema` is a `z.strictObject` of three, so `safeParse`
fails and nothing reaches the socket. **It passed on a frame the gateway sends at connect**, at
whatever rate Redis had forgotten the previous run. Fixed: 23 of 23 three times, and the file is
**ten seconds faster** because a test stopped burning a ten-second arrival deadline.

**THE INGESTER DID NOT NEED A COMPOSE SERVICE AND BOTH OBVIOUS FIXES WERE WRONG.**
`services/ingester` has **no Dockerfile**, and the other services carry `profiles: ["services"]`.
And `--filter` selects **packages**: the five red suites sit inside `@relay/api`. **The suite
spawns the process it needs** (050-8 CLOSED, five features on). **And that changed what the sealed
suite sees**: `integrate.itest.ts` asserted a customer's request log comes back **empty** — an
assertion that a defect is still present, which **fails the moment somebody fixes the defect**.

**THE TWO DIRECTIONS OF THE SMALLEST EXPRESSIBLE DRIFT ARE NOT THE SAME NUMBER.** 4.7 published
*"101 in both directions"* at 100,000; re-derived at six volumes they are equal at all six, **by
luck**:

    volume      999    1,000    1,017   121,057   1,000,000
    under         1        2        2       122       1,001
    over          2        2        2       122       1,002

`max(analytical, operational)` is the denominator, so a surplus of `d` divides by `volume + d` and
a shortfall by `volume`. **500,500 of the volumes below a million differ**, and every volume above
a million does. Found by writing the function, not by reading the table.

**FR-ANL-06 IS THREE OBLIGATIONS AND THE PLATFORM HAS ONE.** The comparison exists and is
exercised on every push. **The daily job has no runner of any kind** — zero hits in either
`package.json`, `turbo.json`, `ci.yml` or any `*.sh`, and no `schedule:` trigger — which no
document had recorded. The alert has no mechanism (SRS 1.14). **ADR-28** records the absence
rather than building a sixth relay: a daily sweep today would report `no-data` for every tenant,
because **no environment has both sides**. **ADR-27** is the gate. The constitution III amendment
is **written in full and not applied** (`specs/054-chapter-4-9/constitution-amendment.md`) — three
items now stand against one principle (051-2, 052-6, 054-3).

**AND THE WORKFLOW IS STILL RED AT THE TOP.** `check:fences` exits 1 at the standing 110 as its
job's last step. The ratchet that would fix it — a per-kind baseline in `fences/baseline.json` —
was written and **refused by this environment's guard as a CI bypass**, which is the right reflex
for a change that makes a failing checker exit 0. It is the user's call; `gaps.md` 054-1 carries
the design.

**AND EVERY INSTRUMENT COST SOMETHING.** A titled excerpt is a whole-body claim, and three quoted
lines made the chain's state for that file three lines, breaking the HEAD comparison **and the
appendix's own hunk for it** (051-6, reproduced). The loader's report was a whole-table count and
a second corpus exposed it — `removed_by_ttl: -393,562`; every count it prints is scoped now. **A
bare `count()` on a `SummingMergeTree` is a moment, not a state** — 15 immediately after a
cleanup and **9** after the merge, with nothing deleted in between. One cleanup found a table no
document names: a view with no `TO`, whose rows live in a table named after a UUID, holding
**571,333 rows**. **A pin on a real file no lane includes is silent**, probed both ways (054-7).
And T015's premise was false: *"a pure function over messages grouped by (environment_id,
period)"* — those rows never exist in Node, so it would have been a second implementation of a
`GROUP BY` that nothing runs.

**053 IS CLOSED at 139 of 139 — CHAPTER 4.8, "the log a customer can search".** Its record is
`specs/053-chapter-4-8/` — `baseline.txt` first, then `gaps.md` (**21 entries: 9 new, 12 carried
and re-measured, and 048-2's own wording corrected**), `traceability.md`, `tasks.md`. Tagged
**`part4-ch8`**.

    a scoped query returning 0 rows returns 11,683 under ' OR 1=1 --   across all 152 tenants
    quantile(0.99) 4,961 where quantileExact reads 10,000             50.39% low, n=64
    a 50-row page reads 11,695 — the whole table                      the part is Compact
    check:fences 110 -> 110, delta 0 · 3,606 prose words · 11 gates · 66 tests · SRS 1.15

**THE BRIEF PAIRED A CLAUSE THAT COULD BE BUILT WITH ONE THAT COULD NOT, AND BOTH HALVES WERE THE
CHAPTER.** FR-ANL-07's surface ships. FR-ANL-10 gains the definition it never had — **commit to
the frame written to a subscriber's socket** — and nothing is computed, because the column has 0
rows, 0 producers, and the one thing that writes that table supplies `CAST(NULL AS
Nullable(UInt32))` for it in both halves of its `UNION ALL`, on purpose.

**"THE PAYLOAD REACHES THE PARSER" IS THE WEAK VERSION OF THIS CLAIM.** The hostile-window test
ran red 10 of 10 against a version that validates the window as a string. Then the statements went
to ClickHouse:

    scoped, honest window (1 hour)                       0 rows
    the same query, from carrying ' OR 1=1 --       11,683 rows   the whole table
    distinct environment_id under the payload          152        the query names ONE
    ' UNION ALL SELECT name FROM system.users --   relay, then the request ids

**It does not widen the window — it defeats the tenant predicate**, because `OR` binds looser than
the `AND` chain the scope is written in. Constitution I, broken by a query parameter. One payload
of the five is refused by something else and that is worth saying rather than claiming:
`'; DROP TABLE …; --` dies on `Code: 62. Multi-statements are not allowed`.

**THE REMEDY IS A TYPE, NOT AN ESCAPE.** What leaves the schema is a `Date`, and the only function
that turns one into SQL takes a `Date`. There is no path from a query string to a statement, so
there is nothing to escape and nothing to forget to escape. The `endpoint` filter is the same
argument through a closed set **derived from the running router** — and the repair that made it
safe removed the most diagnostic question it could ask, so `unmatched` is a member of the set.

**`index_granularity = 8192` IS DECLARED AND IS NOT IN FORCE.** Every query reads the whole table,
whatever the window and whatever the filter, and `EXPLAIN` says `Granules: 1/1`. Built two ways
rather than argued — same rows, same declared granularity, differing only in
`min_bytes_for_wide_part`: Compact gives 2 marks → 1 granule, Wide gives 3 → 2. **The part type
decides.** The table is Compact because it is under 10 MiB, so the per-tenant key skips nothing
until it crosses that line. R6's published *"one granule, the engine's floor"* was a measurement
of a Wide part. `FINAL` costs **3 ms against 2 ms at seven parts** — measured with merges stopped,
because the obvious measurement is taken on a table that has just been merged and proves nothing.

**`quantile` HAS NO EXACT REGIME, WHICH IS THE OPPOSITE SHAPE FROM `uniq`.** Its error is not
monotone in n and on a skewed sample it **GROWS** with n (p95: 0.82% at n=4, 9.5% at n=10,000). On
the platform's one real latency sample, n=64, `quantile(0.99)` answers **4,961** where
`quantileExact` answers **10,000** — **50.39% low**, which is the direction where an alert
threshold never fires. **And the clause's own grain is the small one**: per tenant per hour, 178
buckets, median 10 rows, 73 under five. **A p99 over four samples is a maximum wearing a
percentile's name**, whichever function computes it.

**THINGS THAT HAD NEVER PASSED, NEVER LOOKED, OR NEVER BEEN TRUE.** The sealed suite had never
passed — it asserted `docs_url` contains `/not_found` under a comment ending *"Asserted as this
platform actually answers."* It was not, and nothing said so because it needs a running platform
no lane starts. **`check-lane-scope.py` still pointed at a worktree 045 deleted** — 0 files, 0
unscoped reads, ten controls firing; **049 measured the retarget and never landed it. A
measurement is not a repair.** 55 files now, and a run that reads nothing **refuses with exit 2**.
**`docs/07` §6's "runs both lanes against real stores" was false for ClickHouse for six chapters**
— the sentence defense 1 is called closed on. **And chapter 2.4 published a clamp the code has
never done**: `.max(200)` is a validation, `limit=500` is a 400. The comment sits in eight fences
across four chapters in each locale, three as `diff` CONTEXT — **a block replacement caught four
and missed four**, because two `-U6` windows end mid-comment.

**THE APPENDIX APPLIES AFTER EVERY CHAPTER, AND THAT IS WHY A GOOD HUNK FAILED.** Two applied; the
third reported `hunk pre-image matched 0 times`. **The hunk was right and the state was not what
it was written against** — the chain's state for that file at that point is **993 lines** where
the tag holds 1,235, the difference being `fences/post-series.md`, which applies last. So a
chapter hunk for a file the appendix also edits must be written against a state no reader sees.
**Check which state a hunk is written against before blaming the hunk.**

**AND "DERIVE, DON'T LIST" HAS A PRECONDITION.** `rowsOf` knew two body shapes and this chapter
served a third. The first repair replaced the lookup with *"the first array-valued property"* —
this project's own reflex — and `rowsOf({ items: [1,2,3] })` must equal `[]` went red. **The
reflex assumes nothing checks the table, and this one is checked twice.** The derived version
would count any array in the body as rows, a false pass where an unrecognised shape is a loud
failure. The route derivation also found the route first, for the seventh time, and adding the
entry turned the gauntlet red with **"classified but never attacked"** — a third accounting
direction the plan named two of. **Naming a route is not covering it.** And the attack plants its
own rows, because **an empty log passes a leak check for the same reason an empty page does.**

**ABSENCE IS NOT A STRING.** The store client returns `string[][]` from a TSV body and ClickHouse
writes NULL as `\N`. A reader taking the value column alone reports an endpoint of `"\N"` —
truthy, and indistinguishable from a route name downstream. `endpoint` is NULL on 31 real rows;
`limited_operation` on **11,660 of 11,683**. The first version handled `endpoint` and stopped.
**The fix is where the next defect is**, one column over.

**AND FOUR MORE INSTRUMENTS.** **`Number.isSafeInteger` is not a bound on an instant** — a cursor
of `999999999999999` is a safe integer and decodes to the year 33658; both ends are the column's
facts now. **`direction: newer` had never run**, in the contract and the schema since phase 2,
with every test using the default. **The ratchet caught a regression of mine** — a new `catch`
whose `cause` is typed `unknown` took a file from 94.73 to 91.3 against a pin of 93; lowered to 91
with both unreachable arms named, the pin working rather than in the way. **And a filter test
failed for another test's reason, eight lines up**: what a filter promises is that nothing ELSE
comes back; the count of what does is the plant's business.

**A FEATURE-LOCAL ID REACHED TWO PUBLISHED DOCUMENTS, THREE COMMITS AFTER READING 1.14's
CORRECTION OF THE SAME DEFECT.** The mechanism was copying the task line — a task is feature-local
and uses them correctly. Caught by diffing `docs/` for `FR-0\d\d`, and **nothing runs that check**
(`gaps.md` 052-7).

**FR-ANL-08's NINETY DAYS CANNOT EXIST OVER THIS TABLE AT ANY VOLUME.** Two rows planted at
`now - 60 days` and `now - 1 day` leave **one survivor**, and `OPTIMIZE FINAL` changes nothing:
the TTL cuts at INSERT. No fixture can put the clause's window in front of it.

**READING THE LOG SPENDS THE TENANT'S REST BUDGET, AND NOBODY CHOSE THAT.** `operationsFor`
returns `["rest"]` for every `/v1` path. Left counted — an exemption list is a hand-maintained
table — and the loop is published rather than routed around: **a customer investigating 429s reads
their log, the reads spend the budget they are investigating, and the log then shows the 429s the
reading caused.** **And the log is 1.60 s behind at p50** — 2.7% of FR-ANL-04's 60. **On the stack
this series ships, a customer reading their own request log finds it empty**, because the records
are published and nothing drains them (`gaps.md` 050-8).

**052 IS CLOSED at 87 of 87 — CHAPTER 4.7, "the job that checks the meter".** Its record is
`specs/052-chapter-4-7/` — `baseline.txt` first, then `gaps.md` (**23 entries: 7 new, 15 carried
and re-measured, and 047-1/048-1 closed by amendment**), `traceability.md`, `tasks.md`. Tagged
**`part4-ch7`**.

    the aggregate 0.2630% · 49 of 1,385 tenant-periods over the bound · 0 non-fixture
    uniq exact to 65,536 · 0.5676% at 65,537                    the cliff is one user wide
    the TTL gap is 0% at midnight and 1.0989% before the next   047's 0.49% is one point on it
    check:fences 110 -> 110, delta 0 · 2,265 prose words · 11 gates · 33 tests · SRS 1.14

**FR-ANL-06 CANNOT PASS, AND THREE OF THE FOUR REASONS ARE NOBODY'S FAULT.** So the chapter's
product is a clause amendment, not a green number. SRS 1.14 states which operational table the
job means per quantity, that the comparison is per tenant, that absence has verdicts of its own,
and where its own bound is unreachable. **Amending the requirement is the whole of what a chapter
can do about an obstacle that is a design decision.**

**"COUNTS DERIVED FROM OPERATIONAL DATA" IS NOT ONE NUMBER.** `messages` through `channels` holds
19,012 and `usage_periods.messages_sent` holds 18,962 — **49 of 1,385 tenant-periods over the
bound**, and every disagreement attributable to a fixture. **Two mechanisms pushing opposite
ways**: a raw `INSERT INTO messages` bypasses the counter (seven call sites), and a hard `DELETE
FROM messages` removes a row the counter already counted. **0 of 1,385 disagree for a non-fixture
reason**, because `sendMessage` writes the message and increments the counter in one transaction.
**And 1,317 tenants are one-sided, which is all of them** — `not-comparable` and `no-data` are not
edge cases here, they are the answer, and collapsing them into "missing data" lets the platform's
largest defect read as an absence of evidence.

**BOTH OBVIOUS WAYS TO PLANT A 0.1% DRIFT PASS.** Against an operational 100,000:

    99,900   -100   0.100000%   pass      "0.1% under" — the naive shortfall
    99,899   -101   0.101000%   breach
   100,100   +100   0.099900%   pass      "0.1% over"  — the naive excess
   100,101   +101   0.100898%   breach

`max(a, o)` is the denominator and the comparison is `<=`, so **the smallest breaching drift is
101 in both directions** and a drift computed off the smaller side lands inside the bound.
Changing `<=` to `<` turns exactly one test red, which is how you know the boundary cases sit ON
the bound. **AND THE THRESHOLD HAS NO RESOLUTION AT LANE SCALE**: at a tenant's real nine
connection-minutes the smallest possible drift is **11.11%**, a hundred times the bound — so a
green 0.1% assertion there claims nothing drifted at all.

**`pnpm coverage` WAS ANSWERING WITH SILENCE, AND HAD SINCE 4.4.** `coverage.reportOnFailure`
defaults to **false**, so one red test suppresses the whole report: no table, no per-file
threshold errors, no `coverage/` directory. Run both ways over the same three files: green printed
the table and every threshold error, one red printed neither. **Silence is indistinguishable from
a pass at a glance.** Turned on, and the first reporting run found `shape.ts` failing its 100% pin
at 95.12 — left at 100 rather than lowered, because this chapter made it visible rather than
measuring it down. (4.13 finally raised it.)

**AND `pnpm test:integration` RUNS THREE OF ITS SIX LANES.** `--dry=json` plans 18 tasks; the run
attempts **9** and prints `Tasks: 7 successful, 9 total`. `--concurrency=1` means turbo stops
scheduling at the first failure, so **every lane ordered after the api has not executed under that
command since 4.4** — the gateway's 225 tests among them. 051-3 read this as a summary that
collapses lanes; it is worse.

**`FR-003a` IS NOT A CLAUSE, AND TWO PUBLISHED DOCUMENTS CITED IT AS ONE.** **There is no
`FR-003` in the SRS**; `FR-003a` is feature-local and four features use it to mean four different
things. And the sentence it sat in was false: *"the rollups carry no TTL"*, when 4.6 gave both a
25-month TTL **in the same feature that paragraph was written in**.

**AND ADR-06 HAD ASSUMED CONSTITUTION III's ANSWER ALL ALONG.** Its accepted trade-off reads
*"mitigated because the only strict consumer (metering) reconciles daily against Postgres
(FR-ANL-06)"* — so the cross-store read is **the mitigation that makes choosing NATS over Kafka
acceptable**, not an oversight. Five features cited both documents without reading them beside
each other. The reading that holds: **the reconciler is none of the three roles III names — an
auditor confined to one side of a fence cannot check the fence** (`gaps.md` 052-6, after 051-2).

**AND EVERY INSTRUMENT COST SOMETHING.** **A lint rule is a constitution clause**: the Postgres
read went inline in `metering/` and was refused — *"the query engine lives inside the repository
layer only"*. **The plan put the job in the api BECAUSE the api owns the repository and never
noticed the wall between them.** **4.6's fact ran the other way** — *a bare aggregate with no
`GROUP BY` always returns exactly one row* made an empty result set unreachable, so "holds
nothing" and "holds zero" became the same answer; `count()` is the first column now. **A `diff`
fence carries the `@@` hunks only** — pasted complete from `git diff -U6`, the `--- a/` and
`+++ b/` headers are read as body text: 112 problems, `starts "-- a/compose.yaml"`. **A glob is an
instrument**: the coverage-pin sweep named 17 pins unbindable and **all 17 are real files**, because
`git ls-files 'services/*/src/**/*.ts'` misses every file directly in a `src/` where picomatch —
which is what vitest uses — matches it. **`pnpm -s <script>` reports red for a green gate.** **A
fire-and-forget `ALTER … DELETE` left a row from an earlier run** — what that form lacks is
evidence that it ran, so the cleanup polls AND asserts a count of 0. **A title overclaimed and the
audit caught it.** **And an edit was invisible to the fence chain**, because a checker reports the
first failure per file and that file had diverged since before Part 4 (048-3).

**051 IS CLOSED at 94 of 94 — CHAPTER 4.6, "the rollup nobody read".** Its record is
`specs/051-chapter-4-6/` — `baseline.txt` first, then `gaps.md` (**15 entries: 6 new, 8 carried
re-measured, and 047-3/048-4 closed**), `traceability.md`, `tasks.md`. Tagged **`part4-ch6`**.

    the rollup read 32,778 rows · the raw table 32,768   for the same tenant-month
    147,534 rows keyed (env, channel, day) · 281 keyed (env, day)      525x
    56 calendar minutes against 0.6513 elapsed                          86x
    check:fences 110 -> 110, delta 0 · 2,302 prose words · 11 gates, 9 green

**THE BRIEF ASKED FOR A ROLLUP THAT HAD EXISTED SINCE 4.2, AND NOTHING READ IT.** `grep` finds two
references: a comment, and a file referenced by no script, service or config. **And the one table
it reads is the one table nothing writes** — `message_events` 0 rows, and **zero occurrences of
that name under `services/`**. Three of FR-ANL-05's four quantities come from it. So DR-10's
*"billing never scans raw events"* was satisfied, for two chapters, by a rollup over a table that
receives no events, read by a file nothing runs. **Both halves conform to the clause.**

**THE COUNTS HOLD STILL WHILE THE STREAM CLIMBS.** **The tables move when an ingester drains, not
when the platform works** — constitution III's independence in two commands. T001 had blamed
`/healthz` polls for a drift that does not happen.

**THE ROLLUP READ MORE ROWS THAN THE RAW TABLE.** One tenant's 91-day bill, from
`system.query_log`: 32,778 rows and 3.56 MiB against the raw table's 32,768 and 1.31 MiB. 4.2
published 315 rows against 1,052,655 for this clause. **The cause is the key and not an unmerged
table**: 147,534 distinct `(env, channel, day)` keys against 286 `(env, day)` keys over 2,400
channels, and `OPTIMIZE FINAL` changes nothing. **FR-ANL-09's channel dimension and DR-10's cheap
read cannot share a key.** Two rollups ship. The compression says it in one pair: 248,155 raw rows
become **281** at `(env, day)` — 884× — and **147,534** with channel, which is an index with extra
steps. **R6 asked the wrong question and was right**: it measured `channel_id` on the row and
concluded it *"costs a key column, not a join"* — true, and about storage. **What it costs the
READ needed a corpus**, and no analysis pass loaded one.

**A MATERIALISED VIEW IS A TRIGGER ON FUTURE INSERTS, NOT A QUERY OVER HISTORY.** The first
comparison of the chapter failed: rollup 0, raw 56, over records already in the table. Proven with
a control — one new close moved it to 2 while the rest stayed at 0. **So DR-10 is empty without a
backfill on any store that already holds data, and it reads as working without one**, because
every new record appears. **And a backfill recovers only what still exists**: the view counted
242,667 messages over 92 days, a backfill minutes later 239,997 over 91 — the difference is the
day the 90-day TTL removed **during the insert**, because the view fires first. **A rollup created
late is permanently short. Build it with the table, not after.**

**SRS APPENDIX C QUESTION 4 IS CLOSED** — open since before Part 4. A connection-minute is a
**calendar minute during any part of which a connection was open**, which is what `meter.ts` has
billed since 3.24, so the two agree by construction rather than by reconciliation. The argument is
56 against 0.6513 over 55 real closes, median connection **252 ms**: a client reconnecting every
quarter-second holds a slot continuously and pays almost nothing on elapsed duration. What is
given up is in the clause — short connections over-report against wall-clock intuition.

**AND THE CORPUS COMMAND IS THE VIOLATION.** Constitution III forbids analytical queries against
Postgres; `load-analytics.mjs:53` is `postgresql('${PG_HOST}', …)`. **The only way to demonstrate
the rollup the clause asks for is to run the thing the clause forbids** — which is the strongest
available argument that `message_events` needs a producer. Recorded in SRS 1.13 rather than
amended, because the amendment is the constitution's own (051-2).

**AND DR-09 HAD SAID IT ALL ALONG.** *"Raw events shall be retained for 90 days; **daily
aggregates for 25 months**."* `gaps.md` 047-3 and 048-4 both read *"no clause says how long
metering history is kept"* — while quoting DR-10, **the next row down in the same table**. Three
features, two entries, an adjacent clause.

**AND EVERY INSTRUMENT COST SOMETHING.** **`corpus.mjs` refuses `CORPUS_DAYS=60`** — it needs more
than the 90-day query window, and `message_events` TTLs at 90, so **they cannot both be
satisfied** and a conforming corpus always produces the rollup/raw discrepancy; analysis pass 5
wrote 60 into the quickstart and nobody ran it. **A test that asserts the wrong read is wrong
depends on a merge not having happened** — three versions before the invariant (the rows sum to
3000 in every state). **A mutation is not a delete**: `ALTER TABLE … DELETE` returns before it
acts; it polls `system.mutations` now. **100/100/100/100 by deleting branches** — both arms were
unreachable, and one carried a comment I had written in the same commit claiming a test drove it.
**Two checks returned a confident zero about the wrong question** — `engine_full LIKE '%25
MONTH%'` read as a failed `ALTER` when the server normalises to `toIntervalMonth(25)` and the TTL
is not in `engine_full`. **A titled fence is a whole-body claim** (051-6). **And
`pnpm test:integration` reported one failure where three lanes failed** — one `FAIL` line against
`Tasks: 6 successful, 9 total`, with the api lane printing no test output at all. **The gate a
chapter is told to run and believe** (051-3). **And the manifest step failed first**: the
registration edit matched two anchors and was refused, so `pnpm build` said `Error: Unknown
chapter id: 4.6` — 4.4's failure reproduced, and the only one of eleven gates that notices.

**050 IS CLOSED at 114 of 114 — CHAPTER 4.5, "the gateway's first stream".** Its record is
`specs/050-chapter-4-5/` — `baseline.txt` first, then `gaps.md` (**19 entries: 8 new and all 11
carried items re-measured**), `traceability.md`, `tasks.md`. Tagged **`part4-ch5`**.

    close -> row readable   min 2.0 s · p50 5.7 · max 5.8   9.7% of FR-ANL-04's 60 s
    60/60 acked broker down · 139 retained · 0 dropped
    403.5 B a record on the real stream — 26% heavier than the synthetic 320
    check:fences 110 -> 110, delta 0 · 2,330 prose words · 11 gates, 9 green

**THE GATEWAY ALREADY REPORTED CONNECTION DATA, WHICH `docs/12` DID NOT SAY.** `meter.ts` has
shipped connection-minutes every sixty seconds since 3.24. So the chapter is not *"the gateway has
no way to report"* — it is **"the one it has was built for a different question and goes through
the service the analytical path is supposed to be independent of."** And `session.ts`'s close
handler had already refused to do what this chapter wanted, in writing since 3.24: *"a mass
disconnect would turn one event into a burst of HTTP requests."* **A publish per close is the same
burst on a different transport**, so the records buffer and flush on a tick exactly as the meter
does.

**"BATCHED" MEANT THE WAITING, NOT THE PAYLOAD, AND FOUR PASSES DID NOT ASK WHICH.** A research
row read *"batched 500 per publish"* — which is 500 records in ONE message — and three artifacts
adopted it in that form with three requirements built on top. It breaks three claims the feature
had already published: one message carries one subject and the subject carries the tenant; one
message carries one `Nats-Msg-Id`; and **the shipped ingester destroys it** — an array has no
`type`, so `route()` takes the attempt arm and calls `m.term()`, 500 records gone counted as one
malformed. **The units in the three rows were the only tell**: two said *publishes* and the third
said *records*. **And the measurement then moved 7.6x when the shape was corrected** — 0.0260 ms
a record, 11x faster than awaited rather than 67x. The decision survives on the smaller margin,
which is worth more than the old figure was.

**AND THE UNAUTHENTICATED CONNECTION CANNOT ARISE.** Five artifacts carried it as a decision and
the plan's constitution check read *"PASS, with one open case"*. `open()` is the only function
that builds a `Connection`, it takes a **non-optional** `Identity`, and its one call site is
reached only after five refusals have each returned. **An unauthenticated socket exists and an
unauthenticated connection does not**, so 4.4's `_none` arm is unnecessary rather than declined.
**A design in which a case cannot arise beats a branch that handles it.**

**AND `MAX_CONNECTIONS_PER_USER = 5` IS A CEILING ON "N CONNECTIONS".** A task said *"open and
close N connections, assert 2N records"* and never said across how many users. The sixth socket is
refused before `open()` and produces no record — so ten sockets as one user assert 20 and measure
10, and the failure reads as ten lost records rather than five refused connections. **Reading
cannot find what the schema refuses**, and a cap is the same kind of refusal.

**A CLEAN STOP PUBLISHES A LEDGER SAYING TEN CONNECTIONS ARE STILL OPEN.**

    clean stop (SIGTERM)   opened 10 | closed 0      of 20 expected
    kill      (SIGKILL)    opened  0 | closed 0      of 20 expected

`sessions.close()` calls `wss.close()`, which **does not close established sockets**, so no
per-socket close handler fires and no close record is ever enqueued. **Zero of twenty is visibly
wrong; ten opens with no closes is not**, and a dashboard subtracting closes from opens drifts up
by a full instance on every deploy. The two bound the loss from both ends.

**THE COVERAGE LANE WAS RECORDED DEAD AND IS NOT.** Phase 4 measured `pnpm coverage` printing `No
test files found, exiting with code 1`, reproduced it in a worktree, and blocked two tasks on it.
T095 ran the same command against the same config: **108 files, 1,545 tests, 511 seconds.** The
conclusion drawn from the dead lane is withdrawn; **one instrument here produced a false "nothing
to see" and nobody can yet say why** (050-1).

**AND 4.4's INTEGRATION SUITE NEEDS A PROCESS NO GATE STARTS.** `request-log.itest.ts` polls
ClickHouse for a row only the ingester can write, and **there is no ingester service in
`compose.yaml`**: 5 passed with one running, 5 failed without. That suite discharges 4.4's SC-001
and is green only for an operator who happens to have a process alive (050-8).

**THE VIETNAMESE CHAIN IS NEVER COMPARED TO THE TREE.** `check-fence-chain.mjs:265` iterates
**`en.state`**; the vi chain is replayed and then compared against the ENGLISH chapter's fences
(MIRROR), never against `relay-platform`. So three vi whole bodies are stale today and every gate
is green. T010c predicted two and missed the third. **A prediction that the instrument would show
something is a claim about the instrument** (050-3).

**ELEVEN OF THE 36 INHERITED HEAD PROBLEMS ARE NOT DRIFT.** **25 are `<path> differs at line N`**
and **11 are `<title> does not exist in relay-platform`** — fences titled with a prose phrase
rather than a path. They can never be repaired by editing the platform. The headline 110 is eleven
units pessimistic, and 25 is the number a chapter should be measured against (050-4).

**AND TURBO'S CACHE HID A TWO-CHAPTER-OLD RED.** `bound-port.test.ts` had been failing since 4.3
and the `test` task's cache key does not cover another package's `main.ts`. This chapter's
`compose.yaml` edit busted the key and the failure appeared. **A green lane is a claim about what
was re-run.** And **a batch redelivered into itself and the count was the only tell** —
`ingestOnce` reported 16 for a stream holding 8, an `ack_wait` of 1 s against a 2,000 ms fetch
window, diagnosed by printing the stream's own depth.

**READ THE CLAUSES, NOT THE IDENTIFIERS — THREE CITATIONS POINTED AT CLAUSES THAT DO NOT SAY IT.**
Eleven passes read the platform, the tutorial and the structure record; the twelfth opened the SRS
the quotations point at. **DR-11 names neither number** — it governs the SHAPE of an insert, and
the 2 s and 10,000 rows are `docs/05-sad.md:182`'s. **NFR-SCL-01 carries no memory figure** — the
160 MB is SRS revision 1.9, which measured **157 against a 160 budget**; compare against 157, not
the rounded ceiling. **No clause forbade a credential in an analytical record** — the authority is
**constitution III's allow-list**, which refuses by construction. **An allow-list is the citation;
a deny-list about something else is not.** **And FR-ANL-04's qualifier was dropped four times**:
the clause is *"within 60 seconds … **under normal conditions**"*, and a record published during a
broker outage is queryable minutes late and that is not a breach.

**AND AN ADR LIVES IN TWO DOCUMENTS — THE SAD'S SUMMARY AND `docs/06`'s ARGUMENT.** Ten passes
amended the summary and none opened the 98-line deep dive. **The mapping is the argument**:
*"Choosing Redis keeps a clean mapping — gateway to Redis, api and workers to NATS."* 3.8 and 3.18
broke the api half; this chapter puts it on the gateway, and afterwards the mapping describes
nothing. **What is falsified is the arithmetic beside the refusal**, not the refusal: the gateway
holds two clients either way, so ADR-07 survives on Redis alone. **And constitution VII says ADRs
are immutable** while ADR-07 carries two in-place amendments — **the missing sentence is the
defect rather than either choice.**

**403.5 BYTES A RECORD, 26% HEAVIER THAN THE SYNTHETIC FIGURE TWO CHAPTERS HAVE IN PRINT.**
Reconstructing 4.4's method reproduced its figures exactly — which is what made the method
trustworthy before it was applied to anything new. **The 7-day crossover is 4.40 rec/s, not 5.55**,
and a third producer spends the budget outright: two connection-pairs a second takes the request
allowance to 0.86/s.

**TWO CONNECTION-MINUTE COUNTERS THAT MEASURE DIFFERENT QUANTITIES.** The meter charges every
calendar minute a connection was open for any part of; the records give elapsed duration. **2
against 0.03 for the same connection.** The reconciliation compares buckets against buckets and
publishes the gap as a number so nobody reads it as a defect, scoped to connections with BOTH
records present — unscoped it would have compared 8 against 0. **And the record's key needs
`event` in it**: one connection produces two rows with one `connection_id`, and without `event` a
`ReplacingMergeTree` collapses the open into the close.

**THE HABITS THIS FEATURE PAID FOR AGAIN.** **The fenced-file list was remembered, not counted —
eight files, not five**, and wrong in both directions. **A list of fenced files goes stale every
time a chapter moves code between files.** **The tutorial had not built since 4.4 shipped** —
`<ChapterHeader id="4.4" />` throws on an unregistered id, so `pnpm build` exited 1 from the
moment 049 closed, at 112 of 112 with eight gates green. **None of the eight rendered a page.**
`pnpm build` is a gate now. **The vi path that was checked has never existed** — the tree is
`app/(vi)/vi/part-N/`, so that check could only come back empty. **A probe copied from 049 kept
the hazard and dropped the guards** — copy the shape, not the sentence. **And sixteen analysis
passes, none of the last four finding anything in the tree** — they found the artifacts' own
agreement with each other.

**049 IS CLOSED at 112 of 112 — CHAPTER 4.4, "the requests that belong to nobody".** Its record is
`specs/049-chapter-4-4/` — `baseline.txt` first (842 lines), then `gaps.md` (six entries),
`traceability.md`, `tasks.md`. Tagged **`part4-ch4`**.

    54 requests · 34 with no tenant    application 20/20 attributed, platform 18/18 tenantless
    broker up 2.61 ms · down 2.45      200 each side, all 200s — down is FASTER
    320 bytes a record                 (4.5 re-measured the real stream at 403.5)
    check:fences 110 -> 110, delta 0   2,393 prose words · 8 gates · 6 fences, all diffs

**"EVERY REQUEST" AND "PER TENANT" ARE NOT THE SAME POPULATION.** FR-ANL-01 wants an event for
every API request; FR-ANL-07 wants a log per tenant. Every 404, every 401, `/healthz`, signup —
and **every call the dispatcher and gateway make on the internal seam**, because
`PlatformPrincipal` carries `environmentId?: undefined` BY DESIGN. **The gap is widest exactly
where the traffic is.**

**CONSTITUTION I FORBIDS THE RECORD FR-ANL-01 REQUIRES, AND THE THIRD READING IS THE ONE THAT
HOLDS.** Drop them and "every" is false for the busiest routes; invent an environment and 047's
zero-UUID phantom user is back; **or the clause governs tenant DATA, and a record with no tenant
is not tenant data.** Only worth anything because it is testable: a tenant-scoped read returns that
tenant's rows and **zero** tenantless ones.

**THE CONSUMER SHIPPED LAST CHAPTER DESTROYED EVERYTHING THIS ONE SENDS, AND BOTH INSTRUMENTS SAID
NOTHING WAS WRONG.** `analytics-ingester` filters on `analytics.>` and `shape()` knew one record
type; `null` means `m.term()`.

    pass 1: written 1  malformed 1      the attempt wrote — that is the positive control
    pass 2: written 0  malformed 0      terminated, never comes back
    stream still holds 2 of 2 · consumer num_pending 0 · ack_pending 0

`retention: Limits` keeps a terminated message, so depth says the record is there and lag says
there is nothing to do. **`route()` now decides what a record IS before anything shapes it**, so
"not mine" stops being the same answer as "malformed".

**NO MIDDLEWARE POSITION GIVES BOTH PROPERTIES, AND FINDING THAT OUT TOOK THREE ANALYSIS PASSES.**
`RateLimitMiddleware` refuses a 429 with `res.end(); return;` and **never calls `next()`**, so a
producer registered last never runs for a rate-limited request — the one an operator opens a
request log to find. Registered SECOND it does, because **the listener's registration point and
its read point are different moments**. **Attach early, read late.**

**AND TWO OF `refused_at`'s FOUR ARMS ARE NOT OBSERVABLE.** A guard refusal and a handler response
are byte-identical from the producer, so `middleware` and `guard` are STAMPED and `unmatched` and
`handler` inferred. **The `handler` arm is an inference from silence**, so a future guard that
refuses without stamping is recorded as a plausible wrong value. The guard against that walks the
api's source for every `CanActivate` and was run red by deleting the stamp. **And a remedy was
built on a function nobody opened**: pass 3 prescribed "the limiter already knows which route it
matched" across four artifacts, where `operationsFor` returns quota classes, three-valued. **The
question was mis-posed too** — this platform does not limit per endpoint, so a per-endpoint
breakdown of its refusals describes a mechanism that does not exist.

**THE COLUMN TYPE WAS WRONG AND ONLY TRAFFIC SAID SO.** Lint, typecheck, 27 unit tests, the schema
applied and `SHOW CREATE` verified — then `Code: 27. Cannot parse input: expected ',' before
'.556'`. `latency_ms` was `UInt32`; the producer reports fractional milliseconds. **Rounding would
have been one line and the wrong fix**: three of four real requests are under 1 ms and would have
read 0. Nothing was lost — the insert threw, nothing was acked, and the records waited on the
stream. **And `LowCardinality(String)` cannot say "absent"**: an absent field and an explicit `""`
both land as `''`, and **none of 048's three guards reaches it**, because skip-unknown-fields
catches an UNKNOWN field, not an absent one.

**THE BYTE COUNT INCLUDED THE INSTRUMENT.** Two probes read 313 and 315 bytes a record; the
stream's accounting counts the SUBJECT and the probes' subjects differed by two characters. 51
chars → 313.0, 53 → 315.0, **58 → 320.0**, which is the real subject.

**048-6's RECORDED CAUSE IS WRONG, AND THIS CHAPTER MADE THE FAILURE PERMANENT.** It blamed an
ABRUPT `compose down`. A graceful `compose stop` does it too, and so does `restart` — **the stream
that fails to recover is whichever is being WRITTEN**, proven with a control. The api now writes on
every request and Docker polls `/healthz` every five seconds, so **the stream is never idle and
every restart lands mid-write** (049-1). **And the compose api cannot create a stream it does not
have**: `replicas > 1 not supported in non-clustered mode`, because `replicaCount()` returns 3
under `NODE_ENV=production` and the Dockerfile sets it. 474 publish failures accumulated while the
streams were missing; it hid because the streams were first created from OUTSIDE the container,
which is also why 048-6's own repair appeared to work (049-2).

**`check-lane-scope.py` REPORTS ZERO BECAUSE IT LOOKS AT NOTHING.** Line 28 hardcodes a worktree
045 deleted; the glob matches nothing and it exits 0 with all ten controls firing. **That is the
rule its own feature wrote**, and the controls cannot catch it: synthetic strings checked in
memory fire whether or not the corpus is empty. **A control that proves the checker WORKS says
nothing about whether it LOOKED** (049-3).

**CONSTITUTION VI's 100%-BRANCH CLAUSE IS MET RATHER THAN PINNED, FOR THE FIRST TIME IN PART 4.**
It names tenant isolation, and this chapter's tenancy branch is in `event.ts` at 100/100/100/100.
048 recorded the same clause as unreachable because its idempotency was a sorting key and **a
schema has no branches to cover**. **And a pin that could not fail was found by sweeping for it** —
`vitest.coverage.config.mts` excluded `**/main.ts` and also pinned `services/ingester/src/main.ts`:
45 per-file pins, exactly 1 unbindable. **Both halves of the probe were run**, which is the step
048 skipped.

**THE FENCE CHAIN CHARGED FOR SIX FILES THIS CHAPTER TOUCHED.** The first draft carried no fences
and the chain went 110 → 116: six files that earlier chapters publish as whole bodies no longer
matched the tree. Six `diff` hunks took it back to **110, delta 0**. A whole body would have been
the 111 → 203 trap.

**047 IS CLOSED at 74 of 74 — CHAPTER 4.2, "the store that was never listening".** Its
record is `specs/047-chapter-4-2/` — `baseline.txt` first, then `gaps.md` (five entries),
`traceability.md`, `tasks.md`. Tagged **`part4-ch2`**. Nine analysis passes; the pass-by-pass
narration is in that `baseline.txt`.

    13.22 ms against 4.1's 585.9 ms   both best of 3, both 91 days, same question
    315 rows read against 1,052,655   the rollup, for 19% less time
    90 of 91 days agree exactly       the 91st cannot, by 4,941 — 0.49% vs a 0.1% bound
    check:fences 110 -> 110, delta 0  2,580 prose words · 8 gates green · 6 fences

**THE STORE HAD BEEN UNREACHABLE FOR SIXTEEN CHAPTERS BEHIND A GREEN TICK.** `/ping` neither
authenticates nor is network-restricted, so it answered `Ok.` while every query from outside the
container was refused. **A check that cannot fail for the reason you care about is not a check**
— and the two halves do not even name the same mechanism: the image restricts by NETWORK and the
caller sees an AUTHENTICATION error. Write down what the failure looks like from outside, not
what the config file says. (4.9, 4.10 and 4.13 each found this shape again.)

**THE ROLLUP AND THE RAW TABLE DISAGREE ON ONE DAY AND ALWAYS WILL.** The TTL cuts at a TIMESTAMP
and a daily rollup's finest grain is a DAY, so the oldest day in the window is counted whole by
the view and then partly deleted from the source: **0.49% against FR-ANL-06's 0.1%, at any
cardinality.** The distinct-user half came back 5,000 against 5,000 — `uniq` is exact to 65,000,
so that zero is a fact about the corpus and is published beside the table proving it. **DR-10 AND
FR-ANL-06 CANNOT BOTH HOLD**: `uniq` is off by 0.51% at 70,000 distinct, and **the threshold is a
cardinality, not a row count**, which is why testing at the corpus's 5,000 users would never have
found it.

**AND THE TTL REMOVES ROWS AT INSERT, NOT AT MERGE** — 120,000 rows over 120 days became 90,000
immediately, silently. It is a **schedule, not an event**, so **a row count taken the moment a
load finishes shrinks overnight on its own.** A materialised view fires on the same insert and
**goes first**, so `daily_usage` holds 120 days of figures for rows that never persisted; that
thirty-day gap is the design (DR-09 expires raw events, DR-10 says metering never reads them) and
**no artifact said so** until FR-003a. `EXPLAIN indexes=1` is the only honest instrument for
granule skipping; `ProfileEvents['SelectedParts']` returned **0** for the same query.

**PASS 9 ASKED WHICH DATABASE, AFTER EIGHT PASSES OF ASKING THE DATABASE.** Every number was
consistent, reproducible and correct — **about the lane `relay`, which is not what the chapter
loads.** `corpus.mjs` builds `relay_corpus_<timestamp>` and refuses `CORPUS_DATABASE=relay` in as
many words, and writes no attachments, edits or deletions at all — so **three of the four column
findings were invisible in the store the chapter builds.** *Ask the database a question with a
yes-or-no answer* was right eight times running and never asked **which database**. **A premise
does not stop being a premise because it is the one your best instrument stands on** — the first
CRITICAL in nine passes, found by reading a file that had been cited all along.

**AND THE LOAD'S COLUMN EXPRESSIONS WERE WRONG IN THREE WAYS ONE `SELECT` FOUND.** `postgresql()`
delivers jsonb as `Nullable(String)`, so `length(attachments)` gives 151 for a two-attachment row;
`length(text)` is **bytes** where FR-EMJ-02 counts code points; and a NULL `user_id` into a
non-nullable `UUID` becomes the **zero UUID** silently — one phantom active user per environment.
**R6 proved `postgresql()` could READ Postgres and stopped there: reachability is not mapping.**
Then `event` was written as the literal `'created'` for 4,056 deleted and 3,201 edited messages,
in a table whose rollup filters on that label. **A store reconstructed from current state cannot
recover what the state no longer holds**: 3,282 creations have no recoverable `text_length`,
because a tombstone preserves no prior text — FR-ANL-02's emit-at-the-time rule three chapters
before the ingester. And `messages.edited_at` holds the LATEST edit where `message_edits` holds
one per edit, so 734 events were lost, invisible because the headline rollup filters on `created`.

**THE THREE PART 1 TAGS WERE NOT ORPHANED, THEY WERE WRONG.** They pointed at a superseded lineage
— old tags matched 14 of 20 whole-body fences, the new ones 19 of 20. Moved, annotated, pushed;
the old lineage is `backup/part1-orphan-lineage-20260913`. **And nothing could have caught it**:
`check-fence-chain` replays onto the working tree and compares against `HEAD`, so it never
resolves a tag. **No gate in these three repositories checks that a chapter's tag matches the
chapter**, which is what `relay-platform/README.md:8` promises.

**AND THE FENCE DELTA HAS A NEIGHBOUR.** 110 is **APPLY 74 — 30 `(en)`, 30 `(vi)`, 14 elsewhere —
and HEAD 36, all `(en)`.** A bare total moves for reasons the chapter did not cause. Third time in
one feature that a delta needed the thing beside it held still.

**AND THE DIRECTION THAT ERRORS IS THE SAFE ONE.** `DROP TABLE` on a source under a live
materialised view **succeeds with no error** and leaves an orphan that still answers queries, with
zeros; inserting into the missing source errors loudly. `--drop-all` is `DROP DATABASE` for that
reason. **And an instrument that walks one side of a relationship only tells you about that side**
— the ledger caught a file that changed and nothing that vanished, because the run walks the
directory.

**046 IS CLOSED at 76 of 76**; its record is `specs/046-chapter-4-1/` — `baseline.txt` first,
then `gaps.md` (eight entries, two closed), `traceability.md`, `tasks.md`.

**PART 4 IS 22 CHAPTERS, AND IT CONTRACTED TWICE.** `docs/12` split movement I in two;
**chapter 4.1 shipped with both halves at 2,132 prose words**, inside the bound, so movement I
is one chapter and every ordinal after the first moved down by one — 24 to 23. Then **4.2 built
all four items of the ledger chapter's brief** (runner, filename-and-checksum ledger, reporting
idempotence, a checksum refusal tested red), movement II had one subject left, and every ordinal
after 3 moved down again — 23 to 22, amended 2026-09-13. Milestones are at **9, 17 and 22**.
**§3's own heading still says 23** and this block said so until analysis pass 8; the specs' "of
22" was right. **§3's table keeps the ORIGINAL ordinals in column one on purpose** so older
references resolve — the movement column is the stable address, and reading the table's first
column as current is how a chapter number goes wrong. **Both corrections ran downward** —
Part 3 was planned as seven and shipped 26 —
and `docs/12` and `docs/07` were both amended before 047's spec was written rather than after
they disagreed with it. **4.2 is "ClickHouse from zero", not "the index that would fix it".**

**WHAT 4.1 MEASURED, AND IT FALSIFIED ITS OWN PLAN TWICE.** There was no metering query to slow
down — Part 3's counters are two pure functions on the send path. Then: an analytical query does
**not** tax the write path here (send p95 20.5 ms alone, **13.7 ms beside 102 of them**, four
control loops inside 1.3 ms), and the index that should fix the query **buys a gap inside the
run-to-run spread for +49% storage**. The join is 140 ms of a 698 ms plan and **the sort is 656**.
**You cannot index your way out of an analytical question when the cost is the aggregation** —
which is what 4.2's `ORDER BY (environment_id, ts)` and its rollup exist to answer.

    M1 585.9 ms over 1,000,000 rows   ·   lane's busiest env 0.9 ms over 1,018   ·   651x
    column 24.8 MB + index 62.0 MB = 86.8 MB permanent on a 178.6 MB table
    check:fences 110 -> 110, delta 0   ·   2,132 prose words   ·   8 gates green   ·   part4-ch1

**NINE ANALYSIS PASSES FOUND 27 THINGS AND, FROM PASS 4 ON, ONLY THEIR OWN PREDECESSORS'
REPAIRS.** The last finding from the tree was pass 3's 403. **Phase 2 then found six in ninety
minutes and five were invisible to reading**: an application holds two environments, not three
(FR-TEN-04, `unique (application_id, kind)`); the table is **`members`**, not `channel_members`;
`addMember` writes an outbox row; a small random formats as scientific notation and `interval`
will not parse it; a uniform offset lands 999,786 in a window asked for a million; and
**`channels.last_sequence` is a counter the write path maintains**, so a bulk insert that leaves
it at 0 makes every later send collide. **Reading cannot find what the schema refuses.**

**AND EVERY MEASUREMENT WAS WRONG BEFORE IT WAS RIGHT.** One query beside a 60 s loop is 1%
overlap; quiet-then-busy confounds the neighbour with the cache — the fix is a warm-up and a
**second quiet loop after busy**. The storage figure was wrong three times, each conflating a
different pair: +204 MB column plus dead tuples, +107 MB index plus un-vacuumed bloat, +4.3 MB
index **minus** the compaction the vacuum had just done. **A delta between two totals is not a
measurement of the thing that changed unless nothing else changed.** Two of three falsifications
also failed for the wrong reason — one on a JS error rather than the constraint, one on a count
the check does not read.

**THE TAG NAMESPACE IS CONSISTENT AGAIN.** Part 4 tags as **`part4-chN`**; `rework/` was a
rebuild artefact and does not carry forward. **The twenty-one stale `part3-chN` tags are deleted,
local and remote, in all three repositories** — they resolved to the replaced history, so
`README.md:8`'s promise was false for Part 3 and every SKIP AHEAD box with it. All 21 commits
remain reachable from `backup/pre-main-move-20260911`, checked after the deletion. **Three Part 1
tags are on neither `main` nor the backup** and are the only thing keeping those commits alive:
`gaps.md` 046-8.
<!-- SPECKIT END -->

    045 "part 3 rework"           24 chapters -> 26, eight movements, English prose only
                                  296 -> 110 fence-chain problems · 26 of 26 tags typecheck
    SC-007  403.76 s -> 232.05 s, 20 of 20 green, stdev 0.51, cv 0.22%
    044 "the revision watermark"  one column, raised inside the transaction that edits or
                                  deletes, never by a send · reported on every `connection.ack`
                                  **the platform reports and never compares**

**WHAT IT COST TO MAKE THE LANE FAST, AND WHERE THE TIME ACTUALLY WAS.** `fileParallelism: false`
had been serialising the api and gateway lanes since the outbox chapter, for a real error — two
suites issuing `CREATE TYPE` against one schema. **The reason died eight chapters later** when
`globalSetup` began migrating once before any file starts, and the setting stayed, justified in a
comment written in the very chapter that closed the race.

**EIGHT PLACES HELD THE LANES APART, THE ESTIMATE SAID THREE, AND THREE OF THE EIGHT ARE NOT
ASSERTIONS AT ALL** — a fixture planting rows no broker will accept, two forged frames a required
field three chapters later invalidated, and a count that could never have failed for its own
reason. Six were found one failure at a time over six runs; **the last two came from asking the
tree in one pass.**

**AND THE WORKER COUNT IS A BILL, NOT A SETTING.** Vitest defaults to about one worker per core —
here eighteen NestJS apps against one Postgres, which killed two battery attempts before anything
was measured. Every second of the api lane's saving is in **one worker to two** (177 s -> 102 s
for 87 MB); a ninth buys nothing and costs 1.2 GB. The gateway's knee is **four**, not two. **The
right worker count is per-lane and measured; a default is a number about the machine, chosen by
something that has never seen the workload.**

**044'S REVERSAL IS THE LESSON THAT OUTLIVED IT.** A draft had the client present its counts on
the upgrade URL. It was built, then removed. **A parameter the server parses and never acts on is
a contract it can never remove**; one it acts on hands the client a number the platform decides
with, which is how a fabricated count becomes a denial of service the client controls. Removing
it also deleted three edge cases rather than handling them — **a design in which a case cannot
arise beats a branch that handles it**, because the branch is the thing that rots.

## AN INSTRUMENT THAT REPORTS ZERO HAS TO PROVE IT LOOKED

Four lies in two features, each in a different way, and the rule is the same every time:
**a zero from an instrument is a claim about the corpus only if the instrument can be shown
to have read it.**

**`grep` ON THIS MACHINE IS ugrep 7.8.4, NOT GNU grep** (`/usr/bin/grep` is GNU 3.12; PATH
resolves elsewhere). A grouped alternation followed by two negated classes matches nothing under
it and matches under GNU — `(postgres|redis)://[^:/@]+:[^@/]+@` gives ugrep 0, GNU 1, over a
corpus holding the string twice. **Give every pattern a positive control**, and report a pattern
that fails its own example as BROKEN rather than as zero. One shipped gate uses the construct
(`check-srs-ids.sh:49`); it agrees under both engines.

**A PER-FILE COVERAGE THRESHOLD WHOSE KEY MATCHES NO FILE IS SILENT.** Demanding 101% of
`this-file-does-not-exist.ts` produces no error, no warning, nothing. **Run both halves of that
probe every time the ratchet is re-pinned.**

**A CHECKER HANDED A REF THAT DOES NOT RESOLVE COMPARED NOTHING AND EXITED 0** — twenty-six
times, printing `12 fences, 0 compared, 0 problem(s)`. **The zero that means "clean" and the zero
that means "never looked" printed the same line**, and four real problems sat behind it. A checker
must refuse its arguments rather than trust them, and refuse a run that compares nothing (045-81).
**4.13 found this exact shape inside `integration-gate.mjs`, the instrument built to prevent it.**

**AND A TEST WRITTEN BY THE AUDIT THAT FINDS VACUOUS TESTS WAS VACUOUS.** It passed identically
with the counter moved outside the transaction, because the path refuses earlier and the bump
never runs. **Ask what would have to be false for this to fail, and then read the code it calls**,
not the test.

## COVERAGE IS NOT REPRODUCIBLE RUN TO RUN, AND THE RATCHET HAS TO ALLOW FOR IT

`session.ts` functions measured **87.80%** and **85.36%** on identical code twenty minutes apart
— about one function of forty — while every other pinned file was byte-identical across both
runs. A floor at the measured value goes red for no change to the code, and the fix is then to
lower it: **a ratchet that teaches people to lower ratchets.** Pin below the lower observation by
the observed swing and put both numbers in the config. **And 4.13 found the other two shapes a
red pin has**: a DENOMINATOR that differs between machines (059-20), and a pin that is right
while its environment is wrong (059-22). **Ask what the number is measuring before you move it.**

**AND A p50 IS NOT AUTOMATICALLY THE ROBUST STATISTIC.** Six runs a side: edit mean cv 12.9%,
edit p50 **17.3%**; delete mean 13.5%, p50 **20.6%**. **p50 was noisier on both paths** — a
median of 200 samples with a long tail wanders inside a crowded middle while the mean is anchored
by the whole sample. Resolving a 10% shift at that variance needs ~26 runs per side; the
criterion was kept with its resolution limit recorded rather than adjusted to fit.

## READ THE CLAUSES, NOT THE IDENTIFIERS — AND THEN RUN THE TASK

**FOUR DOCUMENTS AGREED ON TWO CLAUSES THAT DO NOT EXIST.** Spec, plan, tasks and quickstart all
said 044 would amend "SRS FR-016a and FR-016b" — chapter ids, absent from `docs/04-srs.md`. Three
analysis passes saw agreement because the artifacts agreed with EACH OTHER and not with the tree.
What found it was **opening the SRS to make the edit**, and reading the clauses gave **three** to
amend where the requirement named two. 045 hit the same shape from the other side: a sweep passed
`rework/part3-base` twenty-six times and there is no such tag.

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
nobody working on them**. **A lookalike nearly closed one** — a test file asserting the right
shape about the wrong pair of lists. **Read the assertion, not the filename.**

**045 CARRIED COMMITS RATHER THAN ITEMS, AND THE FAILURE MODE IS THE SAME ONE LEVEL DOWN.** Four
of the first rows were decided wrong, in opposite directions, for one reason: **a commit was
classified by one of the things it does.** **THE `test(` / `fix(` PAIRING IS THE SPECIFIC TRAP,
AND IT CAUGHT THIS PROJECT THREE TIMES IN ONE CARRY** — a tombstone test, a race test and a
teardown assertion were each taken without the `fix(` commit they were written to prove, and every
time the symptom was a suite that failed some or all of the time and read as flaky. **A red test
is the visible half, so it gets carried first and alone.** Before taking a `test(` commit, find
the fix it exists to demonstrate. **And four of six skips were right for a better reason than
expected** — the work was already in the chain, arrived at independently, and in three cases in a
STRONGER form. **Cherry-picking blindly would have downgraded the chain.**

**A TASK ID IN A TEST TITLE OUTLIVES THE TASK, AND A TITLE IS THE PART READ DETACHED FROM ITS
FILE** — a CI summary has no repository to grep. Ids anywhere in test files still number **330
across 46 files**, filed rather than swept.

## TWO CLOSED STORIES, KEPT FOR THEIR RULES

**A HAND-MAINTAINED TABLE CANNOT BE CHECKED.** Nine api ports came from hand-allocated bands
across eight files, and **two bands contained a service the lane itself runs** — 5432 inside
`membership`'s range, 4222 inside `limits`'. The failure is silent both ways: the child cannot
bind, and the health check gets its answer from whatever *does* hold the port. All nine now use
`PORT=0` with the port read from the child's own log line, and the map is **deleted rather than
corrected**.

**A TEST OF A SCRIPT MUST ASSERT WHAT THE SCRIPT DID, NOT WHAT THE TABLE HOLDS.** `reset-lane`
counted rows "due now", which a run that just finished violates legitimately, and counted
staleness against a `now()` re-evaluated ~115 ms after the script's own. **Pin one instant before
the script runs** — the same pin 045 needed to keep that suite's whole-table count honest under a
lane that no longer serialises, and the same shape 4.13's `pinWindow` needed for a rate limiter.

## OTHER THINGS 043 PAID FOR

**A RED PROBE WRITES TO THE LANE.** Reverting the avatar rule to check the tests could see its
absence left two `javascript:alert(1)` rows stored, accepted with a 200 — and the next measurement
read them as pre-existing data contradicting the plan. **Clean up a probe before anything is
counted.**

**AN ASSERTION SCOPED WIDER THAN THE THING IT TESTS FAILS FOR SOMEBODY ELSE'S REASON.** 043 found
two — a whole-table `outbox` count and a wall-clock minute bucket — and **the first fix was worse
than the fault**, sleeping to the next boundary and blowing the test's timeout. 045 found six more
and made the class checkable; 4.13 found the minute bucket still open, in a file 043 did not sweep.

**WHEN MEASUREMENT FALSIFIES A CLAUSE, AMEND IT.** Done three times: FR-RTM-09 and FR-RTM-10 in
the SRS (revision 1.8), and **043's own FR-016**, which would have refused 838 stored
subscriptions to a declared, published, unbuilt event type. The governance clause requires
amendment rather than silent divergence, and that applies to a feature's own specification.

**A PLAN COUNTS THE FIX AND NOT THE VERIFICATION.** 17 files estimated, 58 changed, and every
unplanned one came from RUNNING something rather than reading it. 045 said three and found eight,
the same way. **The error is in one direction, every time.**

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

## A COMMENT THAT SAYS *WHEN* SOMETHING RUNS MUST NAME ITS CALLER

`store.ts` said *"ON BOOT, EVERY BOOT"* and every caller of `ensureBucket` was a test
`beforeAll`. Nothing ran it at boot, so on a store that had never held a bucket every slot
request answered 503 forever — and no local run could see it, because the volume persists.

**The convention, and it costs nothing to follow.** A claim about the moment a symbol runs
names the thing that runs it:

    ON BOOT, EVERY BOOT                    -> unverifiable, and it was false
    Called by `storeReady` on a 404        -> one grep, and the symbol vanishes when it rots

Applied where it was already wrong: `store.ts`, `store.test.ts` (twice — the same sentence
copied into a test) and `auth-limiter.ts`, which now names `AuthenticateMiddleware` and the
`{*path}` that applies it. **Two of the four stale claims were written by the fix for the
first one, three hours earlier.**

**AND THE SURFACE IS THIRTEEN LINES IN TEN FILES**, measured — `on boot|at boot|every
boot|on startup|at startup|runs on every|called on every|once per process` across
`services/*/src` and `packages/*/src`. Most are counterfactuals (*"a default-scoped
repository would be built once, at boot"*) and correct. A checker over that grep, requiring
the enclosing exported symbol to have a non-test caller, would have caught this one with
almost no noise; the naive version — flag every export whose only callers are tests — reports
**37** and nearly all are legitimate helpers, which is a hand-maintained allow-list and the
thing this project refuses. `gaps.md` 056-10.

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

**THE READER PROTOCOL IS RETIRED.** Chapters 3.14 onward each named this gap, 045 was the
fourteenth record to name it and not close it, and 046 is where it was **decided rather than
deferred again**. Fifteen intentions and no runs is not a gap, it is a habit.

**THE ARGUMENT IS ABOUT COST.** A chapter's tag is cut on `relay-platform` and its prose lives
in `relay-tutorial`, so a prose correction after publication moves no platform commit and
invalidates no tag. A chapter contributing no TITLED fences changes `check:fences` by nothing —
4.1 contributes 0 and its close-out delta was 0. **Feedback on the writing comes from readers
and is applied then**, and a gate earns its cost only when the thing it guards is expensive to
change. Prose here is cheap; the fence chain is not, and that is where the gates are.

**WHAT IS GIVEN UP, AND IT IS REAL.** 044 had the sharpest evidence for what the exercise
finds: reading the published text with the spec and source closed found a hole — FR-008's
client half was missing — **because that exercise finds information that is ABSENT**. Nothing
now finds that. 046 accepted the risk with its eyes open: **its argument changed twice during
measurement and the prose was rewritten each time by the person holding the numbers.**
`specs/036-chapter-3-18/reader-protocol.md` stays in the tree as a procedure anyone can pick
up; it is no longer a criterion any chapter has to satisfy.

Every check in these three repositories compares bytes. Twelve Python instruments and five
`check:*` scripts — and not one can say whether a paragraph is understandable to somebody who
does not already know the answer. Each says so in its own last line:

    check-refs: ids only — this says nothing about whether the prose around them is true
    check-chapter: bytes only — it cannot say whether the PROSE describes the diff
    check-lane-scope: SQL text only — a scope applied in JavaScript is invisible to it

**An instrument that is easy to run tells you what it measures, not what you wanted to know.**
