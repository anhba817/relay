# Tasks — chapter 4.4, every request is an event

**Feature**: `specs/049-chapter-4-4/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**The order is an argument, and it is the reverse of the obvious one.** The consumer is fixed
**before** the producer exists. Publishing into a consumer that terminates the record is
shipping a defect and then fixing it, and R1 measured that the defect is invisible from both
of the instruments anyone would reach for.

**Verification methods, decided rather than defaulted.** The record-per-request claim is
**D** — demonstrated, counted both sides. The never-costs-a-response claim is **A**, by
analysis of two measured distributions, because the thing being claimed is an absence. The
tenant-isolation claim is **T**, because constitution I is the one principle this project
does not accept a demonstration for. The content prohibition is **I** — inspection of the
field list — since a test that a body is absent passes on every corpus that happens not to
contain one.

**AND THE COVERAGE CLAUSE REACHES THIS CHAPTER WHERE IT DID NOT REACH THE LAST ONE.** 048
recorded that constitution VI's 100%-branch requirement for idempotency could not apply,
because that idempotency was a `ReplacingMergeTree` sorting key and **a schema has no branches
to cover**. Here the clause names **tenant isolation**, and this chapter's tenant isolation is
a branch in TypeScript: environment present, environment absent. It is coverable, so it is
covered, and the number is published either way.

---

## Phase 1: Premises, and the numbers this feature inherited

**Everything blocks on this.** Every figure in `research.md` came from a probe run during
planning, against a stack that had just been rebuilt after 048-6. Re-run each at this
chapter's tag. A premise carried from a planning document and never re-run is what this
project finds most often, and 047 found at pass 9 of 9 that eight passes of correct
measurement had been about the wrong database.

- [ ] T001 Re-run R1 and record the four lines in `specs/049-chapter-4-4/baseline.txt`: `written 1 / malformed 1`, then `written 0 / malformed 0` after `ack_wait`, then the stream's `2 of 2` and the consumer's `num_pending 0`. **`written 1` is the positive control and must be recorded as such** — without it the probe measures a broken consumer rather than a difference between record types.
- [ ] T002 Read `services/ingester/src/shape.ts` and record in `specs/049-chapter-4-4/baseline.txt` the exact field list that makes it return `null`, and `services/ingester/src/main.ts`'s `m.term()` branch. **Read the functions, do not cite line numbers from `research.md`** — this feature's own spec shipped two citations off by one and they were caught by running them.
- [ ] T003 Re-run R4 in this environment and record in `specs/049-chapter-4-4/baseline.txt`: bytes per API request record over 1,000 records, the implied capacity at `max_bytes` 1 GiB, and the sustained requests/second at which seven days stops fitting. Planning measured **313.0 bytes → 3,430,485 records → 5.7 req/s**. Record the live `ANALYTICS` bytes-per-record beside it (planning read 476 over 37; after T005's cleanup it is **487 over 36**) so the two producers are compared rather than one asserted.
- [ ] T004 Read every record on the live `ANALYTICS` stream and record the **key sets** in `specs/049-chapter-4-4/baseline.txt`, not just the count. Measured at this feature's opening: **37** messages, 0 carrying a `type` field, in three shapes — 29 with `status`, 7 with `error` (a timeout has no status), and **1 with no keys at all**. After T005 it is **36 messages, 17,529 bytes, 487 bytes per record, 0 keyless**. Record both, because the difference is the finding.
- [ ] T005 Clear the debris: seq 32 is `analytics.probe.ping.<uuid>` carrying `{}` in 2 bytes, published 2026-09-14T00:58:31Z by **048's own probe work**, on a `probe` domain the grammar does not define. Under this chapter's routing it shapes as an attempt, fails, and terminates — so the first ingester run reports `malformed 1` **that this chapter did not cause**. Delete it or record it as a known non-zero, and do it before anything counts. *A red probe writes to the lane*: 043 left two rows behind and the next measurement read them as data contradicting the plan.
- [ ] T006 [P] Re-run R3b and record in `specs/049-chapter-4-4/baseline.txt` what each filter saw: tenant A exact **1**, tenant B exact **0**, single-token wildcard **6 of 7**. **The 6 is the finding** — the five-token `no.tenant` subject is the one the wildcard missed.
- [ ] T007 [P] Re-run R6 against Nest and record both arrangements in `specs/049-chapter-4-4/baseline.txt`: root-registered controllers give `req.baseUrl=""` and the full template; a mounted router drops the prefix; a 404 gives `undefined`. **Record that this api is the first case and why** — the controllers declare `v1` themselves.
- [ ] T008 [P] Re-run R5 against the running api and record in `specs/049-chapter-4-4/baseline.txt` that all six probe requests produced a `"msg":"request"` line, with the logged `path` for the param route quoted verbatim. **The raw channel id in that line is the reason FR-005 exists.**
- [ ] T009 [P] Count the api's routes by principal class into `specs/049-chapter-4-4/baseline.txt` — total decorators, controllers, and which carry `@Accepts({ platform: [...] })`. Planning counted 41 across 13. **Say plainly that this is a fact about the surface and not about traffic**; the volume-weighted share is T070's and they are different numbers.
- [ ] T010 [P] Run `pnpm check:fences` in `relay-tutorial` and record the opening in `specs/049-chapter-4-4/baseline.txt` **broken down by kind and locale** — APPLY and HEAD, `(en)` and `(vi)`. 047 and 048 both opened and closed at 110. Thirty live in the Vietnamese chain, which is under active translation and is not this chapter's work.
- [ ] T011 [P] Pin the environment in `specs/049-chapter-4-4/baseline.txt`: node, pnpm, the NATS and ClickHouse image tags, `SELECT version()`, **the Nest and Express versions** (11.1.28 and 5.2.1 — Express 5 is why the middleware mounts with `{*path}`), cpus, RAM, `DOCKER_HOST`.
- [ ] T012 [P] Record the analytical store's state fresh in `specs/049-chapter-4-4/baseline.txt`: `system.tables` for `relay_analytics`, the `schema_applied` ledger (tail `0003_webhook_attempts.sql`), and `webhook_attempts` row count. Record the lane's Postgres row counts beside them.
- [ ] T013 Record in `specs/049-chapter-4-4/baseline.txt` that the stack came up clean **without `--no-deps`**, with `/healthz` `{"status":"ok"}` and the container healthy. 048 closed with that gate red; this is the confirmation 048-6 was closed rather than quarantined.
- [ ] T014 Commit phase 1 — `specs/049-chapter-4-4/baseline.txt` only. No platform change yet.

---

## Phase 2: User Story 4 — the ingester stops destroying what it does not recognise (Priority: P2) — and it goes first

**Goal**: a well-formed record of a type the ingester does not write is left alone rather than
terminated.

**Independent test**: publish a record carrying an unknown `type` and show that it is neither
written as an attempt nor terminated — it is still available to a consumer after `ack_wait`.

**Why P2 work is phase 2.** Every later phase publishes onto a stream this consumer reads.
Doing it after the producer would mean a window in which the api destroys its own records, and
R1 measured that the window leaves no trace either instrument can see.

- [ ] T015 [P] [US4] Write the failing test first in `services/ingester/src/shape.test.ts`: a record with `type: "api.request"` must not be classified as malformed. **Run it red and record the failure text in `specs/049-chapter-4-4/baseline.txt`** — a test that has never failed is a test whose condition may not be reachable.
- [ ] T016 [US4] Add the routing rule to `services/ingester/src/shape.ts`: `type` absent → attempt, `type` `"api.request"` → request, anything else → not mine. Return a discriminated result rather than `AttemptRow | null`, so "unknown" and "malformed" stop being the same value.
- [ ] T017 [US4] Add the compatibility test to `services/ingester/src/shape.test.ts`: a record with **no `type` field** shapes as an attempt. **This is the load-bearing case.** The live stream holds 36 records written by a binary that never heard of `type`, and a required field its writer did not have is the mistake that terminated every in-flight `message.created` in 043.
- [ ] T018 [US4] Add the malformed test to `services/ingester/src/shape.test.ts`: a record with a known `type` and missing required fields is still malformed and still terminated. **Poison handling stays load-bearing** — 048's rule is retry forever on transport, terminate at parse, and widening "not mine" must not swallow the parse arm.
- [ ] T019 [US4] Change `services/ingester/src/main.ts` so the "not mine" arm neither acks nor terminates, and record in the batch log line how many were left. A record nobody claims must be visible as a number.
- [ ] T020 [US4] Add the integration test to `services/ingester/src/ingest.itest.ts`: publish attempt + unknown-type + malformed on one stream, run `ingestOnce` twice across `ack_wait`, and assert the unknown record **comes back** on the second pass while the malformed one does not.
- [ ] T021 [P] [US4] Re-run T001's probe against the changed consumer and record the before-and-after pair in `specs/049-chapter-4-4/baseline.txt`. SC-005 asks for it as a pair, not as an after.
- [ ] T022 [US4] Run `pnpm lint`, `pnpm typecheck` and `pnpm test` in `relay-platform`. Record failures in `specs/049-chapter-4-4/baseline.txt` rather than only the green run.
- [ ] T023 [US4] Commit phase 2.

---

## Phase 3: Foundational — the table

**Blocking for US1, US2 and US3.** Nothing can be written to a table that does not exist.

- [ ] T024 Decide `environment_id`'s nullability and record the decision **and its loser** in `specs/049-chapter-4-4/baseline.txt`: one table with `Nullable(UUID)`, or two tables. `data-model.md` §1 states both cases **and both are now measured**: the one-table arm needs `SETTINGS allow_nullable_key = 1`, and with it, three identical tenantless rows collapse to `FINAL 1` while tenant B still sees 0. **No sentinel value is on the table** — 047 measured the zero UUID producing one phantom active user per environment.
- [ ] T025 Write `analytics/0004_api_requests.sql` per `data-model.md` §1. One statement, qualified `relay_analytics.` — `apply.mjs` refuses both otherwise, and each refusal exists because the alternative was silent.
- [ ] T026 If `environment_id` is nullable, the statement **must** carry `SETTINGS allow_nullable_key = 1`. Without it ClickHouse 25.3 answers `Code: 44 … Sorting key contains nullable columns … (ILLEGAL_COLUMN)`. **The first draft of `data-model.md` omitted it and cited 047's identical finding three lines below the statement that repeated it** — and `apply.mjs`'s checksum refusal means fixing this after it is applied costs a second statement file, not an edit.
- [ ] T027 Use `TTL toDateTime(ts) + INTERVAL 30 DAY`, not `TTL ts + INTERVAL`. 047 measured the second refused with `BAD_TTL_EXPRESSION` on a `DateTime64`, after the SAD had published the broken form since its first draft.
- [ ] T028 Give `endpoint` and `limited_operation` the type `LowCardinality(Nullable(String))`. **`LowCardinality(String)` cannot say "absent"**: measured through `JSONEachRow`, an absent field and an explicit `""` both land as `''`, and the contract spends a paragraph defending exactly that distinction. This is 048's defect on a new column, and **none of its three guards reaches it** — `input_format_skip_unknown_fields=0` catches an unknown field, not an absent one, and a CHECK cannot help because absent is legal here.
- [ ] T029 Assert the three cases in an integration test: **absent → NULL, explicit `""` → `""`, a template → the template.** Two of the three are indistinguishable under the wrong column type, so a test that only checks the third passes either way.
- [ ] T030 Include the `ts_is_real` CHECK constraint. 048 measured that an absent column takes its default, a `DateTime64` default is the epoch, and the epoch is older than any TTL — **so the row is deleted at insert while the insert returns OK**.
- [ ] T031 Run `node analytics/apply.mjs` and record `applied 1: 0004_api_requests.sql` in `specs/049-chapter-4-4/baseline.txt`. Run it a second time and record `applied nothing` — SC-007, and the line `CREATE TABLE IF NOT EXISTS` cannot produce.
- [ ] T032 [P] Test the checksum refusal red: change one byte of `0004_api_requests.sql`, re-run, record the refusal text, restore. A ledger that claims a schema is applied when it is not is worse than one that has not run.
- [ ] T033 Extend `services/ingester/src/clickhouse.ts` with the second table, keeping `input_format_skip_unknown_fields=0` and `date_time_input_format=best_effort`. 048 measured all three guards catching **different** failures: `Code: 117` for a renamed field, `Code: 469` for an absent one, `Code: 27` for an ISO string under the default parser.
- [ ] T034 Give `services/ingester/src/main.ts` two row buffers on one fetch loop, and **acknowledge only after both inserts return**. 048's rule: nothing is acked until the write it belongs to has landed.
- [ ] T035 Verify the table's shape against `data-model.md` with `SHOW CREATE TABLE relay_analytics.api_requests` and record it in `specs/049-chapter-4-4/baseline.txt`. **Ask the database rather than reading the file you just wrote.**
- [ ] T036 Run the three gates and commit phase 3.

---

## Phase 4: User Story 1 — every API request leaves a record (Priority: P1) 🎯 MVP

**Goal**: a request served by the api becomes a row in the analytical store.

**Independent test**: issue a known set of requests, count them, count the rows, publish both
numbers side by side.

- [ ] T037 [P] [US1] Add `API_REQUEST_ACTION` and `apiRequestSubject(environmentId)` to `packages/protocol/src/internal.ts`, beside the webhook pair and using `analyticsSubjectFor` unchanged.
- [ ] T038 [P] [US1] Add tests to `packages/protocol/src/internal.test.ts`: the subject matches `ALL_ANALYTICS_SUBJECT`, and a non-UUID environment is refused. **Assert the refusal, not only the success** — a validator tested on valid input is a validator untested.
- [ ] T039 [US1] Write `services/api/src/request-log/event.ts` with a `toRequestEvent()` that **names every field individually**. FR-002: an allow-list fails closed when somebody adds a field and a spread fails open. 3.20's `shape()` makes the same argument in its own comment; cite it rather than restating it.
- [ ] T040 [US1] Add `publishRequest()` to `services/api/src/request-log/event.ts`, modelled on `publishAttempt` — never throws, logs once, no payload in the log line, dedup id is the request id.
- [ ] T041 [US1] Write `services/api/src/request-log/request-log.middleware.ts`: capture the start instant on entry, assemble on `res.on("finish")`, read the request id from `req.requestId` rather than minting one.
- [ ] T042 [US1] Take `endpoint` from `req.route.path` and **assert `req.baseUrl` is empty** rather than assuming it. R6 measured the same field dropping the `/v1` under a mounted router, which is the failure `request-context.middleware.ts` already carries a comment about from chapter 2.2.
- [ ] T043 [US1] Omit `endpoint` when the route is unknown **and record why it is unknown**. Absent, never `""` — `exactOptionalPropertyTypes` is on, and 3.20's comment says why an explicit `undefined` is not an absent key.
- [ ] T044 [US1] Discharge **FR-005b**: record `refused_at` — `handler` | `guard` | `middleware` | `unmatched`. **Two of those four arms are not observable from the producer — see the next task.** **`req.route` is set by the ROUTER, so a middleware refusal has no template yet — which is a different fact from having no route.** Measured: `/v1/mw429` is a defined route and records `route=undefined`; `/v1/guard429` records `route=/v1/guard429`, because a guard runs after routing.
- [ ] T045 [US1] Discharge **FR-005b1**: stamp `refused_at` in the layer that refuses. A guard refusal and a handler response are **identical at `finish`** — same status, same `req.route`, same request properties, measured. So `middleware` and `guard` are stamped; `unmatched` and `handler` are inferred from the absence of a stamp plus whether the router ran.
- [ ] T046 [US1] Stamp in `services/api/src/auth/credential.guard.ts`. **One line in one file**: it is the only class implementing `CanActivate` in this api, applied across 11 controllers, and it throws both the 401 and the `OVER_AUTH_THRESHOLD` 429.
- [ ] T047 [US1] Discharge **FR-005b2**: add a test that **fails if a guard refuses without stamping**, and put the rule where a future guard's author will meet it. The `handler` arm is an inference from silence, so an unstamped refusal is recorded as a plausible wrong value in a column nothing would flag — the fence-chain checker's shape, where the answer meaning *clean* and the answer meaning *never looked* printed the same line. 045's rule applies: **fail on an unknown member rather than trust the input.**
- [ ] T048 [US1] Assert in `services/api/src/request-log/request-log.itest.ts` that a guard 401 and a handler response of the same status record **different** `refused_at`. Without this the stamp can be absent and every test still passes.
- [ ] T049 [US1] Discharge **FR-005a**: have `services/api/src/limits/rate-limit.middleware.ts` stamp the **operation class** it decided on — `send`, `rest` or `signup` — and read it in the producer as `limited_operation`. **Not a route template.** `operationsFor` returns `[]`, `["rest"]` or `["rest", "send"]`; its whole route knowledge is three-valued, and an earlier draft of this task claimed otherwise on the strength of a function it had not opened (R20).
- [ ] T050 [US1] Take the value from **`refusal.operation`**, the single operation that tripped — not from `operationsFor`'s array. The limiter already narrows it and already names it to the customer: `rate-limit.middleware.ts:220` reads `refusal.operation === "send" ? "messages" : "requests"`.
- [ ] T051 [US1] Do **not** type the column as `LimitedOperation`. That union has three members — `rest`, `send`, `connect` — and **`connect` is unreachable here**: it is the gateway's connection limit, counted through `/internal/usage/connections`. A type that admits a value the producer cannot emit is a claim nothing checks.
- [ ] T052 [US1] Discharge **FR-005a1**: state in the chapter that a per-endpoint breakdown of rate-limit refusals is **not available, because the limiter does not limit per endpoint**. Do not build a path matcher to manufacture one — an independent matcher disagrees with the real router eventually, and constitution VII is against a second mechanism for a question that was mis-posed.
- [ ] T053 [US1] Assert both 429s in `services/api/src/request-log/request-log.itest.ts`: the rate limiter's and `CredentialGuard`'s `OVER_AUTH_THRESHOLD`. Same status, different `refused_at`, **both carrying an endpoint**. Without this the chapter ships a request log in which *"which endpoint is being rate-limited"* is unanswerable for half the 429s.
- [ ] T054 [US1] Provide `ANALYTICS_PUBLISHER` in `services/api/src/app.module.ts`. **It is currently module-private to `InternalModule`, which has no `exports:` array**, so a middleware configured in `AppModule.configure()` cannot inject it and Nest throws at boot. `internal.module.ts` states the rule twelve lines below that provider: *"a provider is visible to the module that declares it and to nothing it imports."*
- [ ] T055 [US1] Record the cost of the choice in `specs/049-chapter-4-4/baseline.txt`. A second provider with the same factory is the codebase's own precedent — `LOGGER` is provided twice for exactly this reason — but it means **two publisher instances, two NATS connections, and two `ensureAnalyticsStream` calls racing at boot**. Idempotent, and still a decision. Exporting from `InternalModule` is the alternative and couples the middleware chain to the internal seam's module; say which was taken and why.
- [ ] T056 [US1] Register the middleware in `services/api/src/app.module.ts` **second — immediately after `RequestContextMiddleware` and BEFORE `AuthenticateMiddleware`**. Not last. `RateLimitMiddleware` refuses a 429 with `res.statusCode = 429; res.end(...); return;` at two points and **never calls `next()`**, so a middleware in position 4 is never reached and a rate-limited request produces no record at all. Record the resulting chain in `specs/049-chapter-4-4/baseline.txt`.
- [ ] T057 [US1] Write down why position 2 is safe, because it is not obvious: **the listener's registration point and its read point are different moments.** Registered second, it attaches before anything can short-circuit; when `finish` fires, `AuthenticateMiddleware` has already set `req.principal` if it ran, and has not if the request never got that far. Both are correct records, and the gap between attach and read is what makes them so.
- [ ] T058 [US1] Assert it in `services/api/src/request-log/request-log.itest.ts`: drive a route past its rate limit until a **429** is served, then show the store holds a record for it. **No artifact in this feature mentioned 429 before this was added** — the spec listed the allowance-refusal as an edge case and nothing derived the placement consequence.
- [ ] T059 [P] [US1] Unit-test `toRequestEvent()` in `services/api/src/request-log/event.test.ts`: every field, the absent-`endpoint` case, and that no body, header or credential can reach the output.
- [ ] T060 [US1] Write `services/api/src/request-log/request-log.itest.ts`: issue N requests, drain with the ingester, count rows with `FINAL`, assert equality **against a non-zero floor**. 047's T023 compared three counts over an empty table and called them equal at `0, 0, 0` — a three-way equality with no floor is satisfied by nothing at all.
- [ ] T061 [US1] Discharge **FR-017**: publish one request record, let the ingester take it, force a redelivery, and assert the store's `FINAL` count is unchanged. Publish physical `count()` and `FINAL` as a pair. **FR-017 had no task until this analysis pass** — it is the idempotency requirement, and 048 gave its equivalent a dedicated test for the reason constitution VI names idempotency by name.
- [ ] T062 [US1] Run that count with `SYSTEM STOP MERGES` on the table. **A physical count taken while a background merge is running measures the merge.** This pass's own first probe read `2` after six inserts and it read as four rows vanishing; with merges stopped the same probe reads `6` physical and `2` FINAL.
- [ ] T063 [US1] Run the quickstart's §5 block verbatim and record its output in `specs/049-chapter-4-4/baseline.txt`. Constitution VI requires the quickstart to run unmodified; the way to know is to run it.
- [ ] T064 [US1] Pin the new files in `vitest.coverage.config.mts` with the observed numbers and the swing, per the ratchet rule. **Run both halves of the key-matching probe** — a per-file threshold whose key matches no file is silent.
- [ ] T065 [US1] Run the three gates and commit phase 4. **MVP ends here.**

---

## Phase 5: User Story 3 — the requests that belong to no tenant (Priority: P2)

**Goal**: a request with no resolvable environment produces a record that no tenant can reach.

**Independent test**: call an internal-seam route and a tenant route; a tenant-scoped query
returns the second and not the first.

**Depends on US1.** There is no tenantless record until there is a record.

- [ ] T066 [P] [US3] Add the tenantless subject to `packages/protocol/src/internal.ts` as **its own function** returning the `_none` token, not as a relaxed argument to `analyticsSubjectFor`. R3a measured what a permissive token does: `no.tenant` published a five-token subject, `*` published a literal asterisk, and **neither failed at publish time**.
- [ ] T067 [P] [US3] Test in `packages/protocol/src/internal.test.ts` that the tenantless subject is matched by `ALL_ANALYTICS_SUBJECT` and by **no** exact per-tenant filter.
- [ ] T068 [US3] Resolve the environment in `services/api/src/request-log/request-log.middleware.ts` from `req.principal?.environmentId`, and record `principal_kind` as `application` | `user` | `platform` | `none`. **`platform` and `none` are different facts** and collapsing them loses the chapter's central number.
- [ ] T069 [US3] Cover the tenancy branch in `services/api/src/request-log/event.test.ts` — environment present and absent — and publish the measured branch coverage beside constitution VI's 100%. **Met, or pinned with the shortfall stated as a number.** This is the clause 048 could not reach; this chapter can.
- [ ] T070 [US3] Measure the **volume-weighted** tenantless share and record it in `specs/049-chapter-4-4/baseline.txt`, split by cause. Say which traffic produced it. T009's route count is a fact about the surface; this is a fact about one workload, and the lane is the least representative instrument here.
- [ ] T071 [US3] Write the isolation test in `services/api/src/request-log/request-log.itest.ts`: a tenant-scoped read returns that tenant's rows and **zero** tenantless ones. Verification method **T**, because constitution I does not take a demonstration.
- [ ] T072 [US3] Run `specs/045-part-3-rework/check-lane-scope.py` after adding the integration tests, and record its report. Every whole-table assertion is a neighbour's problem on a lane that no longer serialises.
- [ ] T073 [US3] Run the three gates and commit phase 5.

---

## Phase 6: User Story 2 — the analytics path never costs a response (Priority: P1)

**Goal**: request latency and status are unchanged by the broker's health.

**Independent test**: two latency distributions, broker up and broker stopped, published side
by side against NFR-PRF-02's 150 ms.

- [ ] T074 [US2] Verify by inspection that the publish is not awaited on the request path, and record the call site in `specs/049-chapter-4-4/baseline.txt`. **Verification method I**: a timing test passes on a fast broker whether or not the await is there.
- [ ] T075 [US2] Discharge **FR-007**: record the latency interval's two endpoints in `specs/049-chapter-4-4/baseline.txt` and confirm `contracts/api-request-event.md` states them. Entry to the request-log middleware, to the response's `finish`. **Say what is excluded** — connection accept, TLS, request-body transfer, and any middleware registered earlier. A duration compared against another duration measures the thing that changed only if both use the same endpoints.
- [ ] T076 [US2] Measure request latency with the broker healthy — a warm-up, then the sample — and record the distribution in `specs/049-chapter-4-4/baseline.txt`. 046 published a wrong number twice by comparing a cold run against a warm one.
- [ ] T077 [US2] Stop NATS, repeat the measurement, and record both distributions. **Stop it gracefully.** 048's `EVENTS` store was left unrecoverable by an abrupt `down` mid-write, and the replacement built on the broken one inherited the failure invisibly.
- [ ] T078 [US2] Record the status codes served during the broker-down run. **Latency is half the claim**; a response that is fast and wrong satisfies a timing assertion.
- [ ] T079 [US2] Confirm the api logged its publish failure once per request and that the line carries no payload. A failure path that floods is a failure path that will be turned off.
- [ ] T080 [US2] Restart NATS, confirm `/healthz` returns `{"status":"ok"}` and the container is healthy, and record it. 048-6's lesson: the check that proves a store recovered is **a deliberate restart**, not the fact that it answered once.
- [ ] T081 [US2] Run the three gates and commit phase 6.

---

## Phase 7: The numbers, the amendments, and the chapter

**Where the chapter's argument gets its evidence, and where three published documents get
corrected.**

- [ ] T082 [P] Measure the eviction rate in this environment and record it in `specs/049-chapter-4-4/baseline.txt`: bytes per record, capacity at 1 GiB, the sustained req/s at which seven days stops fitting, and the req/s at which the SAD's 24 h stops fitting. **If the answer is that it does not bite at this platform's scale, publish that too** — SC-006 asks for the number, not for a problem.
- [ ] T083 [P] Record in `specs/049-chapter-4-4/baseline.txt` that **`/healthz` is never rate limited** (`rate-limit.middleware.ts:54` — Docker polls it every five seconds and `up -d --wait` depends on the answer). The health-check share is therefore a fact about the prober's interval alone, comparable across runs without asking what the limiter was doing. A premise that holds is evidence; record it.
- [ ] T084 [P] Record the `/healthz` share of the request log in `specs/049-chapter-4-4/baseline.txt`. R14 decided to record health checks and let the read exclude them; the share is what makes that decision visible rather than implied.
- [ ] T085 Amend **FR-ANL-07** in `docs/04-srs.md` to drop "truncated payload", with the revision-history entry the governance clause requires. R8: the clause conflicts with FR-ANL-11 and constitution VI, and `POST /messages` has a body that is message text.
- [ ] T086 Grep the amended claim everywhere before calling it done — `docs/`, `specs/`, both locales of the tutorial. **Fix the file that describes the thing and the one that instructs it.**
- [ ] T087 Amend `docs/05-sad.md` lines 184 and 919: the stream's absorption is a function of the record rate, not a constant, and the retention is seven days rather than 24 h. Give the crossover number from T082. Bump the revision and run `pnpm sync:docs` — `check:docs` failed after a SAD amendment in both 047 and 048.
- [ ] T088 Amend `docs/12-part-4-structure.md` §4's five cross-references against §3's table (R16). Add a line saying **why** they drifted — the interim 24-chapter numbering — so the next reader does not re-derive it.
- [ ] T089 Record the decision on R12 in `specs/049-chapter-4-4/baseline.txt` — one consumer or two — with T082's number as the reason. If the stream splits, R2's constraint applies: `ANALYTICS` owns `analytics.>`, so a second stream needs that list narrowed on a published stream with a live consumer.
- [ ] T090 If T089 decides **one consumer**, record the measured rate that makes one sufficient and file the crossover in `specs/049-chapter-4-4/gaps.md` as the condition under which a later chapter must revisit it. A decision that holds at today's volume is a decision with an expiry date.
- [ ] T091 If T089 decides **split the stream**, narrow `ANALYTICS`'s subjects to `analytics.webhook.>` in `ensureAnalyticsStream` **before** creating the second stream — R2 measured the broker refusing an overlapping subject space with `err_code 10065`. `subjects` is in the `mutable` set, so it is an update; the live `analytics-ingester` durable and the records already on the stream are what make it a phase rather than a line. **T089 had only one outcome staffed until this analysis pass.**
- [ ] T092 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-04/<slug>/page.mdx`. **Generalise 3.20's fire-and-forget argument, do not re-derive it** (FR-021) — and note that `docs/12` §4 pointed a writer at the wrong chapter for exactly this instruction.
- [ ] T093 Put every mermaid source in `figures.ts`, never in `page.mdx`, and take every number in a figure from `specs/049-chapter-4-4/baseline.txt`. **No checker reads prose, and a mermaid block is prose.**
- [ ] T094 Measure prose words outside code fences against the 2,000–4,000 bound and record the figure whether or not it forces a split. Every Part 4 estimate so far has been wrong downward; this chapter carries three arguments and is expected to run the other way.
- [ ] T095 Publish titled fences as **whole bodies** where the file is new, and as `diff` hunks generated from the checker's own replay where it is not. 048 shipped one as an excerpt and the chain caught it in one run.
- [ ] T096 Run `pnpm check:fences` and report the close as a **delta against T010's opening, broken down by kind and locale**. A bare total moves for reasons this chapter did not cause.
- [ ] T097 Run all eight gates. The five in `relay-tutorial` are **`check:fences`, `check:docs`, `check:srs`, `check:figures`, `check:errors`** — read off `package.json`, not remembered: an earlier draft of `quickstart.md` named `check:refs` and `check:revisions`, **and neither exists** (`pnpm check:refs` exits 254). Revision ordering lives inside `check:docs`. Then `lint`, `typecheck` and `test` in `relay-platform`. **Build before `check:errors`**; it reads the built `dist`.
- [ ] T098 Write `specs/049-chapter-4-4/gaps.md` for everything found and not closed, each entry naming what it would cost to close.
- [ ] T099 Discharge **SC-009**: audit every test this feature added and confirm none asserts only that a record was published. Idempotence, tenancy and redelivery are each asserted on what the store *holds*. **Two 204s prove nothing**, and a conditional assertion is an assertion that may not run. Record the count audited in `specs/049-chapter-4-4/baseline.txt`.
- [ ] T100 Write `specs/049-chapter-4-4/traceability.md` mapping FR-001…FR-023 and SC-001…SC-011 to tasks and to the artifacts that discharge them. **Record the requirements nothing discharged**, if any.
- [ ] T101 Rewrite `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T102 Commit phase 7, tag `part4-ch4` on `relay-platform`, and push all three repositories.

---

## Dependencies & Execution Order

```
Phase 1  premises            ── blocks everything
Phase 2  US4 consumer        ── blocks 3, 4, 5, 6   (publishing into a terminating consumer
                                                     is shipping a defect)
Phase 3  the table           ── blocks 4, 5, 6
Phase 4  US1 producer  🎯MVP ── blocks 5, 6
Phase 5  US3 tenancy         ── independent of 6
Phase 6  US2 independence    ── independent of 5
Phase 7  numbers + chapter   ── needs 4; needs 5 and 6 for its figures
```

### User story dependencies

- **US4** (P2) has no dependency and goes first, because everything else publishes past it.
- **US1** (P1) needs the table.
- **US3** (P2) needs US1 — there is no tenantless record before there is a record.
- **US2** (P1) needs US1 and is independent of US3. Phases 5 and 6 can be taken in either
  order, or together.

### Parallel opportunities

- Phase 1: T006–T012 are all `[P]` — independent probes writing to separate sections.
- Phase 4: T037 and T038 (protocol) run beside T059 (unit tests).
- Phase 5: T066 and T067 (protocol) run beside T068's middleware work.
- Phase 7: T082 and T084 are independent measurements.

---

## Implementation strategy

**MVP is phases 1–4**: a record for every request, in a table, not destroyed by the consumer
that was there first. That is a working feature and a demonstrable one.

**Phases 5 and 6 are what make it correct rather than working.** US3 is the constitution I
argument; US2 is the constitution III one. Neither is optional and both are separable from the
MVP, which is why they are their own phases rather than tasks inside phase 4.

**Phase 7 is the chapter**, and its figures come from phases 5 and 6. A chapter written before
the numbers exist is a chapter whose argument is a plan.

---

## Notes

**Commit each phase.** `git checkout` on a file with uncommitted work has destroyed work twice
in this project.

**Commits stay under five lines with no `Co-Authored-By` trailer.**

**Run `check:fences` after any source edit**, not only at the ratchet.

**The three counts that must be published as a set** (SC-001): requests issued, records
published, rows held with `FINAL`. Two of the three agreeing is the shape 047's T023 had when
it compared `0, 0, 0`.
