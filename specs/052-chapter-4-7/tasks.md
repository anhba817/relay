# Tasks — 052, chapter 4.7, "the job that checks the meter"

**Input**: `spec.md` (23 FR, 13 SC), `plan.md` (7 phases), `research.md` (R1–R10, eight
measured), `data-model.md`, `contracts/reconcile.md`, `quickstart.md`.

**Read `research.md` before starting.** R1 changed the job's shape — it compares one tenant at
a time because aggregating turned 19 breaches into one passing number — and R4 made
`not-comparable` and `no-data` verdicts of their own.

**MVP is phases 1–4**: the job exists, compares per tenant, reports four verdicts, and a
planted drift raises.

**Commit each phase.** Commits stay under five lines with no `Co-Authored-By` trailer.

**Run `pnpm check:fences` after any source edit**, not only at the ratchet.

**Capture every exit code outside a pipeline.**

---

## Phase 1: Premises, and the openings this chapter is measured against

- [X] T001 [P] Re-run R1's two operational counters into `specs/052-chapter-4-7/baseline.txt`: `messages` joined to `channels` against `usage_periods.messages_sent`, aggregate and **per tenant**, with the count of tenants over 0.1%. Planning measured 9,650 / 9,624 / 0.2694% aggregate, 100% worst tenant, 19 over the bound. **The per-tenant figures are the ones that decided the design**, so a re-run that only reproduces the aggregate has not checked the premise.
- [X] T002 **Confirm the cause analysis pass 1 found, and confirm it is still all fixtures.** The send path cannot drift — `repository.ts` inserts at 4214, returns early on `if (inserted.length === 0)`, and increments `usagePeriods` at 4344 in the same transaction. The drift comes from writers that never touch the counter: `backfill.itest.ts:222`, `repository.itest.ts:656`, `dual-write-walk.mjs:71`, `corpus.mjs:308,328`, and `test-harness/sentinel.ts:159`, which **deletes `usage_periods` rows** while the messages survive. Attributed, every disagreeing tenant was `tenant-a`, `history-itest`, `backfill-itest`, `history-drift-itest` or `dual-write-*`, and **zero were anything else**. **Re-run the attribution and record the count of non-fixture tenants** — if it is ever above zero the chapter's framing changes, and "two counters disagree" and "fixtures bypass one of them" are different chapters.
- [X] T003 [P] Re-run R4's tenant counts **and attribute every analytical environment to the application that owns it**. Planning measured 4 against 675 and then found all four to be test fixtures absent from Postgres, so the real figure is **0 against 675**. **NO CLAIM ABOUT WHOSE DATA A ROW IS MAY BE MADE WITHOUT THIS JOIN.** Four numbers in this feature turned out to be about the lane rather than the platform, and the fourth was written in the same commit that added this step — by checking that the application names were not `__sentinel__` and reading that negative as confirmation. A weaker check that comes back clean is not attribution.
- [X] T004 [P] Re-run R3 against the server rather than the plan: `usage_periods`' columns, and whether `usage_active_users` holds what the active-users comparison needs. Planning read `environment_id, period, messages_sent, created_at, connection_minutes`.
- [X] T005 [P] Record which quantities have an operational counterpart and which do not, as the opening for FR-007. **The stored message count has none** — confirm it rather than carry it.
- [X] T006 [P] Measure the fence-chain OPENING with `pnpm check:fences`, **by kind and locale, and with the two HEAD classes split**. 4.6's close was 110 — APPLY 74 (30 en, 30 vi, 14 elsewhere), HEAD 36, split 25 `differs at line` against 11 `does not exist`.
- [X] T007 [P] Count the fenced-file exposure for **every file this chapter will touch**, in both locales, and record which are whole bodies. 4.6 found two of eleven carrying Vietnamese whole bodies and both already stale (050-3), which the checker never reports.
- [X] T008 Take the eleven gates' opening colours **by running the suites directly, not by reading turbo's summary**. `pnpm test:integration` reports one `FAIL` line against `Tasks: 6 successful, 9 total` and the api lane prints no test output at all (051-3). Known inherited at 4.6's close: `request-log.itest.ts` 5 of 5 (050-8), `limits.itest.ts`, and `reset-lane.itest.ts` under load.
- [X] T009 [P] Record `periodOf`'s definition and name the closed period this feature uses, **with what it contains on each side**. Measured: **2026-08-01 holds 216 operational rows with `messages_sent = 0` and `connection_minutes = 5736`, and the analytical side has 0 days in August** — so messages report `no-data` there and connection-minutes a 100% breach. Both are usable demonstrations and an implementer who picks the period blind will think the messages comparison is broken. **And every one of those 216 rows is a fixture** — `Fleet Ops` is `quotas/quota-email.test.ts`'s, `period-roundtrip` is `quotas/period.itest.ts`'s, and the rest are `conn-<uuid>` connection tests. A first version of this task called them *"real applications, not sentinels"*, which is what checking for `__sentinel__` and reading a negative as confirmation produces. **There is no period in this lane with real tenant data on either side** — see T009a. **Never the current month** — its rollup is still being written and its counter still incremented.
- [X] T009a **Record that no period in this lane has real tenant data, and that every figure in this chapter therefore comes from planted data.** Measured: 2026-08 is 216 fixture rows with `messages_sent = 0`; 2026-09 is the open period and also fixtures; `1999-01-01` is 31 `__sentinel__` rows; and the four analytical environments are `metering.itest.ts`'s and `ingest.itest.ts`'s, absent from Postgres. **This is not an obstacle, it is §2.3's premise arriving as a number**: *"0.1% of a small number is an assertion that cannot fail for its own reason"*, which is why both halves of the evidence are constructed: a planted drift (phase 4) and matched planted totals at volume (phase 5). Say it once, plainly, so no reader expects a lane run to show a real reconciliation.
- [X] T010 [P] Record both stores' retention: the rollups at 25 months (chapter 4.6, DR-09) and `message_events` at 90 days. This bounds what the job can verify, and R8 says it is the design rather than a fault.
- [X] T010a **Confirm feature 030's guard covers both operational tables this chapter writes, and that the api lane carries bait.** Asked of the server: `select tgrelid::regclass from pg_trigger where tgname like '__sentinel_guard%'` returns `channels, quota_notifications, read_positions, usage_active_users, usage_connections, usage_periods, users` — **both `usage_periods` and `usage_active_users` are guarded**. And `services/api/vitest.integration.config.mts:32` sets `RELAY_HARNESS_BAIT: "on"`, **unlike the gateway lane, where 4.5 checked this and found none**. Re-run both rather than trusting this line.
- [X] T010b **State the rule that follows, once, before any task writes a row.** The guard fires only when a statement modifies a **sentinel** row — bait planted to belong to no test — so *"one trigger per table carrying `environment_id`, firing only for a sentinel's rows"*. **Every statement this chapter writes against `usage_periods` or `usage_active_users` must name its own environment ids.** A scoped statement never reaches a sentinel and never raises; `sentinel.ts:159`'s own `DELETE FROM usage_periods WHERE environment_id = $1` is the pattern to copy. This is the same constraint 050-2 imposes on the analytical side for an unrelated reason, and the same one R1's per-tenant design already wanted.
- [X] T010c **Decide whether `reconcile.itest.ts` needs an `EXEMPT_FILES` entry, and record the reasoning either way.** The list holds exactly one entry — `outbox.itest.ts`, *"drives the event relay, whose whole subject is a global drain"* — and `exempt.test.ts` asserts it **in both directions**: an unlisted file performing a global operation fails loudly, and a listed file that does not exist fails too. **A needless entry is a defect of its own**, holding a standing exemption over a file that does not need one. 4.5 ran this check for the gateway and recorded it as T010d; its value was in the checking rather than in the answer.
- [X] T011 Commit phase 1 — `baseline.txt` only. No platform change yet.

---

## Phase 2: Foundational — the verdict, with no store in sight

**Blocks every user story.** §2.3's CI half needs a comparison that runs without a corpus, and
this is it: two numbers, a threshold, and a source name in; a verdict out.

- [X] T012 Write the verdict function in `relay-platform/services/api/src/metering/reconcile.ts`: given an analytical total, an operational total (either possibly null), and a threshold, return one of `pass`, `breach`, `not-comparable`, `no-data`. **Import `Db` as a type only** — `db/client.ts` imports `pg` and `drizzle` at module load and creates a pool only inside `createPool()`, and the api's unit lane is a bare `include: ["src/**/*.test.ts"]` with no `globalSetup`, so a type-only import is erased and phase 2 runs Docker-free. A value import would work too and would make that property an accident. **A pure function taking numbers, not a method reaching for a store** — this is the half §2.3's CI gate runs without a corpus.
- [X] T013 The threshold is a **named constant citing FR-ANL-06**, not a literal (FR-009). A number with a clause beside it is the difference between a decision and a guess.
- [X] T014 The percentage is `abs(a - o) / max(a, o)`, **not divided by the operational side**. 671 tenants have an operational total of zero for some quantities, and a zero denominator is a crash where a verdict belongs.
- [X] T015 The percentage is **null whenever either side is null** (`data-model.md`). A number computed against an absent counterpart reads as a measurement and is not one.
- [X] T016 A quantity with no operational counterpart at all returns `not-comparable`, and **both sides absent returns `no-data`**. **And one-sidedness has two directions** — decide what an analytical id absent from Postgres returns, because the store holds four such ids today and nothing enforces referential integrity across a stream. Discharge **FR-004** and **SC-006**: zero against zero is not agreement.
- [X] T017 **Data on exactly one side is a `breach`, not `no-data`.** R4 measured 671 tenants in that state, and calling it missing data would let the platform's largest defect read as an absence.
- [X] T018 [P] Write `reconcile.test.ts` — unit, no store. Cover all four verdicts and **both sides of the tolerance boundary** (FR-011): a difference just over the threshold breaches and one just under passes.
- [X] T019 [P] Assert the null-percentage rule and the `max()` denominator with a case where the operational side is zero, which is the one that would have divided by zero.
- [X] T020 Run `lint`, `typecheck` and `test`, and commit phase 2. **`test` is the lane that matters here** — this phase adds no integration surface.

---

## Phase 3: User Story 1 — the job reads both stores (Priority: P1)

**Goal**: for one tenant and one closed period, every FR-ANL-05 quantity gets both totals, a
named operational source, a percentage and a verdict.

**Independent test**: call it against the lane and read its report.

- [X] T020a [US1] **Write the api's own ClickHouse caller** at `services/api/src/metering/clickhouse.ts` — a `fetch` and a `query()`, about **fifteen lines**, the shape of `services/ingester/src/clickhouse.ts`'s private `post()`. **The type this chapter needs does not exist where the code goes**: the api depends on `@relay/protocol` and `@relay/service-kit` only, and `ClickHouse` is exported from no package. The alternative — moving that interface into `@relay/service-kit`, which has **zero dependencies and five dependents** — would give the logging package a network client, push it onto five services, and edit a file carrying four fences across four chapters. **Record the alternative and its counts**, not just the choice.
- [X] T020b [US1] **Say that 4.6's "one client per service" is a per-service claim.** That chapter gave `ClickHouse` a `query()` method so a read would not open a second client *in the ingester*; this chapter cannot reuse it and makes the api the **second service** to hold a caller. The argument survives exactly as written — and this is the concrete form of the constitution III note T026b carries, because the service that IS the operational path now speaks to the analytical store directly.
- [X] T021 [US1] Discharge **FR-001** and **SC-001**: `reconcile(db, store, { environmentId, period })` — **both handles are parameters**, `db` the api's `Db` and `store` T020a's caller. **The day range is half-open** — `day >= period AND day < nextPeriod(period)`, using the function that already exists beside `periodOf`. `BETWEEN period AND nextPeriod(period)` puts 1 September in August, and **a reconciler's off-by-one does not crash, it reports drift**. A function that constructs its own Postgres pool would open a second one inside a service whose pool is a NestJS provider (`internal.module.ts:48`), and would be testable only against live stores. Chapter 4.6's `metering.ts` takes `store` first and this takes two, for the same reason. Extend it with the gathering: analytical totals from `relay_analytics.daily_usage_billing` over HTTP, operational totals from Postgres. **Not `daily_usage_v2`** — 147,534 rows against 281 for the same data (chapter 4.6), and the reconciler has no use for the channel dimension.
- [X] T022 [US1] Discharge **FR-002** and **SC-004**: the job takes a tenant and an explicit period and **returns its report as a value**. `docs/12` row 8 says *"callable in isolation"*, and §2.3's CI half plants a drift and needs something to assert on.
- [X] T023 [US1] Discharge **FR-003**, **FR-005** and **SC-007**: every breach carries its reason where one is known, and every row names the operational table it used. Two candidates disagree by 0.2694%, so a report that does not say which one it read is asserting the other does not exist.
- [X] T024 [US1] Discharge **FR-006**: choose `usage_periods.messages_sent` over a count of `messages`, and record the reason from the code rather than from preference — `repository.ts:4325`, *"a read over `messages` … proportional to lifetime traffic forever"*, which 4.1 measured at 585.9 ms over 1,000,000 rows. **Publish the rejected candidate's gap WITH ITS CAUSE.** The gap in this lane is fixtures, and publishing the number alone would make a lane artifact read as a platform defect — 047's pass-9 lesson, arriving in a new feature.
- [X] T025 [US1] Discharge **FR-007**: do the same for every other quantity, or state that it has only one candidate. **`usage_active_users` is `(environment_id, period, user_id, first_seen_at)` — one row per user per period, so the operational figure is a `count(*)` over that scope**, not a stored total. **And name the shape mismatch where the comparison is defined**: an exact count against `uniqMerge`'s approximate sketch is where 047-1's 0.51% lives. Connection-minutes come from `usage_periods.connection_minutes`; the stored count has no operational side at all.
- [X] T026 [US1] **One tenant per call.** A sweep is a loop in the caller. R1 measured that aggregating across tenants turns 19 breaches into 0.2694%, which is why this is a constraint rather than a convenience.
- [X] T026a [US1] **Give the api container a way to reach ClickHouse, and expect to owe a fence hunk.** `compose.yaml` carries **13 titled fences** across the chapters, so this edit will move the chain — 4.5 measured the identical edit doing exactly that when the gateway gained `RELAY_NATS_URL`. Write the `diff` hunk in the same phase rather than discovering the debt at the ratchet. Measured: `services/api/src` holds exactly one ClickHouse reference and it is inside a `.itest.ts`; the api's compose block carries `RELAY_NATS_URL` and `RELAY_REDIS_URL` and **no `RELAY_CLICKHOUSE_*`, and no `depends_on: clickhouse`**. Add both, in the shape 4.5 used when the gateway gained `RELAY_NATS_URL`. **And run `pnpm check:fences` immediately** — `compose.yaml` is fenced in five chapters, and 4.5 measured this exact edit costing the chain until a hunk was written.
- [X] T026b [US1] **Record what that change is, because it is not plumbing.** The api becomes the **first operational service to read the analytical store**. Constitution III says *"billing, metering, and dashboard analytics read only from the analytical store"*, and the service that IS the operational path now reads across. This is the sharpest form of the question T053 answers, and it belongs in that amendment rather than in a commit message.
- [X] T027 [US1] Write `scripts/reconcile-usage.mjs` as a thin caller — R5's shape, the one `reset-lane.mjs` and `consumer-walk.mjs` already use. It exits non-zero on any breach.
- [X] T028 [P] [US1] Write `reconcile.itest.ts` — with T010c's exemption decision applied — construct both handles in the test and pass them in — which is what makes T032's planted drift possible without a live send path. Run the job against the lane for a dedicated environment id and assert the report's shape for all four quantities. **A dedicated id and every count scoped by it** — the analytical store has no lane guard (050-2), and five chapters now write it from tests.
- [X] T029 [US1] Discharge **SC-005**: two invocations with the same arguments return the same report, asserted. The job writes nothing, and that is the property that makes it safe to run.
- [X] T030 [US1] Assert tenancy in both directions: a second environment's totals are unreachable from the first's filter.
- [X] T031 [US1] Run the four lanes and commit phase 3.

---

## Phase 4: User Story 2 and 3 — the planted drift 🎯 MVP (Priority: P1)

**Goal**: §2.3's CI half. A deliberate discrepancy is detected, and the same assertion is shown
not firing once it is removed.

- [X] T032 [US2] Plant a drift larger than the threshold on one side for a dedicated tenant, run the job, and assert it raises for that tenant and quantity (FR-010, SC-002).
- [X] T033 [US2] **Remove the drift and assert it does not raise.** Both halves, because a check that only ever fires is not a check — and this project has run the coverage-threshold probe both ways five times for the same reason.
- [X] T034 [US2] Exercise the tolerance boundary from both sides at integration scale as well as in the unit test (FR-011, SC-003).
- [X] T035 [US2] Clean the planted drift up and **verify the cleanup**, before anything else is counted, **scoped by environment id on both sides** (T010b). A mutation is not a delete — chapter 4.6's suite read three creations where it had planted two, because `ALTER TABLE … DELETE` is queued.
- [X] T036 [US3] Discharge **FR-008**: the raise is observable by a test rather than only by a human reading output. Assert on the returned report and on the caller's exit code.
- [X] T037 [US3] Record what "raises an alert" cannot mean here: there is no alerting integration, and the one notification path is `quotas/quota-email.ts`, whose failure mode is already in the lane as `quotas.unaddressable: no member has an email address`. **A notification with no recipient is not an alert** — name what a real one would cost.
- [X] T038 [US1] Pin `services/api/src/metering/reconcile.ts` in `vitest.coverage.config.mts` with freshly measured numbers, **two observations**, and **run both halves of the threshold probe**. Unlike chapter 4.6's read this file has real branches, so constitution VI's clause has something to bind to.
- [X] T039 [US1] Sweep every per-file pin against the include and exclude globs and record the count. 4.6 measured 50 pins, 50 binding. **Expand the globs over the real tree** rather than pattern-matching in memory.
- [X] T040 [US1] Run all four lanes **and `pnpm coverage`**, record failures in `baseline.txt`, and commit phase 4.

---

## Phase 5: User Story 4 — the four obstacles, measured and published (Priority: P2)

- [X] T041 [US4] Discharge **FR-013** and **SC-008**: publish the two operational candidates with the per-tenant split and T002's cause, **as the question FR-006 answers rather than as an obstacle**. There are **four** obstacles and this is not one of them — the missing producer, connection-minutes counting a different population, `uniq`'s approximation, and the TTL boundary. **The count has been wrong in both directions**: a first draft had this as the fourth, removing it left three, and analysis pass 2 measured a real fourth. Publish each with its own cause rather than generalising them.
- [X] T042 [US4] Publish R4's one-sided tenants: **0 real analytical against 675 operational**, and what the job reports for each. The four ids in the rollup are `metering.itest.ts`'s and `ingest.itest.ts`'s fixtures and exist in no Postgres row — **publish that too**, because it is the case Y2 added a verdict for and the reason the analytical side cannot be swept blind.
- [X] T042a [US4] **Measure the connection-minutes obstacle**, which is the only one on a quantity whose producer has shipped. Planning measured **80 analytical against 6,286 operational — 98.7%**, with 44 of 99 connections holding an open and no close. **Establish that it is not a history gap**: both sides start within twenty-three seconds of each other, and a first version of this finding proposed producer age as the cause and was wrong. The cause is `gaps.md` 050-5 — the meter bills every calendar minute a connection is OPEN, the records bill only connections that CLOSED, and `wss.close()` does not close established sockets by design.
- [X] T042b [US4] **Record what that means for FR-ANL-06.** The 0.1% bound cannot hold for connection-minutes while any deploy leaves opens behind, and 4.5 decided that leaving established sockets to the process exit is correct. So this is a clause that cannot be met rather than a defect to fix, which is the distinction T049 exists to keep.
- [X] T043 [US4] **Re-measure 047-1's `uniq` obstacle** — exact to roughly 60,000–65,000 distinct and off by 0.51% at 70,000, against a 0.1% bound. **It needs no corpus**: the error is a property of the sketch at a cardinality, so generate distinct values directly and read `uniqExact` against `uniq` at the cardinalities that matter. 047 loaded a corpus for it and did not have to. Carried since chapter 4.2 and filed *for this movement*.
- [X] T044 [US4] **Re-measure 047-1's TTL obstacle**: 90 of 91 days agreeing and the 91st differing by 4,941 — 0.49% at any cardinality. Chapter 4.6 measured the same effect from the other side, a view counting 242,667 over 92 days where a backfill found 239,997 over 91.
- [X] T045 [US4] Discharge **FR-012** and **SC-009**: **plant matched totals on both sides at volume, in the lane** — N tenant-periods where the analytical and operational figures agree exactly — then measure **the smallest drift the 0.1% threshold detects at that N**. §2.3 asks for *"the 0.1% figure, at a volume where 0.1% is a real threshold"*, and that is a claim about resolution rather than about agreement.
- [X] T045a [US4] **Do not use a corpus for this, and record why.** `scripts/scale/corpus.mjs` writes `applications`, `environments`, `messages` and `message_edits` and **never writes `usage_periods`** — it mentions it once, in a `count(*)` for its own report — and `load-analytics.mjs` does not touch it either. **So a corpus populates only the analytical side**, and every comparison at corpus volume is a 100% breach in the direction Y2's verdict covers. **And the obvious patch is impossible**: `usage_periods.environment_id` has a foreign key to `environments(id)` in the **lane** database while corpus environments live in `relay_corpus_<ts>`. The corpus is the wrong instrument here, not a mis-configured one — a first version of this phase used it for four tasks.
- [X] T046 [US4] Plant against **real lane environments** — there are 1,487 — rather than inventing ids, and **name those ids in every statement** (T010b): `usage_periods` and `usage_active_users` both carry the guard, and the api lane runs with bait on. An environment that exists on only one side is the case the job already reports, and using one here would measure the fixture rather than the threshold.
- [X] T047 [US4] **Cite `gaps.md` 051-2 rather than re-experiencing it.** Chapter 4.6 had to run `load-analytics.mjs` — `postgresql('${PG_HOST}', …)`, the cross-path read constitution III's first prohibition names — to measure its own clause. **This chapter does not**, because T045 plants rather than loads. The bind is real and stays 051-2's; a first version of this task recorded it as something this chapter did.
- [X] T048 [US4] **Remove the planted rows and verify both sides**, before anything else is counted. **Scoped by environment id on the Postgres side** (T010b) — an unscoped `DELETE FROM usage_periods` reaches a sentinel row and raises. The analytical side reaches three rollup tables and 4.2's inner table, and a source delete does not propagate to a materialised view's target; the operational side is `usage_periods` rows scoped to the planted environments. **A mutation is not a delete** — poll `system.mutations` for `is_done = 0` on the ClickHouse side.
- [X] T049 [US4] Discharge **FR-014**: where an obstacle makes the bound unreachable for a quantity, say so and publish no percentage that implies otherwise.
- [X] T050 [US4] Run the four lanes and commit phase 5.

---

## Phase 6: The amendments

- [ ] T051 Discharge **FR-015** and **SC-010**: close or restate `gaps.md` 047-1 and 048-1 with their current numbers. Filed *for movement IV*, carried through four features, and this is the movement.
- [ ] T052 Discharge **FR-016** and **FR-017**: amend **FR-ANL-06** where this chapter's measurements show the clause as written cannot hold. **Read the clause before amending it** — DR-11 and DR-09 were both amended on this precedent, and 4.6 found two gaps entries quoting the wrong row of the same table.
- [ ] T053 State the constitution III reading the plan's Check names: the reconciler is not billing, metering or dashboard analytics, and **an auditor confined to one side of a fence cannot check the fence**. Name the alternative readings and say which document owns the amendment. Second conflict in this family after 051-2.
- [ ] T054 Discharge **FR-018**: amend `docs/12` §3's row 8 where this chapter falsifies its one-line description. **Leave the table's first column alone** — §3 keeps the original ordinals on purpose.
- [ ] T055 [P] Check whether `docs/05-sad.md` needs the job, in the *incomplete rather than wrong* class 050 filed as FR-017a. §6.2 gained two rollups at chapter 4.6 and a checker over them is the same series' next entry.
- [ ] T056 [P] Re-check every clause this feature cites by opening the SRS rather than the artifacts. 4.6 found DR-09's second half unimplemented for three features and filed as absent twice, by two entries quoting the adjacent row.
- [ ] T057 Run `check:docs` and `check:srs` after the amendments, and commit phase 6. **Check the SRS's version header by looking at it** — `check-revision-order` reads the table and never the header, and chapter 4.6 reproduced that defect one revision after recording it.

---

## Phase 7: The numbers, and the chapter

- [ ] T058 **Fix the chapter's title and derive its slug, once.** `docs/12` calls its titles provisional and the last three chapters all shipped different ones. Three places must agree exactly: the directory, the manifest `path`, and the MDX `metadata.alternates`. Record all four strings in `baseline.txt`.
- [ ] T059 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-07/<T058's slug>/page.mdx`. **At least one `<Trap>`** (FR-021). Candidates already measured: the aggregate that hides 19 breaches, zero against zero reading as agreement, and a reconciler that may only stand on one side of the fence it checks.
- [ ] T060 Discharge **FR-020** and **SC-013**: register the chapter in `relay-tutorial/lib/tutorial.ts`. `<ChapterHeader id="4.7" />` throws on an unregistered id and **`pnpm build` is the only gate that notices** — 4.4 shipped at 112 of 112 with a site that did not build, and 4.6 reproduced it before registering.
- [ ] T061 Discharge **FR-019**: do not re-derive 4.2's rollup mechanics, 4.6's two-rollup argument, or `docs/12` §4's two-counters argument. Cite them.
- [ ] T062 [P] Put every mermaid source in `figures.ts`, never in `page.mdx`, and pass each as **`code=`**.
- [ ] T063 [P] Take every number in a figure from `baseline.txt`. No checker reads prose.
- [ ] T064 Discharge **FR-021** and **SC-012**: measure prose words outside code fences against the 2,000–4,000 bound and count the `<Trap>` boxes in the same pass. 4.6's first draft came in at 1,970 — thirty under the floor — and what closed the gap was a measurement already in `baseline.txt`.
- [ ] T065 Publish new files as whole bodies and changed ones as `diff` hunks against `part4-ch6`. **A titled fence is a whole-body claim**: 4.6 published two partial quotes with a `title=` and the chain went 110 → 113 (051-6).
- [ ] T066 Generate hunks from the checker's own replay, or from `git diff -U6 part4-ch6 -- <file>`. **Verify they apply before pasting.**
- [ ] T067 For any file T007 flagged as a vi whole body, file it rather than repairing it — an English chapter cannot fix a Vietnamese fence and the checker will not report it broken either (050-3).
- [ ] T068 Discharge **FR-022** and **SC-011**: report the fence close as a delta against T006's opening, by kind and locale, with the two HEAD classes split.
- [ ] T069 Discharge **FR-023**: run all eleven gates. **Build before `check:errors`.** Diagnose every red against T008's opening **by running the suites directly**, because the integration gate's summary hides two thirds of its failures.
- [ ] T070 Write `specs/052-chapter-4-7/gaps.md`. **Re-measure every carried item**: 051-1 through 051-6, and 050's and 048's survivors. *Measure the carried ledger; do not copy it.*
- [ ] T071 In `gaps.md`, give **051-3 its second reading** — the integration gate that reports one failure where three lanes fail. T008 and T069 both had to work around it, which is two data points rather than one.
- [ ] T072 In `gaps.md`, record what a real alert would cost (T037), and whether the reconciler's cross-store read needs a constitution amendment of its own (T053).
- [ ] T073 Audit every test this feature added and confirm none asserts only that the job ran. Record the count audited. **A conditional assertion whose condition is asserted unconditionally above it is a narrowing, not a hole.**
- [ ] T074 Write `specs/052-chapter-4-7/traceability.md` mapping every FR and SC to tasks and artifacts. **Record the requirements nothing discharged**, if any.
- [ ] T075 Rewrite `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T076 Commit phase 7, tag `part4-ch7` on `relay-platform`, and push all three repositories.

---

## Dependencies & Execution Order

```
Phase 1  premises + openings      ── blocks everything
Phase 2  the verdict, pure        ── blocks 3
Phase 3  US1 both stores          ── blocks 4
Phase 4  US2/US3 drift   🎯MVP    ── blocks 5
Phase 5  US4 the obstacles        ── needs 4
Phase 6  the amendments           ── needs 5's numbers
Phase 7  the chapter              ── needs all
```

### User story dependencies

- **US1** spans phases 3 and parts of 4 — the pins belong with the code they measure.
- **US2** and **US3** share phase 4: the drift proves detection, the alert proves it is
  observable.
- **US4** needs the MVP, because three of its four obstacles are things the job reports.

### Parallel opportunities

- Phase 1: T001, T003–T007, T009 and T010 are independent probes writing to separate sections.
- Phase 2: T018 and T019 are independent test files.
- Phase 6: T055 and T056 touch different documents.
- Phase 7: T062 and T063 are independent of each other.

---

## Implementation strategy

**MVP is phases 1–4**: a verdict with branches a unit test can drive, a job that reads both
stores per tenant, and a planted drift that raises and then does not.

**Phase 2 exists because of §2.3.** *"0.1% of a small number is an assertion that cannot fail
for its own reason"* — so the arithmetic is separated from the gathering, and the CI half runs
with no corpus and no store.

**Phase 5 is where the chapter earns its title.** Building a reconciler is a week's work in any
codebase; publishing why its first honest run fails four ways, with a number behind each, is
what makes this a chapter rather than a commit.

**Nothing in this feature makes the numbers agree.** `docs/12` §2.3 gives agreement to the
milestone at 4.9. A chapter that published a green percentage here would be the most
misleading artifact in the series, and FR-014 forbids it.

---

## Notes

**Commit each phase.**

**The analytical store has no lane guard** (050-2). Every integration test uses a dedicated
environment id and scopes every count by it; anything that plants data removes it and verifies
the removal.

**And the operational store has one that the api lane arms.** `usage_periods` and
`usage_active_users` both carry feature 030's sentinel trigger, and the api's integration config
sets `RELAY_HARNESS_BAIT: "on"`. **So both stores want the same discipline for opposite
reasons**: ClickHouse because nothing would stop an unscoped statement, Postgres because
something will.

**`pnpm test:integration` hides two thirds of its failures** (051-3). Take every gate reading
by running the suites directly.

**A mutation is not a delete.** `ALTER TABLE … DELETE` is queued; poll `system.mutations` for
`is_done = 0` before asserting a cleanup.

**The job writes nothing.** If a task makes it write, the task is wrong.
