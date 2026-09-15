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

- [ ] T001 [P] Re-run R1's two operational counters into `specs/052-chapter-4-7/baseline.txt`: `messages` joined to `channels` against `usage_periods.messages_sent`, aggregate and **per tenant**, with the count of tenants over 0.1%. Planning measured 9,650 / 9,624 / 0.2694% aggregate, 100% worst tenant, 19 over the bound. **The per-tenant figures are the ones that decided the design**, so a re-run that only reproduces the aggregate has not checked the premise.
- [ ] T002 **Find the cause of the 26, which R1 left open.** `repository.ts:4214` is the one `insert(messages)` and it increments `usagePeriods` at `:4344` in the same transaction, on the inserted branch only. Something else writes messages: the gap is entirely inside the current period, and 31 environments carry it at an identical 70-against-68. **A regular shape is a code path, not noise** — find it before the chapter describes the gap, because "two counters disagree" and "one writer bypasses the counter" are different chapters.
- [ ] T003 [P] Re-run R4's tenant counts: environments in `daily_usage_billing` against environments in `usage_periods`. Planning measured 4 against 675.
- [ ] T004 [P] Re-run R3 against the server rather than the plan: `usage_periods`' columns, and whether `usage_active_users` holds what the active-users comparison needs. Planning read `environment_id, period, messages_sent, created_at, connection_minutes`.
- [ ] T005 [P] Record which quantities have an operational counterpart and which do not, as the opening for FR-007. **The stored message count has none** — confirm it rather than carry it.
- [ ] T006 [P] Measure the fence-chain OPENING with `pnpm check:fences`, **by kind and locale, and with the two HEAD classes split**. 4.6's close was 110 — APPLY 74 (30 en, 30 vi, 14 elsewhere), HEAD 36, split 25 `differs at line` against 11 `does not exist`.
- [ ] T007 [P] Count the fenced-file exposure for **every file this chapter will touch**, in both locales, and record which are whole bodies. 4.6 found two of eleven carrying Vietnamese whole bodies and both already stale (050-3), which the checker never reports.
- [ ] T008 Take the eleven gates' opening colours **by running the suites directly, not by reading turbo's summary**. `pnpm test:integration` reports one `FAIL` line against `Tasks: 6 successful, 9 total` and the api lane prints no test output at all (051-3). Known inherited at 4.6's close: `request-log.itest.ts` 5 of 5 (050-8), `limits.itest.ts`, and `reset-lane.itest.ts` under load.
- [ ] T009 [P] Record `periodOf`'s definition and a closed period to use for every measurement in this feature. **Never the current month** — its rollup is still being written and its counter still incremented.
- [ ] T010 [P] Record both stores' retention: the rollups at 25 months (chapter 4.6, DR-09) and `message_events` at 90 days. This bounds what the job can verify, and R8 says it is the design rather than a fault.
- [ ] T011 Commit phase 1 — `baseline.txt` only. No platform change yet.

---

## Phase 2: Foundational — the verdict, with no store in sight

**Blocks every user story.** §2.3's CI half needs a comparison that runs without a corpus, and
this is it: two numbers, a threshold, and a source name in; a verdict out.

- [ ] T012 Write the verdict function in `relay-platform/services/api/src/metering/reconcile.ts`: given an analytical total, an operational total (either possibly null), and a threshold, return one of `pass`, `breach`, `not-comparable`, `no-data`.
- [ ] T013 The threshold is a **named constant citing FR-ANL-06**, not a literal (FR-009). A number with a clause beside it is the difference between a decision and a guess.
- [ ] T014 The percentage is `abs(a - o) / max(a, o)`, **not divided by the operational side**. 671 tenants have an operational total of zero for some quantities, and a zero denominator is a crash where a verdict belongs.
- [ ] T015 The percentage is **null whenever either side is null** (`data-model.md`). A number computed against an absent counterpart reads as a measurement and is not one.
- [ ] T016 A quantity with no operational counterpart at all returns `not-comparable`, and **both sides absent returns `no-data`**. Discharge **FR-004** and **SC-006**: zero against zero is not agreement.
- [ ] T017 **Data on exactly one side is a `breach`, not `no-data`.** R4 measured 671 tenants in that state, and calling it missing data would let the platform's largest defect read as an absence.
- [ ] T018 [P] Write `reconcile.test.ts` — unit, no store. Cover all four verdicts and **both sides of the tolerance boundary** (FR-011): a difference just over the threshold breaches and one just under passes.
- [ ] T019 [P] Assert the null-percentage rule and the `max()` denominator with a case where the operational side is zero, which is the one that would have divided by zero.
- [ ] T020 Run `lint`, `typecheck` and `test`, and commit phase 2. **`test` is the lane that matters here** — this phase adds no integration surface.

---

## Phase 3: User Story 1 — the job reads both stores (Priority: P1)

**Goal**: for one tenant and one closed period, every FR-ANL-05 quantity gets both totals, a
named operational source, a percentage and a verdict.

**Independent test**: call it against the lane and read its report.

- [ ] T021 [US1] Discharge **FR-001** and **SC-001**: extend `reconcile.ts` with the gathering: analytical totals from `relay_analytics.daily_usage_billing` over HTTP, operational totals from Postgres. **Not `daily_usage_v2`** — 147,534 rows against 281 for the same data (chapter 4.6), and the reconciler has no use for the channel dimension.
- [ ] T022 [US1] Discharge **FR-002** and **SC-004**: the job takes a tenant and an explicit period and **returns its report as a value**. `docs/12` row 8 says *"callable in isolation"*, and §2.3's CI half plants a drift and needs something to assert on.
- [ ] T023 [US1] Discharge **FR-003**, **FR-005** and **SC-007**: every breach carries its reason where one is known, and every row names the operational table it used. Two candidates disagree by 0.2694%, so a report that does not say which one it read is asserting the other does not exist.
- [ ] T024 [US1] Discharge **FR-006**: choose `usage_periods.messages_sent` over a count of `messages`, and record the reason from the code rather than from preference — `repository.ts:4325`, *"a read over `messages` … proportional to lifetime traffic forever"*, which 4.1 measured at 585.9 ms over 1,000,000 rows. **Publish the rejected candidate's gap.**
- [ ] T025 [US1] Discharge **FR-007**: do the same for every other quantity, or state that it has only one candidate. Active users comes from `usage_active_users`; connection-minutes from `usage_periods.connection_minutes`; the stored count has no operational side at all.
- [ ] T026 [US1] **One tenant per call.** A sweep is a loop in the caller. R1 measured that aggregating across tenants turns 19 breaches into 0.2694%, which is why this is a constraint rather than a convenience.
- [ ] T027 [US1] Write `scripts/reconcile-usage.mjs` as a thin caller — R5's shape, the one `reset-lane.mjs` and `consumer-walk.mjs` already use. It exits non-zero on any breach.
- [ ] T028 [P] [US1] Write `reconcile.itest.ts`: run the job against the lane for a dedicated environment id and assert the report's shape for all four quantities. **A dedicated id and every count scoped by it** — the analytical store has no lane guard (050-2), and five chapters now write it from tests.
- [ ] T029 [US1] Discharge **SC-005**: two invocations with the same arguments return the same report, asserted. The job writes nothing, and that is the property that makes it safe to run.
- [ ] T030 [US1] Assert tenancy in both directions: a second environment's totals are unreachable from the first's filter.
- [ ] T031 [US1] Run the four lanes and commit phase 3.

---

## Phase 4: User Story 2 and 3 — the planted drift 🎯 MVP (Priority: P1)

**Goal**: §2.3's CI half. A deliberate discrepancy is detected, and the same assertion is shown
not firing once it is removed.

- [ ] T032 [US2] Plant a drift larger than the threshold on one side for a dedicated tenant, run the job, and assert it raises for that tenant and quantity (FR-010, SC-002).
- [ ] T033 [US2] **Remove the drift and assert it does not raise.** Both halves, because a check that only ever fires is not a check — and this project has run the coverage-threshold probe both ways five times for the same reason.
- [ ] T034 [US2] Exercise the tolerance boundary from both sides at integration scale as well as in the unit test (FR-011, SC-003).
- [ ] T035 [US2] Clean the planted drift up and **verify the cleanup**, before anything else is counted. A mutation is not a delete — chapter 4.6's suite read three creations where it had planted two, because `ALTER TABLE … DELETE` is queued.
- [ ] T036 [US3] Discharge **FR-008**: the raise is observable by a test rather than only by a human reading output. Assert on the returned report and on the caller's exit code.
- [ ] T037 [US3] Record what "raises an alert" cannot mean here: there is no alerting integration, and the one notification path is `quotas/quota-email.ts`, whose failure mode is already in the lane as `quotas.unaddressable: no member has an email address`. **A notification with no recipient is not an alert** — name what a real one would cost.
- [ ] T038 [US1] Pin `services/api/src/metering/reconcile.ts` in `vitest.coverage.config.mts` with freshly measured numbers, **two observations**, and **run both halves of the threshold probe**. Unlike chapter 4.6's read this file has real branches, so constitution VI's clause has something to bind to.
- [ ] T039 [US1] Sweep every per-file pin against the include and exclude globs and record the count. 4.6 measured 50 pins, 50 binding. **Expand the globs over the real tree** rather than pattern-matching in memory.
- [ ] T040 [US1] Run all four lanes **and `pnpm coverage`**, record failures in `baseline.txt`, and commit phase 4.

---

## Phase 5: User Story 4 — the four obstacles, measured and published (Priority: P2)

- [ ] T041 [US4] Discharge **SC-008**: publish R1's two operational counters with the per-tenant split and T002's cause (FR-013).
- [ ] T042 [US4] Publish R4's one-sided tenants: 4 analytical against 675 operational, and what the job reports for each of the 671.
- [ ] T043 [US4] **Re-measure 047-1's `uniq` obstacle** at today's corpus: exact to roughly 60,000–65,000 distinct, off by 0.51% at 70,000, against a 0.1% bound. Carried since chapter 4.2 and filed *for this movement*.
- [ ] T044 [US4] **Re-measure 047-1's TTL obstacle**: 90 of 91 days agreeing and the 91st differing by 4,941 — 0.49% at any cardinality. Chapter 4.6 measured the same effect from the other side, a view counting 242,667 over 92 days where a backfill found 239,997 over 91.
- [ ] T045 [US4] Discharge **SC-009**: load a corpus for **FR-012's measurement at a volume where 0.1% is a real threshold**. §2.3: *"0.1% of a small number is an assertion that cannot fail for its own reason."* Set every value explicitly — `CORPUS_DAYS` must **exceed** 90 or the script refuses, and 4.6 shipped `CORPUS_DAYS=60` in a quickstart having never run it.
- [ ] T046 [US4] `corpus.mjs` writes its report to stdout and `load-analytics.mjs` requires `--corpus <corpus.json>`; capture the first and pass it to the second. 4.6's quickstart omitted the flag.
- [ ] T047 [US4] **Record the bind this creates.** The loader is `postgresql('${PG_HOST}', …)`, the cross-path read constitution III's first prohibition names, and `gaps.md` 051-2 already carries it. The chapter measures its own clause by running what the clause forbids, for the second feature running.
- [ ] T048 [US4] **Remove the corpus and verify both directions**, before anything else is counted. It reaches three rollup tables and 4.2's inner table, and a source delete does not propagate to a materialised view's target.
- [ ] T049 [US4] Discharge **FR-014**: where an obstacle makes the bound unreachable for a quantity, say so and publish no percentage that implies otherwise.
- [ ] T050 [US4] Run the four lanes and commit phase 5.

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

**`pnpm test:integration` hides two thirds of its failures** (051-3). Take every gate reading
by running the suites directly.

**A mutation is not a delete.** `ALTER TABLE … DELETE` is queued; poll `system.mutations` for
`is_done = 0` before asserting a cleanup.

**The job writes nothing.** If a task makes it write, the task is wrong.
