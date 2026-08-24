<!-- SPECKIT START -->
**CHAPTERS 3.12, 3.13 AND 3.14 ARE CLOSED.** One feature, three published chapters,
174 of 174 tasks, checklist 16/16, both locales, **`pnpm check:fences` clean — 203
fenced files across 31 chapters, all 31 translated.** Its record is
`specs/033-chapter-3-12/` — read `chapter-notes.md` first (what the plan said
against what shipped), then `gaps.md` (six documentation gaps and the Phase 2
verdict), `traceability.md` (48 requirements mapped both directions) and
`baseline.txt` for every measurement.

**THE CHAPTER BECAME THREE, on a count taken before any prose existed.** The plan
estimated 37 fenced files; the work came to **61**, and the 2,000–4,000 prose-word
bound cannot hold that — one page would have run to ~7,000 words carrying 66
fences. So:

- **3.12 shipped**: the gauntlet. Target list derived from the running router (24
  routes, 21 attacked, 3 exempt with reasons), four attack shapes over one
  indistinguishability oracle, the structural check over the live catalogue (22
  tables — 12 direct, 2 hop, 8 spine), the socket surface attacked from the
  protocol's own frame union, and three reintroductions. **21 files**, 3,440 prose
  words, 20 chain fences, 3 figures, mirrored in Vietnamese.

The partition is in `baseline.txt`, verified by set arithmetic — 21 + 18 + 22 = 61,
nothing unassigned, nothing in two chapters. Assigning by path guessed wrong five
times: `turbo.json`, `package.json` and three gateway suites belong to 3.14, because
their only change is `notFoundDocsUrl` or the outsider's lane split.
- **3.13 published**: the endpoints and the instruments. 2,452 prose words, 11 chain
  fences, 4 figures. **18 files** —
  `channels/*`, `repository.ts`, `app.module.ts`, `eslint.config.mjs`,
  `vitest.coverage.config.mts`, `test-harness/*`, `public-surface.itest.ts`,
  `e2e/src/harness.ts`, and the two suites whose ports changed.
- **3.14 published**: errors that resolve, and an outsider. 2,228 prose words, 17
  chain fences, 4 figures. **22 files** — `codes.ts`, `protocol-error.*`, `zod-validation.pipe.ts`,
  `service-kit/src/index.ts`, `packages/outsider/*`, `scripts/seed-demo-tenant.mjs`,
  `README.md`. **The milestone name lives here**, because this is where the Phase 2
  exit criterion gets its verdict.
- **3.15 was the deferred surface** — the rest of FR-CHN and all of FR-USR, promised
  a number as 3.13 until the split took it. Now specified and planned, and itself
  split in two; see below.

**CHAPTERS 3.15 AND 3.16 ARE SPECIFIED AND PLANNED** — the deferred public surface.
Its record is `specs/034-chapter-3-15/`: read **`plan.md`** for the seventeen phases
and the constitution gate, `research.md` for R1 to R18 (twelve measured against a
running database), then `data-model.md`, `contracts/membership.md`,
`contracts/listing.md` and `quickstart.md` (18 checks, three of them negative).
58 requirements, 22 success criteria, 249 tasks in 21 phases, checklist 16/16.

**Twelve SRS clauses, five dead columns, and four corrections.** The clauses are
FR-CHN-03/04/05/06/08/09/10 and FR-USR-02/03/04/05/06. The columns exist and nothing
reads them: `channels.type`, `channels.archived_at`, `users.avatar_url`,
`users.metadata`, `users.banned_at` — that count is the feature's own headline number
and V0 records it before Phase 2 moves anything.

**THE SPLIT WAS TAKEN FROM A MEASURED FILE COUNT BEFORE ANY PROSE EXISTED** (FR-040),
which is the one thing 3.12's close-out asked the next feature to do differently — and
**the count was then revised FIVE times, because a count is not an enumeration.** R12
counted **25** from the clause list; the task list named **29**; asking which chapter fences
each file gave **34**, including three the tasks imply and never name — `app.module.ts`,
`users.module.ts`, `users.service.ts`; the send call graph added two more for **36**; and
counting the paths the tasks name, instead of reading the total, gave **38**.

**The first of those three was a CRITICAL.** `app.module.ts` appeared in NO TASK. It is
where `ChannelsModule` is registered and chapter 3.13 needed that edit; without it
`UsersModule` never mounts and eight routes across FR-013, FR-016, FR-017, FR-023,
FR-025, FR-027 and FR-031 do not exist. Found by asking which chapter fences each file —
not by rereading the tasks, which had been read twice.

**A COUNT WITHOUT AN ENUMERATION CANNOT BE CHECKED, and each check found more.** The
enumeration is in R18 with the per-chapter assignment, derived from the phases that touch
each file rather than by path — assigning by path guessed wrong five times in 3.12.
**R18's table is the authority and every other document quotes it**, because three
analysis passes produced three wrong overlap figures while each recomputed by hand.

    3.15 "the channel a customer controls"   21 files  ≈ 3,360 words
    3.16 "what a user sees"                  21 files  ≈ 3,360 words
    21 + 21 = 42 instances, union 38, 35 taught, 7 in both chapters, 3 in neither

Seven files 3.15 fences whole and 3.16 diffs: `repository.ts`, `repository.itest.ts`,
`isolation.itest.ts`, `schema.ts`, `0012_*.sql`, `codes.ts`, `codes.test.ts`. Both pages
sit inside 2,000–4,000 with 640 words of headroom; **three chapters would be ~2,240 each**,
which clears the floor — so the arithmetic stopped arguing either way at 38 files and two
chapters holds on subject coherence and ceiling headroom. Analysis pass one
reported that argument gone at ~2,290 a page — **wrong instrument**: it scaled a group
sum by the union's ratio, and instances grow with how many chapters teach a file. The
page phases sit at 9 and 16 rather than last, so each page is written when its own
numbers are real.

**THE MEASUREMENT THAT POINTED THE WRONG WAY, again.** Ordering a user's channels by
`max(messages.created_at)` costs **0.87 ms on the test lane** — whose largest
environment holds 579 messages — and **159 ms at 1,000,000 messages, with a sequential
scan over every message in the environment on every listing**. An indexed
`channels.last_activity_at` is 1.1 ms. 145× apart, and the gap grows with the one
number a chat platform guarantees will grow. Reporting the test lane's number would
have settled the question the wrong way. The unread count needs no such column:
`greatest(channels.last_sequence − read_position, 0)`, because the write path already
maintains `last_sequence` (chapter 2.2 made it the sequencing authority).

**FOUR THINGS THE PLAN FOUND THAT THE SPEC DID NOT NAME.**

1. **R17 — nineteen files send a reader to the wrong chapter.** The previous feature
   was specified as one chapter and shipped as three; 31 files carry 40 "chapter 3.12"
   citations, and only 12 of those files are fenced in chapter 3.12's page.
   `zod-validation.pipe.ts` and `codes.ts` point at 3.12 and are taught in 3.14;
   `repository.ts` points at 3.12 and is taught in 3.13. **Now FR-038a**, with FR-038b
   holding the line that the FR and R identifiers stay — they name the feature record
   `specs/033-chapter-3-12/`, and a feature directory is named once. SC-021 is the
   gate: all 40 classified, the wrong count recorded, that count to zero. **The rule
   needed a boundary**: `last_sequence` is cited to chapter 2.2 in files taught much
   later and that is correct, so the rule is about the chapter a CHANGE was taught in,
   not the chapter that fences the file. Found while checking a citation for R15, which
   is the only reason it was found at all.
2. **`users` has no deletion marker.** R7 decided a deleted user keeps their row, and
   designing that turned up a third new column, `users.deleted_at`. `ON DELETE SET
   NULL` would satisfy the letter of "messages are preserved" and break delivery:
   `backfill.controller`'s `toFrame` drops senderless rows, so "authored by a deleted
   user" and "authored by nobody" are different states and only one is the clause.
3. **Two role vocabularies, one word apart.** `memberships.role` is
   `('owner','admin','member')` — a human in an organisation, FR-TEN-07. FR-CHN-04's
   channel roles are `('owner','moderator','member')`. A migration reusing the
   organisation constraint would accept `admin` on a channel member, refuse
   `moderator`, and look correct in review.
4. **The gauntlet has no same-tenant fixture.** All four attack shapes take another
   tenant's identifiers, so "a user of your own tenant who is not a member" is new
   work rather than a reuse (R10, FR-034).

**PASS FIFTEEN: THE FIFTH REVISION OF THE FILE COUNT CAME FROM NOT APPLYING A
RECOMMENDATION.** Pass four found that T151's ban-at-connect needs
`internal/session.controller.ts` to carry the ban, and its own report said to add the file
"to T151 **and to R18's table**". Only the task got it. `messages.itest.ts`, where the route
tests that prove the check fires are written, was never added either. Union 36 → **38**,
both chapters 21 files, ≈3,360 words each with 640 of headroom. Found by counting the paths
the tasks name rather than reading the total — the first four revisions each came from asking
a new question, this one from re-deriving an old answer.

**"A FIX LANDED IN ONE PLACE AND NOT ITS SIBLINGS" IS NOW FOUR FOR FOUR**: the send path
before the history path, R1's caller count in three documents but not the plan, the
caller/path-user phrasing in nine places, and a recommendation applied to the task and not
the table. The class does not converge by re-reading. It converges by grepping the phrase or
re-deriving the number.

**AND ONE DERIVED NUMBER HELD.** T003a's "57 tasks writing integration assertions" re-derived
to exactly 57 after a pass added a task — because T003a states the pattern that produces it
rather than the figure.

**PASS FOURTEEN: A COLUMN CALLED DEAD THAT THE RESPONSE BODY RETURNS.** `contracts/listing.md`
lists `role` among the fields it returns, from `members.role` — and FR-012's answer, the column
table's Reader cell, two sentences of prose and T176a all said **nothing reads it**. Returning a
column is reading it. The statement worth making is sharper and true: **the listing returns the
role and no operation is authorized by it.** Found by putting a contract's field table next to a
claim about the same field, which no earlier pass had done. The dead-column survivor count went
three → two → one across passes five, fourteen: only `read_positions.updated_at` is left.

**AND "THE CALLER" MEANT THE TENANT ON EVERY `/v1/users/:externalId/…` ROUTE.** Those carry an
application credential, so FR-015 — "a channel **the caller** is not a member of MUST NOT appear
in their listing" — was **vacuous**: an application key is a member of nothing and an empty list
satisfied it. Same in FR-016, the read-position row, the authorization table and T039a. Pass
twelve had already made this correction for one route and left it in five other places.

**WHEN A FINDING IS ABOUT A PHRASE, GREP THE PHRASE.** Told to fix four places, the grep found
nine — and separately found **"six callers" alive in four more documents** after pass seven fixed
three and pass thirteen a fourth. That number lived in **eight** places and hid a CRITICAL in
one of them. Three times now a fix has landed in one place and not its siblings: the send path
before the history path, R1's count everywhere but the plan, and this.

**PASS THIRTEEN SWEPT THE ASSUMPTIONS — the last artifact with no sweep — and found one
that is a claim about a number this feature changes.** "The lane's budget is 240 seconds
against a 193-second measurement" was inherited from 3.12, which set it when the lane held
**407 tests**. This feature has **57 tasks writing integration assertions**, a fifth again as
many tests, which puts the lane near 230–250 s. The budget is enforced by nothing — no turbo,
CI or vitest timeout — so exceeding it fails no build and invalidates the assumption in
silence. Now predicted at T003a and re-derived at T179b instead of carried.

**AND THE PLAN IS THE ARTIFACT THAT DRIFTS MOST QUIETLY.** Pass seven corrected R1's caller
count in three places and missed `plan.md`'s phase table, where "six callers inherit it"
survived six more passes — a fourth document holding a number that hid a CRITICAL. And
**Complexity Tracking had not moved in thirteen passes** while the design under it moved four
times: it listed six things and omitted the by-id route, the bulk removal, and **attributing
the user on the public send — half of a gap R16 had declared out of scope, brought in because
FR-001 cannot hold without it.** The constitution's workflow section names that table as where
a revised scope commitment gets justified, which is exactly what this was.

**SEVEN SWEEPS, SEVEN DIFFERENT LEFT-HAND SIDES, ALL PRODUCTIVE**: files→chapters,
routes→handlers, columns→readers, callers→signatures, scenarios→routes, edge-cases→tasks,
assumptions→reality. `tasks.md` gets edited every pass because implementation reads it;
`plan.md` gets edited when someone remembers it.

**PASS TWELVE SWEPT THE EDGE CASES, which no earlier pass had.** Ten cases, one with no
fixture and no test — and it is a case **this feature creates**. "Two tenants using the same
`external_id`, one private and one public" was an assertion: `seedTwoTenants` writes
`${label}-user` and `${label}-channel`, so the two tenants never share an id, and all four
attack shapes take an id that does **not** exist in the attacker's tenant. Before this
feature every channel was `public` and the two answers matched trivially; now the types
differ. **FR-034a and T080a/T082b.**

**EVERY SWEEP HAS FOUND SOMETHING, AND EACH ONE HAD A DIFFERENT LEFT-HAND SIDE**:
requirements→tasks (nothing after pass one), files→chapters, routes→handlers,
columns→readers, callers→signatures, scenarios→routes, edge-cases→tasks. Six productive
sweeps, six different artifacts, and the identifier grep saw none of them. Still unswept:
the spec's nine **assumptions**, each a claim nothing tests.

**AND A DECLARED FRAME WITH NO SENDER, in a feature about declared columns with no reader.**
R16 deferred presence "in scope only as far as: a non-member's socket is not subscribed, so
it receives no presence for it" — `presenceChangedSchema` is in the frame union and **nothing
emits it**, so the claim was vacuously true. Corrected rather than left to read as though
presence flowed.

**AND THE PASS THAT SPLIT ELEVEN REQUIREMENTS FOR BEING BUNDLED BUNDLED ONE ITSELF.**
Pass eleven's rewrite of FR-011 carried two clauses — the enum with its default, and the
add endpoint accepting a role. Pass twelve split it as FR-011b. The rule is easier to state
than to follow in the same edit that states it.

**AND R1 WAS IN `research.md` TWICE from pass seven to pass twelve.** The pass that appended
the caller-count correction re-emitted the whole section instead of extending it, and five
analysis passes read past a duplicated header without noticing. Nothing downstream was
wrong; the file was 28 lines longer than it said it was.

**PASS ELEVEN: CITATION IS NOT COVERAGE, AND THE CHECK THAT SAID 100% COULD NOT SEE IT.**
Three passes running found a task naming a requirement identifier while implementing something
adjacent. **FR-019** asks what the listing's `last_message` reports for a tombstone; the task
citing it tested the unread *count* — a different field. **FR-022** asks two things and the task
covering the listing half cited the whole requirement, so the socket half had no task for
eleven passes. **US6's first scenario** wanted a member added *with* a role and the plan had add
assign the default and a separate route change it.

**WHAT THE THREE HAD IN COMMON: more than one clause per requirement.** A single-clause
requirement is hard to half-implement; a two-clause one is easy. So eleven requirements were
**split** — FR-011a, FR-017a, FR-020a, FR-022a, FR-025a, FR-028a, FR-031a, FR-033a, FR-039c,
FR-040a — taking the count from 46 to 56, and every new identifier is cited by a task that
implements that clause and no other. FR-021a already existed for the same reason, split out in
pass six, and nothing has half-covered it since.

**AND `grep -c '^- [*][*]FR-'` MEASURES CITATION.** Per-identifier coverage read 100% from pass
one and concealed FR-006's bulk shape, FR-019 entirely, and half of FR-022. The cure is smaller
requirements, not a better grep.

**PASS TEN FOUND A REQUIREMENT WITH ZERO COVERAGE THAT TEN PASSES HAD READ AS COVERED.**
FR-006 says removal takes "up to 100 in one request" and FR-007 says it reports per user —
chapter 3.13's member-add shape in both halves. The contract specified a single-user
`DELETE …/members/:userExternalId`, having read "the shape chapter 3.13 chose" as *named
outcomes* and dropped *bulk*. Every pass compared requirements to tasks, both said
"removal", and identifier coverage read 100% the whole time. **Shape only becomes visible
when you compare an ACCEPTANCE SCENARIO to a route**: US2's scenario 4 names a hundred users
and the route's path named one. Now `POST /v1/channels/:channelId/members/remove`.

**A REFERENCE TO ANOTHER CHAPTER'S DESIGN IS A REQUIREMENT WHOSE CONTENT LIVES ELSEWHERE.**
"In the shape chapter 3.13 chose" compressed two properties and the contract expanded one.
Ten passes read the phrase and none re-derived it.

**AND THE FOUR TABLES DO NOT ASK THIS QUESTION.** Routes have a handler, a credential, a
repository method and a pin; columns have a migration, a writer, a reader and a removal test.
Neither asks whether the route matches the scenario that motivated it.

**AND ON THE NINTH PASS OF CARRYING FOUR FINDINGS, DEFERRAL BECAME A DECISION.** Two are now
fixed — the two-identifier attack (T082a) and the migration backfill moved out of 0011 (T019)
— and two are recorded as accepted: FR-039a/b's missing user story, and FR-002/FR-003's
deliberate overlap. Nine passes of silence is a decision nobody wrote down.

**AND PASS EIGHT FOUND THE SAME HOLE ON THE OTHER ROUTE OF THE SAME CONTROLLER.**
`messages.controller.ts` has exactly two routes — send and history — and both called a
service that dropped the caller into a repository function with no user parameter.
`listMessages(channelId, {beforeSeq, afterSeq, limit})` had nowhere to put a `userId`, so
T041's "add the same check to the history path" was asking for a check with nothing to check
against. **Pass seven fixed send and did not ask whether the read path had the same shape.**

**THREE PLACES, AND A GAP IN ANY ONE MAKES A CHECK UNREACHABLE**: the handler resolves the
principal, the service threads it, the repository function accepts it. `tasks.md` now carries
a five-row table for the routes whose behaviour depends on the caller, with those three as
columns. Two of the five had a gap.

**A REPOSITORY TEST PROVES A CHECK EXISTS; ONLY A ROUTE TEST PROVES IT FIRES.** The send
path had a passing repository test for six analysis passes while its controller supplied no
caller — and the tasks file said the repository test existed "so a controller cannot mask
it", which is the opposite of what happened.

**PASS SEVEN FOUND THE CENTRAL REQUIREMENT UNENFORCED ON THE ONLY ROUTE A CUSTOMER
CALLS.** The membership check is gated on `userId` being present. `MessagesController`
declares **no `@Accepts`**, so the guard falls back to `EITHER` and a user token is
accepted — and `messages.controller.ts:40` calls `this.messages.send(channelId, body)` with
no user at all. So a user sends to a private channel they are not a member of and nothing
checks. The planned tests all missed it: one drove the repository directly, one drove the
internal route, and both supply a `userId` the public route did not.

**R1's ARGUMENT WAS TRUE OF THE SIGNATURE AND FALSE OF THE CALLER.** "Six callers inherit
the check" — counted in pass seven, there are **three call sites**, and the one that matters
supplies nothing. A parameter nobody fills in encodes nothing. The decision survives
(constitution I puts isolation in data access); the argument for it needed the real call
graph, and writing the graph out is what found the hole. **Six passes read that number and
none counted it.**

**FIVE NUMBERS IN THIS FEATURE WERE CARRIED INSTEAD OF DERIVED, AND TWO HID A CRITICAL**:
the file count (25→29→34→36), the chapter overlap, the removal ordinals, the caller count,
and the oracle's verb count (three→four→five, with its verification task left at three
through both widenings). The cure is the same every time — **name the set, not its size** —
and it has now been applied twice: the removals point at a table, and the oracle's
verification points at "any verb T043 covers".

**AND THREE TIMES A TEST WAS PLACED BEFORE THE THING IT TESTS**: T072's ban ordering, then
T072b's ban half, then T043's join and read-position verbs — the last two arriving two tasks
and eight phases after the test that asserted them. A phase whose test cannot pass is a phase
that cannot close.

**PASS SIX FOUND TWO TASKS THAT COULD NOT BOTH PASS.** The contract and three tasks
specified a private channel's send refusal as `403 not_a_member`; SC-002 requires send's
answer — send is one of SC-001's four verbs — to be byte-identical to a channel that does
not exist. A 403 announces the channel exists, so T043's oracle would have failed against
T031's own implementation. **Private sends now answer the not-found envelope**, and
`not_a_member` turns out to have exactly one emitter in the whole feature: the read-position
route on a public channel.

**AND THE REFUSAL ORDER WAS A LEAK.** Ban, then archive, then membership means a non-member
of a private *archived* channel learns it exists from `channel_archived`. FR-021a fixes the
order at **ban → membership and visibility → archive**, with the ban check before the
channel is resolved so a banned user gets one answer for every channel id. Both findings are
chapter 3.12's fifth-pass defect pointed at this feature: a refusal that reveals what it is
refusing.

**AND WHAT MADE THEM FINDABLE was making an artifact more precise.** Five passes of
artifact-vs-artifact reading produced nothing but arithmetic errors. Pass three changed
"all three verbs" to "all four verbs SC-001 names", and adding `send` to the oracle's list
put the send refusal in contact with SC-002. Precision creates contradictions where vagueness
hid them.

**AND THE ORDER MATTERS ON ONE THING.** `POST /v1/channels` accepts `private` only
once the three read paths and the send path enforce it (FR-009). The enum widened
first would sell a guarantee the platform does not keep, which is the mistake 3.12's
fifth analysis pass caught one phase before it shipped.

**THE FENCE CHAIN TAUGHT FIVE THINGS, and four of them cost a wrong first attempt.**

1. A titled fence states the **whole file**, not an excerpt — 26 excerpts produced 43
   problems. `(excerpt)` in a title is the documented escape: the checker's
   `NOT_A_FILE` treats it as a prose illustration and leaves the path out of the chain.
2. **One full fence per path.** Replacing every excerpt with its file gave 4,995 lines,
   because six paths were fenced twice and each copy restated the file.
3. **A diff needs a predecessor in the chain**, and enough context to be a proof.
   Three lines let `repository.ts`'s pre-image match twice; eight made each hunk unique.
4. **A chapter cannot amend a state `post-series.md` builds.** Four files —
   `eslint.config.mjs`, `resume.itest.ts`, `turbo.json`, `package.json` — have entries
   there, which the checker applies AFTER every chapter, so a chapter is upstream of
   its own amendment. Excerpt in the chapter, amendment in post-series.
5. **A reverted reintroduction must never carry a title**, or the chain replays it into
   the canonical tree and FR-015 is violated by the checker itself.

And one question to ask the right way round: **"0 problems naming this chapter's page"
is not "0 problems on files this chapter owns."** The answers differed by one —
`messages.itest.ts` — and I reported the chain clean twice before checking the second.

**THE PHASE 2 EXIT CRITERION IS MET IN PART**, and the missing part is not
documentation. `packages/outsider` completes a full integration against a stack it
does not start, sealed three ways, in CI as its own job — but it passes because a
failing test CORRECTED it about the REST-to-socket path, which is the assistance the
criterion forbids. And content sufficiency is not comprehensibility: a person is the
only instrument for the second and this chapter did not use one.

**FIVE THINGS THE CODE NOW DOES THAT NO DOCUMENT ASKED FOR.** Each was found by
implementation, not by reading:

1. **A REST-sent message reaches no socket, ever** — the api publishes to no fan-out
   AND the public send attributes no user, so `toFrame` drops the row from resume.
   Two independent causes. Pinned by `public-surface.itest.ts`; owner FR-RTM-05.
2. **`field` on every validation error.** EIR-API-06 asked since 1.3;
   `ZodValidationPipe` discarded `issues[0].path` for twenty-two chapters.
3. **`@Accepts` takes a service** (FR-044). The hole was inside the chapter's own
   suite: `usage.itest.ts` presented the dispatcher's credential to the gateway's
   route for a whole chapter and passed. Nine of fifteen tests turned 403.
4. **Nine guarded tables, not five**, and the refusal message needed
   `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)` because three of the
   four new tables have composite keys and no `id`.
5. **`createUser` had `createChannel`'s fault** and R14a named neither.

**THE OUTBOX KEEPS MESSAGE TEXT FOR EVER** — `drainOutbox` sets `published_at` and
never deletes, nothing in the api deletes a row from any table, the payload copies
`data.text`, **286,871 rows** in the test lane. Collides with DR-06, FR-MSG-08,
FR-TEN-08 and FR-MOD-06. The fix is a one-line prune and **not** the tenant column
an earlier draft proposed: the outbox's legitimate mutation *is* cross-environment,
so a tenant column would make feature 030's guard refuse the relay's own sweep.
Owner: FR-MOD-06's chapter. Recorded in `db/catalogue.ts`'s SPINE comment.

**THE CHAPTER CYCLE THIS PROJECT USES**, in order: `/speckit-specify` →
`/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (repeatedly) →
`/speckit-implement` (once per phase). 3.12 ran FOURTEEN analyze passes for 75
findings and 6 CRITICAL; the sharpest was pass five's — `POST /v1/channels` was
about to accept `type: "private"` while nothing in the platform reads
`channels.type`.

**AND WHAT IMPLEMENTATION FOUND THAT FOURTEEN READING PASSES COULD NOT.** Budget
for this:

- **Fourteen passing tests meant nothing.** Every assertion compared two refusals;
  two refusals for an unrelated reason are also indistinguishable. Three control
  tests now prove the attacker works before anything asserts that it fails.
- **The first reintroduction stayed green.** `channelExists` is scoped and runs
  first, so an unscoped `listMessages` below it was never reached. The suite is
  sensitive to the outermost check on a path and blind to an inner one a live outer
  check masks. Recorded rather than reshaped until it failed.
- **Breaking indistinguishability takes an unscoped read.** A route-level 404→403
  moves both halves of the pair and the oracle cannot see it.
- **Three instruments had never produced output** — 61%, 50%, 87.5% branches, every
  uncovered arm in code that runs only when the platform is broken.
- **The fence chain**: a titled fence states the WHOLE file (26 excerpts gave 43
  problems); one full fence per path (all of them gave 4,995 lines); a diff needs a
  predecessor in the chain; and **a reverted reintroduction must never carry a
  title**, or FR-015 is violated by the chain itself.
- **`docker compose --profile services up` serves the last-built image.** Six
  failing tests against a healthy stale stack. `--build` is now in every documented
  command.

**TWO PROCESS MISTAKES THAT RECURRED, BOTH AVOIDABLE.**

**`git checkout` on a file with uncommitted work destroyed it twice** — Phase 3's
`deriveTargets` and Phase 9's five error codes plus `docsUrl`. **Commit before
breaking anything**; Phase 7's reintroductions were safe for exactly that reason.

**NOTHING ELSE RUNS ON THE MACHINE DURING A TWENTY-RUN BATTERY.** Attempt one
failed at run 11 — `api never became healthy`, 57 seconds short of the mean —
because two Next.js dev servers were compiling a 3,000-line MDX page while the api
child had 30 seconds to boot NestJS. Nothing held a port, no `EADDRINUSE`. The
evidence that told defect from interference was the wall-clock timeline, not the
error.

**AND TWENTY RUNS BUYS LESS THAN IT LOOKS.** Twenty green rejects a per-run failure
rate of 13.91% or worse at 95% confidence; a 5% flake survives them 36% of the time,
and rejecting one would take 59 runs. Chapter 3.11 ran twenty green and an
eleven-chapter-old flake surfaced on run twenty-one. The lane's budget is **240
seconds** a run against a 192–196 s measurement.

**COMMIT EACH PHASE.** A bad regex in 3.11's traceability pass broke 36 files;
because everything through the previous phase was committed, the repair was one
`git checkout` and five minutes.
**AND PASS THREE FOUND A ROUTE THAT WAS NEVER BUILT.** `GET /v1/channels/:channelId`
does not exist — `channels.controller.ts` carries a create and a member-add and no read,
so a customer can create a channel and never read its four fields back. **Three
artifacts rested on it**: SC-001 named "read by id" as one of four verbs, FR-003 said
"every read", and `contracts/membership.md` had a row for it. Now FR-003a and T039a, and
the derived-target count moves by **14** rather than 13.

**FIVE ANALYSIS PASSES: 23, 11, 7, 7, 4 findings, and three CRITICALs — all three the
same shape.** Something every comparable case in the repository has that no task provided:
the module registration (`app.module.ts`), the handler (`GET /v1/channels/:channelId`), the
credential class (`@Accepts`). `tasks.md` now holds **two tables** that close the class —
fifteen routes by handler, credential, repository method and pin; ten columns by migration,
schema twin, SAD §6.1, writer, reader, removal test and chapter. Pass five found no CRITICAL,
which is the first pass that did not, and the tables are why.

**AND A HAND-MAINTAINED COUNT WENT STALE IN EVERY SINGLE PASS.** Requirement totals, task
totals, file counts, overlap figures, "three negative checks" — five for five, including the
sentence that said to re-derive with `grep -c` and was carried forward by hand. Both counted
things now point at a table instead of holding a number.

**BOTH CRITICALS CAME FROM ASKING THE REPOSITORY A QUESTION.** Pass two's `app.module.ts`
came from "which chapter fences this file"; pass three's missing route from "does this
verb have a handler". Neither is findable by comparing spec to plan to tasks, which is
what the passes before them did. **Every arithmetic error came from comparing the
artifacts to each other** — three passes, three wrong overlap figures, all hand-computed
from a table that already held the answer. R18's table is the authority now and the other
documents quote it.

**THE FIRST ANALYSIS PASS, and what it cost to be wrong once.** 23 findings, 1 raised
CRITICAL and withdrawn. Four worth carrying forward:

1. **The CRITICAL was mine, not the feature's.** I read constitution VI's "the quickstart
   MUST run unmodified, verified by automated execution in CI" against
   `specs/*/quickstart.md` and found no CI job. Wrong artifact: the clause names the
   PUBLISHED quickstart, and the `outsider` job runs the README's sequence verbatim —
   compose, migrate, seed, sealed suite. 3.14 built exactly that. The real defect was
   five of eighteen checks having no command in a file whose own first line says every
   command is one a maintainer runs.
2. **A plausible worry, refuted by its own measurement.** 23 of 29 files are already
   fenced in earlier chapters, so I predicted diff-heavy chapters would run light on
   prose. Measured: 3.11 was **71% diffs and 107 words/fence, the highest of four**;
   3.14 was 42% diffs and 72, the lowest. Words per fence does not track diff share, and
   R12's base chapter was already the diff-heavy one. Recorded in R18 so it is not
   re-raised.
3. **A correction cannot live downstream of the page that carries the sentence.**
   FR-037's false comment in `channels.schema.ts` sat in tasks phase 17; chapter 3.15
   publishes at phase 9 and fences that file. Moved to phase 4, beside the edit that
   already touches it.
4. **`check:docs` ran before the edit that breaks it**, and both were marked `[P]` — a
   race, not an ordering slip. `04-srs.md` is on `check-docs-drift.sh`'s mirrored list.

**AND ONE CLAUSE IS ANSWERED RATHER THAN MET.** Constitution VI asks 100% branch
coverage of ordering, idempotency and tenant isolation. `repository.ts` holds all three
at 89.51%, pinned at 90 as a ratchet with the gap named in
`specs/024-coverage-and-ci/notes.md`. This feature adds four branch sets to that file and
commits to 100% **on the arms it adds**, per arm rather than by file percentage. A
private-channel membership check is authorization inside a tenant, not tenant isolation
— stated rather than left to whoever next reads the ratchet. And 3.5's failure is
pre-armed: six operations added to that file, exercised only through a child process,
took branches from **85.91% to 78.22%** on the next run.
<!-- SPECKIT END -->
