# Tasks: chapter 4.8, "the log a customer can search"

**Input**: Design documents from `specs/053-chapter-4-8/`
**Prerequisites**: `plan.md`, `research.md`, `data-model.md`, `contracts/request-log.md`,
`quickstart.md`

**Tests are part of the deliverable.** The chapter's subject is what a query surface may say,
and every claim about that is an assertion or it is prose.

**Every statement against `api_requests` names its own environment ids.** The analytical store
has no lane guard (`gaps.md` 050-2) and this feature plants rows in it.

---

## Phase 1: Premises and openings (blocks everything)

**Goal**: measure what this feature will be measured against, and check the premises
`research.md` was written on. Chapter 4.7's opening figures moved while its own phases ran.

- [ ] T001 Bring the stack up on `RELAY_POSTGRES_PORT=15432` and run the quickstart's steps 1–3 **as written**, recording the output. A quickstart nobody runs is how `CORPUS_DAYS=60` shipped.
- [ ] T002 Record the eleven gates at the opening, **each integration lane run directly**. `pnpm test:integration` plans 18 tasks, attempts 9, and prints `Tasks: 7 successful, 9 total` while three lanes never start (`gaps.md` 051-3). Use `pnpm run <script>`, never `pnpm -s` (052's instrument note).
- [ ] T003 Record `check:fences` with both HEAD classes split — `differs at line` against `does not exist in relay-platform` (`gaps.md` 050-4). The second class can never be repaired by editing the platform.
- [ ] T004 [P] Re-measure R5's three shares: total rows, tenantless, attributed, and the `/internal` / `/v1` / other split. State the date beside them.
- [ ] T005 [P] Re-measure R7's per-tenant distribution — median, p95, max, tenant count — and name the busiest tenant's id for later phases.
- [ ] T006 [P] Re-measure R3's tie rate: distinct `(environment_id, ts)` pairs, pairs holding more than one row, rows inside them, worst case.
- [ ] T007 [P] Read `api_requests`' TTL and `ORDER BY` from `SHOW CREATE TABLE`, not from the migration file. Chapter 4.6 read `engine_full` for a TTL, got zero, and read it as a failed `ALTER`.
- [ ] T007a [P] Count active parts and duplicate keys — `count()` against `uniqExact((environment_id, ts, request_id))` — and **record that an analysis probe changed both before this phase ran**: it found 11,684 rows against 11,683 keys over 2 parts, then `OPTIMIZE TABLE … FINAL` took the table to 1 part and 0 duplicates. The probe's planted row was deleted and verified at 0. *Clean up a probe before anything is counted* arrives here as **say what the probe changed**, because the number this phase records is not the number that was there.
- [ ] T008 [P] Re-measure R2's `quantile` vs `quantileExact` table **at the sizes an hour of one tenant's traffic actually has** — single digits to low hundreds — rather than only at 100–1,000,000.
- [ ] T009 Confirm `message_events` still holds 0 rows and count the files under `services/` that name it. At 4.7's close there was exactly one, and it was a test's cleanup.
- [ ] T010 [P] Confirm R1 by reading `services/dispatcher/src/deliver.ts` again: which two instants `latency_ms` sits between, and quote the line rather than the conclusion.
- [ ] T011 List every file this feature will touch that carries a titled fence, **counted rather than remembered** — 4.5's plan and tasks both named a set wrong in both directions. Record the count per locale.
- [ ] T012 Record the api integration lane's inherited reds by name, so a later phase can tell a new failure from an old one. `request-log.itest.ts` is 5 of them at 5,001 ms each (050-8) and it is chapter 4.4's suite over the table this chapter reads.

**Checkpoint**: every figure `research.md` carries is either confirmed or replaced, and the
replacements are in `baseline.txt`.

---

## Phase 2: The query contract, with no store in sight (blocks 3)

**Goal**: the half that can be unit-tested, separated for the reason chapter 4.7 separated its
verdict — a contract with branches a test can drive is worth more than one that needs Docker.

- [ ] T013 Write `contracts/request-log.md`'s open decisions down as decisions: the `Accepts` scope and the `/internal/*` treatment. Both carry arguments already; this task turns them into sentences the code must satisfy. **`CredentialGuard` defaults to `EITHER` — application AND user — when no `Accepts` is present** (`credential.guard.ts:92`), so omitting the decorator is a decision to let any logged-in person in a customer's product read that customer's entire API history. There is no neutral option.
- [ ] T014 [P] Add the query schema in `services/api/src/request-log/request-log.schema.ts` — `from`, `to`, `cursor`, `direction`, `limit` — **mirroring** `historyQuerySchema`'s bounds (1–200, default 50) rather than inventing a second pagination vocabulary (FR-019, FR-005). **Mirror, do not move.** `messages.schema.ts` carries 6 titled fences in each locale and is clean in the chain today; relocating the schema to a shared module would cost twelve hunks for a shape that fits in four lines.
- [ ] T015 [P] Make `to` **exclusive** and `from` inclusive, and say so in a comment beside the code. Chapter 4.7's half-open day range is the precedent: *"a reconciler's off-by-one does not crash, it reports drift"*, and a log's off-by-one duplicates a row across two pages.
- [ ] T016 Implement the cursor as an opaque encoding of `(ts, request_id)` in `services/api/src/request-log/cursor.ts`, with decode refusing anything it did not produce.
- [ ] T017 [P] Unit-test the cursor round trip, and **test the millisecond tie explicitly** — T006's measured pairs are the reason. A `ts`-only cursor skips or repeats those rows.
- [ ] T018 [P] Unit-test every refusal: `limit` out of bounds on both sides, `to` before `from`, a malformed cursor, an unparseable instant.
- [ ] T019 Clamp `from` to the retention edge rather than refusing it, and return the clamped window in the response. A caller asking for 90 days is asking a reasonable question the data cannot answer (R8, and FR-ANL-08 says 90 where FR-ANL-07 retains 30).
- [ ] T020 **Write the hostile-window test first and run it red** against a version that interpolates the caller's values directly (R9). This is the first caller-supplied value this platform puts into a ClickHouse statement, and *"it is validated upstream"* is the sentence that precedes every injection.
- [ ] T021 Pin `request-log.schema.ts` and `cursor.ts` in `vitest.coverage.config.mts` with freshly measured numbers and **two observations each**, and run both halves of the threshold probe — an impossible pin on a real file must fire, and a pin on a path that does not exist must be silent (045's trap, re-run at 4.7).
- [ ] T022 Run lint, typecheck and the unit lane; commit phase 2.

**Checkpoint**: the contract's arithmetic runs with no store, no database and no broker.

---

## Phase 3: The reader and the route (blocks 4)

**Goal**: FR-001 — a tenant's log, read from the analytical store through the api.

- [ ] T023 [US1] Add `services/api/src/request-log/reader.ts` taking a validated query plus a tenant id and returning rows, using `createAnalyticalStore` from `services/api/src/metering/clickhouse.ts`. **No second client** — that file's argument against moving the ingester's interface into `@relay/service-kit` still holds.
- [ ] T023a [US1] **Give the read a deadline, because neither ClickHouse client has one** (FR-025). Both `services/api/src/metering/clickhouse.ts` and the ingester's call `fetch` with no `signal`, so a hung store holds the caller until the OS gives up. On a batch reconciler that is tolerable; **on a customer request it is the coupling constitution III's second clause forbids** — *"failure or backlog of the analytical pipeline MUST NOT affect … API availability."* The platform already has the pattern one outbound call over: `services/dispatcher/src/deliver.ts` uses `AbortSignal.timeout(timeoutMs)`.
- [ ] T023b [US1] Add the deadline as an **option on `createAnalyticalStore`, defaulting to none**, so chapter 4.7's reconciler keeps the behaviour it was measured with and only this route passes one. `metering/clickhouse.ts` carries **0 titled fences in either locale**, so the edit costs the chain nothing — checked rather than assumed.
- [ ] T024 [US1] Build the statement with the tenant id as a bound value in the code's own hands, never from the request body, and with the caller's window already parsed into instants by phase 2.
- [ ] T024a [US1] **Read with `FINAL`, and put the reason in the code.** `api_requests` is a `ReplacingMergeTree` keyed `(environment_id, ts, request_id)` — chapter 4.4 chose that engine because a redelivered batch writes the same request twice, and 4.5 measured `ingestOnce` reporting 16 for a stream holding 8. Measured on this lane before the read was written: **11,684 rows against 11,683 distinct keys — one duplicate, across two parts.** Without `FINAL` a page returns that request twice, so FR-007's *"no row appears in two consecutive pages"* would pass or fail on merge timing. **This is chapter 4.6's rule one engine over**: there the read contract was `sum()` with `GROUP BY`, here it is `FINAL`, and in both a query whose correctness depends on somebody having run `OPTIMIZE` is right in a demo and wrong in production.
- [ ] T025 [US1] Select exactly the six fields FR-ANL-07 names, and decide in the code — with a comment — whether `principal_kind`, `refused_at` and `limited_operation` are returned. The table carries four columns the clause does not name. **FR-004 is discharged here by construction and the comment says so**: the producer never recorded a body, so no column holds one and no filter is removing anything. An assertion that cannot fail for its own reason is worth naming as one rather than writing.
- [ ] T026 [US1] Return `endpoint` as **null** for an unmatched route, never `""`. Chapter 4.4 paid for that difference: `LowCardinality(String)` cannot say "absent", and 22 rows in the lane have no endpoint.
- [ ] T026a [US1] **The store client cannot say null either, and the statement has to.** `AnalyticalStore.query` returns `string[][]` split from TSV, and ClickHouse writes NULL as the two characters `\N` — asked of the server: `\N<TAB>GET<TAB>200`. So a naive read reports an endpoint of `"\N"` for all 22 rows. **Select `<column> IS NULL` as its own column and let the presence column decide**, which is chapter 4.7's `count()` move against the same class of problem one table over: absence gets its own signal rather than a value that has to be interpreted.
- [ ] T026c [US1] **Cover every nullable column the reader selects, not just `endpoint`.** `system.columns` says there are three: `environment_id` `Nullable(UUID)`, `endpoint` and **`limited_operation`**, both `LowCardinality(Nullable(String))`. `limited_operation` is the one chapter 4.4 added so a 429 says which quota class it refused on, and returned naively it reads `"\N"` for every row that is not a 429. The first version of this task named `endpoint` alone — **the fix is where the next defect is**, and this is the same class one column over.
- [ ] T026b [US1] Test both arms against the real store — a row with an endpoint and a row without — and assert the second comes back as `null` rather than as any string. Run it red against a version that reads the value column alone.
- [ ] T027 [US1] Keep `latency_ms` fractional. Rounding reads `0` for three of four real requests (4.4, measured).
- [ ] T028 [US1] Add `services/api/src/request-log/request-log.controller.ts` with `@UseGuards(CredentialGuard)` and T013's `Accepts` decision, wired into the module graph. **Import `ZodValidationPipe` from `services/api/src/messages/zod-validation.pipe.ts`; do not move it.** That file carries **3 titled fences in each locale** and relocating it to a shared directory costs six hunks for an import statement — the same trade T014 makes with `messages.schema.ts`.
- [ ] T029 [US1] Refuse a principal carrying no `environmentId` with 403 rather than answering an empty page (FR-011). A `platform` principal carries none **by design** and its own comment says the absence is what stops it being usable where a tenant is expected.
- [ ] T030 [US1] Write the integration suite at **`services/api/src/request-log/query.itest.ts`**, with a `beforeAll` positive control — ask the store `SELECT 1` before trusting anything else it says. **`request-log.itest.ts` is taken**: 201 lines of chapter 4.4's end-to-end suite, the source of the five reds T012 catalogues, and the file this feature's own opening measures. Writing to it would delete the evidence phase 1 collects.
- [ ] T031 [US1] Plant rows for this suite's own environment ids — **every statement naming them, which is FR-024** — and **verify the cleanup by count**, not by issuing the delete. `ALTER TABLE … DELETE` is a queued mutation, and 4.7 found a row from an earlier run still in the table because the fire-and-forget form leaves no evidence it ran.
- [ ] T032 [US1] Assert the six fields come back for a planted tenant, newest first (FR-006, SC-001) — and assert the order against the contract's stated `direction` rather than against whatever the engine happened to return.
- [ ] T033 Run lint, typecheck and the api integration lane directly; record failures against T012's list; commit phase 3.

**Checkpoint**: a tenant's log comes back through the route, against the real store.

---

## Phase 4: What the log can and cannot show 🎯 MVP (Priority: P1)

**Goal**: the assertions that make the surface a product claim rather than a query.

- [ ] T034 [US1] Plant rows for two tenants and assert **on the second tenant's rows** that none appear in the first's answer (FR-002, SC-002). A total is not an isolation test — 4.4's form is the one that holds.
- [ ] T035 [US1] Plant a row with a NULL `environment_id` and assert it is unreachable from every tenant's query (FR-003, SC-003). 60.5% of the lane's log is in that state.
- [ ] T035a [US1] **Plant the same request twice and assert the SURFACE returns it once** (FR-007's real failure mode), and **run it red against a statement without `FINAL`**. The duplicate this lane held was removed by a merge, so the test makes its own.
  **Copy the whole of 049's shape, not the half that names the hazard** — `services/ingester/src/ingest.itest.ts:299–336`: `SYSTEM STOP MERGES relay_analytics.api_requests`, then `try`, and in a **`finally`** both `SYSTEM START MERGES` **and** a `DELETE FROM … WHERE environment_id = toUUID('<this probe's own id>')`. Feature 050's T056 says why in as many words: *"an earlier version of this task named only the stop, which is the one step with a lane-wide side effect."* A failed assertion between stop and end leaves `api_requests` never collapsing duplicates for every other suite — **and `ingest.itest.ts:300` already stops merges on this exact table, while the api lane runs `maxWorkers: 2`.**
  **Keep the physical count as the positive control**, the way 049 does: assert physical 2 and surface 1. Without it the test passes when the insert never happened.
- [ ] T035b [US1] Say in the test's own comment **what this proves that `ingest.itest.ts:299` does not.** That test proves the ENGINE collapses a duplicate key; this one proves the SURFACE does — a reader that dropped `FINAL` would leave 049's test green and this chapter's page wrong.
- [ ] T036 [US2] Assert two consecutive pages hold different rows and that no row appears in both (FR-007, SC-004), using the cursor the first response returned.
- [ ] T037 [US2] Assert the window excludes rows outside it **from both sides** (FR-008, SC-005) — a row exactly at `from` is in, a row exactly at `to` is out.
- [ ] T038 [US2] Assert the `limit` bound is enforced against the real route, both at the maximum and above it (FR-005).
- [ ] T039 [US3] Implement and assert the `/internal/*` decision (FR-009, SC-006). Whichever way it went, the test names the behaviour rather than describing the filter.
- [ ] T040 [US3] Assert "no requests in this window" is distinguishable from "outside retention" (FR-010, SC-002's sibling). Measured at R8: a 120–60 day window returns `0`, which is the same answer as a quiet period.
- [ ] T040a [US3] **Assert the refusal when the store does not answer** (FR-025, SC-014). Point the reader at a dead address, or at a deadline short enough to expire, and assert the route returns the stated status rather than hanging or reporting an empty log. **An empty page is the dangerous wrong answer here**: it says the tenant made no requests, which is a claim about them rather than about the platform. The spec listed this as an edge case from the first draft and no requirement covered it until analysis pass 3.
- [ ] T041 [US1] Measure rows read against rows returned for a page, and publish it beside FR-ANL-08's bound with **the clause the measurement is made against named** (FR-015, SC-007). R6 measured 8,194 read for 50 returned — one granule, the engine's floor.
- [ ] T041a [US1] Measure what `FINAL` costs, **against a table with more than one part.** An analysis probe measured 8,192 rows and 2.43 ms plain against 2.02 ms with `FINAL` — on a single-part table, because the probe that found the duplicate had merged it. `FINAL`'s cost is a function of part count, so the best case was measured and it proves nothing. Record the part count beside the timing.
- [ ] T042 [US1] Record that **FR-ANL-08's 90-day window is unreachable in this table at any volume**, which is stronger than the lane being small. Measured: two rows inserted for a dedicated environment id at `now() - 60 DAY` and `now() - 1 DAY` left **one survivor**, and forcing a merge changed nothing — the 30-day TTL removes rows at INSERT (4.2's finding, reproduced here). So there is no fixture that makes the clause meaningful over this table. **The first version of this task said "plant a tenant at a volume where the clause means something"; the schema refuses it.** Record the measurement and hand the clause to FR-016 rather than building a fixture that cannot exist. And do not publish a p95 from the 208-row tenant and call the clause discharged.
- [ ] T043 [US1] Pin `reader.ts` and `request-log.controller.ts` in `vitest.coverage.config.mts` with two observations each, and run both halves of the threshold probe.
- [ ] T044 Sweep every per-file pin against the include and exclude globs over the real tree and record the count. **Give the sweep a positive control**: 4.7's first run named 17 pins unbindable and all 17 were real files, because `git ls-files 'services/*/src/**/*.ts'` misses files sitting directly in a `src/`.
- [ ] T044a Run `check-lane-scope.py` over the tree after the new integration suite exists, and **give it a positive control** — 049-3 found it hardcoding a worktree feature 045 had deleted, so its glob matched nothing and it exited 0 with all ten of its own controls firing. **A control that proves the checker works says nothing about whether it looked.** This feature plants rows in a table three chapters share.
- [ ] T045 Run the four lanes **and `pnpm coverage`**, record failures in `baseline.txt`, and commit phase 4. The coverage lane reports on a red run now (`reportOnFailure`, added at 4.7), so the pins bind.

**Checkpoint**: a customer can read their own log, paged and windowed, and cannot read anyone
else's. This is the MVP.

---

## Phase 5: The percentile requirement, resolved rather than approximated (Priority: P2)

**Goal**: FR-ANL-10's quantity is defined before anything computes it.

- [ ] T046 [US4] Publish the three readings of "end-to-end delivery latency" with the instants each needs and what exists for it today (FR-012, SC-008). R1's table is the starting point; verify each row rather than copying it.
- [ ] T047 [US4] Quote `deliver.ts`'s two lines — `const started = Date.now()` before the fetch and `const latencyMs = Date.now() - started` after it — as the evidence that `webhook_attempts.latency_ms` is the last leg only. `analytics/0003_webhook_attempts.sql:20` said so at the time and nothing has checked since.
- [ ] T048 [US4] Choose one reading, write it into the SRS as the definition FR-ANL-10 was missing, and record the two not chosen with what each would cost.
- [ ] T049 [US4] Publish T008's `quantile` vs `quantileExact` table at the bucket sizes FR-ANL-10 produces (FR-014). **`quantile` has no exact regime** — 0.9896% at n=100 — which is the opposite shape from 4.7's `uniq`, and the reason is worth one sentence rather than a generalisation about sketches.
- [ ] T050 [US4] If the chosen reading has a source that exists: compute p50, p95 and p99 per tenant per hour using `quantileExact`, and publish `n` beside them — a p99 over four samples is a maximum wearing a percentile's name.
- [ ] T051 [US4] If it does not: record what building the producer would cost, in the same terms chapter 4.6 used to defer it — a send-path change on the busiest path in the platform — and amend the clause instead (FR-013).
- [ ] T052 [US4] Publish no percentile under a label naming a quantity it does not measure (FR-014, SC-009). This is the task that fails the phase if T050 was taken for the wrong reading.
- [ ] T053 [US4] Close or restate `gaps.md` 048-2, carried through five features and re-measured at 0 files at 4.7's close. **Re-measure it here rather than copying the re-measurement.**
- [ ] T054 Run the four lanes and commit phase 5.

---

## Phase 6: The amendments

- [ ] T055 Amend **FR-ANL-10** to what the platform can produce, or to the definition it was missing (FR-017). **Read the clause before amending it** — 4.7 found `FR-003a` cited as a clause in two published documents and there is no `FR-003` in the SRS.
- [ ] T056 Record FR-ANL-08's 90 days against FR-ANL-07's 30 where the two are read over this table, and amend whichever the measurement falsifies (FR-016).
- [ ] T057 [P] Amend `docs/12` §3's row 9 where this chapter falsifies its one-line description (FR-018). **Leave the table's first column alone** — §3 keeps the pre-contraction ordinals on purpose.
- [ ] T058 [P] Add the query surface to `docs/05-sad.md`'s data view, and **re-check its FR-ANL-10 sentence at :758** — it says the column has no producer *"until FR-ANL-10"*, which this chapter either satisfies or falsifies.
- [ ] T059 [P] Re-check every clause this feature cites by opening the SRS rather than the artifacts. Chapter 4.7's pass found a citation pointing at nothing and a sentence its own feature had already falsified.
- [ ] T060 Bump the SRS revision and **check the version header by looking at it** — `check-revision-order` reads the table and never the header, and 1.13 reproduced that defect one revision after recording it.
- [ ] T061 Run `sync:docs`, then `check:docs` and `check:srs`, and commit phase 6. `check:docs` goes red first when the mirrors are stale, which is correct.

---

## Phase 7: The numbers, and the chapter

- [ ] T062 **Fix the chapter's title and derive its slug, once.** Three places must agree exactly: the directory, the manifest `path`, and the MDX `metadata.alternates`. Record all four strings in `baseline.txt`.
- [ ] T063 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-08/<T062's slug>/page.mdx`. **At least one `<Trap>`** (FR-021). Candidates already measured: a customer's own log opening on the gateway's internal calls, a page that reads 8,194 rows to return 50, and a percentile function with no exact regime.
- [ ] T064 Discharge **FR-020** and **SC-013**: register the chapter in `relay-tutorial/lib/tutorial.ts`. **Assert the anchor is unique before editing** — 4.4's edit matched two anchors, was refused, and `pnpm build` said `Error: Unknown chapter id: 4.4` at 112 of 112 with eight gates green.
- [ ] T065 Discharge **FR-019**: do not re-derive 4.2's store mechanics, 4.4's producer or 4.7's verdict arithmetic. Cite them.
- [ ] T066 [P] Put every mermaid source in `figures.ts`, never in `page.mdx`, and pass each as **`code=`**.
- [ ] T067 [P] Take every number in a figure from `baseline.txt`. No checker reads prose.
- [ ] T068 Discharge **FR-021** and **SC-012**: measure prose words outside code fences against the 2,000–4,000 bound with `scripts/prose-words.mjs`, and count the `<Trap>` boxes in the same pass.
- [ ] T069 Publish new files as whole bodies and changed ones as `diff` hunks against `part4-ch7`. **A titled fence is a whole-body claim** (051-6), and **a `diff` fence carries the `@@` hunks only** — 4.7 lost two attempts to the `--- a/` and `+++ b/` headers.
- [ ] T070 Generate hunks from `git diff -U6 part4-ch7 -- <file>` or from the checker's own replay, and **verify they apply before pasting**.
- [ ] T071 For any file T011 flagged as carrying a Vietnamese fence, file it rather than repairing it — an English chapter cannot fix a Vietnamese fence and the checker will not report it broken either (050-3).
- [ ] T072 Discharge **FR-022** and **SC-011**: report the fence close as a delta against T003's opening, by kind and locale, with the two HEAD classes split. **Name `services/api/src/app.module.ts` explicitly.** It carries 11 titled fences in each locale, this chapter must edit it to register the controller, and it is **already** a HEAD problem — `differs at line 20` — so the edit will read as costing nothing while the file drifts further. That is 4.7's `vitest.coverage.config.mts` measured in advance instead of discovered at the close.
- [ ] T073 Discharge **FR-023**: run all eleven gates. **Build before `check:errors`.** Diagnose every red against T002's opening by running the suites directly.
- [ ] T073a Discharge **SC-010**: re-take T004, T005 and T006's measurements at the close and publish them beside the opening figures with any movement. Chapter 4.7's opening numbers changed while its own phases ran, because the integration lanes write to the store this chapter reads — and this feature plants rows in it deliberately.
- [ ] T074 Write `specs/053-chapter-4-8/gaps.md`. **Re-measure every carried item**: 052's seven, and 051's, 050's and 048's survivors. *Measure the carried ledger; do not copy it.*
- [ ] T075 In `gaps.md`, record whether the `/internal/*` decision left FR-ANL-01's *"every request"* or FR-ANL-07's *"per tenant"* served less well, and which. One of them is, whichever way it went.
- [ ] T076 In `gaps.md`, give `052-3` its second reading if this chapter touched the ingester suite's cleanup, and record whether `052-2`'s `shape.ts` pin is still failing.
- [ ] T077 Audit every test this feature added and confirm none asserts only that the route answered. Record the count audited. **Read every title beside its body** — 4.7's audit found one claiming *"however much analytical data exists"* over a test that planted none.
- [ ] T078 Write `specs/053-chapter-4-8/traceability.md` mapping every FR and SC to tasks and artifacts. **Record the requirements nothing discharged**, and any discharged in a weaker form than their words suggest.
- [ ] T079 Rewrite `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T080 Commit phase 7, tag `part4-ch8` on `relay-platform`, and push all three repositories.

---

## Dependencies & Execution Order

```
Phase 1  premises + openings         ── blocks everything
Phase 2  the contract, pure          ── blocks 3
Phase 3  US1 the reader and route    ── blocks 4
Phase 4  US1/US2/US3     🎯MVP       ── blocks 5
Phase 5  US4 the percentile          ── needs 4's shape, not its data
Phase 6  the amendments              ── needs 5's decision
Phase 7  the chapter                 ── needs all
```

### User story dependencies

- **US1** spans phases 3 and 4 — the route is built once and asserted once.
- **US2** is phase 4's paging and window tasks; it needs US1's route and nothing else.
- **US3** is phase 4's two honesty tasks — the `/internal` decision and the retention edge.
- **US4** is phase 5 alone, and it needs the MVP's shape rather than its data: the percentile
  question is about a quantity, not about the log.

### Parallel opportunities

- Phase 1: T004–T008 and T010 are independent probes writing to separate sections.
- Phase 2: T014, T017 and T018 are independent files.
- Phase 6: T057, T058 and T059 touch different documents.
- Phase 7: T066 and T067 are independent of each other.

---

## Implementation strategy

**MVP is phases 1–4**: a customer reads their own request log, paged and windowed, and cannot
reach another tenant's rows or the 60.5% that belong to nobody.

**Phase 2 exists for the reason chapter 4.7's did.** The contract's arithmetic — the window,
the cursor, the bounds, the refusals — is the half a unit test can drive, and separating it is
what lets the lane check it without a store.

**Phase 5 may end with nothing computed, and that is a complete outcome.** FR-ANL-10 names a
quantity this platform has never defined. Defining it, recording the readings not taken, and
amending the clause is the work; a percentile over the wrong column would be the failure.
