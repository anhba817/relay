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

- [X] T001 Record provenance in `specs/031-chapter-3-10/baseline.txt`: the submodule commits this chapter starts from, and confirmation that `relay-platform` is at `feature-030-global-operation-guard` with both parent pins matching their submodule HEADs
- [X] T002 Record the pre-change platform baseline in `specs/031-chapter-3-10/baseline.txt` — unit and integration counts per package, coverage, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output. Feature 030 finished on **251 unit, 231 integration, 473 coverage at 89.08 / 82.35 / 89.25 / 90.58**, integration wall-clock 3m10.218s
- [X] T003 [P] Record the site baseline in `specs/031-chapter-3-10/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the fence and locale counts the chain reports (165 files, 26 chapters at the last measurement)
- [X] T004 **Run the integration lane three times and record every failure.** Feature 030's battery needed five attempts and three of the red runs were real defects, so a lane that is green three times is the precondition for measuring anything this chapter changes
- [X] T004a **Re-measure the derive-on-read query the chapter will argue against** and record the `EXPLAIN (ANALYZE)` output in `baseline.txt`. Research R1 measured 1.189ms for one environment and 79.807ms for a whole-table sweep against 198,690 messages; the chapter quotes these numbers, so they must be this machine's rather than yesterday's
- [X] T005 Fix forward, with its own commit, anything T004 finds that is not this chapter's work. A lane with a pre-existing intermittent failure cannot measure a new one

**Checkpoint**: the starting numbers exist and the lane is green for a known reason.

---

## Phase 2: Foundational — the period, the arithmetic, and the schema

**Blocking.** US1, US2 and US3 all depend on these. Pure functions and schema only; nothing observable yet.

- [X] T006 [P] Write `services/api/src/quotas/period.test.ts` first: the calendar month in UTC, the boundary at midnight on the first, a timestamp inside the month mapping to the month's first day, and **a timestamp in a non-UTC local zone still mapping by UTC**. The last one is the test that catches a `date_trunc` without `at time zone`
- [X] T007 [P] Implement `services/api/src/quotas/period.ts`: one exported function turning an instant into a period `date`. **One definition, imported by everything** — the migration's default, the repository's predicate and the relay's read all name this rather than repeating `date_trunc`
- [X] T008 [P] Write `services/api/src/quotas/policy.test.ts` first: which thresholds an increase crosses. `40% -> 100%` crosses all three; `49% -> 51%` crosses one; `81% -> 82%` crosses none; a decrease crosses nothing; a quota of zero is 100% at usage zero
- [X] T008a [P] **Include the case where the quota is null** in `services/api/src/quotas/policy.test.ts`. Unlimited crosses no threshold at any usage, and the function must say so rather than dividing by null — the branch that would otherwise appear as a crash in production and as full coverage in the ratchet
- [X] T009 [P] Implement `services/api/src/quotas/policy.ts`: `thresholdsCrossed(before, after, quota)` returning the ascending list. Pure, no database, no clock
- [X] T010 Write `services/api/migrations/0009_quotas.sql` per `data-model.md`: **one CHECK constraint on the `environments.quota_config` column chapter 2.1 already declared** — not four new columns — plus `usage_periods`, `usage_active_users` and `quota_notifications`
- [X] T010a **Record in the migration why null is not zero**, the rule chapter 3.8's `0008_limit_policy.sql` established for the same reason on the same table. Null is no cap; zero refuses everything; an environment can be switched off deliberately, so they cannot share a representation (FR-006)
- [X] T010b **Make `quota_notifications`'s unique constraint carry FR-015** in `services/api/migrations/0009_quotas.sql`, `(environment_id, period, dimension, threshold)`, and say so in the migration. At-most-one-email-per-threshold is then a schema property rather than a promise the writing code makes, and a concurrent double-crossing resolves to one row instead of two emails
- [X] T010c **Record in `services/api/migrations/0009_quotas.sql` that `usage_periods.messages_sent` is `bigint` and why.** A cumulative count on the hot path, where an overflow is a wrong bill rather than a wrapped counter
- [X] T011 Add the three tables to `services/api/src/db/schema.ts` with the check constraints the migration declares. `quotaConfig` is already there and needs no change
- [X] T011c **Write `services/api/src/quotas/config.ts`** — a zod schema and `capsFor()`, because a jsonb column arrives as `unknown` and something has to turn it into numbers. **Fails closed**: an unparseable config yields no caps and an error to log, since an operator's typo must not suspend a tenant. `.strict()`, so a dimension nobody implemented is a parse failure rather than a cap silently ignored
- [X] T011a **Choose drizzle's mode for `period` and prove it round-trips before anything depends on it.** This would be the project's **first `date` column** — the schema declares 28 `timestamp(`, 12 `integer(`, 2 `bigint(` and zero `date(` — and `period` is a **primary key component** on two tables, so a mode mismatch between writer and reader is a silent key miss rather than a type error. Write the round-trip into `services/api/src/quotas/period.test.ts` or a schema test: insert with the period the TS function returns, look the row up by that same value, get the row back
- [X] T011b **Declare `messages_sent` as `bigint("messages_sent", { mode: "number" })`**, the mode the project's two existing bigints use — `channels.last_sequence` and `messages.sequence`. Drizzle requires a mode; `data-model.md` said `bigint` without one
- [X] T012 Run the migration against a fresh database and confirm it is idempotent on a second run, keyed on `schema_migrations` like the eight before it

**Checkpoint**: the arithmetic is tested and the tables exist. Nothing counts yet.

**What Phase 2 changed about the design.** The plan added four typed quota columns
to `environments`. Chapter 3.8 had already refused that column's job in published
prose, reserving `quota_config` for this chapter, and three analysis passes missed
it because none read the artifacts against the published series. The caps now live
in the jsonb column 2.1 left empty (research R4a), which costs a parser and buys
chapter 3.11 a dimension without a migration.

---

## Phase 3: User Story 1 — The month is counted, and the count survives (Priority: P1) 🎯 MVP

**Goal**: usage exists as a number that a Redis flush cannot change.

**Independent test**: quickstart V1 and V2 — send a known number of messages from a known number of users, read the figures, `FLUSHALL`, read them again.

- [X] T013 [US1] Add `quotaPolicyFor(tx, environmentId, period)` to `services/api/src/db/repository.ts`, returning the four quota columns and the current period's usage in one query, joined on `(environment_id, period)`. **Read inside the send transaction and taken `FOR UPDATE`** — this is the authoritative read and the only one
- [X] T013a [US1] **Leave `environmentLimits` alone**, and confirm both its call sites are untouched — `services/api/src/limits/rate-limit.middleware.ts:138` and `services/api/src/internal/session.controller.ts:67`. An earlier draft extended it, on the reasoning that the request path already makes that query. **It has a second caller**: the session controller hands the gateway its connect and send limits on every WebSocket connect, so extending it makes every connect pay for a usage join it never reads, and renaming it edits a response shape that is a contract with another service (research R4)
- [X] T014 [US1] Add the usage increment to `Repository.sendMessage` in `services/api/src/db/repository.ts`: `INSERT … ON CONFLICT (environment_id, period) DO UPDATE SET messages_sent = usage_periods.messages_sent + 1`, inside the transaction that inserts the message
- [X] T014a [US1] Add the active-user membership write, `INSERT … ON CONFLICT DO NOTHING`, in the same transaction — **and only when the send carries a `user_id`**. A key-authenticated REST send is unattributed by design since chapter 3.3, and an unattributed send counts toward the message quota and toward no user (`data-model.md`)
- [X] T015 [US1] Write `usageFor(db, environmentId, period)` in `services/api/src/db/repository.ts`, returning the shape `contracts/quota.md` §3 specifies — **zeros for a period with no rows, not null**, and a null quota carried through as null rather than resolved to a sentinel
- [X] T016 [US1] Write `services/api/src/quotas/quotas.itest.ts`: N messages from M distinct users produce exactly N and M; a second environment of the same application reports zero; a previous month's row stays readable after the boundary
- [X] T016a [US1] **Add the flush test to `services/api/src/quotas/quotas.itest.ts`** (SC-001, FR-002): read the figures, `FLUSHALL` the counter store, read again, assert identical. This is the test that separates a quota from chapter 3.8's limiter, and it is the reason the roll-up exists
- [X] T016b [US1] **Confirm the flush test can fail.** Point `usageFor` in `services/api/src/db/repository.ts` at the counter store instead of the roll-up, watch it go red, and revert byte-identical by `md5sum`. A test whose failure has never been seen is a test nobody has checked
- [X] T017 [US1] **Commit `relay-platform` before T016b's mutation of `services/api/src/db/repository.ts`, not just before the phase.** Chapter 3.9 lost a fix to exactly this revert step, in the chapter that warned about it twice in bold
- [X] T018 [US1] **Prove the send path gains no SCANNING query** (FR-020, SC-006) by capturing `EXPLAIN (ANALYZE, BUFFERS)` for the send transaction into `specs/031-chapter-3-10/baseline.txt`, before and after. **It does gain a query** — the usage row read taken `FOR UPDATE` — and FR-020 permits that; what it forbids is a query proportional to the tenant's traffic. An earlier draft of this task said "must gain no query", which is stronger than the requirement and false of the design it was verifying. Record the plans, not the verdict

**Checkpoint**: usage is counted and survives a flush. Ships alone as observability with nothing enforced.

---

## Phase 4: User Story 2 — Running out is predictable (Priority: P2)

**Goal**: the cap refuses sends and touches nothing a tenant can read.

**Independent test**: quickstart V3 and V4 — one refused send and one successful history read against the same environment in the same test, plus a WebSocket send refused with the socket intact.

- [ ] T019 [US2] Write `services/api/src/quotas/quota.error.ts`: the error the repository raises, carrying dimension, usage, quota and period. **Not an HTTP concern** — the repository layer does not know what status a caller will map it to
- [ ] T020 [US2] Add the cap check to `Repository.sendMessage` in `services/api/src/db/repository.ts`, before the message insert, reading the usage row **`FOR UPDATE` alongside the channel row the transaction already locks** (research R8)
- [ ] T020a [US2] **Record beside the lock in `services/api/src/db/repository.ts` what it buys and what it costs.** It bounds the overshoot to one message — the one that crosses — rather than to concurrency. The cost is that sends to one environment serialise on one row, and T033 measures that rather than assuming it is acceptable
- [ ] T021 [US2] Throw the refusal as an `HttpException` with status `402` from `services/api/src/messages/messages.service.ts`, the one method both routes call — `internal.controller.ts` reaches it through `messages.send`. **`ProtocolErrorFilter` builds the envelope**: it is `@Catch()`-all, globally registered through `APP_FILTER`, and derives `docs_url` from the code
- [ ] T021a [US2] **The throw MUST carry `{ code: "quota_exceeded" }` in its response object.** `ProtocolErrorFilter` falls back by status for 400, 401, 403 and 404 and **everything else becomes `internal_error`** — so an unnamed `402` emits a body calling itself an internal error while carrying a `402`. That is the lie chapter 2.2 fixed for 400 and chapter 3.2 for 403, and 3.2's mechanism, a thrower naming its own code, is what this depends on. **Assert the emitted `code`, not only the status**
- [ ] T021b [US2] **Record in `services/api/src/messages/messages.service.ts` why the status is `402` and not `429`.** A client that retries after `Retry-After` is correct for a rate limit and wrong for a quota, which will still be exceeded in an hour. No `Retry-After` header; the resume date is in the message. **One place, not two** — an earlier draft of these tasks had a mapping per controller, and this service has no per-controller mappings to add one to (research R3)
- [ ] T022 [US2] Write the degradation tests in `services/api/src/quotas/quotas.itest.ts`: with usage above the cap, a send is refused **and** a history read succeeds, in the same test against the same environment (SC-002)
- [ ] T022a [US2] In `services/api/src/quotas/quotas.itest.ts`, assert the refusal body names the dimension, the usage, the quota and the resume date, **by reading the whole body rather than asserting on its fields**. Chapter 3.8's header bug was found by printing a response and not by any of the eighteen tests asserting on its parts
- [ ] T023 [US2] In `services/api/src/quotas/quotas.itest.ts`, test that a cap of zero refuses everything and that a null cap refuses nothing (FR-006)
- [ ] T023a [US2] In `services/api/src/quotas/quotas.itest.ts`, test that **a soft threshold refuses nothing** (FR-013): usage at 100% of a soft threshold with no hard cap configured, and the next send succeeds. The email is T030a's subject; this is the half that says the tenant is still serving traffic
- [ ] T024 [US2] In `services/api/src/quotas/quotas.itest.ts`, test that raising the cap above usage restores sending on the next request, with no restart and nothing to clear (SC-007, FR-012)
- [ ] T025 [US2] In `services/api/src/quotas/quotas.itest.ts`, test that a cap lowered below current usage takes effect immediately, and that the 100% crossing is recorded if it has not been this period
- [ ] T026 [US2] Write the gateway-side test in `packages/e2e/src/` — **that lane, because the test needs a live api child to do the refusing**, which the gateway's own lane does not spawn: a WebSocket send refused by the cap, **and the socket still open and still receiving sixty seconds later** (SC-003, FR-010)
- [ ] T027 [US2] In `services/api/src/quotas/quotas.itest.ts`, test that webhook delivery continues for messages accepted before the cap was reached (FR-011, constitution II)

**Checkpoint**: the cap refuses sends through both doors and nothing else changes.

---

## Phase 5: User Story 3 — Nobody is surprised (Priority: P3)

**This is the seam.** It has its own table, its own relay and its own test surface. If T041's word count comes in over 4,000, this is the phase that becomes its own chapter, and the phase order puts it last so that decision is made against a counted page (research R12).

**Goal**: three emails per quota per period, read out of Mailpit.

**Independent test**: quickstart V5 and V6.

- [ ] T028 [US3] Write the threshold-crossing insert into `Repository.sendMessage`'s transaction in `services/api/src/db/repository.ts`: for each threshold `thresholdsCrossed` returns, one row in `quota_notifications`. **In the same transaction as the message** — the crossing and the thing that caused it commit together or neither does. **Inserted AHEAD of the cap check T020 added** (FR-013a): with a soft threshold and a hard cap at the same value, the email must survive the send that did not, so the crossing row is written first and the refusal is raised after. The spec's Edge Cases promised this order was defined; this task is where it is obeyed. **The ordering belongs to this task, not to T020** — US2 ships without US3, and until this phase there is no crossing row for the refusal to be ordered against
- [ ] T028a [US3] **Confirm the unique constraint is what makes it at-most-once**, not the code path. Write a test in `services/api/src/quotas/quotas.itest.ts` that inserts the same crossing twice and asserts one row (FR-015)
- [ ] T029 [US3] Write `services/api/src/quotas/quota-relay.ts` on chapter 3.9's shape: claim rows with `delivered_at IS NULL`, deliver, mark. **Per-row error handling with a required `onError`** — feature 030's R48 removed the default from `drainDisableNotifications` for a reason, and the fourth relay should not reintroduce it
- [ ] T029a [US3] **Give the drain in `services/api/src/db/repository.ts` a required batch size.** All four batch-taking functions require one as of feature 030; a fifth that carries a default would undo that
- [ ] T030 [US3] Write the email body in `services/api/src/quotas/quota-email.ts` per `contracts/quota.md` §2: application and environment kind named as a human would name them, the percentage, the usage, the quota, the period as a month, and what happens next
- [ ] T030a [US3] **At 100% of a soft threshold with no hard cap, `services/api/src/quotas/quota-email.ts` must say nothing was refused.** An email that threatens a suspension which will not happen is worse than no email
- [ ] T030b [US3] **Register `QuotasModule` in `services/api/src/app.module.ts`**, beside `NotificationsModule`. No task said so until the third analysis pass, and the relay would have been written, tested in isolation and never started
- [ ] T031 [US3] Wire `services/api/src/quotas/quotas.module.ts` and its relay flag, following `RELAY_NOTIFICATION_RELAY`'s shape — and **add the flag to the three lane configs that carry the other relay flags** — `services/api/vitest.integration.config.mts`, `services/dispatcher/vitest.integration.config.mts` and `vitest.coverage.config.mts` — which feature 030's R39 set to `off` for exactly this class of background loop. Three, counted: the gateway and e2e configs got exemption handling and no flag block
- [ ] T032 [US3] Write the Mailpit tests in `services/api/src/quotas/quotas.itest.ts`: crossing 50/80/100 produces exactly three emails per quota per period, **read out of Mailpit rather than asserted on a send call** (SC-004). **Include the jump** — one send taking usage from 40% to 100% produces all three, which T008 covers as arithmetic and nothing yet covers as email (FR-016)
- [ ] T032a [US3] In `services/api/src/quotas/quotas.itest.ts`, test that re-crossing an already notified threshold produces no further email (SC-005), and that a new period resets them (FR-017)
- [ ] T032b [US3] In `services/api/src/quotas/quotas.itest.ts`, test the unaddressable organisation: crossing recorded, cap enforced, failure logged rather than swallowed (FR-018). Chapter 3.9 built this branch; this confirms the fourth table uses it rather than reinventing it
- [ ] T032d [US3] In `services/api/src/quotas/quotas.itest.ts`, **test that the mail server being gone cannot fail a send** (FR-019): point the mailer at a port with nothing behind it, cross a threshold, and assert the send succeeded, the crossing row exists, and the row is still claimable. Writing a row is not sending one, and this is the requirement that says so out loud — chapter 3.9 met the same hazard from the other side, where a drain's failure became a lane's failure
- [ ] T032c [US3] In `services/api/src/quotas/quotas.itest.ts`, **assert the email carries no secret, key, credential or message text**, by reading what Mailpit received. The same test shape chapter 3.9 established, and the reason it exists

**Checkpoint**: three emails, once each, and none of them carrying anything they should not.

---

## Phase 6: Verification

- [ ] T033 **Measure what the `FOR UPDATE` in `services/api/src/db/repository.ts` cost** (T020a): concurrent sends to one environment, before and after, recorded in `baseline.txt` as a number. If serialising on one row is too expensive the design changes here, not after the chapter ships
- [ ] T034 **Run the whole lane against a baited database and confirm the guard stays silent** (quickstart V8, SC-008). Research R5 predicts this design engages feature 030's trigger nowhere. **This task exists to find out the prediction is wrong**, and a refusal here names the table and the row
- [ ] T034a **Confirm no file was added to `packages/test-harness/src/exempt.ts` or to `relay-platform/eslint.config.mjs`'s ignores** (FR-021, SC-008). If one was, R5 is wrong and the reason belongs in `research.md` before the chapter describes the design
- [ ] T035 Run both lanes and coverage; confirm every pre-existing suite passes and record the counts. Coverage must not fall below **89.08% statements and 82.35% branches**, and every per-file ratchet must stay green
- [ ] T035a **Name the mechanism that breaks the `repository.ts` ratchet, and check it before the coverage run rather than after.** That file is pinned at **100% functions** and exports 22 today; this chapter adds three — `quotaPolicyFor`, `usageFor` and the notification drain — and each needs a test caller or the ratchet goes red. Feature 030's R48 found that ratchet already red, and it had been red for a whole feature because nobody named the mechanism
- [ ] T036 **Twenty consecutive integration runs of `pnpm test:integration`, zero false positives**, recorded in `specs/031-chapter-3-10/baseline.txt`. Feature 030's battery took five attempts and three red runs were real defects; budget for that rather than treating a red run as noise
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
- [ ] T040e **Say in `page.mdx` what a cap is denominated in, and introduce no price** (FR-022). Messages and active users, not money: no price, unit cost or currency appears in `docs/04-srs.md` or `docs/05-sad.md`, and FR-RTL-06's design note calls it a purchasing requirement whose harm is unbounded exposure. A reader who assumes the cap is in currency will look for a pricing model that does not exist
- [ ] T041 **Count the finished page's prose words AND its fences** (SC-009), the words excluding fences, front matter and figure captions. **Derive both by reading the page**, never by comparing against a written estimate: chapter 3.8's fence count went stale three times across its analysis passes — 23, then 28, then 33 — each time because a remediation added a file below the sentence stating how many there were, and chapter 3.5 shipped 39 fences against an estimate of 22. Record both in `baseline.txt`
- [ ] T041a **If the count exceeds 4,000, split at Phase 5's seam** and renumber: the notification story becomes its own chapter, connection-minutes moves from 3.11 to 3.12, and the gauntlet to 3.13. Update `docs/07-tutorial-plan.md` and `relay-tutorial/lib/tutorial.ts` together. Three of Part 3's four splits were discovered mid-chapter; this is the instrument that catches the fourth before it publishes

---

## Phase 8: Publication in both locales

- [ ] T041b **Generate every fence from the real files rather than typing them**, and confirm `pnpm check:fences` replays the chain onto `relay-platform`. **Six files this chapter modifies are already fenced and carry 47 fences between them** — `services/api/src/db/repository.ts` (15), `services/api/src/db/schema.ts` (10), `services/api/src/app.module.ts` (8), `services/api/src/messages/messages.service.ts` (7), `vitest.coverage.config.mts` (5) and `services/api/vitest.integration.config.mts` (2). **Those are the chain's own titles — platform paths, no `relay-platform/` prefix.** An earlier draft prefixed the coverage config's, which would have opened a new path in the chain rather than amending the existing one, the failure feature 030's T039a named. The chain compares byte for byte, so a modified fenced file with no new fence diverges the replay. Chapter 3.8 carried this as T061; **an earlier draft of this task list had no equivalent, and T045 would have failed after the chapter was written and translated**
- [ ] T041c **Route each fence to the right home before generating any of them.** A chapter may only fence a change it discusses (chapter 3.8's T025e). The four product files — `repository.ts`, `schema.ts`, `app.module.ts`, `messages.service.ts` — are this chapter's subject and fence in the chapter. **The two vitest configs are not**: adding a relay flag to a lane is hygiene 3.10 never explains, so those go to `relay-tutorial/fences/post-series.md` as extensions of the sections feature 030 already opened there. `services/dispatcher/vitest.integration.config.mts` is fenced by nothing and needs neither
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
- **T028 inserts ahead of T020, not after it.** The crossing write goes in above the cap check inside
  the same transaction (FR-013a). This is an edit to code Phase 4 already shipped, which is why it is
  a US3 task rather than a US2 one — US2 is complete and correct without it.
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
