# Research — chapter 4.23, "★ Milestone: the Priya test"

Every figure below was measured against the development lane and the composed api
on 2026-10-05, before the plan was written.

---

## R1 — Where the journey test lives, and the precedent points the other way from the brief

`packages/e2e/src/tuan.itest.ts` is Journey 4 made executable at chapter 2.8, and
`spec.md`'s Assumptions put Priya's test beside it. **Measuring both homes moved the
answer.**

```
                        lines   fence pages   appendix   boots services?
packages/e2e            231     4             0          yes, in process
  tuan.itest.ts                                          (harness.ts: 19 pages, 3)
packages/outsider     1,677     5             5          no — env vars only
  integrate.itest.ts                                     RELAY_API_URL, WS, CREDENTIAL
```

**`docs/03` DECIDES IT IN ITS FIRST SENTENCE.** *"Priya never touches Relay
directly. She uses an internal support tool that Mai built on Relay's moderation
APIs in an afternoon."* The sealed suite is the one that talks to **deployed
containers** with nothing but a published URL and a credential — which is what Mai's
tool is. The e2e harness boots the services in process and reaches into the api's own
database (`setQuota` exists there precisely because the package may not import `pg`).

**AND THE SEALED SUITE ALREADY WALKS HALF THE JOURNEY**, which was not expected:

```
creates a channel, and creating it twice is not an error      <- Stage 2's workaround
adds two members, creating the users on first membership      <- Stage 1
mints a token for one of those members                        <- the send problem, solved
sends a message over REST and reads it back from history      <- Stage 3
edits a message over REST, and a socket hears message.updated <- Stage 3
carries one image from slot to delivered bytes (4.17)         <- the Phase 3 arrow, four of five
delivers a refused upload as a rejected marker (4.17)         <- docs/07's extra clause
cannot see another tenant's channel                           <- the tenancy floor
```

What it does **not** have: a deletion read back as a tombstone, a ban, the audit log,
the erasure, and any framing that says these are one person's Tuesday.

**DECISION: a new file, `packages/outsider/src/priya.itest.ts`.** New files carry
**0 fence pages**, so the chapter's test costs the chain nothing, and
`integrate.itest.ts` — 1,677 lines across 5 pages with 5 appendix hunks — is not
disturbed. The cost is duplicating `required()`, six lines that read three
environment variables. **Extracting it to a shared module was considered and
refused**: it would edit a published 1,677-line file to save six lines, and 4.17
measured what touching a published file costs when a formatter turned six edits into
23 hunks.

**Alternatives considered.** *`packages/e2e`* — the stated precedent, and it has the
better harness; rejected because the harness's privilege is the opposite of the
journey's premise, and `harness.ts` is 19 fence pages. *Adding to
`integrate.itest.ts`* — cheapest in setup and it already holds the image; rejected on
the file's size and because a journey that is a section of another file is not a
journey anybody can find.

## R2 — Stage 2 is the hole, and the lookup it needs is required by nothing

```
GET /v1/channels/{externalId}      500          <- the natural attempt
GET /v1/channels/{uuid}            200
POST /v1/channels, same ext id     200, same channel id
GET /v1/users/{externalId}         200          <- users ARE addressed this way
```

**THE PLATFORM ADDRESSES ONE NOUN BY THE CUSTOMER'S IDENTIFIER AND THE OTHER BY ITS
OWN**, and has since Part 2. `v1/users/:externalId` takes what the customer chose;
`v1/channels/:channelId` and `v1/channels/:channelId/messages` take a uuid Relay
minted. Journey 3 Stage 2 walks straight into the seam.

**NO CLAUSE REQUIRES THE LOOKUP.** FR-CHN-01 creates a channel with a
customer-supplied identifier; FR-CHN-02 makes *creation* idempotent on it; FR-CHN-08
lists a user's channels. None says a channel can be read by it. So `docs/03`'s *"what
Relay must provide — channel retrieval by external ID"* is a journey asserting a
capability the specification never carried.

**FOUR WAYS OUT, PRICED.**

| | option | platform cost | fence cost | what it costs the reader |
|---|---|---|---|---|
| **A** | a new route, e.g. `GET /v1/channels/by-external-id/{id}` | controller, schema, service, repository — **and the four lists a route joins** (`targets.ts` 13 pages/7, `gauntlet.itest.ts` 13/8, `moderation-routes.ts` 0/1) | ~91 pages | a second way to spell a read |
| **B** | a query parameter on a channel list route | **there is no channel list route**; one would have to be invented first | larger than A | a new surface on a milestone |
| **C** | `GET /v1/channels/:channelId` resolves a uuid **or** an external id | controller/service/repository only — **no new route, so none of the four lists** | ~65 pages | one route, two key spaces |
| **D** | amend FR-CHN to record the idempotent create as the supported resolution | none | 0 | a read performed as a write |

**C IS AMBIGUOUS IN PRINCIPLE AND THE LANE SAYS IT HAS NEVER HAPPENED**: an
`external_id` is `z.string().min(1).max(255)` and may be a uuid, so one input could
name two channels. Measured — **0 of 41,765 channels have a uuid-shaped external id,
and 0 have one equal to their own row id.** A precedence rule (uuid first, then
external id, scoped to the environment) is decidable and testable, and the collision
is a case the chapter can construct rather than wait for.

**THE PLAN DOES NOT PICK ONE HERE.** It is the feature's first task, because a
milestone's rule is rule 4 of `docs/12` §5 — *a milestone appears after all the work
it verifies* — and A, B and C are all new work on a chapter whose job is to verify.
**D is the only option that obeys that rule, and D is the one that leaves Priya
performing a write to perform a read.** That tension is the chapter's, and the
decision belongs in `baseline.txt` with both halves recorded.

## R3 — The 500 is 058-3's, and one of the four options erases it for free

`not-a-uuid` in a uuid-typed path parameter is a caller-triggered `internal_error`
on **22 shipped routes** — 13 `@Param("channelId")`, 6 `@Param("id")`, 3
`@Param("messageId")`, measured at 4.21's close. This chapter does not own that
population and must not try to fix it.

**But it owns the one route Journey 3 opens with**, and FR-004 says a refusal must
name its cause. Options A and B leave the 500 standing on `GET /v1/channels/{uuid}`;
**option C removes it on that route alone**, because an unparseable value stops being
unparseable — it becomes an external id that matches nothing, which is a 404.
Option D leaves it and the chapter publishes it as a limit.

## R4 — Phase 3's fifth arrow, and what it would take

> **SRS §7.3, Phase 3** — *Metered usage reconciles against operational counts
> within 0.1% for 7 consecutive days; an image survives upload → scan → send →
> signed delivery → erasure*

```
upload → scan → send → signed delivery      DEMONSTRATED, chapter 4.17, sealed suite
                              → erasure     NEVER WALKED
```

`docs/12` row 18 names exactly the first four arrows. Chapter 4.21 built erasure,
destroyed a user's attributed media objects and their renditions, and asserted the
row is gone — **in the api's own integration lane, against a slot reserved without
bytes.** The two have never met: no test has uploaded real bytes, delivered them, and
then erased the uploader.

**WHAT THE ARROW NEEDS, AND IT IS SMALL.** The sealed suite's existing image test
already reaches delivered bytes. The missing assertions are: erase the uploader, then
(a) the signed URL no longer serves the object, (b) the renditions are gone, (c) the
receipt names a count, and (d) the message carrying the attachment still reads as a
message. **(d) is the one a reader will not predict** and it is `docs/07`'s own extra
clause for this row, one erasure later: *a rejected upload renders as rejected, not
broken* — and an erased attachment must not render as broken either.

## R5 — Phase 3's first clause cannot be met, and that is the fifth time

*"Metered usage reconciles against operational counts within 0.1% for 7 consecutive
days."* The comparison exists and is exercised on every push (chapter 4.9). **The
seven days need a scheduler and there is none** — ADR-28 records the decision not to
build one, and FR-ANL-06's daily job, DR-17, FR-MOD-03's retention year and
FR-MOD-06's sweep are all bounded by the same absence.

So Phase 3's exit criterion has three clauses with three different verdicts, and the
milestone's product includes saying which: one unmet by a recorded decision, one
demonstrated four arrows of five, and Journey 3 itself — which `docs/07` Rule 2 calls
the exit criterion while §7.3's table does not name it at all.

**THAT DISAGREEMENT IS NOT THIS CHAPTER'S TO INVENT.** §7.6 of `docs/12` already
records that the SRS phase table disagrees with itself and says *amend the clause
rather than diverge from it*. This chapter is the last in Part 4 and the one that
reads §7.3 hardest, which makes it the chapter that owns the amendment.

## R6 — The fence bill, counted now

4.15's rule, and 4.21's correction that the count must be derived from what the tasks
touch rather than remembered.

```
                                 pages   appendix   touched if…
packages/outsider/priya.itest.ts     0   0          NEW FILE — always
docs/04-srs.md                       —   —          always (mirrored, not fenced)
channels.controller.ts               8   0          options A, B, C
channels.schema.ts                   4   0          options A, B, C
channels.service.ts                  5   2          options A, B, C
repository.ts                       52   7          options A, B, C
targets.ts                          13   7          options A and B only
gauntlet.itest.ts                   13   8          options A and B only
moderation-routes.ts                 0   1          options A and B only
integrate.itest.ts                   5   5          only if the arrow is added there
```

**DECIDING R2 DECIDES THE BILL**, and the spread is 0 pages for option D against
roughly 91 for option A. A milestone that spends 91 fence pages on new surface is not
a milestone.

## R11 — The sweep, and the predicate is exact

R2 and R8 found a hole each, one pass apart, and a third turned up at pass 3. **Three
of one shape is a class, and 045's rule is to stop counting failures and ask the tree
once.** Journey 3 has six stages. **Five carry a *"What Relay must provide"* block and
Stage 4 does not** — its one assertion is in its prose — which is the distinction
that made the first version of the count wrong. Swept, all fifteen capabilities:

```
STAGE 1  external IDs on channels and users        FR-USR-01, FR-CHN-01   HOLDS
STAGE 2  CHANNEL RETRIEVAL BY EXTERNAL ID          — no clause —          HOLE
         a user's channel list                     FR-CHN-08              HOLDS
STAGE 3  tombstones                                FR-MSG-08, FR-MSG-10   HOLDS
         immutable edit history                    FR-MSG-07              HOLDS
         server-assigned sequence numbers          FR-MSG-02/03           HOLDS
         complete history via API key              FR-MOD-01              HOLDS
STAGE 4  unambiguous timestamps                    CON-04                 HOLDS
STAGE 5  moderator deletion of any message         FR-MOD-02              HOLDS
         tenant-scoped ban                         FR-USR-06              HOLDS
         the deletion event reaches connected clients  FR-RTM-05          HOLDS
         A BANNED USER'S CONNECTIONS DROP          — no clause —          HOLE
STAGE 6  audit log: actor, action, target, ts, request id   FR-MOD-03     HOLDS
         THE REQUEST ID JOINS TO THE REQUEST LOG ROW  — no clause —       HOLE
         erasure with a completion receipt         FR-MOD-04              HOLDS
```

**THE FINDING IS THE PREDICATE, NOT THE RATIO:** *every capability that cites a
requirement holds, and every capability that cites none is a hole.* **Three of three
in both directions, with no exceptions.**

**COUNTED ONE WAY IT IS TWELVE AND THREE OF FIFTEEN, AND THE UNIT IS A JUDGEMENT.**
One row here can be split or merged by a reader with a different eye: *"external IDs
on channels **and users**"* carries two clauses and is counted once; Stage 6's audit
row lists five fields and is counted once. Split those and the table is sixteen or
twenty, and **the ratio moves while the predicate does not.** That is why the
predicate is the claim and 15/12/3 is an illustration of it — a reader who recounts
and gets 16/13/3 has reproduced the finding, not refuted it.

**THE FIRST VERSION OF THIS SENTENCE SAID FOURTEEN AND ELEVEN, AND THE TABLE ABOVE
IT SAID FIFTEEN AND TWELVE.** The sentence was written off a grep for
`"What Relay must provide"`, which finds **five** blocks because Stage 4 has none;
the table was then built by reading all six stages and gained a CON-04 row the
sentence never counted. **The number IS the finding here** — *three of three* is only
interesting because it is exact — and it was published in four files before anyone
counted the rows underneath it. Analysis pass 4, by counting — **and pass 5 found
that fixing the arithmetic had not made it checkable**, because the denominator still
had no definition. A ratio with an undefined unit invites the recount that discredits
it; the predicate above does not.

**SO THE CHAPTER'S THESIS IS A PREDICATE, NOT A LIST OF GAPS**: *a capability
`docs/03` asserts without naming a requirement is a capability nobody built.* It is
mechanical, it is checkable by anyone with the two documents, and it explains why
nobody noticed — **each hole is a sentence in a journey map, and a journey map is
prose.** No checker in these three repositories reads prose; `check-refs` says so in
its own last line.

**AND IT IS 4.17's FINDING ONE LEVEL UP.** That chapter found that seven suites each
stood in for the step beside it and the aggregate was a path nobody had walked. Here
fifteen capabilities each had a chapter, except three that had no clause — so no
chapter owned them, so no suite covered them, so no aggregate existed to notice.
**The milestone is the only instrument that looks at the whole journey**, which is
what makes finding three holes a success rather than an embarrassment.

**WHAT THIS DOES NOT CLAIM.** The predicate is perfect on this journey's fifteen
and nowhere else; Journey 4 has its own blocks and nobody has swept them. A rule
measured once is a hypothesis with one confirmation — worth publishing, worth not
generalising past Part 4 (`gaps.md` at close).

## R10a — Hole 3: a banned user's connections do not drop

> **`docs/03` Stage 5** — *"tenant-scoped ban (FR-USR-06), both effective in real
> time: connected clients see the deletion event immediately (FR-RTM-05), and **a
> banned user's connections drop**. Latency of moderation is a safety property, not
> a convenience."*

```
FR-USR-06          "preventing CONNECTION and message send while preserving history"
auth.ts:93         a ban is an outcome at AUTH — close code 4003 on a NEW connection
api-client.ts:40   `user_banned` refuses a send
frames.ts          no ban frame — nothing tells a live socket anything
```

**THE BAN IS CHECKED WHEN A SOCKET OPENS AND WHEN IT SENDS, AND NEVER IN BETWEEN.**
Measured by reading the gateway: nothing closes an established connection, and the
protocol has no frame that could ask it to. FR-USR-06's word is **connection**,
singular, which the implementation satisfies exactly.

**THE BOUND IS WHAT THE CHAPTER PUBLISHES, NOT THE ALARM.** After a ban: sending
stops immediately, reconnecting is refused with 4003, and **an already-open socket
keeps receiving until it closes on its own.** Whether that matters is the customer's
judgement — `docs/03` calls it a safety property and the platform does not implement
it as one, and those are both facts the chapter can state without choosing.

**T020 IS ALREADY CORRECT AND THAT IS WORTH NOTING RATHER THAN QUIETLY PASSING.** It
asserts connect and send because it was written off FR-USR-06's wording rather than
off the journey's sentence. **Reading the clause rather than the prose is what kept
the assertion honest**, which is the same habit that produced the hole in the first
place — somebody wrote the prose without reading the clause.

## R9 — The sealed package runs files in parallel, and this chapter is the first to add a second

Measured at analysis pass 2, with two throwaway files that do nothing but sleep:

```
Tests     2 passed (2)
Duration  3.10s   (… tests 6.01s …)
```

**Six seconds of test time in three seconds of wall clock.** `packages/outsider/
vitest.integration.config.mts` sets `include` and `testTimeout` and **no
`fileParallelism`**, so vitest's default applies. That has never mattered, because
`integrate.itest.ts` has been the only file in the package since it was created.
**This chapter adds the second.**

**AND THE TENANT IS SHARED.** `ci.yml:355` seeds once and exports one
`RELAY_DEMO_CREDENTIAL` for the whole `pnpm test:outsider` run, so both files
address a single environment — its channels, its users, its quota, its audit log and
its request log.

**THE COLLISION IS NOT HYPOTHETICAL AND IT IS ON THE SURFACE STAGE 6 READS.**
`integrate.itest.ts:1224` issues a moderator `DELETE` of a message with the
application credential — FR-MOD-02 — which writes an `audit_log` entry into the same
tenant, concurrently with Priya's Stage 6 read. An assertion about what the log
contains, or how many entries it holds, is a neighbour's.

**THE FIX IS THE SCOPE, NOT THE ORDERING.** 045-74's rule: *an assertion scoped
wider than the thing it tests fails for somebody else's reason* — and 043's first
attempt at the same class was worse than the fault, because it serialised instead of
scoping. Every Priya assertion matches on a fixture this test created: the audit
query accepts `action`, and the target id is one the test minted. **Setting
`fileParallelism: false` is refused**: it would make the package slower for every
future file to avoid writing one predicate.

**AND `check-lane-scope.py` CANNOT SEE THIS CLASS.** It globs
`packages/*/src/**/*.itest.ts`, so it *reads* the new file — and it scans for **SQL
table reads**. The sealed package talks HTTP and contains no SQL, so it will report
**0 unscoped reads** over a file that has the hazard in it. The checker's own last
line already says *"SQL text only — a scope applied in JavaScript is invisible to
it"*; this is the same blind spot one transport further out, and T031 records the
zero with that bound attached rather than as evidence.

## R10 — The journey's fixture uses a route that does not exist in production

`POST /auth/dev-token` is how the sealed suite mints user tokens, and the journey
needs them: an application credential may send only as a bot, so Priya's key cannot
create the conversation she investigates.

```
dev-token.controller.ts:78
  if (environment.kind !== "development") {
    throw new NotFoundException("Cannot POST /auth/dev-token");
```

Its own comment: *"a development affordance that does not exist in production"*, 404
rather than 403 on purpose, so nobody goes looking for the permission that would
unlock it.

**SO *"ONLY THE PUBLISHED API"* IS TRUE OF PRIYA'S SIX STAGES AND FALSE OF THE
FIXTURE THAT SETS THEM UP.** The split is the honest statement and it costs a
sentence: the conversation's two participants authenticate through a development
affordance standing in for the customer's own identity provider; **every one of
Priya's own actions — locate, read, delete, ban, audit, erase — uses a route that
exists in production and an application credential a customer really holds.**

Recorded rather than worked around. A real deployment's conversation is created by
real users against FR-AUT's flow, which is Part 2's subject and not something a
sealed suite can exercise.

## R8 — Stage 6 names a join neither log can perform, which is Stage 2's shape again

Found at analysis pass 1, by opening the two query schemas rather than the two
documents that describe them.

> **`docs/03` Stage 6** — *"the request id is what joins an entry to the request
> log's row for the same request, so Priya can go from **a ban happened** to **this
> is the call that made it**."*

```
audit.schema.ts         filters: cursor · limit · action
request-log.schema.ts   filters: from · to · cursor · direction · limit · endpoint · status
```

**BOTH ROWS CARRY `request_id` AND NEITHER SURFACE ACCEPTS IT.** `audit.reader.ts:41`
returns it and chapter 4.18 added the field precisely for this join — `docs/03`'s own
Stage 6 note says the list *"said four of five until chapter 4.18 came to build it,
and the missing one is the field doing the most work."* The field exists. The query
does not.

**SO PRIYA'S TOOL MUST PAGE BOTH LOGS AND MATCH IN MEMORY**, which is the same
answer Stage 2 gives — a capability the journey asserts, no chapter owned, and no
clause carries.

**AND THE TWO HOLES HAVE ONE CAUSE, WHICH IS THE ARGUMENT FOR THE MILESTONE RATHER
THAN A PROBLEM WITH IT.** Chapter 4.8 built the request log and chapter 4.18 built
the audit log; each is correct and each was verified by its own suite. The join
between them belongs to neither, so nobody built it and nothing noticed — **which is
4.17's finding exactly**: *every suite stood in for the step beside it, and the
aggregate is a path nobody had walked.* Two chapters apart this time instead of
seven, and found by the same instrument.

**THREE OPTIONS, AND THE PLAN DOES NOT PICK ONE** (task T011a):

| | option | cost | what it leaves |
|---|---|---|---|
| **a** | publish it as a limit; the tool pages both logs | 0 | the journey's sentence is aspirational and the chapter says so |
| **b** | add a `request_id` filter to one or both readers | two fenced schemas, two readers, and a milestone that builds | the join `docs/03` promises |
| **c** | amend `docs/03` to describe the paging | 0 platform | a journey that matches the platform |

**(b) IS WHAT A READER WANTS AND WHAT RULE 4 FORBIDS.** Same shape as R2's option A,
one document over — and the two decisions should be taken together, because choosing
to build for one hole and not the other needs a reason better than which was found
first.

## R7 — The margin, which is the test's actual contract

`tuan.itest.ts`: *"Read the right margin: each step names the chapter that made it
possible. **Remove that chapter's work and a named assertion here fails.**"*

That sentence is a falsifiable claim and SC-002 asks this chapter to demonstrate it
for at least three chapters by reverting. The chapters Journey 3's stages depend on,
read off `docs/03`'s own "what Relay must provide" lines:

```
Stage 1   external ids on users and channels        FR-USR-01, FR-CHN-01   Part 2
Stage 2   channel retrieval by external id          — no clause —          THIS CHAPTER
Stage 3   tombstones                                FR-MSG-08/10           Part 3
          immutable edit history                    FR-MSG-07              Part 3
          server-assigned sequence                  FR-MSG-02/03           Part 2
          complete history via API key              FR-MOD-01              4.19
Stage 4   unambiguous timestamps                    CON-04                 Part 2
Stage 5   moderator deletion                        FR-MOD-02              Part 3
          tenant-scoped ban                         FR-USR-06              Part 3
          real-time deletion event                  FR-RTM-05              Part 3
Stage 6   audit log with request id                 FR-MOD-03              4.18
          erasure with a completion receipt         FR-MOD-04              4.21
```

**The three cheapest reverts to demonstrate are 4.18, 4.19 and 4.21** — each is one
movement-VII chapter, each has a single named mechanism, and each is recent enough
that reverting it is a `git revert` rather than an archaeology exercise.
