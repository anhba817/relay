# Tasks: Tutorial Chapter 3.10 — "Quotas and what they cost"

**Feature**: `specs/031-chapter-3-10` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: a monthly quota that a cache flush cannot erase, a cap that
refuses sends without touching anything a tenant can read, and the outbox pattern
for the fourth time — plus the discovery that none of it needs a global operation.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story from spec.md this task serves
- Setup, Foundational, Verification, Publication and Close-out tasks carry no
  story label
- **A lettered id** (`T031a`) is a task inserted by an `/speckit-analyze` pass,
  numbered against the task it belongs beside. It may run *before* its base task
  where it is a prerequisite

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to
`relay-tutorial/`, spec paths to `specs/031-chapter-3-10/`.

---

## Phase 1: Setup & baseline

- [ ] T001 Record provenance in `specs/031-chapter-3-10/baseline.txt`: the submodule commits this chapter starts from, and confirmation that `relay-platform` is at `feature-030-global-operation-guard` with both parent pins matching their submodule HEADs
- [ ] T002 Record the pre-change platform baseline in `specs/031-chapter-3-10/baseline.txt` — unit and integration counts per package, coverage, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output. Feature 030 finished on **251 unit, 231 integration, 473 coverage at 89.08 / 82.35 / 89.25 / 90.58**, integration wall-clock 3m10.218s
- [ ] T003 [P] Record the site baseline in `specs/031-chapter-3-10/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the fence and locale counts the chain reports (165 files, 26 chapters at the last measurement)
- [ ] T004 **Run the integration lane three times and record every failure.** Feature 030's battery needed five attempts and three of the red runs were real defects, so a lane that is green three times is the precondition for measuring anything this chapter changes
- [ ] T004a **Re-measure the derive-on-read query the chapter will argue against** and record the `EXPLAIN (ANALYZE)` output in `baseline.txt`. Research R1 measured 1.189ms for one environment and 79.807ms for a whole-table sweep against 198,690 messages; the chapter quotes these numbers, so they must be this machine's rather than yesterday's
- [ ] T005 Fix forward, with its own commit, anything T004 finds that is not this chapter's work. A lane with a pre-existing intermittent failure cannot measure a new one

**Checkpoint**: the starting numbers exist and the lane is green for a known reason.

---

## Phase 2: Foundational — the period, the arithmetic, and the schema

**Blocking.** US1, US2 and US3 all depend on these. Pure functions and schema only; nothing observable yet.

- [ ] T006 [P] Write `services/api/src/quotas/period.test.ts` first: the calendar month in UTC, the boundary at midnight on the first, a timestamp inside the month mapping to the month's first day, and **a timestamp in a non-UTC local zone still mapping by UTC**. The last one is the test that catches a `date_trunc` without `at time zone`
- [ ] T007 [P] Implement `services/api/src/quotas/period.ts`: one exported function turning an instant into a period `date`. **One definition, imported by everything** — the migration's default, the repository's predicate and the relay's read all name this rather than repeating `date_trunc`
- [ ] T008 [P] Write `services/api/src/quotas/policy.test.ts` first: which thresholds an increase crosses. `40% -> 100%` crosses all three; `49% -> 51%` crosses one; `81% -> 82%` crosses none; a decrease crosses nothing; a quota of zero is 100% at usage zero
- [ ] T008a [P] **Include the case where the quota is null** in `services/api/src/quotas/policy.test.ts`. Unlimited crosses no threshold at any usage, and the function must say so rather than dividing by null — the branch that would otherwise appear as a crash in production and as full coverage in the ratchet
- [ ] T009 [P] Implement `services/api/src/quotas/policy.ts`: `thresholdsCrossed(before, after, quota)` returning the ascending list. Pure, no database, no clock
- [ ] T010 Write `services/api/migrations/0009_quotas.sql` per `data-model.md`: four nullable quota columns on `environments`, `usage_periods`, `usage_active_users`, `quota_notifications`
- [ ] T010a **Record in the migration why null is not zero**, the rule chapter 3.8's `0008_limit_policy.sql` established for the same reason on the same table. Null is no cap; zero refuses everything; an environment can be switched off deliberately, so they cannot share a representation (FR-006)
- [ ] T010b **Make `quota_notifications`'s unique constraint carry FR-015** in `services/api/migrations/0009_quotas.sql`, `(environment_id, period, dimension, threshold)`, and say so in the migration. At-most-one-email-per-threshold is then a schema property rather than a promise the writing code makes, and a concurrent double-crossing resolves to one row instead of two emails
- [ ] T010c **Record in `services/api/migrations/0009_quotas.sql` that `usage_periods.messages_sent` is `bigint` and why.** A cumulative count on the hot path, where an overflow is a wrong bill rather than a wrapped counter
- [ ] T011 Add the four columns and three tables to `services/api/src/db/schema.ts`, with the check constraints the migration declares
- [ ] T012 Run the migration against a fresh database and confirm it is idempotent on a second run, keyed on `schema_migrations` like the eight before it

**Checkpoint**: the arithmetic is tested and the tables exist. Nothing counts yet.

---

## Phase 3: User Story 1 — The month is counted, and the count survives (Priority: P1) 🎯 MVP

**Goal**: usage exists as a number that a Redis flush cannot change.

**Independent test**: quickstart V1 and V2 — send a known number of messages from a known number of users, read the figures, `FLUSHALL`, read them again.

- [ ] T013 [US1] Extend `environmentLimits` in `services/api/src/db/repository.ts` into a policy read that also returns the four quota columns and the current period's usage, joined on `(environment_id, period)`. **One query, not two** — the request path already makes this one for chapter 3.8, and FR-020 is then satisfied by construction rather than by care (research R4)
- [ ] T013a [US1] **Rename it for what it now returns** in `services/api/src/db/repository.ts` and at every call site. `environmentLimits` returning quotas would be a name that lies, and the next reader pays for it
- [ ] T014 [US1] Add the usage increment to `Repository.sendMessage` in `services/api/src/db/repository.ts`: `INSERT … ON CONFLICT (environment_id, period) DO UPDATE SET messages_sent = usage_periods.messages_sent + 1`, inside the transaction that inserts the message
- [ ] T014a [US1] Add the active-user membership write, `INSERT … ON CONFLICT DO NOTHING`, in the same transaction — **and only when the send carries a `user_id`**. A key-authenticated REST send is unattributed by design since chapter 3.3, and an unattributed send counts toward the message quota and toward no user (`data-model.md`)
- [ ] T015 [US1] Write `usageFor(db, environmentId, period)` in `services/api/src/db/repository.ts`, returning the shape `contracts/quota.md` §3 specifies — **zeros for a period with no rows, not null**, and a null quota carried through as null rather than resolved to a sentinel
- [ ] T016 [US1] Write `services/api/src/quotas/quotas.itest.ts`: N messages from M distinct users produce exactly N and M; a second environment of the same application reports zero; a previous month's row stays readable after the boundary
- [ ] T016a [US1] **Add the flush test to `services/api/src/quotas/quotas.itest.ts`** (SC-001, FR-002): read the figures, `FLUSHALL` the counter store, read again, assert identical. This is the test that separates a quota from chapter 3.8's limiter, and it is the reason the roll-up exists
- [ ] T016b [US1] **Confirm the flush test can fail.** Point `usageFor` in `services/api/src/db/repository.ts` at the counter store instead of the roll-up, watch it go red, and revert byte-identical by `md5sum`. A test whose failure has never been seen is a test nobody has checked
- [ ] T017 [US1] **Commit `relay-platform` before T016b's mutation, not just before the phase.** Chapter 3.9 lost a fix to exactly this revert step, in the chapter that warned about it twice in bold
- [ ] T018 [US1] Measure the send path against T002's figure and record it in `baseline.txt`: the request path must gain no query (FR-020, SC-006). Record the number, not the verdict

**Checkpoint**: usage is counted and survives a flush. Ships alone as observability with nothing enforced.

---

## Phase 4: User Story 2 — Running out is predictable (Priority: P2)

**Goal**: the cap refuses sends and touches nothing a tenant can read.

**Independent test**: quickstart V3 and V4 — one refused send and one successful history read against the same environment in the same test, plus a WebSocket send refused with the socket intact.

- [ ] T019 [US2] Write `services/api/src/quotas/quota.error.ts`: the error the repository raises, carrying dimension, usage, quota and period. **Not an HTTP concern** — the repository layer does not know what status a caller will map it to
- [ ] T020 [US2] Add the cap check to `Repository.sendMessage`, before the message insert, reading the usage row **`FOR UPDATE` alongside the channel row the transaction already locks** (research R8)
- [ ] T020a [US2] **Record beside the lock in `services/api/src/db/repository.ts` what it buys and what it costs.** It bounds the overshoot to one message — the one that crosses — rather than to concurrency. The cost is that sends to one environment serialise on one row, and T033 measures that rather than assuming it is acceptable
- [ ] T021 [US2] Map the error in `services/api/src/messages/` to `402` with the body `contracts/quota.md` §1 specifies
- [ ] T021a [US2] Map the same error in `services/api/src/internal/internal.controller.ts`, the route the gateway posts a WebSocket send to. **Two mappings, and this is the second** — research R3 records why there is no single middleware that could have done both
- [ ] T021b [US2] **Record in both controllers why the status is `402` and not `429`.** A client that retries after `Retry-After` is correct for a rate limit and wrong for a quota, which will still be exceeded in an hour. No `Retry-After` header; the resume date is in the message
- [ ] T022 [US2] Write the degradation tests in `services/api/src/quotas/quotas.itest.ts`: with usage above the cap, a send is refused **and** a history read succeeds, in the same test against the same environment (SC-002)
- [ ] T022a [US2] Assert the refusal body names the dimension, the usage, the quota and the resume date, **by reading the whole body rather than asserting on its fields**. Chapter 3.8's header bug was found by printing a response and not by any of the eighteen tests asserting on its parts
- [ ] T023 [US2] Test that a cap of zero refuses everything and that a null cap refuses nothing (FR-006)
- [ ] T024 [US2] Test that raising the cap above usage restores sending on the next request, with no restart and nothing to clear (SC-007, FR-012)
- [ ] T025 [US2] Test that a cap lowered below current usage takes effect immediately, and that the 100% crossing is recorded if it has not been this period
- [ ] T026 [US2] Write the gateway-side test in `services/gateway/src/` or `packages/e2e/`: a WebSocket send refused by the cap, **and the socket still open and still receiving sixty seconds later** (SC-003, FR-010)
- [ ] T027 [US2] Test that webhook delivery continues for messages accepted before the cap was reached (FR-011, constitution II)

**Checkpoint**: the cap refuses sends through both doors and nothing else changes.

---

## Phase 5: User Story 3 — Nobody is surprised (Priority: P3)

**This is the seam.** It has its own table, its own relay and its own test surface. If T041's word count comes in over 4,000, this is the phase that becomes its own chapter, and the phase order puts it last so that decision is made against a counted page (research R12).

**Goal**: three emails per quota per period, read out of Mailpit.

**Independent test**: quickstart V5 and V6.

- [ ] T028 [US3] Write the threshold-crossing insert into `Repository.sendMessage`'s transaction: for each threshold `thresholdsCrossed` returns, one row in `quota_notifications`. **In the same transaction as the message** — the crossing and the thing that caused it commit together or neither does
- [ ] T028a [US3] **Confirm the unique constraint is what makes it at-most-once**, not the code path. Write a test that inserts the same crossing twice and asserts one row (FR-015)
- [ ] T029 [US3] Write `services/api/src/quotas/quota-relay.ts` on chapter 3.9's shape: claim rows with `delivered_at IS NULL`, deliver, mark. **Per-row error handling with a required `onError`** — feature 030's R48 removed the default from `drainDisableNotifications` for a reason, and the fourth relay should not reintroduce it
- [ ] T029a [US3] **Give the drain a required batch size.** All four batch-taking functions require one as of feature 030; a fifth that carries a default would undo that
- [ ] T030 [US3] Write the email body in `services/api/src/quotas/` per `contracts/quota.md` §2: application and environment kind named as a human would name them, the percentage, the usage, the quota, the period as a month, and what happens next
- [ ] T030a [US3] **At 100% of a soft threshold with no hard cap, the email must say nothing was refused.** An email that threatens a suspension which will not happen is worse than no email
- [ ] T031 [US3] Wire `services/api/src/quotas/quotas.module.ts` and its relay flag, following `RELAY_NOTIFICATION_RELAY`'s shape — and **add the flag to the four lane configs' `env` blocks**, which feature 030's R39 set to `off` for exactly this class of background loop
- [ ] T032 [US3] Write the Mailpit tests: crossing 50/80/100 produces exactly three emails per quota per period, **read out of Mailpit rather than asserted on a send call** (SC-004)
- [ ] T032a [US3] Test that re-crossing an already notified threshold produces no further email (SC-005), and that a new period resets them (FR-017)
- [ ] T032b [US3] Test the unaddressable organisation: crossing recorded, cap enforced, failure logged rather than swallowed (FR-018). Chapter 3.9 built this branch; this confirms the fourth table uses it rather than reinventing it
- [ ] T032c [US3] **Assert the email carries no secret, key, credential or message text**, by reading what Mailpit received. The same test shape chapter 3.9 established, and the reason it exists

**Checkpoint**: three emails, once each, and none of them carrying anything they should not.

---

## Phase 6: Verification

- [ ] T033 **Measure what the `FOR UPDATE` cost** (T020a): concurrent sends to one environment, before and after, recorded in `baseline.txt` as a number. If serialising on one row is too expensive the design changes here, not after the chapter ships
- [ ] T034 **Run the whole lane against a baited database and confirm the guard stays silent** (quickstart V8, SC-008). Research R5 predicts this design engages feature 030's trigger nowhere. **This task exists to find out the prediction is wrong**, and a refusal here names the table and the row
- [ ] T034a **Confirm no file was added to `packages/test-harness/src/exempt.ts` or to `relay-platform/eslint.config.mjs`'s ignores.** If one was, R5 is wrong and the reason belongs in `research.md` before the chapter describes the design
- [ ] T035 Run both lanes and coverage; confirm every pre-existing suite passes and record the counts. Coverage must not fall below **89.08% statements and 82.35% branches**, and every per-file ratchet must stay green — `repository.ts` is at 100% functions and this chapter adds branches to it
- [ ] T036 **Twenty consecutive integration runs, zero false positives.** Feature 030's battery took five attempts and three red runs were real defects; budget for that rather than treating a red run as noise
- [ ] T037 Run quickstart V0 to V12 end to end, reading exit codes rather than output
- [ ] T038 Capture the transcripts into `specs/031-chapter-3-10/captured-output.md`: the refusal body in full, the three emails as Mailpit received them, the flush test's two identical readings, and the twenty-run result
- [ ] T039 Scan `captured-output.md` for leaked credentials, **recording the patterns searched rather than only the verdict**

---

## Phase 7: The chapter, in English — and the size gate

- [ ] T040 Write `relay-tutorial/app/(en)/part-3/chapter-10/quotas-and-what-they-cost/page.mdx` and its colocated `figures.ts`. **Open on the distinction**: a rate limit is about this second and forgets; a quota is about this month and must not
- [ ] T040a **Quote T004a's measurement in `page.mdx` rather than describing it.** The chapter's argument for a roll-up is 1.189ms today and proportional to lifetime traffic; a reader who is shown the `EXPLAIN` output can check the reasoning, and one who is told "it does not scale" cannot
- [ ] T040b **Say in `page.mdx` that the outbox pattern is appearing for the fourth time**, and why four concrete tables beat one generic one (research R6). A reader who has seen it three times deserves to be told it is deliberate
- [ ] T040c **Tell the story in `page.mdx` of the sweep that was not needed** (research R5). The obvious design is a periodic job; the send transaction already knows what crossed. This is the chapter's best paragraph and it is easy to leave out, because nothing went wrong
- [ ] T040d Use `<Figure code={...} />` — the prop is `code`, not `chart` — and give `<ChapterFooter />` its `id`. Both were found in chapter 3.8 only because a headless browser rendered the page
- [ ] T041 **Count the finished page's prose words** (SC-009), excluding fences, front matter and figure captions. Record the number in `baseline.txt`
- [ ] T041a **If the count exceeds 4,000, split at Phase 5's seam** and renumber: the notification story becomes its own chapter, connection-minutes moves from 3.11 to 3.12, and the gauntlet to 3.13. Update `docs/07-tutorial-plan.md` and `relay-tutorial/lib/tutorial.ts` together. Three of Part 3's four splits were discovered mid-chapter; this is the instrument that catches the fourth before it publishes

---

## Phase 8: Publication in both locales

- [ ] T042 Mark 3.10 `published` in `relay-tutorial/lib/tutorial.ts`
- [ ] T043 Translate to `relay-tutorial/app/(vi)/vi/part-3/chapter-10/quotas-and-what-they-cost/`, with **every fence byte-identical to its English counterpart, comments included** — a translated comment fails `check:fences`
- [ ] T044 Translate the mermaid labels in `figures.ts`; participants, identifiers, table and column names stay English
- [ ] T045 Run `pnpm check:fences`, `pnpm check:docs`, `pnpm lint` and `pnpm build` in `relay-tutorial/`, reading exit codes

---

## Phase 9: Close-out

- [ ] T046 Confirm `docs/07-tutorial-plan.md`'s Part 3 table still describes what shipped, including the FR-RTL-05 split across 3.10 and 3.11
- [ ] T047 Traceability: confirm every `FR-*`, `NFR-*` and `ADR-*` this chapter's **source comments** cite resolves in `docs/` or the constitution. **Feature 030 leaked fourteen feature-local ids into source and found sixty more from earlier chapters that resolve nowhere** — the SRS numbers requirements `FR-XXX-NN`, so a bare `FR-0xx` in a comment is the leak
- [ ] T048 Write `specs/031-chapter-3-10/chapter-notes.md` from what happened rather than what was planned, including the parts that went badly
- [ ] T048a **Record in `specs/031-chapter-3-10/chapter-notes.md` whether R5's no-sweep prediction survived**, and whether the `FOR UPDATE` cost T033 measured changed the design
- [ ] T049 Tag `relay-platform` `part3-ch10` at the close-out commit

---

## Dependencies

```
Phase 1 (baseline)
    ↓
Phase 2 (period, arithmetic, schema)   ← blocking: all three stories need it
    ↓
Phase 3 (US1, the roll-up)             ← ships alone as observability
    ↓
Phase 4 (US2, the cap)                 ← needs a number to compare against
    ↓
Phase 5 (US3, the emails)              ← THE SEAM; needs a cap to be a percentage of
    ↓
Phase 6 (verification) → 7 (chapter + size gate) → 8 (locales) → 9 (close-out)
```

**Story independence.** US1 ships without US2: usage counted and readable is a
feature on its own, and the flush test is the chapter's central claim. US2 needs
US1 — a cap compares against a number. US3 needs US2, because a threshold is a
percentage of a cap.

**Three orderings that matter:**

- **T013 before T014.** The policy read must return usage before the send path can
  compare against it, and doing it in the other order produces a second query that
  FR-020 then has to be walked back.
- **T028a before T032.** Prove the unique constraint is what makes the email
  at-most-once before writing tests that would pass for the wrong reason.
- **T034 before T040.** Discover whether the no-sweep prediction holds before
  writing the paragraph that claims it does.

## Parallel opportunities

- **Phase 1**: T003 alongside T001, T002 and T004a.
- **Phase 2**: T006/T007 (the period) and T008/T009 (the arithmetic) are different
  files with no shared state. T010's migration is independent of both.
- **Phase 4**: T021 and T021a are different controllers.
- **Phase 5**: T030's email body and T029's relay are separable once the table
  exists.

## Implementation strategy

**MVP is Phase 3.** A counted month that survives a flush is the chapter's
central claim and the thing chapter 3.8's mechanism could not do. Shipping it and
stopping would leave no enforcement, which is a smaller feature but not a wrong one.

**Then Phase 4**, because a quota nobody enforces is a metric, and FR-RTL-08's
"degrade predictably" is the requirement with the most ways to get it wrong.

**Phase 5 last, and separable.** It is the third relay this series has built on the
same pattern, so a reader who stops before it has still learned the chapter's
subject — which is what makes it the right thing to cut if the page runs long.
