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

**Tasks that run a command rather than edit a file carry no path** — the baseline
runs, the gates, the batteries, the counts. Every other task names one, and the
test tasks name it through the map below rather than repeating it on 21 lines.

### Which lane, and which file

**Decided in R24, against a precedent pointing the other way.** Chapter 3.10 put
its socket-level cap test in `packages/e2e/src/` because "the gateway's own lane
does not spawn" a live api — which `session.itest.ts:116` has done since chapter
3.2. The deciding argument is different: **e2e cannot drive a clock**, because
there the gateway is a child process, and every timing assertion in this chapter
is stated in calendar minutes. `packages/e2e/src/harness.ts` is therefore not
touched, and does not become a 22nd file in R16's fence table.

| Tasks | File | Why there |
|---|---|---|
| T030, T030a, T031, T032, T033, T035, T036, T037, T051 | `services/api/src/quotas/connections.itest.ts` | the credit, its failure modes, and the degradation that involves no socket |
| T060, T061, T062, T063 | `services/api/src/quotas/connections.itest.ts` | a new file, not 3.10's `quotas.itest.ts`, so the scoped-assertion discipline of T060a is established rather than inherited from a suite that asserts `toBeGreaterThan(0)` |
| T033a, T033e, T033f, T039 | `services/api/src/internal/usage.itest.ts` | the route's own credential and isolation surface |
| T010a | `services/api/src/quotas/config.itest.ts` | the recreated CHECK, against a live database |
| T011a | `services/api/src/quotas/config.test.ts` | `capsFor` failing closed — pure, no database |
| T042, T043, T043a, T040b, T041 | `services/gateway/src/meter.itest.ts` | the meter's lifecycle; the last two spawn a gateway process |
| T049a, T050, T052, T053, T054 | `services/gateway/src/session.itest.ts` | anything that needs a real socket, with an in-process gateway so the clock is injectable |
| T017 | `services/api/src/auth/credentials.itest.ts` | extends the suite that already sets the credential |
| T021a | `services/gateway/src/api-client.test.ts` | pure, no api needed |
| T023b | `services/gateway/src/meter.ts` | the retention, beside the timer that reports it |
| T057 | `services/api/src/db/repository.ts` | the crossing call, inside the report transaction |

---

## Phase 1: Setup & baseline

- [X] T001 Record provenance in `specs/032-chapter-3-11/baseline.txt`: the submodule commits this chapter starts from, confirmation that `relay-platform` is at `part3-ch10`, and that both parent pins match their submodule HEADs
- [X] T002 Record the pre-change platform baseline in `specs/032-chapter-3-11/baseline.txt` — unit and integration counts per package, coverage, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output. Chapter 3.10 closed on **256 integration tests** across twenty runs; record what this machine measures
- [X] T003 [P] Record the site baseline in `specs/032-chapter-3-11/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the file, chapter and locale counts the chain reports
- [X] T004 **Run the integration lane three times and record every failure.** A lane with a pre-existing intermittent failure cannot measure a new one, and chapter 3.10 found instance 12 of this project's recurring fault at exactly this step
- [X] T004a **Measure the connect path before it changes.** Record `POST /internal/session` latency at 1-, 8- and 32-way concurrency, and the `EXPLAIN (ANALYZE, BUFFERS)` for what it reads today, into `baseline.txt`. SC-012 compares against this. Chapter 3.10's T033 chased three wrong causes across an uncontrolled benchmark reporting 273% to 411% before instrumentation showed 0.56ms — the instrument goes in first
- [X] T005 Fix forward, with its own commit, anything T004 finds that is not this chapter's work
- [X] T006 [P] **Verify research R16's fence count rather than trusting it.** **Generate** R16's fence table from the pages with a one-line loop over `grep -rho 'title="<path>"'`, for all **twenty-one** files including the four build-gate ones (`compose.yaml`, `turbo.json`, `vitest.coverage.config.mts`, `eslint.config.mjs`), and confirm the total is **95**. The table has been wrong in every analysis pass — 12/62, 13/66 with a row asserted rather than counted, 17/77 counting only source files — and every error came from extending a list by hand. Do not hand-edit it again and record the table in `baseline.txt`. Chapter 3.8's fence count went stale three times across its analysis passes

**Checkpoint**: the starting numbers exist, the lane is green for a known reason, and the connect path has a measured "before".

---

## Phase 2: Foundational — the minute, the schema, and the third key

- [ ] T007 Add `minuteOf(at: Date): string` to `services/api/src/quotas/period.ts` beside `periodOf`, returning a UTC minute identity, with the comment saying why it takes an instant rather than calling `now()` (FR-003)
- [ ] T008 [P] Unit tests in `services/api/src/quotas/period.test.ts` for `minuteOf`: the second boundary, the minute boundary, the month boundary, and that `periodOf(minuteOf-derived instant)` agrees with `periodOf(instant)` (FR-003, FR-009)
- [ ] T009 Write `services/api/migrations/0010_connection_minutes.sql` per `data-model.md`: `usage_connections`, the `connection_minutes` column on `usage_periods`, and `environments_quota_config_shape` and `quota_notifications_dimension_check` dropped and recreated. The migration's comments carry the chapter's argument, not a changelog. **Do not touch `migrations/meta/_journal.json`** — it is drizzle-kit's, it is already stale at `0007` while `0008` and `0009` shipped, and `migrate.ts` applies files by reading the directory and sorting
- [ ] T010 Add `usageConnections` and the `connectionMinutes` column to `services/api/src/db/schema.ts`. `bigint(..., { mode: "number" })` and `date()` in its default string mode — chapter 3.10's R7a is that a `Date` on one side of a `date` comparison is a row that cannot be found rather than an error
- [ ] T010a **Integration test the recreated constraints in `services/api/src/quotas/config.itest.ts`**: a `connection_minutes` cap is accepted, a negative one is refused, a non-object is refused, and a `connection_minutes` notification row is accepted while an unknown dimension is still refused. The constraint is the guarantee; a migration that silently dropped a clause looks identical from TypeScript
- [ ] T011 Add `connection_minutes` to `quotaConfigSchema` in `services/api/src/quotas/config.ts`, and a test that an unknown dimension is still a parse failure — the schema is `.strict()` and that is the property being preserved, not the key being added (FR-013)
- [ ] T011a [P] **Test that `capsFor` still fails closed** for a `connection_minutes` config that the CHECK would accept but the parser rejects. A quota that cannot be read must refuse nothing rather than everything, and adding a dimension is where that inverts by accident
- [ ] T012 [P] Fix `publicMessage()` in `services/api/src/quotas/quota.error.ts`. **There is no union to edit** — `Dimension` is `keyof QuotaConfig`, so it widens the moment T011 lands. What needs editing is the two-way ternary `dimension === "messages" ? "message" : "active user"`, which renders a connection-minutes breach as "monthly **active user** quota exhausted". The compiler catches nothing and the wrong word ships (FR-016)
- [ ] T012a [P] In the same file, make the resumed operation follow the dimension. `publicMessage()` ends "sends resume on …" and `resumesOn()`'s doc comment says "The date sends resume" — for connection-minutes what resumes is **connecting**. Unit test one message per dimension, asserting the noun and the verb, against `contracts/metering.md` §2
- [ ] T013 Add the report request and response schemas to `packages/protocol/src/internal.ts` per `contracts/metering.md` §1, with `.strictObject()` and a `period` refinement that rejects anything but the first of a month, plus tests in `internal.test.ts`
- [ ] T014 [P] Write the credit arithmetic as a pure function — `creditFor(reported, credited): number` returning `max(0, reported − credited)` — in `services/api/src/quotas/credit.ts` with unit tests for the replay, the reorder and the first report (FR-006, FR-007)
- [ ] T015 Write **the pure half** of `services/gateway/src/meter.ts`: the gateway's own `periodOf` and `minuteOf` (R18 duplicates them because the gateway cannot import from the api), and the bucket arithmetic over them — given an opened-at instant and a now, return the per-period bucket totals. No timer and no transport; T023 adds those to the same file. **`erasableSyntaxOnly` is on for the gateway** (ADR-15, `services/gateway/tsconfig.json`), so no constructor parameter properties and no enums — `api-client.ts`'s `ApiError` documents that trap in a published fence. Unit tested on a driven clock in `meter.test.ts`, including the 00:00:59-to-00:01:01 case that costs two and the five-second case that costs one (FR-002, FR-009)
- [ ] T015a **The drift test R18 requires**, in both packages: the gateway's duplicated `periodOf`/`minuteOf` and the api's agree on the same set of instants, including a month boundary and a leap day. `limits.ts` duplicated the api's window arithmetic with an argument; this duplicates a calendar, and a calendar that disagrees puts a tenant's minutes in a month nobody reads

**Checkpoint**: the unit can be computed and stored, and nothing yet computes it.

---

## Phase 3: The credential — the gateway speaks for itself

**Early on purpose.** Every integration test in Phases 4 to 7 needs a report to
be accepted, so a credential the gateway does not hold blocks all of them.

- [ ] T016 Replace the hardcoded `service: "dispatcher"` in `services/api/src/auth/authenticate.middleware.ts` with a walk over a small map of `{ env var → service name }`, returning the service whose secret matched. The constant-time compare moves inside the loop and does not otherwise change (R1a, FR-011). `PLATFORM_CREDENTIAL_ENV` is exported and consumed only inside its own file — confirm that with one grep and record the result, rather than preserving or dropping an export on a guess. **Keep the `process.env` read at call time**: `credentials.itest.ts:404` SETS the variable during the test and says so in a comment, and hoisting the read to a module-level constant would break that pattern silently
- [ ] T017 [P] Tests in `services/api/src/auth/credentials.itest.ts`: the dispatcher's credential still resolves to `service: "dispatcher"`, the gateway's resolves to `"gateway"`, a credential shorter than 32 characters resolves to nothing, and an unconfigured variable makes its service unusable rather than universal. Set the variables in the test the way `credentials.itest.ts:404` already does — `pnpm coverage` runs vitest directly rather than through turbo, so T019's env list does not reach that lane
- [ ] T018 Add `RELAY_INTERNAL_CREDENTIAL_GATEWAY` to the `gateway:` block in `compose.yaml` — the block has no credential variable today — and to the api's block so it can verify one
- [ ] T019 Add `RELAY_INTERNAL_CREDENTIAL_GATEWAY` to `turbo.json`'s `test:integration` env list. **Turborepo runs in strict env mode**: a variable absent from the list is absent from the task, and the failure is a test that cannot authenticate rather than a missing-variable error
- [ ] T020 Read the credential in `services/gateway/src/main.ts` and pass it to `createApiClient`, absent by default. A gateway with no credential must start, serve sockets and log that it is not metering — metering may not be a startup dependency (FR-012)
- [ ] T021 Add the report call to `services/gateway/src/api-client.ts` per `contracts/metering.md` §1, presenting the platform credential rather than forwarding a user token, and parsing the response against the protocol schema like every other call in that file
- [ ] T021a **Test that the report call carries no user token**, in `services/gateway/src/api-client.test.ts`. The whole of R1 is that a report is nobody's user action; an implementation that reached for `identity.token` would pass every other test in this chapter

**Checkpoint**: the gateway can be authenticated by the api, and says which service it is in a log line that is now true.

---

## Phase 4: User Story 1 — A duration becomes a number (Priority: P1) 🎯 MVP

**Goal**: connection-minutes recorded per environment per period, by the api, from a claim the gateway makes.

**Independent test**: hold a connection open across three minute boundaries on a driven clock and read the figure; hold two and confirm it doubles; open and close one inside a single interval and confirm it still counts; flush Redis and confirm nothing moves.

- [ ] T022 [US1] Add what a connection remembers about time to `Connection` in `services/gateway/src/registry.ts` — the instant it opened, and the totals last reported — beside `marks` and `sendLimit`, which are there for the same reason: it describes one socket and dies with it
- [ ] T023 [US1] Build **the timer half** of `services/gateway/src/meter.ts` on top of T015: a second `setInterval`, `meterIntervalMs`, default 60 s, injectable the way `pingIntervalMs` beside it already is, walking the registry and posting one report for every connection it holds (R10, FR-005)
- [ ] T023a [US1] **Meter the close path, which the registry cannot.** `session.ts` calls `registry.remove(connection.id)` on the line after its `close` handler opens, so a socket that opens and closes between two reports is gone before the meter sees it and is counted **zero** — FR-002 forbids that, and it would make reconnect churn free, which is the one thing R2 chose the bucket model to charge. The close handler hands the connection's final per-period totals to the meter (R19, FR-005). **Not a synchronous report from the handler**: that handler is documented as "the last place that should throw", and a mass disconnect would become a burst of HTTP requests
- [ ] T023b [US1] Retain a closed connection's total until a report carrying it is **accepted**, bounded, with a discard at the cap logged and counted rather than dropped silently (FR-029). This is the one place R3's "totals repair themselves, so nothing is queued" stops applying — a closed connection has no next report — and the code comment says so rather than leaving the exception to be inferred
- [ ] T024 [US1] Wire the meter into `attachSessions` in `services/gateway/src/session.ts` and clear its timer in `sessions.close()` beside the heartbeat's
- [ ] T025 [US1] Write `creditConnectionMinutes(db, entries)` in `services/api/src/db/repository.ts` as a **standalone exported function** taking explicit ids, next to `usageFor` and for the reason `usageFor` gives: the caller is the platform, not a tenant (R8)
- [ ] T026 [US1] Inside that function: `SELECT … FOR UPDATE` on the accounting row by primary key, credit the delta to `usage_periods`, upsert the accounting row to the new total, one transaction. Chapter 3.10 wanted this lock and could not have it — `FOR UPDATE cannot be applied to the nullable side of an outer join` — and here it is a single table by primary key
- [ ] T027 [US1] Create `services/api/src/internal/usage.controller.ts`: `POST /internal/usage/connections`, `@Accepts("platform")` and nothing else, body validated by the protocol schema through `ZodValidationPipe`. A separate controller from the `@Accepts("user")` internal routes, following `dispatch.controller.ts` — mixing credential classes in one controller makes the class decorator stop answering "who may call this"
- [ ] T028 [US1] Register the controller in `services/api/src/internal/internal.module.ts`, where `SessionController` and `DispatchController` already are. **Not `app.module.ts`** — it carries `controllers: [HealthController]` and already imports `InternalModule`, so a task pointing there would have found nothing to do and concluded the work was done. Chapter 3.10's third analysis pass found a module that was written, unit-tested and never started because no task said to register it
- [ ] T029 [US1] Extend `usageFor` with `connectionMinutes` and `connectionMinuteQuota` per `contracts/metering.md` §4, reading the roll-up column and not summing `usage_connections`
- [ ] T030 [P] [US1] Integration tests in `services/api/src/quotas/connections.itest.ts`: one connection across three boundaries records the minutes it occupied, two concurrent connections double the figure for a shared minute, and an environment with no prior `usage_periods` row gets one (SC-001, SC-002, FR-001)
- [ ] T030a [P] [US1] **Integration test the socket that lives and dies between two reports**: opened and closed inside one interval, it records one connection-minute rather than zero (SC-021, FR-005, US1 scenario 5). Then the churn case the unit exists for — a thousand five-second sockets are not free
- [ ] T031 [P] [US1] **The flush test.** `FLUSHALL` against Redis, then read the figure and compare numerically to before (SC-016, FR-026). This is the property that separates a quota from chapter 3.8's limiter, and chapter 3.10's first draft shipped without its equivalent
- [ ] T032 [P] [US1] Integration test for the period boundary: a connection driven across midnight on the first places its minutes in both periods and the two sum to its total (SC-011, FR-009)
- [ ] T033 [P] [US1] **Integration test that the accounting state is bounded by connections, not minutes**: ten connections driven through one minute and ten driven through sixty produce the same row count in `usage_connections` (SC-017, FR-010). The naive implementation passes every other test in this phase and this one fails at 43.2 million rows a month
- [ ] T033a [P] [US1] **Integration test that an unrefused report is the only report that counts.** Read the environment's figure, POST a report with no credential and with a valid API key, and read the figure again: `401`, `403 wrong_credential_type`, and the figure numerically unchanged (SC-010, FR-011). T017 proves the credential resolves; this proves a refusal changed nothing, which is the property a billing route actually owes
- [ ] T033b [US1] **Cover the new repository branches here, not in Phase 8.** `services/api/src/db/repository.ts` is ratcheted at branches 90 / functions 100 / lines 99 / statements 97, and `vitest.coverage.config.mts` records that chapters 3.5 and 3.6 each turned it red by adding operations without tests — 3.5 fell from 85.91% to 78.22% (R23). Measure after T025–T029 and write the tests the number asks for
- [ ] T033c [US1] Add ratchet entries to `vitest.coverage.config.mts` for `services/api/src/quotas/credit.ts` and the pure half of `services/gateway/src/meter.ts`, pinned at what they achieve, with the reason each earns — the convention chapter 3.6 set for `disable.ts` and 3.8 set for `bucket.ts` (R23)
- [ ] T033d [US1] **Cover `meter.ts` from in-process unit tests, not from the spawned ones.** A child process's coverage is not attributable in the coverage lane, which is exactly how chapter 3.5 lost 7.69 points of branch coverage. T040b and T041 spawn a gateway and stay spawned; the logic they exercise is covered on a driven clock in `meter.test.ts` (R23)
- [ ] T033e [P] [US1] **The FR-TEN-05 test constitution I requires**, in `services/api/src/internal/usage.itest.ts`. Every endpoint this series adds carries one — `test-event.itest.ts:481`, `backfill.itest.ts:155`, `webhooks.itest.ts:135`, `signup.itest.ts:247` — and the principle says the suite "MUST attack every endpoint with foreign IDs on every build. A build that fails this suite MUST NOT ship." Test the two halves `contracts/metering.md` §1 names: a valid API key and a valid end-user token are both refused before the body is read, and a report naming a different environment for an existing `connection_id` is refused with 409
- [ ] T033f [US1] **Say in the test's comment what is deliberately not prevented**: a platform caller may write usage for any environment, because that is what a platform credential is. Chapter 3.5 added the first platform-credentialled routes and left no `dispatch.itest.ts` in `services/api/src/internal/` at all — the precedent is silence, and silence about an isolation property is what constitution I calls a configuration mistake
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
- [ ] T039 [US2] Implement R20's decision — a report naming an unseen connection is accepted as that connection's first, because the api is never told when a connection opens, so "unknown" and "first" are the same state — and write the reasoning into the controller's comment. The specification asked for this decision in the plan; the first analysis pass found the plan had not made it, and R20 now does
- [ ] T040 [US2] **Give the gateway a graceful shutdown, because it has none.** `serve()` returns a bare `node:http` Server, nothing calls `server.close()`, and only the dispatcher installs signal handlers — so the `server.on("close")` path in `main.ts` never runs and the flush four documents promised had no mechanism (R11, FR-031). Install SIGINT and SIGTERM handlers in the gateway's `main.ts` in the dispatcher's shape (`services/dispatcher/src/main.ts:313`). **Only the wiring goes in `main.ts`** — it is excluded from coverage by policy (`**/main.ts`), so any flush logic that follows the handler in there becomes unmeasurable. The flush itself lives in `meter.ts`
- [ ] T040a [US2] Flush a final report from `sessions.close()`, and **make it async** — `close: () => void` today, and a flush that is not awaited is the same non-guarantee one line further down. The signal handler awaits it before `process.exit(0)` (FR-008, FR-031)
- [ ] T040b [P] [US2] Integration test the signal path: send the spawned gateway SIGTERM with a connection open and confirm its minutes are recorded after the process has exited (SC-023). Distinct from T041, which sends SIGKILL and asserts the opposite
- [ ] T040c [US2] **Build the harness T041 and T040b need.** Both gateway integration suites spawn **the api** as a child (`session.itest.ts:116`, `limits.itest.ts:124`) and run the gateway **in-process** via `attachSessions` — so there is no gateway process to signal or kill. Spawn `services/gateway/dist/main.js` as a child and copy the existing spawn-and-wait-for-healthz shape rather than inventing a second one. **`meter.itest.ts` then runs two children** — an api and a gateway — plus a socket client: wire the gateway child's `RELAY_API_URL` to the api child's ephemeral port, and pass `RELAY_INTERNAL_CREDENTIAL_GATEWAY` so its reports authenticate (R24)
- [ ] T041 [US2] Integration test the crash in `services/gateway/src/meter.itest.ts`: **SIGKILL** the spawned gateway with a connection open, confirm the figure advanced by no more than one interval, then **read it again ten intervals later and confirm it is identical** (SC-005, FR-008). The second read is the assertion — the first shows the loss is bounded, the second shows nothing is still billing for a socket nobody holds
- [ ] T042 [P] [US2] Integration test that a failing report path closes no socket, refuses no connect and fails no send, with every report forced to error (SC-019, FR-012)
- [ ] T043 [P] [US2] **Test that there is no queue for open connections.** Force every report to fail and assert the gateway retains nothing for a connection that is still open — its next report carries the same total plus what accrued, so there is nothing to keep (R3). A buffer of open-connection reports means the delta protocol crept back in
- [ ] T043a [P] [US2] **And test that there IS one for closed connections, bounded.** Force every report to fail, close a connection, then let a report succeed and confirm its minutes arrive; separately, exceed the retention cap and confirm the discard is logged and counted rather than silent (FR-029, R19). The two halves of this pair are the exception R19 narrows R3 with, and a test that only asserted "no buffer" would forbid the fix T023b makes

**Checkpoint**: every failure mode in `contracts/metering.md` §5 has a test, including the one that loses minutes.

---

## Phase 6: User Story 3 — The cap brakes the thing it meters (Priority: P2)

**Goal**: at or above the hard cap, new connections are refused with the quota code; everything already working keeps working.

**Independent test**: set a cap below usage, watch the api answer 402 and the client receive an error frame then close 4008, with a socket opened before the breach still receiving sixty seconds later.

- [ ] T044 [US3] Write the connect-time quota read in `services/api/src/db/repository.ts`: `environments` left-joined to `usage_periods` on two primary keys, one round trip, early exit when nothing is configured. `environmentLimits` is **not** extended — chapter 3.10's H2 refused that and its second caller is this same path (R7, FR-025)
- [ ] T045 [US3] Raise `QuotaExceededError` for `connection_minutes` in the connect path and **catch it in `services/api/src/internal/session.controller.ts`, rethrowing as an `HttpException` that names `quota_exceeded` with status 402** — the shape `messages.service.ts` already uses. Not left to the filter: `ProtocolErrorFilter` is `@Catch()`-all, infers a code for four statuses, and renders everything else as `internal_error`, which is chapter 3.10's H3 arriving a second time (FR-016)
- [ ] T046 [US3] Add the fourth outcome to `Authentication` in `services/gateway/src/auth.ts` and update its comment from "Three outcomes, not two" to four. A 402 today becomes `ApiError` → `unavailable` → close 1011, which tells the client we are broken and that retrying helps, and is wrong about both (R6)
- [ ] T047 [US3] Map `402` in `services/gateway/src/api-client.ts`'s `session()` beside the `401 || 403` branch, distinctly from both — refused and unavailable are already taken and neither fits
- [ ] T048 [US3] Refuse the connection **in the protocol's own vocabulary**, per `contracts/metering.md` §2b: complete the handshake, send an `error` frame carrying `quota_exceeded`, the figures and the resume date, then `close(4008)`. This is the 4001 path's shape for the 4001 path's reason — EIR-WS-06 asks for a close code on quota exhaustion, and a close code needs a socket to arrive on (FR-030, R21). **`refuseUpgrade` is not extended**: its raw 429 stays chapter 3.8's, for chapter 3.8's refusal
- [ ] T048a [P] [US3] Register `quota_exceeded` in `ERROR_CODES` in `packages/protocol/src/codes.ts`. The frame schema types `code` as `z.string().min(1)` so nothing forces it; the registry is the documented vocabulary and `codes.test.ts` enforces its uniqueness, which is why chapter 3.2 put `wrong_credential_type` there rather than inline
- [ ] T048b [US3] **Invert chapter 3.8's absence test.** `services/gateway/src/session.test.ts:929`, "STILL emits close code 4008 from nowhere (quickstart V7)", greps four gateway sources for `close(400[89])` and asserts no match — written by 3.8 saying "quotas are a later chapter". This is that chapter. It becomes: 4008 IS emitted, 4009 still is not, and the self-check that makes it honest — "a grep that can only pass is not a check" — survives on 4009. Drop the stale "quickstart V7" from the name, which is 3.8's numbering. Two other files cross-reference this test — `packages/test-harness/src/bait-size.test.ts:14` calls it the proof that "close code 4008 is emitted by nothing", which stops being true, and `no-trigger-in-migrations.test.ts:34` calls it the precedent for proving absence, which survives on 4009. Update the first. Two more numbers in this chapter's own artifacts were wrong for the same reason and are fixed in R15, R16, R21 and R22: a count living in a second place while only the first place was edited
- [ ] T049 [P] [US3] Integration test the api's half off the wire: `POST /internal/session` answers `402` with `quota_exceeded`, four fields, and **no `Retry-After`** (FR-015, FR-016). Read the response, not a log line
- [ ] T049a [P] [US3] Integration test the client's half off a **real socket**: the handshake completes, an `error` frame arrives naming the dimension and the resume date, and the close code is `4008` (SC-022, FR-030). A test that asserted only the close code would pass against a refusal that told the client nothing about when to come back
- [ ] T050 [P] [US3] Integration test the degradation: a connection opened before the breach is still open and still receiving sixty seconds later, in the same test and against the same environment as the refused connect (SC-006, FR-017)
- [ ] T051 [P] [US3] Integration test that a REST send and a history read both succeed while the connection-minutes cap is breached (SC-007, FR-018)
- [ ] T052 [P] [US3] Integration test the two configuration edges: a cap of zero refuses every connect, and no cap configured accepts every connect while still recording the minutes (FR-014, US3 scenarios 5 and 6)
- [ ] T053 [P] [US3] Integration test that raising the cap above usage restores connecting on the next attempt, with no restart (SC-008, FR-020)
- [ ] T054 [US3] Integration test that a connection open past the cap **keeps accruing**, and write the overshoot bound into the code comment that owns it: `(connections open at the crossing) × (minutes until each closes) + one reporting interval`, with the right-hand side having no numeric ceiling (FR-017, FR-019)
- [ ] T055 [US3] Add `services/api/src/internal/session.perf.itest.ts`, the connect-path performance test T065 and quickstart V8 both name, so Phase 8 measures a committed thing rather than an ad-hoc script

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
- [ ] T060 [P] [US4] Mailpit integration test: crossing 50%, 80% and 100% produces exactly three emails for the connection-minutes dimension in a period, read out of the mail server rather than asserted on a send call — **scoped to the recipient this test created** (SC-009, FR-022, FR-032). Mailpit is shared by the whole lane, and "exactly three" counted across every suite's mail is a claim about the lane
- [ ] T060a [US4] **Do not copy chapter 3.10's drain assertion.** `quotas.itest.ts:476` reads `expect(await relay().drainOnce()).toBeGreaterThan(0)`, which is true whether it drained this test's row or a neighbour's. Assert the rows this test wrote were delivered, by id (FR-032, R22)
- [ ] T061 [P] [US4] Mailpit integration test: re-crossing an already notified threshold sends nothing, and the thresholds are notifiable again after the period rolls over (FR-022)
- [ ] T062 [P] [US4] Integration test that one report crossing two thresholds notifies both (FR-023). A cap of 4 with four minutes crosses three thresholds, because 80% of 4 is 3.2 — chapter 3.10 got this expectation wrong twice
- [ ] T063 [P] [US4] Integration test that a soft threshold with no hard cap emails and refuses no connect (SC-020, FR-021)

- [ ] T063a [US4] **Add `drainQuotaNotifications` to the restricted-import list** in `eslint.config.mjs`, beside the six functions already there. Chapter 3.10 added a seventh function of the same kind and listed it in neither the lint rule nor `exempt.ts`, whose comment says the two "MUST AGREE" (R22, FR-027). **Say in the task's commit what this does not buy**: this chapter's tests reach the drain through `createQuotaRelay`, and the rule's own comment admits it cannot see an indirect call. T060a is the half that protects the chapter
**Checkpoint**: FR-RTL-05 is closed on all three dimensions.

---

## Phase 8: Verification

- [ ] T064 **The guard's prediction.** Run the lane against a freshly baited database and record every refusal into `captured-output.md`, with the count and whether any names `usage_connections`, `usage_periods` or `quota_notifications`. Confirm `git diff --stat packages/test-harness/src/exempt.ts` is empty (SC-014, R5). If a file does need an exemption, it is named in `exempt.ts` **with the tables it needs** and in the matching lint ignores list, and the chapter says which global operation required it (FR-027). A refusal here is the interesting result, not a failure. **And record what the run does not prove** (SC-014): the guard watches five tables, none of them a usage or notification table, so silence about them means nobody is looking (R5a, R22)
- [ ] T065 **Measure the connect path against T004a**, at 1-, 8- and 32-way concurrency, with `EXPLAIN (ANALYZE, BUFFERS)` for the added read. Record both in `captured-output.md`. Index lookups on two primary keys, not a scan (SC-012, FR-025). If the number is bad, instrument before changing anything — chapter 3.10 made two code changes chasing a warm-up artefact
- [ ] T066 **Count the places** the third dimension had to be named — the count is the measurement, so do not carry R15's prediction into the counting; R15 has already been wrong once about which places cost anything, having charged for a type alias that widens itself and not for the ternary beside it — and write the number into `chapter-notes.md` beside chapter 3.10's written prediction of "a new key plus a one-line constraint change", quoted from `0009_quotas.sql` and `quotas/config.ts` (SC-013, FR-024). A higher number is the result
- [ ] T067 Run `pnpm coverage` and confirm every per-file ratchet holds, and that the entries T033c added are met. Where a ratchet moves, record the before and after figures rather than the direction
- [ ] T068 **Twenty consecutive integration runs**, recording exit code, wall-clock and test count for each into `baseline.txt` (SC-014). `failing-files=0` beside `exit=1` is interference, not a defect — a real failure names a test. Do not edit source and do not run a concurrent `turbo run test --force` while the battery is running: chapter 3.10 invalidated two of its three attempts that way, once by editing source mid-battery and once by letting `nest build` rewrite `dist/` under a running import
- [ ] T069 [P] **Traceability pass.** Confirm every `FR-0xx`/`SC-0xx` id in code and comments introduced by this chapter reads as a feature-local id with its spec named, and **check every altered line against `part3-ch10`** before committing. Chapter 3.10's equivalent pass rewrote six pre-existing comments belonging to chapters 3.5, 3.6 and 3.9 while fixing sixteen of its own
- [ ] T070 [P] **Credential scan, recording the patterns searched and not only the verdict.** Grep the captured transcripts, `captured-output.md`, `baseline.txt`, both locale pages and every fence for: `rk_svc_`, `rk_live_`, `rk_dev_`, `rk_svc_local_development_credential_0000`, `RELAY_INTERNAL_CREDENTIAL`, `RELAY_WEBHOOK_SECRET_KEY`, `Bearer ey`, and any 32-or-more-character hex or base64 run. **This chapter gives the gateway a credential and the quickstart shows an `Authorization: Bearer rk_svc_…` header**, so the compose default is the specific thing most likely to be pasted into a published page. Record the pattern list and the file count searched
- [ ] T071 Re-run every gate: `pnpm turbo run test --force`, `pnpm test:integration`, `pnpm coverage`, `pnpm lint`, and the tutorial's `check:fences`, `check:docs`, `lint` and `build`. Record exit codes, not grep output

**Checkpoint**: every measurable outcome in spec.md has a number, including the ones that came out wrong.

---

## Phase 9: The chapter, in English — and the size gate

- [ ] T072 Write `specs/032-chapter-3-11/chapter-notes.md`: what the plan said, what shipped, and where they disagreed. Written before the page, so the page has something to be honest about
- [ ] T073 Create `relay-tutorial/app/(en)/part-3/chapter-11/counting-a-connection/figures.ts` — the bucket diagram, the cumulative-versus-delta comparison, and the state transition from `data-model.md`, with **at least one in each half of the chapter** (`docs/07-tutorial-plan.md` §2: two to four per chapter, placed at key-concept moments, ≥1 per half). 3.10 shipped four and 3.9 three. **The §5 loss table is prose, not a figure** — the rule counts diagrams separately from specimen fences and says nothing about tables, and a four-column table of failure modes reads better inline than in a `Figure` frame
- [ ] T074 Write `relay-tutorial/app/(en)/part-3/chapter-11/counting-a-connection/page.mdx`, with the series' recurring boxes: `<Why>` linking each decision to its requirement or ADR, **at least one `<Trap>`** — a counted box class per `docs/07-tutorial-plan.md` §2, and this chapter has three earned candidates in the socket that counts zero, the flush with no shutdown path, and the drain both guards miss — a `<Checkpoint>`, and a `<SkipAhead>` if the phase order gives a natural place to stop. 3.10 shipped 5 Why / 4 Trap / 1 Checkpoint; 3.9 shipped 3 / 3 / 1 / 1. The spine: messages and users were already rows, a connection is not, and the only process that can see one owns no tables and — until this chapter — no identity. Say out loud that reports carry totals and why that deletes the retry buffer
- [ ] T075 The page must state the overshoot bound with its open right-hand side (FR-019), the counted cost of a third dimension against chapter 3.10's written prediction (FR-024), and the answer to `docs/04-srs.md`'s open question 4 with the rounding rule and who it charges (FR-028)
- [ ] T075a In the same `page.mdx`, address in one sentence what a shipped chapter said about this. Chapter 3.2's fenced test comment reads "After chapter 3.2 neither of them holds a secret". In context it means *signing* secrets and stays defensible, but the bare sentence stops being true the moment the gateway holds `rk_svc_…`. Say which kind of secret the gateway still does not hold, rather than letting a reader who remembers 3.2 catch the chapter out
- [ ] T076 **Count the finished page**: prose words excluding fences, front matter and figure captions, the fence count, and **the recurring boxes by class** — `<Why>`, `<Trap>`, `<Checkpoint>`, `<SkipAhead>` — all read from the page. Expected 2,000–4,000 words and at least one `<Trap>` (SC-015). Chapter 3.10's estimate ran 18% high against the page it produced
- [ ] T076a **If the count exceeds 4,000, split at Phase 7's seam** and renumber: the notification story and the cap become their own chapter, the isolation gauntlet moves from 3.12 to 3.13, and `docs/07-tutorial-plan.md` and `relay-tutorial/lib/tutorial.ts` are updated together. Three of Part 3's four splits were discovered mid-chapter; this is the instrument that catches the fifth

**Checkpoint**: the page exists and has been counted rather than estimated.

---

## Phase 10: Publication in both locales

- [ ] T077 **Write the chapter's fences**, routing each change to where it belongs: a file this chapter discusses gets a diff fence on the page; a change the chapter does not teach goes to `relay-tutorial/fences/post-series.md`. Twenty-one files carry 95 existing fences between them (T006), with 5 further entries in `post-series.md` — the four build-gate files and `repository.ts`, and the chain applies hunked diffs — each hunk's pre-image must appear in the predecessor state exactly once
- [ ] T077a **Decide `compose.yaml` and `turbo.json` routing explicitly.** The chapter does discuss the gateway's new credential, so both belong on the page rather than in `post-series.md`. Chapter 3.10 sent its `turbo.json` change to `post-series.md` because it discussed no part of it; the test is what the chapter teaches, not which file changed
- [ ] T077b **Fence the comment chapter 3.8 got right and this chapter falsifies.** `services/api/src/limits/rate-limit.middleware.ts` says the gateway "forwards the END USER's token on all three of its api calls" and that "Only the dispatcher carries the platform credential". There is a fourth call and a second holder now. The middleware's *behaviour* does not change — `operationsFor` returns `[]` for anything outside `/v1/`, so the report route was never counted — so this is a comment diff, and the chapter should say that finding a shipped chapter's sentence go stale is what the fence chain is for
- [ ] T077c **Fence the two files the second analysis pass added to the surface**: `packages/protocol/src/codes.ts`, where `quota_exceeded` joins `ERROR_CODES` and 4008 stops being decorative, and `services/gateway/src/session.test.ts`, where 3.8's absence assertion inverts. Six fences on the test file alone — the chapter should show the inversion, because a shipped test that says "quotas are a later chapter" being answered by the later chapter is the fence chain doing its job
- [ ] T078 Run `pnpm check:fences` and fix every divergence. This is the cheapest place to find a hunk written against the wrong pre-image
- [ ] T079 Write the Vietnamese mirror at `relay-tutorial/app/(vi)/vi/part-3/chapter-11/counting-a-connection/`, with every fence **byte-identical** to its English counterpart under the same title — the chain's MIRROR property. **Figures are the ungated half**: `docs/07-tutorial-plan.md` §2 says Vietnamese editions translate narrative labels while requirement, driver and ADR identifiers stay English, and `check:fences` checks fences only — nothing verifies a figure label, so this one is read rather than run
- [ ] T080 Register the chapter in `relay-tutorial/lib/tutorial.ts`: status from `forthcoming` to published, and the `readerProduces` line checked against what the chapter actually produced
- [ ] T081 Run the tutorial's full gate set: `check:fences`, `check:docs`, `lint`, `build`. **Leave the author's uncommitted prose edits in other chapters alone** unless a code fence is involved

**Checkpoint**: the chain is byte-exact in both locales and no chapter has been made to lie.

---

## Phase 11: Close-out

- [ ] T082 Update `docs/07-tutorial-plan.md`'s 3.11 row and its Part 3 narrative with what this chapter turned out to be against what the plan said — including the word count against the estimate, and R5a's finding about chapter 3.10's guard coverage
- [ ] T082a [P] Revisit chapter 3.2's standing limitation, in `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx` and its `(vi)` mirror. Its published prose says "**Service-to-service credentials on the internal hop.** The gateway and api still trust the network between them, exactly as chapter 2.5 recorded." One of the gateway's four calls now presents a credential of its own, so the entry is narrower than it was — narrow it in print rather than leaving a shipped chapter overstating what is still open
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

**Twelve orderings that matter:**

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
- **T023a before T030a.** The test for the socket that lives and dies between two
  reports fails against a registry-only meter, which is the point — but it fails
  for a reason the fix has to exist to remove, not as a discovery.
- **T023b before T043a.** T043 asserts there is no buffer and T043a asserts there
  is a bounded one for closed connections. Written in the other order, the first
  looks like the whole rule and the second like a contradiction.
- **T040c before T040b and T041.** Both send a signal to a gateway *process*, and
  there is no gateway process in the suite today — the existing integration files
  spawn the api and run the gateway in-process. The harness is the prerequisite,
  not a detail of the tests.
- **T048a before T048.** The frame's `code` is `z.string()`, so an unregistered
  code compiles and ships. Registering it first makes `codes.test.ts` the thing
  that notices, which is what a vocabulary registry is for.
- **T033b inside Phase 4, not Phase 8.** `repository.ts`'s ratchet went red in
  chapters 3.5 and 3.6 for the same reason, and both times the fix was tests that
  should have been written beside the code. Measuring in Phase 8 finds it after
  four more phases are stacked on top.
- **T060a with T060, not after it.** The weak assertion is the one that ships,
  because it passes. Writing the scoped version first means never having the
  green-for-the-wrong-reason version in the history.

## Parallel opportunities

- **Phase 1**: T003 and T006 alongside T001, T002 and T004a.
- **Phase 2**: T007/T008 (the minute), T013 (the protocol) and T014 (the credit
  arithmetic) are three files with no shared state. T009's migration is
  independent of all three. T012 and T012a are one file and go in that order.
- **Phase 3**: T017 alongside T018 and T019 — a test, a compose file and a turbo
  file.
- **Phase 4**: T030, T030a, T031, T032, T033, T033a and T033e are seven independent
  integration files once T027 and T028 exist. T033c is a config file and parallel
  with all of them; T033b and T033d are not — both wait on a coverage run, and
  T033f is a comment on T033e. T023a and T023b are not parallel
  with T023 — all three are `meter.ts`.
- **Phase 5**: T035, T036, T037 and T042 are independent. T043 and T043a are one pair in one file and go in that order, and T040b and T041 both wait on T040c.
- **Phase 6**: T048a is independent of everything in the phase and can go first. T049, T049a and T050 to T053 are independent once T044 to T048b are in.
- **Phase 7**: T058/T059 (the copy) run alongside T060 to T063 (the Mailpit
  reads), and both need T057. T063a is an eslint config change, parallel with
  everything.
- **Phase 8**: T069 and T070 alongside T064 to T068.

## Implementation strategy

**MVP is Phase 4.** A connection-minute recorded per environment per month, from
a service that owns no tables, is the chapter's subject and closes the metering
half of FR-RTL-05. Stopping there would leave the dimension uncapped, which is a
smaller feature and not a wrong one.

**Then Phase 5**, because the failure modes are the chapter — and note that one
of them moved into Phase 4 during the first analysis pass. The socket that lives
and dies between two reports looked like a failure mode and is a *counting* bug:
under a registry-only meter it records zero, so churn is free and the unit chosen
to charge churn charges nothing.

The rest of Phase 5 stands. Metering an event is
a write in the transaction that caused it; metering a duration is a claim from
another process about time that has already passed, and every way that claim can
go wrong shows up as money. A chapter that shipped Phase 4 and not Phase 5 would
have taught the easy half.

**Phase 6 next**, because FR-RTL-05 says enforce, not meter.

**Phase 7 last, and separable.** It is the fourth telling of the outbox and for
this chapter it is nearly all reuse — the right thing to cut if the page runs
long, because a reader who stops before it has the chapter's subject.
