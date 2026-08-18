# Tasks: Tutorial Chapter 3.6 — "When to stop trying"

**Feature**: `specs/027-chapter-3-6` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: a published chapter in two locales, and the platform state it
fences. The platform work comes first because a chapter cannot fence code that
does not exist.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story from spec.md this task serves
- Setup, Foundational and Polish tasks carry no story label

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to
`relay-tutorial/`, spec paths to `specs/027-chapter-3-6/`.

---

## Phase 1: Setup

- [ ] T001 Record provenance in `specs/027-chapter-3-6/baseline.txt`: the submodule commits and tags this chapter starts from, confirming `relay-platform` is at `part3-ch5` and both pins match their HEADs
- [ ] T002 Record the pre-change baseline in `specs/027-chapter-3-6/baseline.txt` — unit and integration counts per package, the four coverage figures, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output
- [ ] T003 [P] Record the site baseline in `specs/027-chapter-3-6/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the fence count and locale count the chain reports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Blocks every user story.** The columns and the stream grammar are read by all
three pieces.

- [ ] T004 Write `relay-platform/services/api/migrations/0007_webhook_attempts.sql` by hand — four columns on `webhook_endpoints` and the `webhook_disable_notifications` table per `data-model.md` — forward-only, no destructive statement (ADR-16)
- [ ] T005 Review `0007_webhook_attempts.sql` before running it and record the disposition in a header comment: nullability, the absence of a default that would backfill a failure run onto healthy endpoints, and the index list (chapter 2.1's rule, after a generated migration was applied unread)
- [ ] T006 Amend `relay-platform/services/api/src/db/schema.ts`: `failureRunStartedAt`, `failureRunAttempts`, `disabledAt`, `disabledReason` on `webhookEndpoints`, and the `webhookDisableNotifications` table with its `environment_id` index
- [ ] T007 [P] Amend `relay-platform/packages/protocol/src/internal.ts` with the analytics subject grammar — `ANALYTICS_STREAM`, `ALL_ANALYTICS_SUBJECT`, `analyticsSubjectFor(domain, action, environmentId)` — beside the two grammars already there (research R4)
- [ ] T008 [P] Extend `relay-platform/packages/protocol/src/internal.test.ts` with cases for `analyticsSubjectFor`, including that it refuses an environment id that is not a UUID
- [ ] T009 Amend `relay-platform/services/api/src/outbox/jetstream.publisher.ts` with `ensureAnalyticsStream` — `analytics.>`, 7-day `max_age`, `discard: old` — reusing the `ensure` parameter chapter 3.5 added rather than adding a second mechanism

**Checkpoint**: migrations apply, `pnpm typecheck` exits 0, no behaviour has changed yet.

---

## Phase 3: User Story 1 — Every attempt leaves a record (Priority: P1) 🎯 MVP

**Goal**: a customer's integration engineer can be shown what happened to each
attempt, without the platform consulting logs.

**Independent test**: drive an endpoint through success, failure and timeout;
confirm one event per attempt carrying timestamp, status, latency and error, and
that a timeout is recorded with no status rather than omitted.

- [ ] T010 [US1] Write `relay-platform/services/api/src/webhooks/analytics.ts`: `publishAttempt(publisher, logger, record)` shaping the payload in `contracts/attempts.md`, with the subject built from the protocol grammar
- [ ] T011 [US1] Make the publish swallow its own failure in `analytics.ts` — log and return, never throw — so a caller cannot accidentally make an analytics outage a delivery outage (contract invariant 4)
- [ ] T012 [US1] Amend `relay-platform/services/api/src/internal/dispatch.controller.ts` to call `publishAttempt` **after** `recordAttemptOutcome` returns, outside its transaction, passing the `latency_ms` the seam has carried and discarded since 3.5 (FR-003, research R5, R6)
- [ ] T013 [P] [US1] Write `relay-platform/services/api/src/webhooks/analytics.test.ts`: the payload shape, that a timeout produces no `status` field rather than a zero, and that no payload, secret, signature or header can appear in any field (FR-004, SC-006)
- [ ] T014 [US1] Write `relay-platform/services/api/src/webhooks/attempts.itest.ts` — one event per recorded outcome against a real broker, all four identifiers present, and the subject's environment matching the payload's (FR-002, SC-001, contract invariants 1, 2, 3)
- [ ] T015 [US1] Add the case to `attempts.itest.ts` that matters most: with the `ANALYTICS` stream absent or the broker unreachable, the outcome is still recorded and the response to the dispatcher is unchanged (contract invariant 5, quickstart V3)
- [ ] T016 [US1] Add a second-environment case to `attempts.itest.ts` confirming no attempt event crosses a tenant boundary (FR-018)
- [ ] T017 [US1] Parameterise `relay-platform/scripts/stream-info.mjs` to take a stream name, defaulting to `EVENTS` — quickstart V2 inspects `ANALYTICS` and the script currently hardcodes `"EVENTS"`, so the step would report on the wrong stream and pass
- [ ] T018 [US1] Run `pnpm coverage` and confirm `analytics.ts` is measured and every ratchet still passes — checked here rather than at the end, because 3.5 deferred it and found four thresholds red with the chapter otherwise finished (research R11)

**Checkpoint**: attempts are published and the delivery path is provably independent of them.

---

## Phase 4: User Story 2 — An endpoint failing for an hour is switched off (Priority: P2)

**Goal**: an endpoint that has returned nothing but failures for over an hour
stops being delivered to, once, with the reason recorded.

**Independent test**: drive an endpoint into continuous failure past the
threshold; confirm one disablement, one notification, deliveries stopped, and a
second healthy endpoint in the same environment still receiving.

- [ ] T019 [P] [US2] Write `relay-platform/services/api/src/webhooks/disable.ts`: `shouldDisable({ runStartedAt, runAttempts, now })` and the two constants `DISABLE_AFTER_MS = 1h` and `DISABLE_MIN_ATTEMPTS = 5`, pure and free of database, clock and broker
- [ ] T020 [P] [US2] Write `relay-platform/services/api/src/webhooks/disable.test.ts` covering research R3's arithmetic: 5 attempts inside the hour disables, 4 does not, an hour with 4 attempts does not, a run of zero length does not, and a clock that moves backwards yields no negative window
- [ ] T021 [US2] Amend `recordAttemptOutcome` in `relay-platform/services/api/src/db/repository.ts` to open or extend the failure run on a failed outcome and clear it on a delivered one, taking `SELECT … FOR UPDATE` on the endpoint row inside the existing transaction (FR-006, research R2)
- [ ] T022 [US2] Add the disable to `recordAttemptOutcome` in `relay-platform/services/api/src/db/repository.ts`: when `shouldDisable` holds, set `enabled = false`, `disabled_at`, `disabled_reason`, and write one `webhook_disable_notifications` row with `delivered_at` null, all in the same transaction (FR-007, FR-011)
- [ ] T023 [US2] Make the disable update in `relay-platform/services/api/src/db/repository.ts` carry `enabled = true` in its predicate so a second disable updates zero rows — the at-most-once rule enforced by the statement rather than by a check somebody has to remember (FR-008, contract invariant 8)
- [ ] T024 [US2] Resolve the organisation at write time in `relay-platform/services/api/src/db/repository.ts` through `environments.application_id → applications.organisation_id`, and store it on the notification rather than joining for it later (data-model.md)
- [ ] T025 [US2] Write `sweepDisabledEndpoints` in `relay-platform/services/api/src/db/repository.ts` — one statement finding endpoints whose run has outrun the hour, disabling and notifying them by the same path T022 uses
- [ ] T026 [US2] Amend `relay-platform/services/api/src/webhooks/delivery-relay.ts` to call the sweep from the loop it already runs, behind `RELAY_DISABLE_SWEEP` (default on), with one log line reporting how many endpoints it disabled (research R1)
- [ ] T027 [US2] Add `--watch-disable` to `relay-platform/scripts/webhook-walk.mjs` — poll the endpoint row and print the failure run growing and the disablement when it lands. Quickstart V4 already invokes this flag; without it the chapter's headline demonstration cannot be run
- [ ] T028 [US2] Expose `disabled_at`, `disabled_reason`, `failure_run_started_at` and `failure_run_attempts` on the endpoint representation in `relay-platform/services/api/src/webhooks/webhooks.controller.ts` so a customer can tell a platform disablement from their own (FR-009)
- [ ] T029 [US2] Extend `relay-platform/services/api/src/webhooks/deliveries.itest.ts` with the run lifecycle: opens on failure, grows, clears on success, and an endpoint succeeding once an hour is never disabled (SC-003, contract invariants 6, 7)
- [ ] T030 [US2] Add the disablement cases to `deliveries.itest.ts`: exactly one notification, no second disable on further failures, no deliveries created for a disabled endpoint, and pending deliveries for it not attempted (FR-010, SC-002, contract invariants 8, 9, 11). Include the concurrent case: two overlapping outcome reports against one endpoint produce one disablement and one notification, which is what `FOR UPDATE` and the `enabled = true` predicate are for
- [ ] T031 [US2] Add the isolation case to `deliveries.itest.ts` — disabling one endpoint changes nothing for a second endpoint in the same environment or another (FR-012, SC-004, contract invariant 10)
- [ ] T032 [US2] Write the sweep's own test in `deliveries.itest.ts`: an endpoint whose run has outrun the hour with no further attempts arriving is disabled by the sweep alone, which is the case an outcome-only check never reaches (contract invariant 12, research R1)
- [ ] T033 [US2] Run `pnpm coverage` and pin `services/api/src/webhooks/disable.ts` at 100 branches in `relay-platform/vitest.coverage.config.mts` — it is the chapter's idempotency logic and constitution VI names that at 100% — then raise the `repository.ts` ratchets to what this phase achieves, or write the missing tests — the file had between 0.28 and 0.51 of a point of headroom before this phase added five operations to it (research R11)

**Checkpoint**: FR-WHK-07 is met except for sending the email, and the schema says so.

---

## Phase 5: User Story 3 — Proving it works again (Priority: P3)

**Goal**: a customer can establish a repaired endpoint works before re-enabling it.

**Independent test**: disable an endpoint, send a test event, see it delivered and
recorded and marked synthetic, then re-enable and confirm the run is cleared.

- [ ] T034 [US3] Add `sendTestEvent(endpointId)` to `relay-platform/services/api/src/webhooks/webhooks.service.ts` — one endpoint, one attempt, no retry schedule, delivered even when disabled (FR-013, research R8)
- [ ] T035 [US3] Build the synthetic envelope in `webhooks.service.ts` with `type: "webhook.test"` and `test: true`, signed by the same path a real event takes so a success proves something about real deliveries (FR-014, FR-015)
- [ ] T036 [US3] Make the test event's outcome bypass the failure run entirely in `relay-platform/services/api/src/db/repository.ts`, so a failed test cannot push an endpoint toward disablement and a successful one cannot mask a real outage (contract invariant 13)
- [ ] T037 [US3] Add `POST /v1/webhook-endpoints/{id}/test` to `relay-platform/services/api/src/webhooks/webhooks.controller.ts` returning `delivered`, `status`, `latency_ms`, `error` and `event_id`, with a non-2xx from the customer reported as `delivered: false` rather than as an HTTP error (FR-016)
- [ ] T038 [US3] Amend the enable route in `webhooks.controller.ts` to clear all four columns in one transaction, so the hour is measured from the next failure (FR-017)
- [ ] T039 [P] [US3] Write `relay-platform/services/api/src/webhooks/test-event.itest.ts`: delivered to one endpoint only, delivered while disabled, marked twice, signature verified by an independent recipe, and the run untouched by its outcome (SC-005). Include an endpoint whose URL no longer resolves: `delivered: false` with an error, not a 5xx from our own API
- [ ] T040 [US3] Add the re-enable case to `test-event.itest.ts` — all four columns null afterwards, and a subsequent failure starting a fresh run rather than resuming the old one
- [ ] T041 [US3] Add the foreign-tenant case to `test-event.itest.ts`: a test against an endpoint in another environment answers 404, the same answer a missing endpoint gets

**Checkpoint**: the disable → repair → re-enable loop closes without a person editing the database.

---

## Phase 6: Verification

- [ ] T042 Run the sabotage battery per `specs/027-chapter-3-6/quickstart.md` V8 — five mutations, each reverted and the file verified byte-identical by `md5sum`, recording which test failed for each (SC-009)
- [ ] T043 Run the fourth sabotage against a **stopped broker**, because publishing inside the transaction keeps passing while the broker is healthy — the mutation proves nothing otherwise (quickstart V8)
- [ ] T044 Run both lanes and confirm every pre-existing suite passes unchanged in substance, recording the chapter-end counts in `specs/027-chapter-3-6/baseline.txt` (FR-018, SC-008)
- [ ] T045 Run `pnpm coverage`, confirm exit 0 with every ratchet intact, and record the four figures and the per-file numbers in `specs/027-chapter-3-6/captured-output.md`
- [ ] T046 Run quickstart V6 in both halves — sweep off, then sweep on — and capture both, because the first is what an outcome-only check ships and the second means nothing without it
- [ ] T047 Capture every transcript the chapter will quote into `specs/027-chapter-3-6/captured-output.md`: R1's timeline, the attempt event, the analytics-down demonstration, the disablement, the quiet-endpoint pair, the test event, and the coverage summary (FR-021)

---

## Phase 7: The chapter, in English

- [ ] T048 Write the English chapter at `relay-tutorial/app/(en)/part-3/chapter-06/when-to-stop-trying/page.mdx`: the record before the decision, why that order, and the two halves this chapter does not deliver (FR-001…FR-012, FR-005, SC-007)
- [ ] T049 Add the section to `page.mdx` that shows R1's measurement and what it changed — the attempt timeline, why an outcome-only check never fires for a quiet endpoint, and why the answer was a sweep in an existing loop rather than a new one (research R1)
- [ ] T050 Add the section to `page.mdx` that states the analytics trade in the same paragraph that introduces the attempt record: at-most-once, published after the commit, because a metering pipeline must not be able to stop a customer's webhooks (research R5, constitution III)
- [ ] T051 [P] Write `relay-tutorial/app/(en)/part-3/chapter-06/when-to-stop-trying/figures.ts` — the failure run as a state machine, the two triggers against the attempt timeline, and where the attempt event goes
- [ ] T052 Generate every fence from the real files rather than typing them, and confirm `pnpm check:fences` replays the chain onto `relay-platform` (FR-020)
- [ ] T053 Measure the battery on the published page and record it in `specs/027-chapter-3-6/battery.txt`, counting fences against research R10's 18–22 budget and confirming the SKIP AHEAD names `part3-ch6`
- [ ] T054 Traceability: confirm every `FR-*`/`NFR-*`/`ADR-*` the chapter cites resolves in `docs/`, and every table and column it names exists in `relay-platform/services/api/src/db/schema.ts`

---

## Phase 8: Publication in both locales

- [ ] T055 Translate the chapter to `relay-tutorial/app/(vi)/vi/part-3/chapter-06/when-to-stop-trying/page.mdx`, splitting prose from fences mechanically before translating anything and leaving every fence byte-identical (FR-019, translate-mdx §2.4)
- [ ] T056 [P] Translate `relay-tutorial/app/(vi)/vi/part-3/chapter-06/when-to-stop-trying/figures.ts` — mermaid labels only; participants, identifiers, table and column names stay English
- [ ] T057 Amend `relay-tutorial/lib/tutorial.ts`: 3.6 published, `translatedIn: ["vi"]`, with `readerProduces` in both languages describing what the chapter builds rather than what FR-WHK-06 and FR-WHK-07 promise in full
- [ ] T058 Verify publication of both routes: 200, the reading shell present, and the figures rendering as **SVG in a headless browser** (SC-010) — a page that returns 200 is not a page that is laid out, and 3.5 shipped three blank diagrams past a passing build (quickstart V10)
- [ ] T059 Run `pnpm check:fences` and confirm the Vietnamese fences mirror the English byte for byte and the locale count has risen

---

## Phase 9: Close-out

- [ ] T060 Amend `docs/07-tutorial-plan.md` if this chapter's scope moved, and confirm the Part 3 numbering it already carries still matches `relay-tutorial/lib/tutorial.ts`
- [ ] T061 Run quickstart V1–V10 end to end from `specs/027-chapter-3-6/quickstart.md`, reading exit codes rather than grepping output
- [ ] T062 Scan `specs/027-chapter-3-6/captured-output.md` and both published pages for leaked credentials — signing secrets, the encryption key, and internal credentials — recording the patterns searched rather than the conclusion alone
- [ ] T063 Write `specs/027-chapter-3-6/chapter-notes.md` from what happened rather than what was planned, including the budget-versus-actual fence count and what R1's measurement changed
- [ ] T064 Fix forward any defect this chapter exposes in an earlier chapter, in every locale that chapter has, and record it in `specs/027-chapter-3-6/chapter-notes.md`
- [ ] T065 Tag `relay-platform` as `part3-ch6` at the chapter-end commit, because the chapter's SKIP AHEAD tells readers that tag exists — 3.5 published that claim before the tag was created

---

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1 → Phase 2**: the baseline is measured before anything changes, or there is nothing to compare against
- **Phase 2 → Phases 3, 4, 5**: the columns and the subject grammar are read by all three stories
- **Phase 3 → Phase 4**: only loosely. The disable does not read the attempt event (research R5 — it reads columns), so US2 could be built first. US1 is first because it is smaller and because the chapter argues the record must exist before the decision.
- **Phase 4 → Phase 5**: US3 needs a disabled endpoint to test against
- **Phases 3–5 → Phase 6**: sabotage needs mechanisms to remove
- **Phase 6 → Phase 7**: the chapter quotes captured transcripts, so they must exist first
- **Phase 7 → Phase 8**: the translation mirrors an English page that must be final

### User story dependencies

US1 is independent. US2 is independent of US1 in code and dependent on it in
narrative. US3 depends on US2 for something to test.

### Within each story

Pure logic before the code that calls it (T019 before T021), the operation before
its test, and the coverage check last — T018 and T033 exist because 3.5 proved
that deferring them to the end finds four red thresholds with the chapter
otherwise done.

### Parallel opportunities

- **Phase 2**: T007 and T008 (protocol) run alongside T004–T006 (schema) — different packages
- **Phase 3**: T013 is independent of T014–T016; the unit test needs no broker
- **Phase 4**: T019 and T020 are pure and independent of everything else in the phase
- **Phase 5**: T039 can be written while T034–T038 are in progress
- **Phase 7**: T051 (figures) is independent of the prose tasks
- **Phase 8**: T056 (figures) is independent of T055 (page)

---

## Implementation Strategy

**MVP is Phase 3 alone.** With Phases 1–3, every delivery attempt is recorded on
the analytical path and the delivery path is provably independent of it. That is
FR-WHK-06's half, shippable and demonstrable without any of the disable work, and
it is the half the other two stories rest on.

Phase 4 is where the chapter earns its title. Phase 5 is the smallest of the three
and the only one that could be cut without leaving a requirement half-met — it was
accepted into scope as a modest widening, and research R10 names it as the thing
to check if the fence count approaches 19.

---

## Notes

**On the two triggers.** T026's sweep looks like belt-and-braces next to T022's
on-outcome check, and it is not. Research R1 computed the attempt timeline against
the one-hour window: one failing delivery attempts at +35m36s and then not again
until +2h35m36s, and if it dead-letters with no further events arriving the
endpoint is never disabled at all. T032 is the test for that case and it is the
one most likely to be dropped as redundant. It is not redundant; it is the only
test that covers the customer the requirement is actually about.

**On the fourth sabotage.** Moving the attempt publish inside the outcome
transaction keeps every test green against a healthy broker. T043 exists because a
mutation that cannot fail is not a check — the same lesson chapter 3.5 learned when
its "terminated, not retried" assertion turned out to be unfalsifiable at a 30-second
ack wait and a 2-second window.

**On the ratchet.** `repository.ts` sits at 89.51 branches against a ratchet of 89.
Phase 4 adds five operations to it. T033 raises the ratchet to what the work
achieves; it does not lower the ratchet to what the work happens to reach.

**On the fence budget.** Research R10 estimates 18–22, with test files and script
amendments counted — the categories 3.5's first two budgets omitted. That number
was itself wrong once: the first pass said 15–19 and had counted a file no task
touches while missing four that tasks do. T053 measures the actual count against
the corrected figure.
