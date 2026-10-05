**THIS FILE HAS A LENGTH BUDGET: 150,000 CHARACTERS, AND THE HARNESS REFUSES IT OVER THAT.**
173,971 on 2026-09-27, 149,985 at 067's close with **15 characters to spare**, and **89,302
after the compression below.**

**THE OLD CONVENTION — compress the previous feature's entry when one closes — STOPPED PAYING
FOR ITSELF AND 067 IS WHERE IT RAN OUT.** Compressing 066 exactly as prescribed recovered 2,173
characters against an entry that wanted 6,000, so the active-plan block went too, then five
paragraphs of 065, then the new entry was cut seven times. Fifteen characters is not a margin,
it is a coincidence.

**WHAT REPLACED IT.** An entry older than the last four is cut to **its headline, its
measurement blocks, any paragraph carrying a gap id cited from elsewhere in this file, and a
one-line digest of every other finding's claim.** The claim survives so a session knows the
finding exists; the argument lives in `specs/<feature>/`, where `baseline.txt` carries the
measurements in the order they were taken and `gaps.md` the numbered entries. Applied to 046
through 059 it recovered **60,683 characters** — roughly ten chapters of runway — and lost no
cited id, which was checked both ways rather than assumed.

**WHAT IS NOT COMPRESSED, EVER.** The durable-rule sections from "AN INSTRUMENT THAT REPORTS
ZERO" onward are not per-feature; they are what a fresh session actually needs, and the
compression left them **byte-identical**. The last four features keep their full entries,
because a finding is still being cited while it is recent.

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

**PART 4 IS 23 CHAPTERS. IT CONTRACTED TWICE AND THEN EXPANDED ONCE** — 24 to 23 when
movement I shipped as one chapter, 23 to 22 when 4.2 built all four items of the ledger
chapter's brief, and **22 to 23 when the Priya milestone's premise check found the channel
routes contradicting FR-USR-01 and ADR-18 on thirteen routes** (feature 068). Rule 4 says a
milestone verifies rather than builds, so the fix is its own chapter placed BEFORE it.
**Milestones are at 9, 17 and 23.** `docs/12` §3's table keeps the **original** ordinals in column one on
purpose so older references resolve, so reading that column as current is how a chapter number
goes wrong; the movement column is the stable address. **Part 4 tags as `part4-chN`** —
`rework/` was a Part 3 rebuild artefact and does not carry forward, and the 21 stale
`part3-chN` tags were deleted in all three repositories (`gaps.md` 046-8).

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

**ACTIVE PLAN: `specs/068-chapter-4-22/plan.md`** — chapter 4.22, "The identifier the
customer gave it". The milestone that found this is **069 / chapter
4.23** and comes after.

**PART 4 EXPANDED TO 23 FOR THIS.** The Priya milestone's premise check could not complete
Journey 3 Stage 2: `GET /v1/channels/{externalId}` answers **500**, and so does every route
under that prefix — **13 of 13 take a uuid Relay minted.** FR-USR-01 says *"Relay shall not
generate end-user identities"* and ADR-18 says an end user's identity *"is whatever
`external_id` the customer already had for them"*, so **a uuid here is a KEY and the
customer's string is the IDENTITY.** A customer must store Relay's uuid to post to a channel
they named — the lookup table FR-CHN-01 exists to remove. Rule 4 says a milestone verifies
rather than builds, so the fix is its own chapter placed BEFORE it.

**EXACTLY TWO TABLES CARRY A CUSTOMER IDENTIFIER — `users` AND `channels` — AND THE PLATFORM
ALREADY DEMONSTRATES THE RIGHT ANSWER ON ONE.** Users: 8 of 8 routes take the identity and
the upsert returns no uuid. Channels: 0 of 13, and the create returns the uuid first. The
users side needs **one** change — the listing cursor is base64 of `{a, id}` and its own
comment says *"OPAQUE IS NOT SECURITY"*, which is also where 4.23's ADR-37 reversal condition
rests.

**THE 500 IS A FAILED CAST, WHICH MAKES THE FIX AND THE REPAIR ONE EDIT.**
`'order-88412'::uuid` raises in Postgres before any `OR` can short-circuit, so a value that
cannot be a uuid is never cast under the new resolution and the error cannot arise. **And the
api logs the status without the cause** — one `"status":500` line, no `22P02`, nothing an
operator can act on (058-3 counts 22 routes that can produce one; not this chapter's to fix).
**The design is a pipe, because the cheaper middleware runs BEFORE guards** and an unscoped
resolution is a cross-tenant read. **157 existing call sites pass a uuid** and must not change.

**THE AGENT-CONTEXT HOOK CANNOT RUN HERE AND EXITS 0 WHEN IT DECLINES.** PyYAML is not
importable by this `python3`, so it skips with a clear message. **It would also have pointed
at the wrong feature** — it auto-detects the most recent `plan.md`, which is 069's — and its
replacement block is three generated lines, which would delete everything above. **These
markers span only this block, deliberately**, moved during 067's planning when they enclosed
118,636 bytes.

<!-- SPECKIT END -->

**067 IS CLOSED — CHAPTER 4.21, "Erasure, and every path it must find".** Movement VII's
fourth. Its record is `specs/067-chapter-4-21/` — `baseline.txt` first, then `gaps.md`
(**3 new plus the carried ledger re-measured**), `clauses.md`, `traceability.md`,
`contracts/erasure.md`, `quickstart.md` (run, **wrong twice**), `tasks.md`. **SRS 1.28**, **ADR-37**, `docs/12` row 22 CLOSED,
three sites in `docs/05-sad.md`, both Part 4 tables. Tagged **`part4-ch21`**.

    check:fences 6 -> 0 -> 1 -> 0 · 291 files across 64 chapters      from 63
    2,649 prose words · 4 figures · 2 TRAP · 4 WHY · 0 titled fences
    11 appendix hunks across 7 files — six, then the pin file made a seventh
    api integration 53 files, 904 tests, EXIT 0   from 52 files and 1 failed
    coverage 154 files, 2,205 tests · ZERO threshold errors · 77 pins from 74
    the analytical half costs 16 ms · the operational half 10
    FIVE ANALYSIS PASSES: 14 findings, 3 CRITICAL, all three fixed before any code

**ONE DECISION PRODUCED THE WHOLE STRUCTURE AND IT WAS NOT A MECHANISM.** FR-MOD-04's hard
word is `messages`: it says erase them and FR-USR-05 says keep them, both deliberately. The
reading taken is Slack's and Teams' — **a compliance erasure asks for removal of a PERSON,
not of a conversation**. Keeping the messages means `messages.user_id` stays; all five
foreign keys to `users` are `NO ACTION`; **so the row can never be deleted and erasure leaves
a tombstone.** The chapter opens on a behaviour rather than an error: you delete a user the
way the platform already allows and find everything still there, every bit of it a clause
working.

**AND THE TOMBSTONE TURNED THE HARDEST STORES INTO THE EASIEST — ADR-37.** `usage_active_users`
(22,774 rows) and seven `AggregateFunction(uniq, Nullable(UUID))` sketch columns could not
have one user removed: a sketch has no subtract operation and deleting billing rows
retroactively breaks an invoice. **A key into an erased row names nobody**, so both are left
untouched and the `count(*)` that is the billing figure is unchanged to the row. **What was
going to be published as the chapter's weakest limitation became its argument.** The line is
**keys against contents**, and it is testable: `messages` and `media_objects` both hold
contents, were decided on their own clauses, and **went opposite ways**.

**AND THE STORE THAT CANNOT COMPLY IS NOT ANALYTICAL.** `audit_log.target_id` is the person's
EXTERNAL id on **1,357 of 1,357** user-target rows, append-only under ADR-35 — **and the
erasure writes one more**, because that entry is the operator's only proof. **The one place
the name survives is the record that the name was erased.** Narrowing ADR-35 a second time
was refused: two exceptions three chapters apart is a list (`gaps.md` 067-1). `external_id`
is **replaced, not cleared** — `NOT NULL` under a unique index — with `erased:<users.id>`,
legal only because of ADR-37.

**A PUBLISHED PAYLOAD THAT DOES NOT REPRODUCE ITS OWN FINDING.** `research.md` R9 named
`ev'il OR 1=1 --`; it is a **syntax error**, `Code: 62`, which an interpolating implementation
survives as a caught error and a `not_reached` line — a SAFE failure. `' OR 1=1 --` is the one
that parses, and the leading quote has to CLOSE the literal. **The probe run against the
published payload went red on the wrong assertion and would have been recorded as proof.**
**A payload that errors tests the error path; only one that parses tests the predicate.**
Measured correctly: one erasure of one user destroyed **1,113 of 1,116** `connection_events`
rows belonging to other tenants. The remedy is bound parameters on `AnalyticalStore` — 4.8's
*a type, not an escape* does not transfer, because a free-text external id has no type.

**THE PIN PROBE CAUGHT MY OWN PIN AS A SIDE EFFECT OF TESTING ITSELF.** Both halves at once:
the absent-file pin silent, the impossible-pin-on-a-real-file fired — **and the same run
reported `erasure.ts` at 81.81% against a pin of 90 written assuming 100.** **A pin above the
real number is loud; a pin below it is as silent as a pin on a file that does not exist.**
Run both halves every re-pin, not once a feature.

**AND A COVERAGE NUMBER FOUND A CLAIM NOTHING CHECKED.** `repository.ts` held at **179 of 180
functions across two runs whose failures differed**, ruling out the flaky-neighbour reading
and leaving `eraseUser`'s `owned.map(...)`: **every fixture made a user with no uploads, so
the receipt reported `media_objects: rows 0` for a branch no test had entered.** The pin
stayed at 100 and the fix was a test — a third shape, neither a moving denominator nor a
wrong environment but **an arm the suite never reached**, where a red pin is simply right.

**AND THREE OF FOUR TENANCY ARMS WERE INVISIBLE.** Deleting `@Accepts("application")` turned
nothing red — 4.18's finding one route over with the consequence inverted: here an end-user
token reaching the handler **destroys another person's data** and every read-shaped assertion
still passes. Two arms became tests; the fourth is redundant behind a scope one call down,
and deleting BOTH turns 2 of 122 red.

**A FEATURE-LOCAL ID REACHED A CUSTOMER-FACING RESPONSE, AND THE SWEEP SAID ZERO.** `FR-028`
and `FR-029` resolve to nothing in the SRS and went into the receipt's `note` fields — read by
a compliance officer **at a customer**, who cannot resolve them at all. 053's defect one step
out. **And `git diff <tag>..HEAD -- docs/` reads COMMITTED state**, reporting 0 while two
`FR-014`s sat in the working tree. `..HEAD` is how a diff quietly stops looking (067-3).

**AND TWO TASK PREMISES DIED BECAUSE TWO DECISIONS WERE DEFERRED INTO IMPLEMENTATION.** T021's
probe could not go red, T031's receipt does not exist, and the quickstart was wrong twice —
one cause. **A prediction written before a decision is a prediction about the draft**, and
deferring one is paid for in every artifact that assumed the other answer.

**066 IS CLOSED — CHAPTER 4.20, "The messages that expire".** Movement VII's third. Its record
is `specs/066-chapter-4-20/` — `baseline.txt` first, then `gaps.md` (4 new plus the carried
ledger), `clauses.md`, `traceability.md`, `quickstart.md` (run, **wrong five times**),
`tasks.md`. **SRS 1.27**, **ADR-36**, `docs/12` row 21 CLOSED. Tagged **`part4-ch20`**.
CI 37199508332 green on all four jobs, first push, error set empty both ways.

    check:fences 5 -> 0 -> 1 -> 0 · 291 files across 63 chapters      from 62
    2,812 prose words · 4 figures · 2 TRAP · 2 WHY · 0 titled fences in the chapter
    12 appendix hunks across 6 files — and the bill named all six at ANALYSIS
    api lane 52 files, 1 failed — from 50 and 3 · sealed suite 21 of 21
    a message costs 0.04 ms to destroy and a media object 2.05 ms — ~48x
    SIXTEEN ANALYSIS PASSES: 4,4,4,4,3,4,6,3,3,4,3,3,2,2,2,2 — 5 CRITICAL

**THE REFUSAL IS A PINCER WITH A THIRD JAW.** The foreign key refuses the parent, 4.19's
trigger refuses the children, and **`ON DELETE CASCADE` is refused too — a cascade issues an
ordinary `DELETE` and a ROW trigger fires on it**, with the error naming the generated
statement. **A cascade is not a privileged path.** Only `session_replication_role = replica`
works, which is the hole ADR-35 published as the limit of its own guarantee.

**AND THE CHAPTER'S FIRST PRODUCT IS A READING, NOT A MECHANISM.** Three documents reserved
hard deletion and a fourth required it. **The constitution says `path` where FR-MSG-08 said
`endpoint`** — so the rule hardest to change is the one that already permitted this, and
FR-MSG-08 and DR-06 were amended instead (ADR-36). The option refused is **soft expiry**:
clearing `text` satisfies all three reserving clauses word for word and is the only reading
that keeps every internal rule and still tells a compliance team their data is gone while the
row is there.

**THE GUARANTEE IS ONE KEYWORD AND BOTH WAYS OF GETTING IT WRONG ARE SILENT.** Plain `SET`
leaves the flag on a pooled connection; **`SET LOCAL` outside a transaction block is a
WARNING**, leaves it unset, and every cascade is refused indistinguishably from the trigger
working. **The test asserts the flag's VALUE at the moment of the delete.**

**A CACHED TURBO RUN REPLAYS THE COUNTED LINE AS WELL AS THE EXIT CODE.** `pnpm test` answered
**EXIT 0 with every `Test Files N passed` line in 17 ms**, `Cached: 13 of 13` — nothing ran.
055-4's *assert the counted line* is **necessary and not sufficient against a cache**; the
tells are `Cached:` and the elapsed time. **And a positive control that did not fire looked
exactly like a passing probe**: an impossible coverage pin on a REAL file produces nothing
under a filtered `vitest run`, because **a filtered run does not evaluate per-file
thresholds**. The probe has to go through `pnpm coverage`.

**REUSING A FUNCTION THAT ALREADY EXISTED WOULD HAVE ENFORCED THE WRONG CLAUSE.**
`unreferencedMediaIn` asks *which objects older than X does no message reference* — a superset
including objects nothing ever attached, which are FR-MED-10's orphans. **Its second query is
reusable and its first is a different question**, and **its comment stays true, so it must NOT
be repaired** — the mirror of leaving a stale one.

**AND THREE TESTS WRITTEN BY EARLIER CHAPTERS FIRED ON THIS ONE.** `rendition.itest.ts`
asserted that nothing deletes a `media_objects` row **and told whoever broke it what to do**.
`repository.itest.ts`'s source walk caught a `Repository` built with no actor; the answer is
`RECORDS_NOTHING`. And **the fence bill named all six files at analysis**, including
`gauntlet.itest.ts` — a route is not one edit, and **three lists key off one derived route
set** (`targets.ts`, the gauntlet, `moderation-routes.ts`), enumerated only by
`grep -rn deriveTargets`.

**064 IS CLOSED — CHAPTER 4.18, "The log that cannot be edited".** Movement VII opens. Its
record is `specs/064-chapter-4-18/`. **SRS 1.25**, **ADR-35**, `docs/12` row 19 CLOSED.
Tagged **`part4-ch18`**.

    check:fences 21 -> 0 · EXIT 0 · 291 files across 61 chapters      from 60
    2,937 prose words · 4 figures · 2 TRAP · 2 WHY · **0 titled fences**
    49 appendix hunks across 21 files — every one applied FIRST TIME
    FR-MOD-03: ten obligations, nine met or demonstrated

**THE CLAUSE NAMES A POPULATION AND SUPPLIES NO MEMBERSHIP RULE, SO THE CHAPTER'S PRODUCT IS A
DECISION.** 48 routes derived from a booted application, 33 mutating, **24 owing a decision
each — not an entry each**. The set is **eight** where a reader predicts nine, and the rule the
spec proposed misclassified two routes in the same direction, which is what named the line it
actually draws: **standing, not data.** 4.20 used that line to classify its own route
`not-moderation` and recorded the cost it avoided rather than the cost as the reason.

**`REVOKE UPDATE, DELETE` DOES NOTHING** — the api connects as a superuser, so the obvious
mechanism is inert and a `BEFORE UPDATE OR DELETE` trigger is the one that fires. **Both
bypasses are measured and published.** **A mechanism that fits the tool is not a mechanism that
works, and the second has to be attempted.** **AND THE TRIGGER WAS FORBIDDEN BY A TEST WHOSE
RULE WAS WIDER THAN ITS REASON** — scoped in its own comment to the sentinel guard, which
refuses the api's own legitimate sweeps, where this refuses writes the api must never make:
**opposites wearing the same syntax.** Narrowed by name, and the narrowing asserted.

**TWO OF THREE TENANCY SCOPES WERE INVISIBLE AND THE THIRD GUARDS THE WRONG CASE.** Deleting the
controller's 403 for a principal with no environment turned nothing red, because
`@Accepts("application")` refuses such a principal first — while **deleting that decorator
answers an end-user token 200 with the tenant's whole moderation history.** The branch defends a
case that cannot arise; **the decorator is the decision and nothing had tested it.** 4.20 ran the
same probe on a WRITE route and found it covered, which is the contrast worth keeping.

**AND THE KEYSET CURSOR WRITTEN AS AN `OR` IS NOT A KEYSET CURSOR** — it lands in a `Filter:` and
re-walks every earlier page; a SQL row value reaches the `Index Cond`. **4.20 checked whether
that transfers to containment predicates and it does not**: a hundred `@>` tests OR together into
a `BitmapOr` over the GIN index. **And `timestamptz(3)` is not cosmetic** — Postgres stores
microseconds, `toISOString` emits milliseconds, so a cursor minted from the wire value sits
before every row inside the lost fraction.

**AND `git commit -F -` IN A BACKGROUNDED COMMAND COMMITS NOTHING** — no stdin, an empty message,
git aborts, and the background task reports only the other command's exit code. **Then `git add
-A` in the superproject staged a gitlink that had not moved**, because the submodule still held
the whole chapter uncommitted: a green, complete-looking commit carrying none of it. **060's push
order is a commit rule too.**

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
true **after** the deletion and false at the write site. **Is this reason true at the moment the
code runs, or only afterwards?** 4.20 paid the other half: a comment that is STILL accurate must
be left alone.

**A MICROSECOND COLUMN THAT HAS ONLY EVER HELD MILLISECONDS.** Every value written to
`message_edits.edited_at` arrived as a JavaScript `Date`, so the key's collision window was **a
thousand times wider** than `schema.ts` claimed and a concurrent edit and deletion collided **1 run
in 10**. The fix is `sql`now()``. **The edit path still writes a `Date` (065-2)**, re-measured at
4.21: `ended_by='edit'` **5,929 of 5,929** millisecond-exact, `ended_by='deletion'` **51 of 1,472**
— 3.5%, which is chance, so the fix holds where it was applied and nowhere else.

**AND A REQUIRED FIELD REACHED A STRICT SCHEMA ONE SEAM AWAY** — 4.11's rule a third time: *an
argument right about the producer can invert about the reader.* **Find the readers by the TYPE.**

**THREE SCOPED READS AND REMOVING ANY TWO IS INVISIBLE.** Only all three together move 1 of 62.
**A single-mutation probe measures the DEFENCE, not the arm** (`gaps.md` 065-4) — 4.20 and 4.21 hit
it again, the second time on an arm whose failure is a LOSS rather than a leak.

**A LINT RULE IS A CONSTITUTION CLAUSE, FOR THE THIRD TIME.** A `drizzle-orm` import in a test
outside `services/api/src/db/**` was refused. **Not needing an exemption is better than earning
one** — test fixtures go in `repository.ts` as `…Raw` methods (`listMessagesRaw`'s precedent),
which 4.20 and 4.21 both followed.

**AND THE QUICKSTART WAS WRONG ZERO TIMES AT PHASE 9** — wrong twice during the analysis
passes instead. **The failures moved to where they are cheap.**
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

**AND A PER-FILE BRANCH PIN IS A CLAIM ABOUT THE MACHINE.** `media.controller.ts` measures **33
branch points locally and 13 in CI**, same commit, same Node. **The DENOMINATOR moves**, so the
two figures are not two samples of one quantity. 059-20.

**AND THE LAST COVERAGE PIN WAS RIGHT WHILE ITS ENVIRONMENT WAS WRONG.** `ci.yml` set
`RELAY_CLICKHOUSE_HOST: localhost`, *the value the file already defaults to*, so `?? "localhost"`
never evaluated its right side and that arm was dead in CI alone. **The repair is a deletion,
not a lower pin. Both cases present as a red pin; ask what the number is measuring before you
move it.** 059-22.

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE EVENT THE SAD SAYS THE WORKER CONSUMES HAS NO PRODUCER, AND ADR-13 IS WHY
- JAVASCRIPT'S `<<` IS SIGNED, AND IT SURFACED AS AN API 400 THREE LAYERS AWAY
- A LIVENESS PROBE PASSES AGAINST A SIGNATURE DATABASE THIRTEEN DAYS OLD
- THE SIGNATURE MATCHES THE FILE, NOT A SUBSTRING
- AND THE STORE'S TWO HEADERS ARE NOT EQUALLY TRUSTWORTHY
- FR-MED-03's "CONTRADICT THEIR DECLARATION" IS EXACT, AND THE QUOTA SETTLED IT
- CONSTITUTION VII WAS ENGAGED TWICE AND ONLY ONE HAD BEEN WRITTEN DOWN
- THE COMPOSED WORKER COULD NOT REACH THE SCANNER AND NOTHING FAILED
- AND A CHAPTER THAT PUBLISHES WHAT THE APPENDIX WAS CARRYING MAKES ITS HUNK OBSOLETE
- AND THE PUSH FOUND SOMETHING THAT IS NOT THIS CHAPTER'S
- THE TWO QUERY-PLAN ASSERTIONS REQUIRED THE PLANNER TO MAKE A BAD CHOICE
- AND `pnpm test:integration` REPORTED 0 OF 63 SUITES WHILE EVERY ONE PASSED
- AND 059-12's OWN FIXTURE WAS A SLOW LEAK
- EIGHT ANALYSIS PASSES: 6 findings, 5, 4, 4, 4, 3, 3, 2

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

    remove the scope from the REFERENCE LOOKUP   delivery 16/16 GREEN · gauntlet 60/60 GREEN
    remove the scope from the OBJECT READ        delivery 16/16 GREEN · gauntlet 60/60 GREEN
    remove the scope from `channelVisibleTo`     delivery 16/16 GREEN · gauntlet 5 red, and
                                                 NONE of them the media read attack
    remove ALL THREE                             delivery 2 of 16 RED

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE INDEX'S HEADLINE WAS A MEASUREMENT OF A QUERY THIS CHAPTER DOES NOT SEND
- AND THE PASSES' OWN REPAIR MADE THE INDEX DEAD
- AND "THE REFUSAL IS THE EXPENSIVE CASE" INVERTED WITH IT
- 4.1's CONCLUSION STILL HOLDS AND SO DOES THIS ONE
- THREE TENANCY PREDICATES, AND NO SINGLE-MUTATION PROBE SEES ANY
- SRS 1.19: THE CLAUSE'S OWN WORDS WERE STRICTER THAN THE MESSAGE THEY GUARD
- A MALFORMED PATH PARAMETER IS A CALLER-TRIGGERED 500 ON SIXTEEN SHIPPED ROUTES
- AND THE SEALED SUITE ASSERTED A FACT THE PLATFORM PUBLISHES AS FALSE
- AND THE QUICKSTART WAS WRONG THREE TIMES, THE FIRST OF THEM THIS CHAPTER'S OWN SUBJECT
- A HUNK'S ANCHOR CAN BE THE APPENDIX'S OWN LINE, FOR THE THIRD TIME
- THE BROKER'S HEALTH CHECK NAMES ONE UNRECOVERABLE STREAM AT A TIME
- THREE ANALYSIS PASSES: 3 findings, 1, 1

**057 IS CLOSED at 108 of 108 — CHAPTER 4.11, "the half of the union that was refused".**
Its record is `specs/057-chapter-4-11/` — `baseline.txt` first, then `gaps.md` (**11 entries: 6
new, 5 carried and re-measured**), `traceability.md`, `tasks.md`. **SRS 1.18**, and **both**
copies of the Part 4 table amended. Tagged **`part4-ch11`**.

    check:fences 22 -> 0 · EXIT 0 · 290 files across 54 chapters
    1,576 diff lines over 22 files — 8 in the chapter, 14 in the appendix
    2,396 prose words · 3 figures · 34 error codes, 34 sections
    12 of 12 lanes · 19 of 19 sealed · 126 files, 1,814 tests under coverage

    e8b5c3c  baseline        3 distinct
    e539403  the chapter     3 · empty diff both ways
    8bc0a8f  the CI fix      6 · three extra, absent before AND after
    81761a0  the record      3 · empty diff both ways

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE PREDICATE IS FOUR LINES OF SQL AND EVERYTHING ELSE WAS THE CHAPTER
- FIVE READERS HAD TO LEARN THE ARM BEFORE THE PRODUCER SHIPPED, AND THE TABLE BUILT TO FIND THEM SAID ONE WAS INERT
- AND THE TASKS' OWN PROBE PREMISE HAD MOVED UNDER THEM
- CONSTITUTION VI's BRANCH CLAUSE, ANSWERED BY DELETING EACH ARM
- SRS 1.18: THE CLAUSE WAS SILENT, NOT STRICT
- AND THE COMPOSED API HAD ANSWERED 503 TO EVERY SLOT REQUEST SINCE 4.10
- THREE KINDS OF STALE BUILD, AT THREE LAYERS
- AND THE QUICKSTART WAS RUN, WHICH IS NFR-USE-03's WHOLE VERIFICATION
- A GOOD HUNK FAILED FOR 4.8's REASON
- AND THE SEALED SUITE HAD NEVER RUN IN CI, WHICH THE PER-ERROR COMPARISON FOUND
- THE CI ERROR SET IS IDENTICAL TO THE BASELINE ON TWO RUNS OF THREE, AND ONE COMPARISON WOULD HAVE MISSED THAT
- TEN ANALYSIS PASSES: 12 findings, 7, 3, 3, 3, 1, 3, 4, 2, 1

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

    plain SELECT        B blocked: no    B saw sum=0     B inserted   committed 1,200
    SELECT FOR UPDATE   B blocked: yes   B saw sum=600   B refused    committed   600
                                                                      against a cap of 1,000

    anchors at -U6                          8   chapter fences
    anchors only at -U2 / -U3               2   chapter fences, context trimmed
    anchors at no width                     7   appendix
    anchors, and unanchors the appendix     2   appendix, placed last

## AND 056-9 AND 056-10 ARE CLOSED, WHICH TOOK FOUR CHANGES AND ONE REFUSAL

**AND 056-10's CHECKER IS LEFT UNBUILT ON PURPOSE.** The targeted version's surface is 13 lines
in 10 files; the naive one reports **37** exports whose only callers are tests, nearly all
legitimate, and needs a hand-maintained allow-list. One instance is not a class.

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

**What else it found** — the argument for each is in that feature's `gaps.md`:

- A PRESIGNED URL NEEDS NO DEPENDENCY, AND NO CONTACT WITH THE STORE
- `docs/12` SAID FOUR REFUSALS WHERE FR-MED-02 NAMES THREE, AND THE ROW WAS RIGHT
- STORAGE IS A LEVEL AND THE MISSING WORD WAS `monthly`
- TEN CONCURRENT SLOT REQUESTS COULD NOT LOSE THE RACE
- AND `FOR UPDATE` FROM OUTSIDE PROVES NOTHING ABOUT THE METHOD
- TWO COMPOSE SERVICES CLAIMED HOST PORT 9000
- THE TASK TABLE SAID TWELVE AND NAMED ONE THIS CHAPTER NEVER TOUCHES
- THE UNIT LANE WAS NOT DOCKER-FREE AND NOW IS
- AND THE PLATFORM JOB IS TWO JOBS
- AND `pnpm test:integration` HAD NOT RUN IN CI SINCE 2026-09-13 — NINE FEATURES
- The two `relay-platform` jobs failed at the same steps as the run before, **and that is not the same as failing for…
- AND THE PLATFORM JOB RUNS FIVE STEPS OF ELEVEN WHEN ONE UNIT TEST FAILS

**055 IS CLOSED at 105 of 105 — THE FENCE CHAIN IS ZERO.** Its record is
`specs/055-fence-chain-repair/` — `baseline.txt` first (it carries every phase's measurements and
the method), then `gaps.md` (**12 entries: 7 new, 4 closed, 1 corrected**), `traceability.md`,
`tasks.md`. **ADR-29**. No tag: the feature cuts no chapter.

    check-fence-chain: 282 fenced files replay onto relay-platform across 52 chapters
    110 -> 0 · EXIT 0 · the first green tutorial job since feature 045
    42 hunks re-anchored · 8 files published whole · 29 appendix hunks · 30 fences declared
    2,379 published diff lines became 1,882 — the series shows readers LESS, not more

**FIVE OF THE SEVEN GATE SCRIPTS EXIT 0 WHEN THEIR CORPUS IS ABSENT.** Every one prints a counted
success line when it really looked, so **assert the line, not the exit code**. And **a copy of the
checker at any other path replays nothing and exits 0**, because the platform is resolved from the
script's own location — which is the copy fence-chain rule 1a tells you to make. 055-4 and 055-5.

**WHAT ZERO DOES NOT MEAN.** Not that the chapters are readable, not that the listings are
pedagogically right, and not that **614 fences outside every gate** — 360 untitled and 254 skipped
by name — mean anything. Not that the Vietnamese chain is compared to the repository (050-3). And
the success line's chapter count is **pages the walker found**. One property — every titled fence
replays onto `relay-platform`, byte for byte.

**What else it found** — the argument for each is in that feature's `gaps.md`:

- A COUNT OF 110 WAS NEITHER 110 DEFECTS NOR AN UPPER BOUND ON THEM
- AND THE LAST ONE WOULD NOT CLOSE, WHICH IS HOW THE REAL DEFECT SURFACED
- THE METHOD IS NOT "REGENERATE AGAINST THE TAG"
- AND THE INTRODUCTIONS HAVE A FOURTH DESIGN THE PLAN DID NOT LIST
- THE 110th PROBLEM HAS A NAME AND IT IS NOT PART 3's
- `check:errors` IS A SCRIPT NO WORKFLOW RUNS — AND THE CHECK ITSELF DOES RUN
- `check:fences` GAINED `--dump <dir> [--at <page>]`
- AND THE LOOP COMMAND NEVER PRINTED THE COUNT

**054 IS CLOSED at 114 of 114 — CHAPTER 4.9, "Milestone: the meter agrees".** Its record is
`specs/054-chapter-4-9/` — `baseline.txt` first, then `gaps.md` (**8 new, 14 carried and
re-measured, 2 closed, 1 corrected twice**), `constitution-amendment.md`, `traceability.md`,
`tasks.md`. Tagged **`part4-ch9`**. Movement IV is closed.

    121,057 vs 121,057 · 0.0000%   the first volume where 0.1% is a real threshold
    smallest expressible drift 122 · 121 passes and 122 breaches, both directions
    54 of 54 suites · EXIT 0       the first green test:integration since chapter 4.4
    one assertion of 676 moves when `<=` becomes `<`
    check:fences 110 -> 110, delta 0 · 2,826 prose words · 3 figures · SRS 1.16

    volume      999    1,000    1,017   121,057   1,000,000
    under         1        2        2       122       1,001
    over          2        2        2       122       1,002

**THE INGESTER DID NOT NEED A COMPOSE SERVICE AND BOTH OBVIOUS FIXES WERE WRONG.**
`services/ingester` has **no Dockerfile**, and the other services carry `profiles: ["services"]`.
And `--filter` selects **packages**: the five red suites sit inside `@relay/api`. **The suite
spawns the process it needs** (050-8 CLOSED, five features on). **And that changed what the sealed
suite sees**: `integrate.itest.ts` asserted a customer's request log comes back **empty** — an
assertion that a defect is still present, which **fails the moment somebody fixes the defect**.

**FR-ANL-06 IS THREE OBLIGATIONS AND THE PLATFORM HAS ONE.** The comparison exists and is
exercised on every push. **The daily job has no runner of any kind** — zero hits in either
`package.json`, `turbo.json`, `ci.yml` or any `*.sh`, and no `schedule:` trigger — which no
document had recorded. The alert has no mechanism (SRS 1.14). **ADR-28** records the absence
rather than building a sixth relay: a daily sweep today would report `no-data` for every tenant,
because **no environment has both sides**. **ADR-27** is the gate. The constitution III amendment
is **written in full and not applied** (`specs/054-chapter-4-9/constitution-amendment.md`) — three
items now stand against one principle (051-2, 052-6, 054-3).

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

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE PREMISE FIVE ARTIFACTS CARRIED WAS FALSE, AND THE TRUTH IS WORSE
- ONE UNSET VARIABLE WAS COSTING MORE THAN THE TEST THAT REPORTED IT
- A GATEWAY TEST HAD NEVER DELIVERED THE FRAME IT PUBLISHED
- THE TWO DIRECTIONS OF THE SMALLEST EXPRESSIBLE DRIFT ARE NOT THE SAME NUMBER
- `max(analytical, operational)` is the denominator, so a surplus of `d` divides by `volume + d` and a shortfall by…
- AND THE WORKFLOW IS STILL RED AT THE TOP

**053 IS CLOSED at 139 of 139 — CHAPTER 4.8, "the log a customer can search".** Its record is
`specs/053-chapter-4-8/` — `baseline.txt` first, then `gaps.md` (**21 entries: 9 new, 12 carried
and re-measured, and 048-2's own wording corrected**), `traceability.md`, `tasks.md`. Tagged
**`part4-ch8`**.

    a scoped query returning 0 rows returns 11,683 under ' OR 1=1 --   across all 152 tenants
    quantile(0.99) 4,961 where quantileExact reads 10,000             50.39% low, n=64
    a 50-row page reads 11,695 — the whole table                      the part is Compact
    check:fences 110 -> 110, delta 0 · 3,606 prose words · 11 gates · 66 tests · SRS 1.15

    scoped, honest window (1 hour)                       0 rows
    the same query, from carrying ' OR 1=1 --       11,683 rows   the whole table
    distinct environment_id under the payload          152        the query names ONE
    ' UNION ALL SELECT name FROM system.users --   relay, then the request ids

**A FEATURE-LOCAL ID REACHED TWO PUBLISHED DOCUMENTS, THREE COMMITS AFTER READING 1.14's
CORRECTION OF THE SAME DEFECT.** The mechanism was copying the task line — a task is feature-local
and uses them correctly. Caught by diffing `docs/` for `FR-0\d\d`, and **nothing runs that check**
(`gaps.md` 052-7).

**READING THE LOG SPENDS THE TENANT'S REST BUDGET, AND NOBODY CHOSE THAT.** `operationsFor`
returns `["rest"]` for every `/v1` path. Left counted — an exemption list is a hand-maintained
table — and the loop is published rather than routed around: **a customer investigating 429s reads
their log, the reads spend the budget they are investigating, and the log then shows the 429s the
reading caused.** **And the log is 1.60 s behind at p50** — 2.7% of FR-ANL-04's 60. **On the stack
this series ships, a customer reading their own request log finds it empty**, because the records
are published and nothing drains them (`gaps.md` 050-8).

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE BRIEF PAIRED A CLAUSE THAT COULD BE BUILT WITH ONE THAT COULD NOT, AND BOTH HALVES WERE THE CHAPTER
- "THE PAYLOAD REACHES THE PARSER" IS THE WEAK VERSION OF THIS CLAIM
- It does not widen the window — it defeats the tenant predicate
- THE REMEDY IS A TYPE, NOT AN ESCAPE
- `index_granularity = 8192` IS DECLARED AND IS NOT IN FORCE
- `quantile` HAS NO EXACT REGIME, WHICH IS THE OPPOSITE SHAPE FROM `uniq`
- THINGS THAT HAD NEVER PASSED, NEVER LOOKED, OR NEVER BEEN TRUE
- THE APPENDIX APPLIES AFTER EVERY CHAPTER, AND THAT IS WHY A GOOD HUNK FAILED
- AND "DERIVE, DON'T LIST" HAS A PRECONDITION
- FR-ANL-08's NINETY DAYS CANNOT EXIST OVER THIS TABLE AT ANY VOLUME

**052 IS CLOSED at 87 of 87 — CHAPTER 4.7, "the job that checks the meter".** Its record is
`specs/052-chapter-4-7/` — `baseline.txt` first, then `gaps.md` (**23 entries: 7 new, 15 carried
and re-measured, and 047-1/048-1 closed by amendment**), `traceability.md`, `tasks.md`. Tagged
**`part4-ch7`**.

    the aggregate 0.2630% · 49 of 1,385 tenant-periods over the bound · 0 non-fixture
    uniq exact to 65,536 · 0.5676% at 65,537                    the cliff is one user wide
    the TTL gap is 0% at midnight and 1.0989% before the next   047's 0.49% is one point on it
    check:fences 110 -> 110, delta 0 · 2,265 prose words · 11 gates · 33 tests · SRS 1.14

    99,900   -100   0.100000%   pass      "0.1% under" — the naive shortfall
    99,899   -101   0.101000%   breach
   100,100   +100   0.099900%   pass      "0.1% over"  — the naive excess
   100,101   +101   0.100898%   breach

**AND `pnpm test:integration` RUNS THREE OF ITS SIX LANES.** `--dry=json` plans 18 tasks; the run
attempts **9** and prints `Tasks: 7 successful, 9 total`. `--concurrency=1` means turbo stops
scheduling at the first failure, so **every lane ordered after the api has not executed under that
command since 4.4** — the gateway's 225 tests among them. 051-3 read this as a summary that
collapses lanes; it is worse.

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

**What else it found** — the argument for each is in that feature's `gaps.md`:

- FR-ANL-06 CANNOT PASS, AND THREE OF THE FOUR REASONS ARE NOBODY'S FAULT
- "COUNTS DERIVED FROM OPERATIONAL DATA" IS NOT ONE NUMBER
- BOTH OBVIOUS WAYS TO PLANT A 0.1% DRIFT PASS
- `max(a, o)` is the denominator and the comparison is `<=`, so **the smallest breaching drift is 101 in both…
- `pnpm coverage` WAS ANSWERING WITH SILENCE, AND HAD SINCE 4.4
- `FR-003a` IS NOT A CLAUSE, AND TWO PUBLISHED DOCUMENTS CITED IT AS ONE

**051 IS CLOSED at 94 of 94 — CHAPTER 4.6, "the rollup nobody read".** Its record is
`specs/051-chapter-4-6/` — `baseline.txt` first, then `gaps.md` (**15 entries: 6 new, 8 carried
re-measured, and 047-3/048-4 closed**), `traceability.md`, `tasks.md`. Tagged **`part4-ch6`**.

    the rollup read 32,778 rows · the raw table 32,768   for the same tenant-month
    147,534 rows keyed (env, channel, day) · 281 keyed (env, day)      525x
    56 calendar minutes against 0.6513 elapsed                          86x
    check:fences 110 -> 110, delta 0 · 2,302 prose words · 11 gates, 9 green

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

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE BRIEF ASKED FOR A ROLLUP THAT HAD EXISTED SINCE 4.2, AND NOTHING READ IT
- THE COUNTS HOLD STILL WHILE THE STREAM CLIMBS
- THE ROLLUP READ MORE ROWS THAN THE RAW TABLE
- A MATERIALISED VIEW IS A TRIGGER ON FUTURE INSERTS, NOT A QUERY OVER HISTORY
- SRS APPENDIX C QUESTION 4 IS CLOSED

**050 IS CLOSED at 114 of 114 — CHAPTER 4.5, "the gateway's first stream".** Its record is
`specs/050-chapter-4-5/` — `baseline.txt` first, then `gaps.md` (**19 entries: 8 new and all 11
carried items re-measured**), `traceability.md`, `tasks.md`. Tagged **`part4-ch5`**.

    close -> row readable   min 2.0 s · p50 5.7 · max 5.8   9.7% of FR-ANL-04's 60 s
    60/60 acked broker down · 139 retained · 0 dropped
    403.5 B a record on the real stream — 26% heavier than the synthetic 320
    check:fences 110 -> 110, delta 0 · 2,330 prose words · 11 gates, 9 green

    clean stop (SIGTERM)   opened 10 | closed 0      of 20 expected
    kill      (SIGKILL)    opened  0 | closed 0      of 20 expected

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

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE GATEWAY ALREADY REPORTED CONNECTION DATA, WHICH `docs/12` DID NOT SAY
- "BATCHED" MEANT THE WAITING, NOT THE PAYLOAD, AND FOUR PASSES DID NOT ASK WHICH
- AND THE UNAUTHENTICATED CONNECTION CANNOT ARISE
- AND `MAX_CONNECTIONS_PER_USER = 5` IS A CEILING ON "N CONNECTIONS"
- A CLEAN STOP PUBLISHES A LEDGER SAYING TEN CONNECTIONS ARE STILL OPEN
- `sessions.close()` calls `wss.close()`, which **does not close established sockets**, so no per-socket close handler…
- ELEVEN OF THE 36 INHERITED HEAD PROBLEMS ARE NOT DRIFT
- AND TURBO'S CACHE HID A TWO-CHAPTER-OLD RED
- READ THE CLAUSES, NOT THE IDENTIFIERS — THREE CITATIONS POINTED AT CLAUSES THAT DO NOT SAY IT
- AND AN ADR LIVES IN TWO DOCUMENTS — THE SAD'S SUMMARY AND `docs/06`'s ARGUMENT
- 403.5 BYTES A RECORD, 26% HEAVIER THAN THE SYNTHETIC FIGURE TWO CHAPTERS HAVE IN PRINT
- TWO CONNECTION-MINUTE COUNTERS THAT MEASURE DIFFERENT QUANTITIES
- THE HABITS THIS FEATURE PAID FOR AGAIN

**049 IS CLOSED at 112 of 112 — CHAPTER 4.4, "the requests that belong to nobody".** Its record is
`specs/049-chapter-4-4/` — `baseline.txt` first (842 lines), then `gaps.md` (six entries),
`traceability.md`, `tasks.md`. Tagged **`part4-ch4`**.

    54 requests · 34 with no tenant    application 20/20 attributed, platform 18/18 tenantless
    broker up 2.61 ms · down 2.45      200 each side, all 200s — down is FASTER
    320 bytes a record                 (4.5 re-measured the real stream at 403.5)
    check:fences 110 -> 110, delta 0   2,393 prose words · 8 gates · 6 fences, all diffs

    pass 1: written 1  malformed 1      the attempt wrote — that is the positive control
    pass 2: written 0  malformed 0      terminated, never comes back
    stream still holds 2 of 2 · consumer num_pending 0 · ack_pending 0

**048-6's RECORDED CAUSE IS WRONG, AND THIS CHAPTER MADE THE FAILURE PERMANENT.** It blamed an
ABRUPT `compose down`. A graceful `compose stop` does it too, and so does `restart` — **the stream
that fails to recover is whichever is being WRITTEN**, proven with a control. The api now writes on
every request and Docker polls `/healthz` every five seconds, so **the stream is never idle and
every restart lands mid-write** (049-1). **And the compose api cannot create a stream it does not
have**: `replicas > 1 not supported in non-clustered mode`, because `replicaCount()` returns 3
under `NODE_ENV=production` and the Dockerfile sets it. 474 publish failures accumulated while the
streams were missing; it hid because the streams were first created from OUTSIDE the container,
which is also why 048-6's own repair appeared to work (049-2).

**What else it found** — the argument for each is in that feature's `gaps.md`:

- "EVERY REQUEST" AND "PER TENANT" ARE NOT THE SAME POPULATION
- CONSTITUTION I FORBIDS THE RECORD FR-ANL-01 REQUIRES, AND THE THIRD READING IS THE ONE THAT HOLDS
- THE CONSUMER SHIPPED LAST CHAPTER DESTROYED EVERYTHING THIS ONE SENDS, AND BOTH INSTRUMENTS SAID NOTHING WAS WRONG
- `retention: Limits` keeps a terminated message, so depth says the record is there and lag says there is nothing to…
- NO MIDDLEWARE POSITION GIVES BOTH PROPERTIES, AND FINDING THAT OUT TOOK THREE ANALYSIS PASSES
- AND TWO OF `refused_at`'s FOUR ARMS ARE NOT OBSERVABLE
- THE COLUMN TYPE WAS WRONG AND ONLY TRAFFIC SAID SO
- THE BYTE COUNT INCLUDED THE INSTRUMENT
- `check-lane-scope.py` REPORTS ZERO BECAUSE IT LOOKS AT NOTHING
- CONSTITUTION VI's 100%-BRANCH CLAUSE IS MET RATHER THAN PINNED, FOR THE FIRST TIME IN PART 4
- THE FENCE CHAIN CHARGED FOR SIX FILES THIS CHAPTER TOUCHED

**047 IS CLOSED at 74 of 74 — CHAPTER 4.2, "the store that was never listening".** Its
record is `specs/047-chapter-4-2/` — `baseline.txt` first, then `gaps.md` (five entries),
`traceability.md`, `tasks.md`. Tagged **`part4-ch2`**. Nine analysis passes; the pass-by-pass
narration is in that `baseline.txt`.

    13.22 ms against 4.1's 585.9 ms   both best of 3, both 91 days, same question
    315 rows read against 1,052,655   the rollup, for 19% less time
    90 of 91 days agree exactly       the 91st cannot, by 4,941 — 0.49% vs a 0.1% bound
    check:fences 110 -> 110, delta 0  2,580 prose words · 8 gates green · 6 fences

**What else it found** — the argument for each is in that feature's `gaps.md`:

- THE STORE HAD BEEN UNREACHABLE FOR SIXTEEN CHAPTERS BEHIND A GREEN TICK
- THE ROLLUP AND THE RAW TABLE DISAGREE ON ONE DAY AND ALWAYS WILL
- AND THE TTL REMOVES ROWS AT INSERT, NOT AT MERGE
- PASS 9 ASKED WHICH DATABASE, AFTER EIGHT PASSES OF ASKING THE DATABASE
- AND THE LOAD'S COLUMN EXPRESSIONS WERE WRONG IN THREE WAYS ONE `SELECT` FOUND
- THE THREE PART 1 TAGS WERE NOT ORPHANED, THEY WERE WRONG
- AND THE FENCE DELTA HAS A NEIGHBOUR
- AND THE DIRECTION THAT ERRORS IS THE SAFE ONE

**046 IS CLOSED at 76 of 76**; its record is `specs/046-chapter-4-1/` — `baseline.txt` first,
then `gaps.md` (eight entries, two closed), `traceability.md`, `tasks.md`.

    M1 585.9 ms over 1,000,000 rows   ·   lane's busiest env 0.9 ms over 1,018   ·   651x
    column 24.8 MB + index 62.0 MB = 86.8 MB permanent on a 178.6 MB table
    check:fences 110 -> 110, delta 0   ·   2,132 prose words   ·   8 gates green   ·   part4-ch1

    045 "part 3 rework"           24 chapters -> 26, eight movements, English prose only
                                  296 -> 110 fence-chain problems · 26 of 26 tags typecheck
    SC-007  403.76 s -> 232.05 s, 20 of 20 green, stdev 0.51, cv 0.22%
    044 "the revision watermark"  one column, raised inside the transaction that edits or
                                  deletes, never by a send · reported on every `connection.ack`
                                  **the platform reports and never compares**

**What else it found** — the argument for each is in that feature's `gaps.md`:

- PART 4 IS 22 CHAPTERS, AND IT CONTRACTED TWICE
- WHAT 4.1 MEASURED, AND IT FALSIFIED ITS OWN PLAN TWICE
- NINE ANALYSIS PASSES FOUND 27 THINGS AND, FROM PASS 4 ON, ONLY THEIR OWN PREDECESSORS' REPAIRS
- AND EVERY MEASUREMENT WAS WRONG BEFORE IT WAS RIGHT
- THE TAG NAMESPACE IS CONSISTENT AGAIN
- WHAT IT COST TO MAKE THE LANE FAST, AND WHERE THE TIME ACTUALLY WAS
- EIGHT PLACES HELD THE LANES APART, THE ESTIMATE SAID THREE, AND THREE OF THE EIGHT ARE NOT ASSERTIONS AT ALL
- AND THE WORKER COUNT IS A BILL, NOT A SETTING
- 044'S REVERSAL IS THE LESSON THAT OUTLIVED IT

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
