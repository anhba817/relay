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
and the constitution gate, `research.md` for R1 to R17 (twelve measured against a
running database), then `data-model.md`, `contracts/membership.md`,
`contracts/listing.md` and `quickstart.md` (V0 to V16, three of them negative).
42 requirements, 20 success criteria, checklist 16/16.

**Twelve SRS clauses, five dead columns, and three corrections.** The clauses are
FR-CHN-03/04/05/06/08/09/10 and FR-USR-02/03/04/05/06. The columns exist and nothing
reads them: `channels.type`, `channels.archived_at`, `users.avatar_url`,
`users.metadata`, `users.banned_at` — that count is the feature's own headline number
and V0 records it before Phase 2 moves anything.

**THE SPLIT WAS TAKEN FROM A MEASURED FILE COUNT BEFORE ANY PROSE EXISTED** (FR-040),
which is the one thing 3.12's close-out asked the next feature to do differently.
25 platform files, 16 changed and 9 new. **Three chapters fails at the FLOOR** —
groups A and B land at ~1,900 words against a 2,000 minimum, the first time the low
end of the bound has decided anything — and **one chapter fails at the ceiling**,
because 25 files lands at 4,000 with an estimate that has run low twice (3.5
estimated 22 fences and shipped 39; 3.12 estimated 37 files and shipped 61). So:
**3.15 "the channel a customer controls"** (membership, private type, removal, roles,
archiving — 17 files, ~2,730 words) and **3.16 "what a user sees"** (listing, unread,
and the whole user surface — 20 files, ~3,210 words). The page phases sit at 9 and 16
rather than last, so each page is written when its own numbers are real.

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

1. **R17 — nineteen files send a reader to the wrong chapter, and no requirement
   covers it.** The previous feature was specified as one chapter and shipped as
   three; 31 files carry 40 "chapter 3.12" citations, and only 12 of those files are
   fenced in chapter 3.12's page. `zod-validation.pipe.ts` and `codes.ts` point at
   3.12 and are taught in 3.14; `repository.ts` points at 3.12 and is taught in 3.13.
   The FR and R identifiers in those comments stay — they belong to the feature,
   `specs/033-chapter-3-12/`. Only the chapter number is wrong. Found while checking a
   citation for R15, which is the only reason it was found at all.
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
<!-- SPECKIT END -->
