# Tasks: Tutorial Chapter 3.11 — "Counting a connection"

**Feature**: `specs/032-chapter-3-11` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: connection-minutes metered by a service that owns no tables and,
until this chapter, no identity either — reported as totals so a lost report
repairs itself and a repeated one costs nothing, capped at the socket door, and a
crash that under-bills by a bounded amount instead of over-billing for ever.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1] [US2] [US3] [US4]** — the user story from spec.md this task serves
- Setup, Foundational, Credential, Verification, Publication and Close-out tasks
  carry no story label
- **A lettered id** (`T031a`) is a task inserted by an `/speckit-analyze` pass,
  numbered against the task it belongs beside. It may run *before* its base task
  where it is a prerequisite

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to
`relay-tutorial/`, spec paths to `specs/032-chapter-3-11/`.

---

## Phase 1: Setup & baseline

- [ ] T001 Record provenance in `specs/032-chapter-3-11/baseline.txt`: the submodule commits this chapter starts from, confirmation that `relay-platform` is at `part3-ch10`, and that both parent pins match their submodule HEADs
- [ ] T002 Record the pre-change platform baseline in `specs/032-chapter-3-11/baseline.txt` — unit and integration counts per package, coverage, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output. Chapter 3.10 closed on **256 integration tests** across twenty runs; record what this machine measures
- [ ] T003 [P] Record the site baseline in `specs/032-chapter-3-11/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the file, chapter and locale counts the chain reports
- [ ] T004 **Run the integration lane three times and record every failure.** A lane with a pre-existing intermittent failure cannot measure a new one, and chapter 3.10 found instance 12 of this project's recurring fault at exactly this step
- [ ] T004a **Measure the connect path before it changes.** Record `POST /internal/session` latency at 1-, 8- and 32-way concurrency, and the `EXPLAIN (ANALYZE, BUFFERS)` for what it reads today, into `baseline.txt`. SC-012 compares against this. Chapter 3.10's T033 chased three wrong causes across an uncontrolled benchmark reporting 273% to 411% before instrumentation showed 0.56ms — the instrument goes in first
- [ ] T005 Fix forward, with its own commit, anything T004 finds that is not this chapter's work
- [ ] T006 [P] **Verify research R16's fence count rather than trusting it.** Re-count the titled fences for each of the twelve files in the plan's structure tree and record the table in `baseline.txt`. Chapter 3.8's fence count went stale three times across its analysis passes

**Checkpoint**: the starting numbers exist, the lane is green for a known reason, and the connect path has a measured "before".

---

## Phase 2: Foundational — the minute, the schema, and the third key

- [ ] T007 Add `minuteOf(at: Date): string` to `services/api/src/quotas/period.ts` beside `periodOf`, returning a UTC minute identity, with the comment saying why it takes an instant rather than calling `now()` (FR-003)
- [ ] T008 [P] Unit tests in `services/api/src/quotas/period.test.ts` for `minuteOf`: the second boundary, the minute boundary, the month boundary, and that `periodOf(minuteOf-derived instant)` agrees with `periodOf(instant)` (FR-003, FR-009)
- [ ] T009 Write `services/api/migrations/0010_connection_minutes.sql` per `data-model.md`: `usage_connections`, the `connection_minutes` column on `usage_periods`, and `environments_quota_config_shape` and `quota_notifications_dimension_check` dropped and recreated. The migration's comments carry the chapter's argument, not a changelog
- [ ] T010 Add `usageConnections` and the `connectionMinutes` column to `services/api/src/db/schema.ts`. `bigint(..., { mode: "number" })` and `date()` in its default string mode — chapter 3.10's R7a is that a `Date` on one side of a `date` comparison is a row that cannot be found rather than an error
- [ ] T010a **Integration test the recreated constraints in `services/api/src/quotas/config.itest.ts`**: a `connection_minutes` cap is accepted, a negative one is refused, a non-object is refused, and a `connection_minutes` notification row is accepted while an unknown dimension is still refused. The constraint is the guarantee; a migration that silently dropped a clause looks identical from TypeScript
- [ ] T011 Add `connection_minutes` to `quotaConfigSchema` in `services/api/src/quotas/config.ts`, and a test that an unknown dimension is still a parse failure — the schema is `.strict()` and that is the property being preserved, not the key being added (FR-013)
- [ ] T011a [P] **Test that `capsFor` still fails closed** for a `connection_minutes` config that the CHECK would accept but the parser rejects. A quota that cannot be read must refuse nothing rather than everything, and adding a dimension is where that inverts by accident
- [ ] T012 [P] Add `connection_minutes` to the `Dimension` union in `services/api/src/quotas/quota.error.ts` and to `publicMessage()`, naming the dimension in the customer's words rather than the column's (FR-016)
- [ ] T013 Add the report request and response schemas to `packages/protocol/src/internal.ts` per `contracts/metering.md` §1, with `.strictObject()` and a `period` refinement that rejects anything but the first of a month, plus tests in `internal.test.ts`
- [ ] T014 [P] Write the credit arithmetic as a pure function — `creditFor(reported, credited): number` returning `max(0, reported − credited)` — in `services/api/src/quotas/credit.ts` with unit tests for the replay, the reorder and the first report (FR-006, FR-007)
- [ ] T015 Write the bucket arithmetic as a pure function in `services/gateway/src/meter.ts`: given an opened-at instant and a now, return the per-period bucket totals. Unit tested on a driven clock in `meter.test.ts`, including the 00:00:59-to-00:01:01 case that costs two and the five-second case that costs one (FR-002, FR-009)
- [ ] T015a **The drift test R18 requires**, in both packages: the gateway's duplicated `periodOf`/`minuteOf` and the api's agree on the same set of instants, including a month boundary and a leap day. `limits.ts` duplicated the api's window arithmetic with an argument; this duplicates a calendar, and a calendar that disagrees puts a tenant's minutes in a month nobody reads

**Checkpoint**: the unit can be computed and stored, and nothing yet computes it.

---

## Phase 3: The credential — the gateway speaks for itself

**Early on purpose.** Every integration test in Phases 4 to 7 needs a report to
be accepted, so a credential the gateway does not hold blocks all of them.

- [ ] T016 Replace the hardcoded `service: "dispatcher"` in `services/api/src/auth/authenticate.middleware.ts` with a walk over a small map of `{ env var → service name }`, returning the service whose secret matched. The constant-time compare moves inside the loop and does not otherwise change (R1a, FR-011)
- [ ] T017 [P] Tests in `services/api/src/auth/credentials.itest.ts`: the dispatcher's credential still resolves to `service: "dispatcher"`, the gateway's resolves to `"gateway"`, a credential shorter than 32 characters resolves to nothing, and an unconfigured variable makes its service unusable rather than universal
- [ ] T018 Add `RELAY_INTERNAL_CREDENTIAL_GATEWAY` to the `gateway:` block in `compose.yaml` — the block has no credential variable today — and to the api's block so it can verify one
- [ ] T019 Add `RELAY_INTERNAL_CREDENTIAL_GATEWAY` to `turbo.json`'s `test:integration` env list. **Turborepo runs in strict env mode**: a variable absent from the list is absent from the task, and the failure is a test that cannot authenticate rather than a missing-variable error
- [ ] T020 Read the credential in `services/gateway/src/main.ts` and pass it to `createApiClient`, absent by default. A gateway with no credential must start, serve sockets and log that it is not metering — metering may not be a startup dependency (FR-012)
- [ ] T021 Add the report call to `services/gateway/src/api-client.ts` per `contracts/metering.md` §1, presenting the platform credential rather than forwarding a user token, and parsing the response against the protocol schema like every other call in that file
- [ ] T021a **Test that the report call carries no user token**, in `services/gateway/src/api-client.test.ts`. The whole of R1 is that a report is nobody's user action; an implementation that reached for `identity.token` would pass every other test in this chapter

**Checkpoint**: the gateway can be authenticated by the api, and says which service it is in a log line that is now true.

---

## Phase 4: User Story 1 — A duration becomes a number (Priority: P1) 🎯 MVP

**Goal**: connection-minutes recorded per environment per period, by the api, from a claim the gateway makes.

**Independent test**: hold a connection open across three minute boundaries on a driven clock and read the figure; hold two and confirm it doubles; flush Redis and confirm nothing moves.

- [ ] T022 [US1] Add what a connection remembers about time to `Connection` in `services/gateway/src/registry.ts` — the instant it opened, and the totals last reported — beside `marks` and `sendLimit`, which are there for the same reason: it describes one socket and dies with it
- [ ] T023 [US1] Build the meter in `services/gateway/src/meter.ts`: a second `setInterval`, default 60 s, injectable the way `pingIntervalMs` already is, walking the registry and posting one report for every connection it holds (R10, FR-005)
- [ ] T024 [US1] Wire the meter into `attachSessions` in `services/gateway/src/session.ts` and clear its timer in `sessions.close()` beside the heartbeat's
- [ ] T025 [US1] Write `creditConnectionMinutes(db, entries)` in `services/api/src/db/repository.ts` as a **standalone exported function** taking explicit ids, next to `usageFor` and for the reason `usageFor` gives: the caller is the platform, not a tenant (R8)
- [ ] T026 [US1] Inside that function: `SELECT … FOR UPDATE` on the accounting row by primary key, credit the delta to `usage_periods`, upsert the accounting row to the new total, one transaction. Chapter 3.10 wanted this lock and could not have it — `FOR UPDATE cannot be applied to the nullable side of an outer join` — and here it is a single table by primary key
- [ ] T027 [US1] Create `services/api/src/internal/usage.controller.ts`: `POST /internal/usage/connections`, `@Accepts("platform")` and nothing else, body validated by the protocol schema through `ZodValidationPipe`. A separate controller from the `@Accepts("user")` internal routes, following `dispatch.controller.ts` — mixing credential classes in one controller makes the class decorator stop answering "who may call this"
- [ ] T028 [US1] Register the controller in `services/api/src/app.module.ts`. Chapter 3.10's third analysis pass found a module that was written, unit-tested and never started because no task said to register it
- [ ] T029 [US1] Extend `usageFor` with `connectionMinutes` and `connectionMinuteQuota` per `contracts/metering.md` §4, reading the roll-up column and not summing `usage_connections`
- [ ] T030 [P] [US1] Integration tests in `services/api/src/quotas/connections.itest.ts`: one connection across three boundaries records the minutes it occupied, two concurrent connections double the figure for a shared minute, and an environment with no prior `usage_periods` row gets one (SC-001, SC-002, FR-001)
- [ ] T031 [P] [US1] **The flush test.** `FLUSHALL` against Redis, then read the figure and compare numerically to before (SC-016, FR-026). This is the property that separates a quota from chapter 3.8's limiter, and chapter 3.10's first draft shipped without its equivalent
- [ ] T032 [P] [US1] Integration test for the period boundary: a connection driven across midnight on the first places its minutes in both periods and the two sum to its total (SC-011, FR-009)
- [ ] T033 [P] [US1] **Integration test that the accounting state is bounded by connections, not minutes**: ten connections driven through one minute and ten driven through sixty produce the same row count in `usage_connections` (SC-017, FR-010). The naive implementation passes every other test in this phase and this one fails at 43.2 million rows a month
- [ ] T033a [P] [US1] **Integration test that an unrefused report is the only report that counts.** Read the environment's figure, POST a report with no credential and with a valid API key, and read the figure again: `401`, `403 wrong_credential_type`, and the figure numerically unchanged (SC-010, FR-011). T017 proves the credential resolves; this proves a refusal changed nothing, which is the property a billing route actually owes
- [ ] T034 [US1] Confirm the chapter 2.1 lint ban is still in force and still refuses a database client in the gateway, as a test rather than an intention (SC-018, FR-004)

**Checkpoint**: a number exists, survives a flush, lands in the right month, and nothing enforces anything on it.

---

## Phase 5: User Story 2 — The report is unreliable, and the number is not (Priority: P1)

**Goal**: replay, loss, reordering and a crash all leave the figure right, or wrong by a bounded and stated amount.

**Independent test**: replay a report and watch the figure not move; drop one and watch the next repair it; kill the gateway and watch the figure stop.

- [ ] T035 [P] [US2] Integration test: the identical report delivered twice moves the figure once, and the second response body says `{"credited": 0}` (SC-003, FR-006). Assert the response, not only the stored figure — a test that reads only the figure passes against an implementation that credits twice and clamps
- [ ] T036 [P] [US2] Integration test: a discarded report followed by the next one lands on the figure neither loss nor duplication would have produced (SC-004, FR-007)
- [ ] T037 [P] [US2] Integration test: a report carrying a lower total credits zero and lowers nothing (FR-007, spec Edge Cases)
- [ ] T038 [US2] Refuse a report whose `connection_id` was first seen for a different environment with `409 connection_environment_conflict` per `contracts/metering.md` §1, and test it. A connection does not move tenants, and reconciling one that appears to would be inventing a fact (constitution I)
- [ ] T039 [US2] Decide and implement what a report naming an unseen connection does — accept it as that connection's first report — and write the decision into the controller's comment. The specification listed this as a decision the plan must make and state; this is where it gets stated in code
- [ ] T040 [US2] Flush a final report from `sessions.close()` so a graceful shutdown loses nothing, and wire it to the `server.on("close")` path `main.ts` already has (R11, FR-008)
- [ ] T041 [US2] Integration test the crash in `services/gateway/src/meter.itest.ts`: kill the process with a connection open, confirm the figure advanced by no more than one interval, then **read it again ten intervals later and confirm it is identical** (SC-005, FR-008). The second read is the assertion — the first shows the loss is bounded, the second shows nothing is still billing for a socket nobody holds
- [ ] T042 [P] [US2] Integration test that a failing report path closes no socket, refuses no connect and fails no send, with every report forced to error (SC-019, FR-012)
- [ ] T043 [P] [US2] **Test that there is no queue.** Force every report to fail and assert the gateway holds no buffer of undelivered reports (R3). A test asserting a buffer length here means the delta protocol crept back in, and a delta protocol needs the buffer this design exists to avoid

**Checkpoint**: every failure mode in `contracts/metering.md` §5 has a test, including the one that loses minutes.

---

## Phase 6: User Story 3 — The cap brakes the thing it meters (Priority: P2)

**Goal**: at or above the hard cap, new connections are refused with the quota code; everything already working keeps working.

**Independent test**: set a cap below usage, watch a connect refused with 402 and a socket opened before the breach still receiving sixty seconds later.

- [ ] T044 [US3] Write the connect-time quota read in `services/api/src/db/repository.ts`: `environments` left-joined to `usage_periods` on two primary keys, one round trip, early exit when nothing is configured. `environmentLimits` is **not** extended — chapter 3.10's H2 refused that and its second caller is this same path (R7, FR-025)
- [ ] T045 [US3] Raise `QuotaExceededError` for `connection_minutes` from `services/api/src/internal/session.controller.ts` and map it to a named `402`. The code is named by the thrower: `ProtocolErrorFilter` infers a code for four statuses and calls everything else `internal_error` (FR-016)
- [ ] T046 [US3] Add the fourth outcome to `Authentication` in `services/gateway/src/auth.ts` and update its comment from "Three outcomes, not two" to four. A 402 today becomes `ApiError` → `unavailable` → close 1011, which tells the client we are broken and that retrying helps, and is wrong about both (R6)
- [ ] T047 [US3] Map `402` in `services/gateway/src/api-client.ts`'s `session()` beside the `401 || 403` branch, distinctly from both — refused and unavailable are already taken and neither fits
- [ ] T048 [US3] Write the raw 402 onto the upgrade socket in `services/gateway/src/session.ts`, beside `refuseUpgrade`'s 429, per `contracts/metering.md` §2. **No `Retry-After`** — that header is the whole difference between the two refusals at this door
- [ ] T049 [P] [US3] Integration test the refusal off the wire: `402`, `quota_exceeded`, four fields, and no `Retry-After` (FR-015, FR-016). Read the response, not a log line
- [ ] T050 [P] [US3] Integration test the degradation: a connection opened before the breach is still open and still receiving sixty seconds later, in the same test and against the same environment as the refused connect (SC-006, FR-017)
- [ ] T051 [P] [US3] Integration test that a REST send and a history read both succeed while the connection-minutes cap is breached (SC-007, FR-018)
- [ ] T052 [P] [US3] Integration test the two configuration edges: a cap of zero refuses every connect, and no cap configured accepts every connect while still recording the minutes (FR-014, US3 scenarios 5 and 6)
- [ ] T053 [P] [US3] Integration test that raising the cap above usage restores connecting on the next attempt, with no restart (SC-008, FR-020)
- [ ] T054 [US3] Integration test that a connection open past the cap **keeps accruing**, and write the overshoot bound into the code comment that owns it: `(connections open at the crossing) × (minutes until each closes) + one reporting interval`, with the right-hand side having no numeric ceiling (FR-017, FR-019)
- [ ] T055 [US3] Add the connect-path performance test file the verification phase measures, so Phase 8 measures a committed thing rather than an ad-hoc script

**Checkpoint**: the cap refuses the operation it meters and refuses nothing else.

---

## Phase 7: User Story 4 — Nobody is surprised by a third dimension (Priority: P3)

**THE SEAM.** Almost entirely reuse: a new value in an existing column, a new
branch in existing copy, an existing UNIQUE constraint doing the work. If Phase
9's count comes in over 4,000 words, this phase moves out and Phase 6 goes with
it.

- [ ] T056 [US4] Extract `recordCrossings` and `organisationOf` from `Repository` in `services/api/src/db/repository.ts` into standalone functions taking `(tx, environmentId, …)`, with the private methods becoming one-line delegations. About forty lines moved, no behaviour changed (R8)
- [ ] T056a [US4] **Run the full lane after T056 before writing anything on top of it.** A pure extraction that changes behaviour is the worst kind of finding to make three tasks later, and `sendMessage` is the caller
- [ ] T057 [US4] Call the extracted `recordCrossings` from the report transaction, above the credit and inside the same transaction, so the crossing and the credit commit together — chapter 3.10's argument for why there is no sweep, reused rather than restated (FR-022, FR-023, R5)
- [ ] T058 [P] [US4] Add the connection-minutes copy to `services/api/src/quotas/quota-email.ts` per `contracts/metering.md` §3: the dimension in the customer's words, and at 100% of a hard cap the sentence naming what stops (new connections) and what does not (open sockets, REST sends, history reads)
- [ ] T059 [P] [US4] Unit tests for the copy in `quota-email.test.ts`, including that 100% of a **soft** threshold says nothing was refused
- [ ] T060 [P] [US4] Mailpit integration test: crossing 50%, 80% and 100% produces exactly three emails for the connection-minutes dimension in a period, read out of the mail server rather than asserted on a send call (SC-009, FR-022)
- [ ] T061 [P] [US4] Mailpit integration test: re-crossing an already notified threshold sends nothing, and the thresholds are notifiable again after the period rolls over (FR-022)
- [ ] T062 [P] [US4] Integration test that one report crossing two thresholds notifies both (FR-023). A cap of 4 with four minutes crosses three thresholds, because 80% of 4 is 3.2 — chapter 3.10 got this expectation wrong twice
- [ ] T063 [P] [US4] Integration test that a soft threshold with no hard cap emails and refuses no connect (SC-020, FR-021)

**Checkpoint**: FR-RTL-05 is closed on all three dimensions.

---

## Phase 8: Verification

- [ ] T064 **The guard's prediction.** Run the lane against a freshly baited database and record every refusal into `captured-output.md`, with the count and whether any names `usage_connections`, `usage_periods` or `quota_notifications`. Confirm `git diff --stat packages/test-harness/src/exempt.ts` is empty (SC-014, R5). If a file does need an exemption, it is named in `exempt.ts` **with the tables it needs** and in the matching lint ignores list, and the chapter says which global operation required it (FR-027). A refusal here is the interesting result, not a failure
- [ ] T065 **Measure the connect path against T004a**, at 1-, 8- and 32-way concurrency, with `EXPLAIN (ANALYZE, BUFFERS)` for the added read. Record both in `captured-output.md`. Index lookups on two primary keys, not a scan (SC-012, FR-025). If the number is bad, instrument before changing anything — chapter 3.10 made two code changes chasing a warm-up artefact
- [ ] T066 **Count the six places** the third dimension had to be named and write the number into `chapter-notes.md` beside chapter 3.10's written prediction of "a new key plus a one-line constraint change", quoted from `0009_quotas.sql` and `quotas/config.ts` (SC-013, FR-024). A higher number is the result
- [ ] T067 Run `pnpm coverage` and confirm every per-file ratchet holds. Where a ratchet moves, record the before and after figures rather than the direction
- [ ] T068 **Twenty consecutive integration runs**, recording exit code, wall-clock and test count for each into `baseline.txt` (SC-014). `failing-files=0` beside `exit=1` is interference, not a defect — a real failure names a test. Do not edit source and do not run a concurrent `turbo run test --force` while the battery is running: chapter 3.10 invalidated two of its three attempts that way, once by editing source mid-battery and once by letting `nest build` rewrite `dist/` under a running import
- [ ] T069 [P] **Traceability pass.** Confirm every `FR-0xx`/`SC-0xx` id in code and comments introduced by this chapter reads as a feature-local id with its spec named, and **check every altered line against `part3-ch10`** before committing. Chapter 3.10's equivalent pass rewrote six pre-existing comments belonging to chapters 3.5, 3.6 and 3.9 while fixing sixteen of its own
- [ ] T070 [P] **Credential scan, recording the patterns searched and not only the verdict.** Grep the captured transcripts, `captured-output.md`, `baseline.txt`, both locale pages and every fence for: `rk_svc_`, `rk_live_`, `rk_dev_`, `rk_svc_local_development_credential_0000`, `RELAY_INTERNAL_CREDENTIAL`, `RELAY_WEBHOOK_SECRET_KEY`, `Bearer ey`, and any 32-or-more-character hex or base64 run. **This chapter gives the gateway a credential and the quickstart shows an `Authorization: Bearer rk_svc_…` header**, so the compose default is the specific thing most likely to be pasted into a published page. Record the pattern list and the file count searched
- [ ] T071 Re-run every gate: `pnpm turbo run test --force`, `pnpm test:integration`, `pnpm coverage`, `pnpm lint`, and the tutorial's `check:fences`, `check:docs`, `lint` and `build`. Record exit codes, not grep output

**Checkpoint**: every measurable outcome in spec.md has a number, including the ones that came out wrong.

---

## Phase 9: The chapter, in English — and the size gate

- [ ] T072 Write `specs/032-chapter-3-11/chapter-notes.md`: what the plan said, what shipped, and where they disagreed. Written before the page, so the page has something to be honest about
- [ ] T073 Create `relay-tutorial/app/(en)/part-3/chapter-11/counting-a-connection/figures.ts` — the bucket diagram, the cumulative-versus-delta comparison, the loss table from `contracts/metering.md` §5, and the state transition from `data-model.md`
- [ ] T074 Write `relay-tutorial/app/(en)/part-3/chapter-11/counting-a-connection/page.mdx`. The spine: messages and users were already rows, a connection is not, and the only process that can see one owns no tables and — until this chapter — no identity. Say out loud that reports carry totals and why that deletes the retry buffer
- [ ] T075 The page must state the overshoot bound with its open right-hand side (FR-019), the six-place count against chapter 3.10's prediction (FR-024), and the answer to `docs/04-srs.md`'s open question 4 with the rounding rule and who it charges (FR-028)
- [ ] T076 **Count the finished page**: prose words excluding fences, front matter and figure captions, and the fence count read from the page. Expected 2,000–4,000 (SC-015). Chapter 3.10's estimate ran 18% high against the page it produced
- [ ] T076a **If the count exceeds 4,000, split at Phase 7's seam** and renumber: the notification story and the cap become their own chapter, the isolation gauntlet moves from 3.12 to 3.13, and `docs/07-tutorial-plan.md` and `relay-tutorial/lib/tutorial.ts` are updated together. Three of Part 3's four splits were discovered mid-chapter; this is the instrument that catches the fifth

**Checkpoint**: the page exists and has been counted rather than estimated.

---

## Phase 10: Publication in both locales

- [ ] T077 **Write the chapter's fences**, routing each change to where it belongs: a file this chapter discusses gets a diff fence on the page; a change the chapter does not teach goes to `relay-tutorial/fences/post-series.md`. Twelve files carry 62 existing fences between them (T006), and the chain applies hunked diffs — each hunk's pre-image must appear in the predecessor state exactly once
- [ ] T077a **Decide `compose.yaml` and `turbo.json` routing explicitly.** The chapter does discuss the gateway's new credential, so both belong on the page rather than in `post-series.md`. Chapter 3.10 sent its `turbo.json` change to `post-series.md` because it discussed no part of it; the test is what the chapter teaches, not which file changed
- [ ] T078 Run `pnpm check:fences` and fix every divergence. This is the cheapest place to find a hunk written against the wrong pre-image
- [ ] T079 Write the Vietnamese mirror at `relay-tutorial/app/(vi)/vi/part-3/chapter-11/counting-a-connection/`, with every fence **byte-identical** to its English counterpart under the same title — the chain's MIRROR property
- [ ] T080 Register the chapter in `relay-tutorial/lib/tutorial.ts`: status from `forthcoming` to published, and the `readerProduces` line checked against what the chapter actually produced
- [ ] T081 Run the tutorial's full gate set: `check:fences`, `check:docs`, `lint`, `build`. **Leave the author's uncommitted prose edits in other chapters alone** unless a code fence is involved

**Checkpoint**: the chain is byte-exact in both locales and no chapter has been made to lie.

---

## Phase 11: Close-out

- [ ] T082 Update `docs/07-tutorial-plan.md`'s 3.11 row and its Part 3 narrative with what this chapter turned out to be against what the plan said — including the word count against the estimate, and R5a's finding about chapter 3.10's guard coverage
- [ ] T083 [P] Record R5a as scheduled work rather than a remembered gap: the four environment-scoped tables feature 030's guard does not watch, and the `OLD.id` problem that makes the extension more than an array change. Name the feature or chapter that owns it
- [ ] T084 [P] Update `specs/032-chapter-3-11/chapter-notes.md` with the final numbers: the twenty-run battery, the connect-path measurement, the six-place count, and every place the plan was wrong
- [ ] T085 Mark `specs/032-chapter-3-11/checklists/requirements.md` against the finished chapter, including SC-015 which could not be evaluated until the page existed
- [ ] T086 Commit and tag `part3-ch11`, confirming all three repositories clean and both parent pins matching their submodule HEADs before the tag is cut

---

## Dependencies

```
Phase 1 (baseline, including the connect path's "before")
    ↓
Phase 2 (minute, schema, third key, protocol)   ← blocking: every story needs it
    ↓
Phase 3 (the credential)                         ← blocking: gates every integration
    ↓                                              test in Phases 4 to 7
Phase 4 (US1, the number)                        ← ships alone as metering
    ↓
Phase 5 (US2, the number under failure)          ← needs a number to break
    ↓
Phase 6 (US3, the cap)                           ← needs a number to compare against
    ↓
Phase 7 (US4, the emails)   ← THE SEAM; needs a cap to be a percentage of
    ↓
Phase 8 (verification) → 9 (chapter + size gate) → 10 (locales) → 11 (close-out)
```

**Story independence.** US1 ships without US2, US3 or US4: a recorded figure is
observability and is worth having on its own. US2 needs US1 — there has to be a
number before losing one means anything. US3 needs US1 for the same reason. US4
needs US3, because a threshold is a percentage of a cap.

**Six orderings that matter:**

- **T004a before everything.** SC-012 compares the connect path against a
  measurement, and a measurement taken after the change is not one.
- **Phase 3 before Phase 4.** The report route refuses an unauthenticated caller,
  which is FR-011 working correctly and every downstream integration test failing.
- **T015a beside T015, not after Phase 4.** The duplicated calendar is the thing
  most likely to be quietly wrong, and the drift test is the only thing checking it.
- **T028 with T027.** A controller nobody registers is a route that does not
  exist, and chapter 3.10 found exactly that in its third analysis pass.
- **T056a between T056 and T057.** T056 is a pure extraction on the critical path
  of `sendMessage`. Verifying it in isolation is cheaper than finding it under
  three tasks of new code.
- **T064 before T074.** Discover whether the no-sweep prediction holds before
  writing the paragraph that claims it does.

## Parallel opportunities

- **Phase 1**: T003 and T006 alongside T001, T002 and T004a.
- **Phase 2**: T007/T008 (the minute), T013 (the protocol) and T014 (the credit
  arithmetic) are three files with no shared state. T009's migration is
  independent of all three.
- **Phase 3**: T017 alongside T018 and T019 — a test, a compose file and a turbo
  file.
- **Phase 4**: T030 to T033 are four independent integration files once T027 and
  T028 exist.
- **Phase 5**: T035, T036, T037, T042 and T043 are all independent.
- **Phase 6**: T049 to T053 are independent once T044 to T048 are in.
- **Phase 7**: T058/T059 (the copy) run alongside T060 to T063 (the Mailpit
  reads), and both need T057.
- **Phase 8**: T069 and T070 alongside T064 to T068.

## Implementation strategy

**MVP is Phase 4.** A connection-minute recorded per environment per month, from
a service that owns no tables, is the chapter's subject and closes the metering
half of FR-RTL-05. Stopping there would leave the dimension uncapped, which is a
smaller feature and not a wrong one.

**Then Phase 5**, because the failure modes are the chapter. Metering an event is
a write in the transaction that caused it; metering a duration is a claim from
another process about time that has already passed, and every way that claim can
go wrong shows up as money. A chapter that shipped Phase 4 and not Phase 5 would
have taught the easy half.

**Phase 6 next**, because FR-RTL-05 says enforce, not meter.

**Phase 7 last, and separable.** It is the fourth telling of the outbox and for
this chapter it is nearly all reuse — the right thing to cut if the page runs
long, because a reader who stops before it has the chapter's subject.
