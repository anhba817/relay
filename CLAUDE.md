<!-- SPECKIT START -->
**CHAPTER 3.12 IS SHIPPED BUT THE FEATURE IS NOT CLOSED.** "Milestone: the
isolation gauntlet" — 172 of 174 tasks, checklist 16/16, published in both locales,
committed in all three repositories. **NOT TAGGED AND NOT PUSHED**, and the reason
is the next paragraph. Its record is
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
- **3.13 IS WRITTEN BUT NOT PUBLISHED**: the endpoints and the instruments. All the
  code is in `relay-platform` and green; the page does not exist. **18 files** —
  `channels/*`, `repository.ts`, `app.module.ts`, `eslint.config.mjs`,
  `vitest.coverage.config.mts`, `test-harness/*`, `public-surface.itest.ts`,
  `e2e/src/harness.ts`, and the two suites whose ports changed.
- **3.14 IS WRITTEN BUT NOT PUBLISHED**: errors that resolve, and an outsider. Same
  state. **22 files** — `codes.ts`, `protocol-error.*`, `zod-validation.pipe.ts`,
  `service-kit/src/index.ts`, `packages/outsider/*`, `scripts/seed-demo-tenant.mjs`,
  `README.md`. **The milestone name lives here**, because this is where the Phase 2
  exit criterion gets its verdict.
- **3.15 is the deferred surface** — the rest of FR-CHN and all of FR-USR, promised
  a number as 3.13 until the split took it.

**`pnpm check:fences` EXITS 1 — 20 HEAD problems, and they are exactly 3.13's and
3.14's files** (6 and 14; the other 22 files those chapters change are not in the
chain at all). Every other gate is green: 20 consecutive lane runs at 407 tests,
`pnpm coverage` passing every ratchet, lint, typecheck, build, `check:docs`,
`check:errors`.

**So `part3-ch12` is deliberately NOT tagged and nothing is pushed.** A tag here
would mark a state where the CI job that keeps the series honest is red, for a
reason this chapter created. The two remaining tasks — T125's tag and T126's push —
wait on those two pages. Writing them is the whole of the outstanding work.

One correction worth carrying forward: "0 problems naming chapter-12's page" is NOT
the same question as "0 problems on files 3.12 owns", and the two answers differed
by one — `messages.itest.ts`, which 3.12 changed and had not fenced. Check the
second question.

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
