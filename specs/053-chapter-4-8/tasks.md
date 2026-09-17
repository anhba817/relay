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

- [X] T001 Bring the stack up on `RELAY_POSTGRES_PORT=15432` and run **all eight of the quickstart's steps as written**, recording the output of each. A quickstart nobody runs is how `CORPUS_DAYS=60` shipped, and a first draft of this task ran three of eight — which is the same defect one size down. Steps 7 and 8 are the gates and the expected reds; run them here rather than trusting T002's summary.
- [X] T001a **Open `.github/workflows/ci.yml`, which nine analysis passes did not** (FR-033, SC-021), and read **all three jobs**. The `platform` job provides `postgres:18-alpine`, `redis:8-alpine`, `nats:2.12-alpine` and **no ClickHouse** — so four suites that reach the analytical store cannot pass there (`ingest.itest.ts`, `metering.itest.ts`, `request-log.itest.ts`, `reconcile.itest.ts`) and this feature plans a fifth. **The `outsider` job is different and pass 9 missed it**: `docker compose up -d --wait` starts the whole stack, and compose's `clickhouse` carries no `profiles:` key. Pass 9 grepped `ci.yml` for the word, got 0, and published *"CI has no ClickHouse"* — **a grep for a word is not a check for a capability**, and the word lives in `compose.yaml`. Record the correction beside the finding.
- [X] T001b **Add the ClickHouse service to the `platform` job**, matching `compose.yaml` so a lane that passes locally passes there — `clickhouse/clickhouse-server:25.3`, `CLICKHOUSE_USER: relay`, `CLICKHOUSE_PASSWORD: relay`, `CLICKHOUSE_DB: relay_analytics`, port 8123 — plus `RELAY_CLICKHOUSE_HOST` in the job's `env` and a **`node analytics/apply.mjs`** step after the Postgres migration, because the schema does not exist until something applies it. **Provision rather than declare the suites local-only**: constitution VI's third bullet makes the cross-tenant suite and the scans release gates, and four chapters of analytical work being ungated is the larger of the two costs.
- [X] T001c **Unblock the two gates that sit behind the failing lane** (Y2). `pnpm test:integration` runs at `ci.yml:112`, `pnpm coverage` at `:117` and `check-error-codes.mjs` at `:135` — same job, sequential, **no `continue-on-error`** — so whenever the lane fails, constitution VI's measurable half and the error-registry gate never execute. That registry gate is the one T029a's code and catalogue entry are written for. Move `check-error-codes.mjs` above the lane (it needs only `pnpm build`, already at `:108`) and give `pnpm coverage` `if: always()`.
- [X] T001d Record what CI **still** cannot do after T001b, rather than implying it is now complete: `pnpm test:integration` is `turbo … --concurrency=1` and stops scheduling at the first failure (`gaps.md` 051-3), so a single red suite still hides every lane ordered after it — in CI exactly as locally.
- [X] T002 Record **every gate** at the opening, **each integration lane run directly**. `pnpm test:integration` plans 18 tasks, attempts 9, and prints `Tasks: 7 successful, 9 total` while three lanes never start (`gaps.md` 051-3). Use `pnpm run <script>`, never `pnpm -s` (052's instrument note).
  **THE LIST, ENUMERATED, BECAUSE THE COUNT HAS BEEN WRONG SINCE FEATURE 043.** `CLAUDE.md:1159`
  carries the lesson in capitals — *"FOURTEEN GATES, NOT ELEVEN"* — and `CLAUDE.md:288` says
  *"the only one of eleven gates that notices"*, so **the same document says both**. Features
  050, 051 and 052 each wrote "eleven". A number is the smallest possible hand-maintained table,
  and feature 045 deleted a nine-row one rather than correcting it.

      relay-platform
        1  pnpm lint
        2  pnpm typecheck
        3  pnpm test
        4  pnpm build
        5  api integration lane              --filter @relay/api
        6  gateway integration lane          --filter @relay/gateway
        7  ingester integration lane         --filter @relay/ingester
        8  test-harness integration lane     --filter @relay/test-harness
        9  pnpm coverage
       10  targets.itest.ts                  the cross-tenant gauntlet, BOTH directions
       11  check-lane-scope.py               with its positive control
       12  packages/outsider                 the sealed suite — needs RELAY_API_URL,
                                             RELAY_WS_URL and RELAY_DEMO_CREDENTIAL, and is
                                             excluded from `pnpm test:integration` by
                                             `--filter=!@relay/outsider`, so nothing else runs it
      relay-tutorial
       13  pnpm run check:docs
       14  pnpm run check:srs
       15  pnpm run check:figures
       16  pnpm build
       17  pnpm run check:errors             AFTER the build
       18  pnpm check:fences

  **Eighteen, and the number is not the point** — the list is. Anything this feature adds joins
  it, and a count nobody can check is what carried "eleven" through four chapters.
  **AND A GREEN IS NOT A PASS UNTIL IT IS SHOWN TO HAVE LOOKED.** Four of the six tutorial gates
  `exit 0` when their corpus is absent, printing a warning nobody reads on a passing step:

      check-fence-chain.mjs:199    relay-platform not found
      check-error-codes.mjs:39     reference or built protocol package not found
      check-srs-ids.sh:41          SRS not found (standalone clone?)
      check-docs-drift.sh:36       parent docs directory not found

  **The skip is correct for one caller and wrong for this one.** A standalone `relay-tutorial`
  clone should not fail on a missing sibling repository, which is why the scripts are not the
  thing to change — the gate list is. **Capture each gate's output and treat the word
  `skipping` as red.** It matters most for `check:errors`, the gate this feature added
  `analytics_unavailable` and its catalogue entry to satisfy, and which already has a second way
  to not run at all (T001c, CI's ordering).

  This is `gaps.md` 045-81 in the gates 045 did not reach: *"the zero that means clean and the
  zero that means never looked printed the same line."*
- [X] T003 Record `check:fences` with both HEAD classes split — `differs at line` against `does not exist in relay-platform` (`gaps.md` 050-4). The second class can never be repaired by editing the platform.
- [X] T004 [P] Re-measure R5's three shares: total rows, tenantless, attributed, and the `/internal` / `/v1` / other split. State the date beside them.
- [X] T005 [P] Re-measure R7's per-tenant distribution — median, p95, max, tenant count — and name the busiest tenant's id for later phases.
- [X] T006 [P] Re-measure R3's tie rate: distinct `(environment_id, ts)` pairs, pairs holding more than one row, rows inside them, worst case.
- [X] T007 [P] Read `api_requests`' TTL and `ORDER BY` from `SHOW CREATE TABLE`, not from the migration file. Chapter 4.6 read `engine_full` for a TTL, got zero, and read it as a failed `ALTER`.
- [X] T007a [P] Count active parts and duplicate keys — `count()` against `uniqExact((environment_id, ts, request_id))` — and **record that an analysis probe changed both before this phase ran**: it found 11,684 rows against 11,683 keys over 2 parts, then `OPTIMIZE TABLE … FINAL` took the table to 1 part and 0 duplicates. The probe's planted row was deleted and verified at 0. *Clean up a probe before anything is counted* arrives here as **say what the probe changed**, because the number this phase records is not the number that was there.
- [X] T008 [P] Re-measure R2's `quantile` vs `quantileExact` table **at the sizes an hour of one tenant's traffic actually has** — single digits to low hundreds — rather than only at 100–1,000,000.
- [X] T009 Confirm `message_events` still holds 0 rows and count the files under `services/` that name it. At 4.7's close there was exactly one, and it was a test's cleanup.
- [X] T010 [P] Confirm R1 by reading `services/dispatcher/src/deliver.ts` again: which two instants `latency_ms` sits between, and quote the line rather than the conclusion.
- [X] T011 List every file this feature will touch that carries a titled fence, **counted rather than remembered** — 4.5's plan and tasks both named a set wrong in both directions. Record the count per locale.
- [X] T012 Record the api integration lane's inherited reds by name, so a later phase can tell a new failure from an old one. `request-log.itest.ts` is 5 of them at 5,001 ms each (050-8) and it is chapter 4.4's suite over the table this chapter reads.

**Checkpoint**: every figure `research.md` carries is either confirmed or replaced, and the
replacements are in `baseline.txt`.

---

## Phase 2: The query contract, with no store in sight (blocks 3)

**Goal**: the half that can be unit-tested, separated for the reason chapter 4.7 separated its
verdict — a contract with branches a test can drive is worth more than one that needs Docker.

- [X] T013 Write `contracts/request-log.md`'s open decisions down as decisions: the `Accepts` scope and the `/internal/*` treatment. Both carry arguments already; this task turns them into sentences the code must satisfy. **`CredentialGuard` defaults to `EITHER` — application AND user — when no `Accepts` is present** (`credential.guard.ts:92`), so omitting the decorator is a decision to let any logged-in person in a customer's product read that customer's entire API history. There is no neutral option.
- [X] T014 [P] Add the query schema in `services/api/src/request-log/request-log.schema.ts` — `from`, `to`, `cursor`, `direction`, `limit` — **as a `z.strictObject`, mirroring `historyQuerySchema`'s form and bounds** (1–200, default 50). **Strict is the half that is easy to drop**: a plain `z.object` accepts `limt=200` silently and serves the default 50, so a caller's typo becomes a wrong answer rather than a 400. The schema being copied is strict; a first draft of this task copied its bounds and not its strictness rather than inventing a second pagination vocabulary (FR-019, FR-005). **Mirror, do not move.** `messages.schema.ts` carries 6 titled fences in each locale and is clean in the chain today; relocating the schema to a shared module would cost twelve hunks for a shape that fits in four lines.
- [X] T015 [P] Make `to` **exclusive** and `from` inclusive, and say so in a comment beside the code. Chapter 4.7's half-open day range is the precedent: *"a reconciler's off-by-one does not crash, it reports drift"*, and a log's off-by-one duplicates a row across two pages.
- [X] T015a [P] **Add `endpoint` and `status` as optional equality filters** (FR-035, SC-022). FR-DSH-03 asks for a request log *"filterable by endpoint, status, and time range"*, and EIR-DSH-02 binds the dashboard to *"only the same public API available to customers"* — so if this route does not filter, the dashboard clause is unbuildable. Time range alone is one of the three.
- [X] T015b [P] **Validate `endpoint` against the live router rather than escaping it**, because `AnalyticalStore.query` takes a SQL string and has no parameter binding — this is the sharpest caller-supplied value in the feature (R9). The mechanism already exists in this codebase and this feature already touches it: `deriveTargets(app.getHttpAdapter().getInstance())` enumerates every route template from the running application (`isolation/targets.itest.ts:40`). **A closed set derived from the router is not text reaching SQL**, and an unknown value is a 400 rather than an empty page. `status` is `UInt16`: validate as an integer in range.
- [X] T015c [P] **Add `unmatched` to the accepted set, because the router contains no route for the request that matched none** — and that is the query a 404 investigation opens the log for. Measured: **32 rows** carry `endpoint IS NULL` today. It maps to `endpoint IS NULL` in the statement and is a closed-set member like any other, so the injection argument is unchanged. **The repair that made the filter safe made it unable to ask the most diagnostic question**, which is the class this project keeps finding in its own fixes.
- [X] T015d [P] **State what a retired route costs.** The accepted set is derived from the router as it is **now**; the log holds **30 days**. A route removed in a later release leaves rows that are returned and cannot be filtered for, until they expire. Deriving the set from the data instead — `SELECT DISTINCT endpoint` in the window — would cover them and costs a query per request; record the choice and the window rather than discovering it in a support ticket.
- [X] T016 Implement the cursor as an opaque encoding of `(ts, request_id)` in `services/api/src/request-log/cursor.ts`, with decode refusing anything it did not produce.
- [X] T017 [P] Unit-test the cursor round trip, and **test the millisecond tie explicitly** — T006's measured pairs are the reason. A `ts`-only cursor skips or repeats those rows.
- [X] T018 [P] Unit-test every refusal: `limit` out of bounds on both sides, `to` before `from`, a malformed cursor, an unparseable instant, **and an unknown query parameter** — `limt=200` is a 400, not a page of 50.
- [X] T019 Clamp `from` to the retention edge rather than refusing it, and return the clamped window in the response. A caller asking for 90 days is asking a reasonable question the data cannot answer (R8, and FR-ANL-08 says 90 where FR-ANL-07 retains 30).
- [X] T020 **Write the hostile-window test first and run it red** against a version that interpolates the caller's values directly (R9). This is the first caller-supplied value this platform puts into a ClickHouse statement, and *"it is validated upstream"* is the sentence that precedes every injection.
- [X] T021 Pin `request-log.schema.ts` and `cursor.ts` in `vitest.coverage.config.mts` with freshly measured numbers and **two observations each**, and run both halves of the threshold probe — an impossible pin on a real file must fire, and a pin on a path that does not exist must be silent (045's trap, re-run at 4.7).
- [X] T022 Run lint, typecheck and the unit lane; commit phase 2.

**Checkpoint**: the contract's arithmetic runs with no store, no database and no broker.

---

## Phase 3: The reader and the route (blocks 4)

**Goal**: FR-001 — a tenant's log, read from the analytical store through the api.

- [X] T023 [US1] Add `services/api/src/request-log/reader.ts` taking a validated query plus a tenant id and returning rows, using `createAnalyticalStore` from `services/api/src/metering/clickhouse.ts`. **No second client** — that file's argument against moving the ingester's interface into `@relay/service-kit` still holds.
- [X] T023a [US1] **Give the read a deadline, because neither ClickHouse client has one** (FR-025). Both `services/api/src/metering/clickhouse.ts` and the ingester's call `fetch` with no `signal`, so a hung store holds the caller until the OS gives up. On a batch reconciler that is tolerable; **on a customer request it is the coupling constitution III's second clause forbids** — *"failure or backlog of the analytical pipeline MUST NOT affect … API availability."* The platform already has the pattern one outbound call over: `services/dispatcher/src/deliver.ts` uses `AbortSignal.timeout(timeoutMs)`.
- [X] T023b [US1] Add the deadline as an **option on `createAnalyticalStore`, defaulting to none**, so chapter 4.7's reconciler keeps the behaviour it was measured with and only this route passes one. `metering/clickhouse.ts` carries **0 titled fences in either locale**, so the edit costs the chain nothing — checked rather than assumed.
- [X] T023c [US1] **Give the deadline its second half (FR-025), because `AbortSignal` stops the caller waiting and leaves the query running.** ClickHouse keeps executing after a client abort, so a tenant retrying a slow page accumulates server-side work — the amplification the deadline exists to prevent. The server half rides in the SQL and needs no interface change: `SETTINGS max_execution_time = N`, measured against the server as `Code: 159. DB::Exception: Timeout exceeded: elapsed 1000.760448 ms, maximum: 1000 ms` returning in 1.02 s.
- [X] T023d [US1] **Set the server limit slightly SHORTER than the client's**, so the server's refusal wins the race and the caller receives `Code: 159` to map onto a status. The other ordering gives an `AbortError` with nothing in it, and a refusal that names no cause is the empty page this requirement exists to avoid.
- [X] T023e [US1] **Carry ClickHouse's HTTP status out of the client, because it already tells the two cases apart and the client throws it away.** `createAnalyticalStore` keeps only `text.trim().split("\n")[0]`, so distinguishing a timeout from a bad query means string-matching `Code: 159` — a parse of a server error message. Measured: the server answers **408** for `TIMEOUT_EXCEEDED` and **404** for an unknown identifier. Attach the status to the thrown error and map on it; keep the message for the log and never for the response (T029b).
- [X] T024 [US1] Build the statement with the tenant id as a bound value in the code's own hands, never from the request body, and with the caller's window already parsed into instants by phase 2.
- [X] T024a [US1] **Read with `FINAL`, and put the reason in the code.** `api_requests` is a `ReplacingMergeTree` keyed `(environment_id, ts, request_id)` — chapter 4.4 chose that engine because a redelivered batch writes the same request twice, and 4.5 measured `ingestOnce` reporting 16 for a stream holding 8. Measured on this lane before the read was written: **11,684 rows against 11,683 distinct keys — one duplicate, across two parts.** Without `FINAL` a page returns that request twice, so FR-007's *"no row appears in two consecutive pages"* would pass or fail on merge timing. **This is chapter 4.6's rule one engine over**: there the read contract was `sum()` with `GROUP BY`, here it is `FINAL`, and in both a query whose correctness depends on somebody having run `OPTIMIZE` is right in a demo and wrong in production.
- [X] T025 [US1] Select exactly the six fields FR-ANL-07 names, and decide in the code — with a comment — whether `principal_kind`, `refused_at` and `limited_operation` are returned. The table carries four columns the clause does not name. **FR-004 is discharged here by construction and the comment says so**: the producer never recorded a body, so no column holds one and no filter is removing anything. An assertion that cannot fail for its own reason is worth naming as one rather than writing.
- [X] T026 [US1] Return `endpoint` as **null** for an unmatched route, never `""`. Chapter 4.4 paid for that difference: `LowCardinality(String)` cannot say "absent", and 22 rows in the lane have no endpoint.
- [X] T026a [US1] **The store client cannot say null either, and the statement has to.** `AnalyticalStore.query` returns `string[][]` split from TSV, and ClickHouse writes NULL as the two characters `\N` — asked of the server: `\N<TAB>GET<TAB>200`. So a naive read reports an endpoint of `"\N"` for all 22 rows. **Select `<column> IS NULL` as its own column and let the presence column decide**, which is chapter 4.7's `count()` move against the same class of problem one table over: absence gets its own signal rather than a value that has to be interpreted.
- [X] T026b [US1] Test both arms against the real store — a row with an endpoint and a row without — and assert the second comes back as `null` rather than as any string. Run it red against a version that reads the value column alone.
- [X] T026c [US1] **Cover every nullable column the reader selects, not just `endpoint`.** `system.columns` says there are three: `environment_id` `Nullable(UUID)`, `endpoint` and **`limited_operation`**, both `LowCardinality(Nullable(String))`. `limited_operation` is the one chapter 4.4 added so a 429 says which quota class it refused on, and returned naively it reads `"\N"` for every row that is not a 429. The first version of this task named `endpoint` alone — **the fix is where the next defect is**, and this is the same class one column over.
- [X] T026d [US1] **Build the envelope this API already serves** (FR-030, FR-032): the array named for the resource and a cursor for each direction, as `messages.service.ts:327` returns `{ messages, next_cursor, prev_cursor }`. **And add `has_more`, which EIR-API-06 requires and the platform has never had** — `grep has_more` over `services/` and `packages/` returns nothing, so `messages.service.ts` has been non-conforming since chapter 2.4. It reports the direction the query ran, and the `limit + 1` fetch computes it already. **Added rather than amended away**: EIR-API-04's worked example was brought to the code in SRS 1.3 because reshaping an error body would have been breaking under CON-05, and adding a field is not, so that escape does not reach this clause. A first draft called the array `rows` and shipped one cursor beside a two-way `direction`, which leaves a caller reading `newer` with no way back. **And derive the end of the page by fetching `limit + 1` and dropping the extra**, the convention `repository.ts:3823` states — otherwise a page that exactly exhausts the window advertises a next page that is empty.
- [X] T027 [US1] Keep `latency_ms` fractional. Rounding reads `0` for three of four real requests (4.4, measured).
- [X] T028 [US1] Add `services/api/src/request-log/request-log.controller.ts` with `@UseGuards(CredentialGuard)` and T013's `Accepts` decision, wired into the module graph. **Import `ZodValidationPipe` from `services/api/src/messages/zod-validation.pipe.ts`; do not move it.** That file carries **3 titled fences in each locale** and relocating it to a shared directory costs six hunks for an import statement — the same trade T014 makes with `messages.schema.ts`.
- [X] T028a [US1] **Classify the route in the cross-tenant gauntlet, in the same phase that registers it** (FR-029, SC-018). Constitution I's fourth bullet is a MUST — *"an automated cross-tenant access test suite MUST attack every endpoint with foreign IDs on every build; a build that fails this suite MUST NOT ship"* — and `services/api/src/isolation/targets.ts` derives its targets **from the live router** (`targets.itest.ts:40`). Its own comment: *"NOTHING MAY BE EXEMPT BY OMISSION. A derived target matching no entry fails the suite, and an entry matching no derived target fails it too."* **So the suite goes red the moment the controller exists**, in this lane, in this phase.
- [X] T028b [US1] The classification is `{ method: "GET", path: "/v1/request-log", accepts: "application", shape: "list" }`, and `GET /v1/webhooks` at `targets.ts:134` is the precedent word for word: *"There is no identifier in the path at all — the tenant comes from the key — so what the attack shows is that a key for one environment sees none of another's endpoints in a 200."* **The shape is the one thing no derivation can make**, which is why the file exists at all; write the argument beside the entry rather than the entry alone.
- [X] T028c [US1] Run `targets.itest.ts` and the gauntlet suites directly, **both directions** — a derived target with no entry, and an entry matching no target. The second is the one that catches a stale exemption after a rename, and it is why adding the entry without running the suite proves nothing.
- [X] T028d [US1] Record the fence cost: `services/api/src/isolation/targets.ts` carries **6 titled fences in each locale** and is **already a HEAD problem at line 130**, so this edit is invisible to `check:fences` — the fourth file in this feature with that property, after `app.module.ts`, `vitest.coverage.config.mts` and `codes.ts`. T072 collects them.
- [X] T029 [US1] Refuse a principal carrying no `environmentId` with 403 rather than answering an empty page (FR-011). A `platform` principal carries none **by design** and its own comment says the absence is what stops it being usable where a tenant is expected.
- [X] T029a [US1] **Add the refusal's error code where the registry lives, and document it, in this phase** (FR-026, SC-015). `ProtocolErrorFilter` maps a status onto a code from `ERROR_CODES` in `packages/protocol/src/codes.ts`, and `scripts/check-error-codes.mjs` compares that registry against `docs/08-error-reference.md` **in both directions**. The catalogue holds no 503 and no service-unavailable entry today. **Leave this to phase 7 and `check:errors` goes red at T073 for work that belongs here** — the gate fires five phases after the cause.
- [X] T029a1 [US1] **Registering the code is necessary and not sufficient: name it on the throw.** `ProtocolErrorFilter`'s status ladder covers **400, 401, 403 and 404 only**, so a 503 falls past it into the fallback. The mechanism that works is the one the filter's own comment describes — a `code` on the thrown `HttpException`, **checked against the registry rather than trusted**, because "a thrower can put any string in `code`". Throw with the code named.
- [X] T029a2 [US1] Note in the task's own words that **`docs_url` is derived from the code**, so the catalogue entry is load-bearing rather than documentation hygiene: an undocumented code ships a customer a link to a page that cannot exist. The filter's comment records that four of five codes it could emit were once unregistered for exactly that reason.
- [X] T029b [US1] Name the code for what a client does about it, which is the test this registry sets on itself — its own comment argues three refusals apart because *"a client acts on them differently"*. `analytics_unavailable` says which subsystem is out and that the request is worth retrying, where a bare `internal_error` says neither. **The message names the subsystem and never the store's answer**: `Code: 159 … elapsed 1000.760448 ms` in a customer response is infrastructure detail in a support ticket, which is the argument `codes.ts` already makes about credentials (NFR-SEC-06).
- [X] T029c [US1] `packages/protocol/src/codes.ts` carries **12 titled fences in each locale and is already a HEAD problem at line 209**, so this edit costs the fence chain nothing visible — checked, not assumed, and recorded beside `app.module.ts` in T072's list of edits the checker cannot see.
- [X] T030 [US1] Write the integration suite at **`services/api/src/request-log/query.itest.ts`**, with a `beforeAll` positive control — ask the store `SELECT 1` before trusting anything else it says. **`request-log.itest.ts` is taken**: 201 lines of chapter 4.4's end-to-end suite, the source of the five reds T012 catalogues, and the file this feature's own opening measures. Writing to it would delete the evidence phase 1 collects.
- [X] T031 [US1] Plant rows for this suite's own environment ids — **every statement naming them, which is FR-024** — and **verify the cleanup by count**, not by issuing the delete. `ALTER TABLE … DELETE` is a queued mutation, and 4.7 found a row from an earlier run still in the table because the fire-and-forget form leaves no evidence it ran.
- [X] T032 [US1] Assert the six fields come back for a planted tenant, newest first (FR-006, SC-001) — and assert the order against the contract's stated `direction` rather than against whatever the engine happened to return.
- [X] T033 Run lint, typecheck and the api integration lane directly; record failures against T012's list; commit phase 3.

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
- [ ] T035c [US1] **Stand up what the sealed suite needs, in this phase, because nothing else in phases 1–4 does.** The lanes boot the app in process and the quickstart's step 1 is `docker compose up -d` — stores only. `packages/outsider` needs a running api and gateway and a seeded tenant. **Copy CI's `outsider` job rather than paraphrasing it** (`ci.yml:36–58`):

      RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
      DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
      RELAY_POSTGRES_PORT=15432 docker compose --profile services build
      RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
      RELAY_DEMO_CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
      export RELAY_DEMO_CREDENTIAL RELAY_API_URL RELAY_WS_URL

  **The seed PRINTS the credential to stdout** — *"stdout is the interface"* — so it is captured, not exported afterwards, and it takes `RELAY_POSTGRES_PORT` rather than `DATABASE_URL` for that call. A first version of this task wrote *"then `node scripts/seed-demo-tenant.mjs`, then export"*, which fails at the shell: **it cited CI's job as the model and did not copy it.** *Copy the shape, not the sentence.*

  **A test written here and first run at T073 is a test nobody has seen fail.**
- [ ] T035d [US1] **Add the route to the sealed outsider suite** (FR-038, SC-025). `packages/outsider/src/integrate.itest.ts` is the customer's-eye pass over the public API — channels, private channels, members, tokens, bots, both send refusals, REST send and history read, socket delivery, attachments — run in CI's third job against a stack it does not start. A new `/v1` endpoint belongs in it, and `outsider` appears in no artifact of this feature.
- [ ] T035e [US1] **Let the sealed result be the demonstration rather than skipping the route.** `grep ingester compose.yaml` returns 0, so even the sealed stack drains nothing and the log comes back empty there. A customer's-eye test that shows an empty log **because the platform ships no ingester** is worth more than one that omits the endpoint — and it is the same finding as FR-028's freshness gap, arriving where a customer would meet it.
- [ ] T036 [US2] Assert two consecutive pages hold different rows and that no row appears in both (FR-007, SC-004), using the cursor the first response returned. **Assert `has_more` on both pages** (SC-020): true on the first, false on the last, and false on a page that exactly exhausts the window — which is the case the `limit + 1` fetch exists for.
- [ ] T036a [US2] Assert both filters against the real store (FR-035, SC-022): a planted 429 and a planted 200 for one tenant, filtered by `status`, then by `endpoint`, then by both — and **an unknown `endpoint` refused with 400 rather than answered with an empty page**, which is the same distinction FR-010 draws for the retention edge. **And `endpoint=unmatched`**: plant a row with a null endpoint and assert it comes back under that value and under no other.
- [ ] T036b [US2] Measure what the filters cost — rows read against rows returned, beside T041's unfiltered figure. `ORDER BY (environment_id, ts, request_id)` indexes neither column, so the filter runs inside the granule the tenant predicate already selected; publish the number rather than the reassurance.
- [ ] T037 [US2] Assert the window excludes rows outside it **from both sides** (FR-008, SC-005) — a row exactly at `from` is in, a row exactly at `to` is out.
- [ ] T038 [US2] Assert the `limit` bound is enforced against the real route, both at the maximum and above it (FR-005).
- [ ] T039 [US3] Implement and assert the `/internal/*` decision (FR-009, SC-006). Whichever way it went, the test names the behaviour rather than describing the filter.
- [ ] T039a [US3] **Decide, and assert, that reading the log spends the tenant's REST budget** (FR-027, SC-016). `operationsFor` returns `["rest"]` for **every** path under `/v1` — there is no route list and no exemption, so the new route is counted the moment it exists and nobody chose that. **Leave it counted**, and say why: an exemption list is a hand-maintained table, which is the thing feature 045 deleted rather than corrected when nine ports came from hand-allocated bands and two of them collided with services the lane runs. Assert the count with a test so the decision is visible rather than inherited.
- [ ] T039b [US3] **Publish the loop that follows from it.** A customer investigating 429s reads their request log; the reads spend the budget they are investigating; and the log then shows the 429s the reading caused. That is the chapter's, not a defect to route around.
- [ ] T039c [US3] **Measure that reading the log writes to the log, and decide what the surface does about it.** `RequestLogMiddleware` records on `res.on("finish")` for every request including GETs, so each page adds a row that appears in the next one. Read a page, read it again, and publish the difference. **Give the measurement a positive control first**: with no ingester draining, the difference is **zero**, and zero reads as *"the surface excludes its own reads"* when it means *"nothing filled the table."* Assert the row arrived before concluding anything from its absence — this is the instrument defect that has cost this project a wrong published conclusion more than once. Then choose: excluding `/v1/request-log` from its own answer makes the log incomplete against FR-ANL-01's *"every request"*, and including it means a reader sees their own reads — **the same trade as the `/internal/*` decision, one route over**, and it is asserted by a test either way.
- [ ] T040 [US3] Assert "no requests in this window" is distinguishable from "outside retention" (FR-010, SC-002's sibling). Measured at R8: a 120–60 day window returns `0`, which is the same answer as a quiet period.
- [ ] T040a [US3] **Assert the refusal when the store does not answer** (FR-025, FR-032, SC-014, SC-020, and **EIR-API-04's five fields**: `code`, `message`, `docs_url`, `request_id`, and `field` where one applies, top-level and not nested — asserted rather than the status alone). Point the reader at a dead address, or at a deadline short enough to expire, and assert the route returns the stated status rather than hanging or reporting an empty log. **An empty page is the dangerous wrong answer here**: it says the tenant made no requests, which is a claim about them rather than about the platform. The spec listed this as an edge case from the first draft and no requirement covered it until analysis pass 3.
- [ ] T040b [US3] **Measure how far behind the log actually is** (FR-028, SC-017), which is the FR-ANL-04 verification this chapter is the natural place for: *"analytical events shall be available for query within 60 seconds of the originating operation under normal conditions."* Make a request, poll the surface for it, and record the time — the same shape chapter 4.5 used for `close -> row readable` (min 2.0 s, p50 5.7, max 5.8). **The measurement needs an ingester running and `compose.yaml` has none** (050-8, and `grep ingester compose.yaml` returns 0), so the task starts one and says it did. Without it the poll times out and the number is about the lane rather than about the platform. The command is `RELAY_NATS_URL=… pnpm --filter @relay/ingester dev` — `services/ingester/package.json` carries `dev` and `start`, and `main.ts` reads `RELAY_NATS_URL` with the ClickHouse address defaulting to localhost. **Starting one drains `ANALYTICS` for every other suite on the lane**, which is the same class of lane-wide side effect as `SYSTEM STOP MERGES`: say what it drained, stop it when the measurement is done, and take the figure in one pass rather than leaving it running.
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
- [ ] T055a **Amend FR-DSH-03, whose twin was amended without it** (FR-036, SC-023). The clause asks the dashboard for a request log *"with full request and response detail"*; **FR-ANL-07 was amended at SRS 1.11 to forbid recording bodies at all**, for two reasons that reach further than the one clause — FR-ANL-11 keeps message content out of the analytical store and constitution VI keeps it out of logs — and **EIR-DSH-02 forbids the dashboard from getting them anywhere else**. The three cannot all hold.
- [ ] T055b Carry 1.11's own sentence into the amendment rather than writing a new argument: *"a request log with no payload cannot answer what exactly did they send, only what did they call and what happened."* That revision **stated the loss and did not propagate it**, which is this project's recurring shape — DR-09's second half filed as absent twice, `FR-003a` cited as a clause in two documents. **An amendment that fixes one clause and leaves its twin standing is the defect, not the clause.**
- [ ] T056 Record FR-ANL-08's 90 days against FR-ANL-07's 30 where the two are read over this table, and amend whichever the measurement falsifies (FR-016).
- [ ] T056a **Write ADR-26: the api serves a customer request from the analytical store** (FR-031, SC-019). Constitution VII: *"Every architecture decision is recorded as an ADR stating its drivers, rejected alternatives, and reversal condition."* The SAD holds 25, through ADR-25. **Chapter 4.7's precedent does not cover this**: that chapter put ClickHouse behind a batch job, where an unbounded wait costs a job that was slow anyway. This one puts it on the request path and invents a failure mode the platform did not have — a 503 on a customer route when the store is slow.
- [ ] T056b The rejected alternatives are already measured and go in as measurements: a client-side deadline alone (R17 — the query keeps running), `LIMIT BY` instead of `FINAL` (R13 — it silently changes what `LIMIT` counts), and serving the log from Postgres (constitution III's first sentence forbids it, and the producer writes nowhere else).
- [ ] T056c **State the reversal condition, which is the part nobody has written.** An ADR without one is a decision with no exit: name the signal that would make the platform undo this — the analytical store's availability showing up in the API's error budget is the candidate, and FR-025's 503 is what would make it visible.
- [ ] T056d **Write it in BOTH documents** — `docs/05-sad.md`'s summary and `docs/06-adr-deep-dives.md`'s argument. Chapter 4.5 found ten analysis passes amending the SAD's summary of ADR-07 and none opening the 98-line deep dive, which held the two lines that chapter falsified.
- [ ] T057 [P] Amend `docs/12` §3's row 9 where this chapter falsifies its one-line description (FR-018). **Leave the table's first column alone** — §3 keeps the pre-contraction ordinals on purpose.
- [ ] T057a [P] Correct `docs/07-tutorial-plan.md` §6, which says CI *"runs both lanes **against real stores**"* — false for the analytical store since chapter 4.2 introduced it, and the sentence is the basis for calling defense 1 closed. T001b is what makes it true; the document should say when it became so.
- [ ] T057b [P] Fix `docs/07` §3's Part 4 heading, which reads *"23 chapters"* where Part 4 is 22, and `docs/12` §3's heading, which reads the same. **Known and disclaimed** — §3 says *"where they disagree, 12 is newer"* — so this is tidying a recorded staleness rather than a discovery, and the two headings are fixed together or not at all.
- [ ] T058 [P] Add the query surface to `docs/05-sad.md`'s data view, and **re-check its FR-ANL-10 sentence at :758** — it says the column has no producer *"until FR-ANL-10"*, which this chapter either satisfies or falsifies.
- [ ] T058a [P] **Cite the external interface requirements, and record why nobody did for eight analysis passes.** Across all artifacts this feature named two non-FR identifiers — NFR-SEC-06 and NFR-SEC-09 — and **zero EIR**, while SRS §3 is titled *"External interface requirements"* and this chapter adds an external interface. Bind EIR-API-03 (503 is in its status list), 04 (the five error fields), 05 (`X-Request-Id`, set centrally by `request-context.middleware.ts`), 06 (`has_more`) and 07 as a forward note.
- [ ] T059 [P] Re-check every clause this feature cites by opening the SRS rather than the artifacts. Chapter 4.7's pass found a citation pointing at nothing and a sentence its own feature had already falsified.
- [ ] T060 Bump the SRS revision and **check the version header by looking at it** — `check-revision-order` reads the table and never the header, and 1.13 reproduced that defect one revision after recording it.
- [ ] T061 Run `sync:docs`, then `check:docs` and `check:srs`, and commit phase 6. `check:docs` goes red first when the mirrors are stale, which is correct.

---

## Phase 7: The numbers, and the chapter

- [ ] T062 **Fix the chapter's title and derive its slug, once.** Three places must agree exactly: the directory, the manifest `path`, and the MDX `metadata.alternates`. Record all four strings in `baseline.txt`.
- [ ] T063 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-08/<T062's slug>/page.mdx`. **At least one `<Trap>` and at least one `<Why>`** (FR-021, FR-034). `docs/07-tutorial-plan.md` §4 Rule 3 governs every chapter — *"every chapter cites its paperwork. Each `WHY` box links the code being written to its requirement ID and ADR"* — and all three shipped Part 4 chapters carry exactly one `<Why>`. **This is the first with an ADR of its own to link**: ADR-26, written at T056a. Candidates already measured: a customer's own log opening on the gateway's internal calls, a page that reads 8,194 rows to return 50, and a percentile function with no exact regime.
- [ ] T063a **Decide the `<Checkpoint>` question rather than inheriting it.** `docs/07` §6 builds defense 1 on `CHECKPOINT` blocks run against each chapter's tag; 4.5 and 4.6 each carry one and **4.7 shipped with none**. A convention that lapsed once lapses silently twice. Either reinstate it here or record in `gaps.md` that the component was retired, with the date it last appeared.
- [ ] T064 Discharge **FR-020** and **SC-013**: register the chapter in `relay-tutorial/lib/tutorial.ts`. **Assert the anchor is unique before editing** — 4.4's edit matched two anchors, was refused, and `pnpm build` said `Error: Unknown chapter id: 4.4` at 112 of 112 with eight gates green.
- [ ] T064a **Say in the chapter what this log cannot answer, and name the journey that asks it** (FR-037, SC-024). `docs/03-journey-map.md`'s Stage 8 — Operate lists the pain point as *"no way to trace a specific user's reported problem"* and the opportunity as *"per-user and per-channel message tracing for support investigations."* **`api_requests` carries no user and no channel** — `environment_id, ts, request_id, endpoint, method, status, latency_ms, principal_kind, refused_at, limited_operation` — so the producer records what KIND of principal called and never which one. **This log answers "what did this tenant call and what happened"; the journey asks "what happened to this user", and those are different questions.** FR-ANL-07's six fields never asked for the second, so this is a motivating document naming a capability no requirement carried rather than a clause anyone broke.
- [ ] T064b In `gaps.md`, file the journey-map gap with what closing it would cost: a column on `api_requests`, a producer change in chapter 4.4's `event.ts`, a migration, and the tenancy question 4.4 answered by recording `principal_kind` instead of an identity. **Not this chapter's to build**, and this is the chapter that found it.
- [ ] T065 Discharge **FR-019**: do not re-derive 4.2's store mechanics, 4.4's producer or 4.7's verdict arithmetic. Cite them.
- [ ] T066 [P] Put every mermaid source in `figures.ts`, never in `page.mdx`, and pass each as **`code=`**.
- [ ] T067 [P] Take every number in a figure from `baseline.txt`. No checker reads prose.
- [ ] T068 Discharge **FR-021** and **SC-012**: measure prose words outside code fences against the 2,000–4,000 bound with `scripts/prose-words.mjs`, and count the `<Trap>` boxes in the same pass.
- [ ] T069 Publish new files as whole bodies and changed ones as `diff` hunks against `part4-ch7`. **A titled fence is a whole-body claim** (051-6), and **a `diff` fence carries the `@@` hunks only** — 4.7 lost two attempts to the `--- a/` and `+++ b/` headers.
- [ ] T069a **Correct the published claim that `limit` clamps, which it has never done**, found while executing T014 and scheduled here because the repair is a fence-chain edit. Chapter 2.4 publishes *"the page cap clamps rather than rejects, so a client asking for 500 gets 200 and a cursor instead of a lecture"* in prose AND in the code comment inside its `diff` fence. `z.coerce.number().int().min(1).max(200)` is a validation, not a transform: measured, `limit=500` is `too_big` and a 400. **The comment appears in EIGHT fences across FOUR chapters in each locale** — 2.4 adds it, and 3.11, 3.17 and 3.18 carry it as `diff` CONTEXT, so changing the tree's comment without changing all of them unanchors six hunks. Fix the words rather than the code: nothing in the tree asserts either behaviour, the refusal is what customers' clients have been written against since 2.4, and this chapter's own surface refuses `limit` for a reason it states (`resolveWindow`'s comment). Measure the chain delta either side and file it in `gaps.md` if the repair is deferred.
- [ ] T070 Generate hunks from `git diff -U6 part4-ch7 -- <file>` or from the checker's own replay, and **verify they apply before pasting**.
- [ ] T071 For any file T011 flagged as carrying a Vietnamese fence, file it rather than repairing it — an English chapter cannot fix a Vietnamese fence and the checker will not report it broken either (050-3).
- [ ] T072 Discharge **FR-022** and **SC-011**: report the fence close as a delta against T003's opening, by kind and locale, with the two HEAD classes split. **Name the three CLEAN fenced files this feature edits, because they are the only ones the checker can see**: `packages/outsider/src/integrate.itest.ts` (phase 1, T035d edits it), and `services/api/src/isolation/attack.ts` and `services/api/src/isolation/gauntlet.itest.ts` — phase 3 edited both and the chain went 110 → 112, delta +2, naming them at `attack.ts:135` and `gauntlet.itest.ts:10`. **And name `services/api/src/app.module.ts` explicitly.** It carries 11 titled fences in each locale, this chapter must edit it to register the controller, and it is **already** a HEAD problem — `differs at line 20` — so the edit will read as costing nothing while the file drifts further. That is 4.7's `vitest.coverage.config.mts` measured in advance instead of discovered at the close.
- [ ] T073 Discharge **FR-023**: run **every gate T002 enumerated**, the sealed outsider suite included, **and refuse a skip as a pass** — capture each gate's output and treat `skipping` as red, for the four that exit 0 with an absent corpus. **Build before `check:errors`**, which is the one where a skip is indistinguishable from success and where this feature's own error code is verified. Diagnose every red against T002's opening by running the suites directly.
- [ ] T073a Discharge **SC-010**: re-take T004, T005 and T006's measurements at the close and publish them beside the opening figures with any movement. Chapter 4.7's opening numbers changed while its own phases ran, because the integration lanes write to the store this chapter reads — and this feature plants rows in it deliberately.
- [ ] T074 Write `specs/053-chapter-4-8/gaps.md`. **Re-measure every carried item**: 052's seven, and 051's, 050's and 048's survivors. *Measure the carried ledger; do not copy it.*
- [ ] T074a In `gaps.md`, record the tension the **next** chapter inherits, **with the figure that makes it measurable**: constitution V says *"every metered unit is visible in the dashboard the moment it is counted"*, III says billing, metering and dashboard analytics *"read only from the analytical store … fed via a durable queue"*, and **FR-DSH-02 puts a number on it — *"API calls as they occur, with a latency under 2 seconds"*, against FR-ANL-04's 60**. EIR-DSH-02 binds the dashboard to this API, so the 2 seconds is a claim about the route this chapter builds. **Immediacy and a queue cannot both hold**, and the gap is 30x rather than rhetorical. It is not this route's problem — a request log is not a metered unit — but this chapter is the first customer-facing read of that store, and the usage dashboard is the next one. File it forward so that chapter inherits a question rather than discovering one, the way 047-1 was filed for movement IV.
- [ ] T074b In `gaps.md`, file the two EIR gaps this chapter uncovered and does not close. **EIR-API-06's `has_more` is absent from `messages.service.ts`** — the platform's other list endpoint, non-conforming since chapter 2.4, and not this chapter's file to change (6 titled fences per locale). **And EIR-API-07** — *"an OpenAPI 3.1 specification shall be published, machine-readable and complete for every public endpoint"* (P4) — has no implementation anywhere in the tree, and this chapter grows the surface it would have to cover by one route.
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
