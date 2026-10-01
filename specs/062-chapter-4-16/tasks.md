# Tasks — Chapter 4.16, "Storage on the bill"

**Feature**: `specs/062-chapter-4-16/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

Nine phases. Commit each one.

**Read before starting.** `research.md` R1 explains why `shape.ts` is phase 2 and not phase 5 —
the ingester does not claim a type it does not know, and a record from an unknown producer is
**redelivered for seven days while nothing reaches ClickHouse and nothing fails** — 049's
repair, which replaced 4.4's outright termination. The probe asserts the current behaviour. R2 found that
the bucket listing already works with the existing signer and that pagination does not. R5 is
the chapter's argument and its numbers.

---

## Phase 1: Setup — the numbers this chapter is compared against

- [X] T001 Bring the stores up and record what answers: `cd relay-platform && RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`. Seven containers. If NATS comes up unhealthy it **names one unrecoverable stream at a time** (058-7) — clear them one at a time; the bulk form was refused by this environment's guard.
- [X] T002 Record the opening `check:fences` figure as an **absolute number**, run in `relay-tutorial` — the gates live there and `pnpm` in the wrong repository exits silently and reads as green. At `part4-ch15` it was `291 fenced files … across 58 chapters`, EXIT 0.
- [X] T003 [P] Record the opening dependency count across every `package.json` in `relay-platform` — **32 entries, 14 third-party** at `part4-ch15`. SC expects this NOT to move: this chapter adds nothing.
- [X] T004 [P] Record the opening lane state with the composed services **stopped** (057-5): `pnpm exec turbo run test --force` (the plain form reports a cached number — 4.14 read 553 where the truth was 867), `pnpm test:integration`, `pnpm coverage` **without a pipe**, `pnpm lint`, `pnpm exec turbo run typecheck --force`. **Lint and typecheck are on this list because 061's CI failed on a lint no task named.**
- [X] T005 [P] Record the analytical baseline: row counts for `media_events` (does not exist yet), `message_events` (**0** — the precedent's source has never carried data), `daily_usage_v2`, `daily_usage_billing`, `api_requests`. Use `docker compose exec -T clickhouse clickhouse-client --query "… FORMAT TSV"`.
- [X] T006 [P] Record the operational baseline: `media_objects` chargeable count, total `declared_bytes`, environment count, and the **size distribution** — mean, p50 and max. At planning: 8,120 objects, 4,255 MB, 1,576 environments, mean 537 kB, **p50 1,024 bytes**, max 25 MB. R5 publishes this spread and the p50 is the point.
- [X] T007 Record the opening CI error set **per error**, uuids normalised, from the most recent run on `main`. Per error, not per colour.
- [X] T007a [P] **Count the fence exposure of every file this chapter will touch, BEFORE editing any of them**, with `grep -rl 'title="<path>"' app/ fences/` in `relay-tutorial`. 061 moved this to phase 1 and it predicted that chapter's bill exactly, including which files would cost nothing. Expect `services/api/src/db/repository.ts` and `services/api/src/media/*` to be exposed and `analytics/*.sql` and `services/ingester/*` to be checked rather than assumed.
- [X] T008 [P] Record whether the ingester is running and how it is started. **It is not a compose service** (4.9 — no Dockerfile), so every analytical figure in this chapter depends on a process two test files spawn (050-8, still open).

---

## Phase 2: Foundational — the consumer learns the record before anything sends one

**Blocking**: every user story depends on these. Nothing here is story-specific.

- [X] T009 Read `services/ingester/src/shape.ts` end to end, including the R11 comment on why `route()` discriminates on the **payload's `type`** and not the subject. Note the three claimed types and what happens to a fourth.
- [X] T010 **Write the red probe FIRST, and assert what the consumer does TODAY rather than what 4.4 measured.** Publish a `media.stored` record onto `analytics.media.stored.{env}` against the consumer as it stands, and assert it comes back **`unclaimed`** and is **redelivered** — not terminated. 049's repair changed this, and `ingest.ts:100` says so: *"NEITHER ACKED NOR TERMINATED. Acking would consume a record this consumer did not write; terminating would destroy it. Left alone it is redelivered until something claims it or the stream's seven days expire — and the count below is the only way anyone finds out."* **4.4's transcript — written 0, malformed 0, terminated, never comes back — is the PRE-repair behaviour**, and a probe looking for a termination that no longer happens fails for the wrong reason. Run it red before T012.
- [X] T011 [P] Add the record schema to `packages/protocol/src/analytics.ts` per `contracts/storage-events.md` — `type`, `environment_id`, `media_id`, `event`, `kind`, `bytes_delta` (signed), `occurred_at`. **The sign is carried, never inferred from `event`**: a reader that derives it puts the rule in two places.
- [X] T012 Add the fourth arm to `route()` and the shaper in `services/ingester/src/shape.ts`, then re-run T010's probe and watch it turn green. **`route()` decides what a record IS before anything shapes it** (049's repair), so "not mine" never becomes the same answer as "malformed".
- [X] T012a **A fourth record type is FIVE edits in `ingest.ts` and one in the store client, not one.** Enumerated so none is missed: the accumulator array (`:69-71`), the branch (`:109-111`), the insert (`:121-123`), the `written` total (`:127`) and the per-type counts (`:128`), plus a fourth method beside `insert`, `insertRequests` and `insertConnections` — three names, inconsistently formed, and the fourth should say what it inserts.
- [X] T012c **Add the fourth counter to `ingest.itest.ts:429-433`'s accounting block.** That block names every counter and asserts the rest are zero — `writtenConnections` = N, `writtenAttempts` = 0, `writtenRequests` = 0, `unclaimed` = 0 — so a fourth added without extending it is **never asserted absent**, and the test keeps passing while the accounting stops being complete. This is the quiet half of 4.14's finding, where five frame counts all fired; here none would.
- [X] T012b **Replace `ingest.ts:111`'s catch-all `else connections.push(routed.row)` with an exhaustive `switch` and a `never` assertion.** A fourth `kind` currently falls into the connections array by default. 4.14 replaced exactly this shape in `session.ts` for exactly this reason: an exhaustive switch makes a fifth record type a compile error in one place instead of a row in the wrong table.
- [X] T013 [P] Write `analytics/0016_media_events.sql` per `data-model.md` §1. **`LowCardinality(String)` cannot say "absent"** (4.4): an absent field and an explicit `""` both land as `''` and none of the ingester's three guards catches an absent one, so `event` and `kind` are required in the schema. 90-day TTL, matching `message_events` and DR-09.
- [X] T014 [P] Write `analytics/0017_billing_stored_bytes.sql` — `stored_bytes_delta Int64` and `uploads_by_kind SimpleAggregateFunction(sumMap, Map(String, UInt64))` on `daily_usage_billing`. **NOT a plain `Map`**: measured on ClickHouse 25.3.14.14, `SummingMergeTree` keeps the FIRST row's map and sums nothing — `map('image',2,…)` merged with `map('image',3,…)` answers 2. Plain `String` keys fail the same way, so `LowCardinality` is not the cause. **Not `stored_bytes`**: the neighbouring `stored_delta` counts stored MESSAGES, and two similar names on one table is the collision the premise check found by reading the view.
- [X] T015 Write `analytics/0018_mv_billing_storage.sql` — the **third** materialised view into that rollup, alongside the two from `message_events` and `connection_events`. **A materialised view is a trigger on future inserts** (4.6), so it computes nothing about existing rows — which is harmless here **only because `media_events` starts empty**, and the file says so.
- [X] T016 Apply with `node analytics/apply.mjs`. **This applier is not the Postgres one**: it keys the ledger on `(filename, checksum)` and **refuses a changed file**, where the Postgres runner skips one in silence (0019's comment). And it is **one statement per file** — `Code: 62, Multi-statements are not allowed`.
- [X] T017 [P] Assert the map merges: insert two rows for one `(environment_id, day)` with overlapping keys and read the result. **This task was written to assert a behaviour the data model had asserted wrongly** — an analysis pass ran it against a scratch table first and found a plain `Map` keeping the first row. Keep the test: the type is unusual enough that a later simplification to `Map` would look harmless and would silently stop summing. Read it and read after `OPTIMIZE FINAL` as well as before — 4.6 found a bare `count()` on a `SummingMergeTree` answering 15 then 9 with nothing deleted in between, because it is a moment and not a state.
- [X] T018 Run `pnpm exec turbo run test --force` and `pnpm test:integration`. Phase 2 changes no behaviour, so anything red is the schema breaking an existing assumption.

---

## Phase 3: User Story 1 — a tenant's stored bytes have a daily history (P1) 🎯 MVP

**Goal**: every change to a tenant's stored bytes is recorded when it becomes true, and a day's
net change is readable per tenant without scanning raw events.

**Independent test**: take a slot, reject it, read the day's delta for that tenant; the figure
matches what the quota's own sum says changed.

- [X] T019 [US1] Write the emitter (FR-001) in `services/api/src/metering/storage-event.ts` — one function taking a tenant, a media id, a cause, a kind and a signed byte count. **One function for all four causes**, because the reaper's `deleted` arrives in another chapter and R4 requires it to need no rework.
- [X] T020 [US1] Comment the emitter's `deleted` cause with the chapter that will call it (`docs/12` row 22, erasure). `CLAUDE.md`'s convention: a claim about when something runs names the thing that runs it, because *"on boot, every boot"* was false for `ensureBucket` for two chapters.
- [X] T021 [US1] **Emit `reserved` AFTER `reserveMediaSlot` COMMITS, from its caller in `services/api/src/media/media.service.ts` — never inside the transaction.** `webhooks/analytics.ts:14-32` is an explicit decision record against that: *"guarantee independence → the publish happens after the commit, outside it, and a crash in that gap loses the record"*, chosen because *"a blocked outcome transaction is a customer's webhooks stopping because a metering pipeline is unwell — which constitution III names as a design failure in as many words."* **And the second reason is worse than the coupling**: a publish inside a transaction that rolls back emits a delta for a slot that was never created, which is a permanent overcount, and R5 is the whole argument that nothing corrects it. Carry `declared_bytes` — **the quota's quantity, not the store's** (FR-002): it sums `declared_bytes` where `state <> 'rejected'`, so a `pending` object is already charged and the meter must agree.
- [X] T021a [US1] Follow `request-log.middleware.ts:118`'s shape — `void publishRequest(this.analytics, this.logger, facts)`, fire-and-forget — rather than `dispatch.controller.ts:143`'s awaited `publishAttempt`. **Two call patterns exist and this task names which**, because the slot route is a request path and the dispatcher is not.
- [X] T022 [US1] **Extend `recordMediaVerdict`'s `RETURNING` list with `declaredBytes` and `mimeType` FIRST.** The function needs the bytes to negate and the mime type for FR-009's kind, and today it returns `state`, `objectKey`, `environmentId`, `userId` and nothing else. Its input carries a field called `kind` — **the rendition's** (`"thumbnail"`), not the media kind, which is the near-miss a reader would use by accident. **This is the third consecutive chapter whose producer seam was missing something**: 4.14 added `environmentId` and 4.15 added `userId`, both to this list, both because the statement that already reads the row is the one that should say.
- [X] T022a [US1] Emit `rejected` and `rendition` **from the verdict handler in `services/api/src/internal/media.controller.ts`, after `recordMediaVerdict` returns** — beside `announce`, which 4.14 put there for the same reason and which is the precedent to copy. Both hang off `applied`, the compare-and-set that makes a second verdict emit nothing. **Not inside the transaction** (T021's rule): the facts travel out on the return value, which is what T022's `RETURNING` extension is for.
- [X] T023 [US1] **Publishing must not be able to fail the request** (constitution III, FR-004). Whatever the api's existing analytics publisher does on failure is what this does; do not add a second policy. Read that path before writing this task's code.
- [X] T024 [P] [US1] Write `storedBytes(store, environmentId, asOf)` (FR-003, and SC-001's read) in `services/ingester/src/metering.ts`, beside `storedMessages`. **Comment the retention horizon where the query is**: this sums from the beginning of time over a table with a 25-month TTL, so the answer is short by whatever the TTL removed — a defect `storedMessages` shares and has never shown, because its source is empty. Copy its two details with its shape: **no empty-result guard** — *"a bare aggregate with no `GROUP BY` always returns exactly one row"*, asked of the server directly, and the guard it replaced was half the file's branches — and `flat()[0]` rather than `rows[0]?.[0]`, because the optional chain is a branch too.
- [X] T025 [P] [US1] Write `services/api/src/media/storage-metering.itest.ts` (SC-001) covering US1 scenarios 1–3: a slot moves the day's delta by exactly the declared bytes; a rejection takes them back and the net is zero; two tenants' figures are separate.
- [X] T026 [P] [US1] Assert US1 scenario 4: a tenant with no activity reads **zero, not absent** — a caller cannot tell "no change" from "no tenant".
- [X] T027 [P] [US1] Assert US1 scenario 5: a rendition's bytes appear in the same delta as an upload's, which 4.15 settled when it made renditions count against the quota.
- [X] T028 [US1] **Backdate any `pending` fixture 30 days.** 061 lost 8 of the worker's tests to this: `GET /internal/media/pending` is oldest-first over the whole platform with no tenant parameter, so a `pending` row planted in a test joins a queue another suite sweeps. The sweep excludes anything older than 24 hours, which is the repair.
- [X] T029 [US1] Assert FR-005 and SC-004 with a **deliberate duplicate**: deliver the same verdict twice, read the events, expect one. 4.15's idempotence class was caught by issuing one rather than reasoning that the upstream guard made it impossible.
- [X] T030 [US1] Run `python3 specs/045-part-3-rework/check-lane-scope.py`. **Assert the counted line, not the exit code** (055-4): five of seven gate scripts exit 0 over an absent corpus. 67 files at 061's close.
- [X] T031 [US1] Run the US1 suite, the media suites, `messages.itest.ts` **and** `packages/outsider`. 4.14's fifth whole-array assertion was a directory away from the suite that found the other four, and its fifth was in `outsider`, which no local lane reaches.

---

## Phase 4: User Story 2 — the bill can be checked against the store (P2)

**Goal**: someone can ask whether the metered level matches what the object store holds, per
tenant, and get a verdict that names the direction of any drift.

**Independent test**: plant a disagreement and confirm the comparison reports that tenant, the
direction, and how many tenants it examined.

- [X] T032 [US2] Extend **`services/api/src/media/presign.ts`** to take extra query parameters — **not the media worker's `sign()`, which is where the first draft sent it.** The reconciliation reads the rollup and the inventory together, the worker holds no database credential (ADR-04, `Dockerfile:6`), and the api cannot import the worker's code. **Measured: appending `&list-type=2` outside the signature answers `SignatureDoesNotMatch`** — every parameter has to be inside it, and neither signer takes extras today.
- [X] T032a [US2] **Re-run R2's probe against `presign` before building on it.** The 48 ms, the 1,000 keys, the `IsTruncated: true` and the `<Size>` per key were all measured through the *worker's* signer. `presign` already takes four methods and already documents the key-less bucket call (*"Empty for a BUCKET operation … `/{bucket}` with no key segment and no trailing slash"*, 4.10), so it should behave the same — and "should" is what this task exists to replace.
- [X] T033 [US2] Write `listObjects` in **`services/api/src/media/store.ts`**, beside `ensureBucket`, `storeReady` and `deleteObject`. **`GET /{bucket}` with no key already works** — 200, a `ListBucketResult`, 1,000 keys, 377 kB in 48 ms — so this adds pagination rather than the capability.
- [X] T034 [US2] **Page it with `marker`, and assert more than 1,000 keys were seen.** The measured working call is the **V1** listing, which pages with `marker`; `list-type=2` is V2 and pages with `continuation-token`. Picking the wrong one is either a signature failure or a silently unpaged read. One response carries 1,000 with `IsTruncated: true` against the lane's 8,120 objects. **4.13's sweep read one page** and an object nobody uploaded to stayed `pending` for ever; a reconciliation that reads one page reports agreement for the 7,120 it never looked at.
- [X] T035 [P] [US2] Parse the inventory without a database join: an uploaded object's key is `${environment_id}/${id}` and every entry carries a `<Size>`. **Heading each object instead costs 11.5 s against 430 ms** for nine pages.
- [X] T035a [US2] **Report keys that do not parse as a tenant as their own category** — *N keys, M bytes, attributable to no tenant*. The bucket holds four such prefixes today (`analyze-probe`, `probe`, `r9-measure`, `thumbnail-itest`), all test and probe debris, and **none of them is on page one** — the research claimed 100% tenant-prefixed from a single page, which is T034's own warning committed by the document that wrote it. Skipping them silently means a bucket full of debris reports clean.
- [X] T036 [US2] Write the verdict logic (FR-006, FR-008) as **pure functions** in `services/api/src/metering/storage-reconcile.ts` — agreement, a direction, a one-sided verdict, and the input validators. **Follow `reconcile.ts`'s split, which is deliberate**: its header says *"THIS FILE IS THE HALF THAT RUNS WITHOUT A STORE"*, it exports `verdictFor`, `differencePct`, `smallestExpressibleDrift` and `exitCodeFor` as pure functions with `reconcile()` as a thin composed one over them, and it validates with `assertEnvironmentId`/`assertPeriod`. Model the vocabulary on it too: it distinguishes `not-comparable` from `no-data`, which 4.7 found was the whole answer for 1,317 of 1,385 tenants.
- [X] T036a [US2] Write the composed function that reads the rollup and the inventory and hands both to the pure half. Read ClickHouse through `metering/clickhouse.ts`, which is how `reconcile.ts` does it and which is why the `no-restricted-imports` rule that caught 4.7 in this directory does not bite.
- [X] T036b [P] [US2] Write `services/api/src/metering/storage-reconcile.test.ts` — **the unit half, beside `reconcile.test.ts`**. The thresholds, the direction of a drift, the one-sided verdict, the unattributable-keys category and the exit code are arithmetic, and arithmetic tested only through a live store is tested slowly and rarely.
- [X] T036c [US2] Give it an exit code: non-zero on breach, following `exitCodeFor`. **ADR-28 records that an exit code is "what the clause can currently mean"** in the absence of any alerting mechanism, and DR-17's weekly cadence has no runner either — so the exit code is the whole of what a future scheduler would read.
- [X] T037 [US2] **Report how many tenants were examined** (FR-007). A zero that does not say what it looked at is this project's most-repeated instrument failure.
- [X] T038 [P] [US2] Write `services/api/src/metering/storage-reconcile.itest.ts` (SC-006): an agreeing tenant, a planted disagreement in each direction, and a tenant present on one side only.
- [X] T039 [P] [US2] Assert the reconciliation's own scope: a tenant's verdict is computed from that tenant's keys alone. Probe by deleting the prefix filter.
- [X] T040 [US2] Record what the comparison **cannot** catch yet: with no producer for `deleted`, the metered level only rises, so a drift in the direction the clause exists to find cannot occur. State it in the code and in `gaps.md`, not only in the chapter.
- [X] T041 [US2] Record that the **weekly cadence has no runner** (ADR-28 — no `schedule:` trigger, one hand-run script). The comparison ships invokable; the cadence is unmet by decision on ADR-28's own precedent.

---

## Phase 5: User Story 3 — uploads are counted by kind (P3)

- [X] T042 [US3] Carry `kind` on every record including `deleted`, so the same view that builds the counts can reverse them.
- [X] T043 [P] [US3] Extend the materialised view to populate `uploads_by_kind` (FR-009).
- [X] T044 [P] [US3] Write the test: uploads of two kinds on one day give separate counts that sum to the day's total (SC-007).
- [X] T045 [US3] **Answer FR-010 once and assert the answer at every reader**: a rendition is **not** an upload for the count — nobody uploaded it — and its bytes **are** in the level. Two answers about one object is how a count and a sum drift apart, which is why this is a requirement rather than a note.

---

## Phase 6: The measurements and the probes

- [X] T046 Probe every scope arm **by deletion** (SC-003): remove each individually, re-run the storage suites and the isolation gauntlet, and record each as **tested** or **unnecessary** by name. **An arm here is an SQL or predicate clause, not a JavaScript branch**, so a coverage number reports nothing about it (048's shape, 4.12's confirmation). 061 found that choosing too few suites looks exactly like an uncovered arm — name the suites in the record.
- [X] T047 [P] Measure SC-002: the rollup read against accumulating the same answer from raw `media_events`. **This is the comparison DR-10 asks for**, and `research.md` R8 records that the 252-buffer operational sum is not it.
- [X] T048 [P] Measure SC-009: the drift from one lost delta, as the distribution rather than a number — p50, mean and max over the chargeable objects — and state that it never self-corrects.
- [X] T049 [P] Measure the inventory's cost at the lane's size: pages, bytes, wall clock, against heading every object.
- [X] T050 SC-005: stop ClickHouse, issue a slot request, assert **201**, restart, and then **say which of the two happened** — the record survived or it was lost. The criterion requires the chapter to state it, not to prefer one.
- [X] T051 Run `pnpm coverage` and read the **real** exit code, without a pipe. `pnpm coverage | sed > f; echo EXIT=$?` reads `sed`'s status — **six occurrences in this project**, the last one mine.
- [X] T052 [P] Check the per-file coverage pins this chapter's files fall under, and run **both halves** of the unbindable-key probe (049). If a pin has to move, ask what the number is measuring first: 059 found a denominator that differs between machines and a pin that was right while its environment was wrong. **061 fixed six threshold errors with tests rather than lower pins.**
- [X] T053 Run `pnpm lint` and `pnpm exec turbo run typecheck --force`. **Both, by name, because 061's CI failed on the first and had 15 turbo tasks where per-service checks covered 5.**
- [X] T054 [P] Run the five gates that exist — `check:docs`, `check:errors`, `check:fences`, `check:figures`, `check:srs` — read off `package.json`. **There is no `check:refs`**; 061's task list named it and got `Command not found`.
- [X] T055 Run `pnpm test:outsider` with the composed services up and the three variables set. No local lane reaches it.

---

## Phase 7: The documents

- [X] T056 Amend **FR-MED-12** in `docs/04-srs.md`: the daily figure and the per-kind counts met; *"visible in the dashboard"* unmet because there is no dashboard and FR-DSH-04/05 are unbuilt. **Read the clause before editing it** — four documents once agreed on two clauses that do not exist, and what found it was opening the SRS to make the edit.
- [X] T057 Amend **DR-17**: the rollup met, the **weekly cadence** unmet by decision (ADR-28), and the reconciliation's blind spot recorded — it cannot fail in the direction it exists to catch until something deletes.
- [X] T057a **Bound FR-MED-12's daily figure at the rollup's retention horizon** (FR-003, FR-003a) and say what re-bases it. 25 months, measured; a level accumulated from deltas is understated by everything the TTL removed, and **DR-17's inventory is the re-base** — the store holds the level directly. 4.7's precedent: when measurement shows a clause's bound is unreachable, amend the clause rather than let the number stand.
- [X] T058 Add revision row 1.23.
- [X] T059 [P] **Count the clauses** and put the counts in the chapter (SC-008): how many met, how many unmet by decision, how many unreachable. A chapter that says "mostly met" is one nobody can check.
- [X] T060 [P] Amend **both** copies of the Part 4 table — `docs/12` row 17 CLOSED, `docs/07` row 17 SHIPPED. Two copies, and amending one is how they drift.
- [X] T061 [P] Record in `docs/05-sad.md` §6 or the data-model section that `stored_delta` and `stored_bytes_delta` are different quantities, since the next reader will meet them side by side.
- [X] T062 [P] Grep `docs/` for feature-local ids leaking in, by **diffing** rather than grepping the tree: `git diff HEAD -- docs/ | grep '^+' | grep -oE 'FR-0[0-9][0-9]'`. Nothing runs this check (052-7).
- [X] T063 Run `pnpm sync:docs` then `check:docs` — the tutorial keeps mirrored copies, and 061's first run of that gate was red for exactly this.

---

## Phase 8: The chapter

- [X] T064 Register 4.16 in `relay-tutorial/lib/tutorial.ts` with **all seven fields**. `path` is checked by no gate, and an unregistered id throws at build.
- [X] T065 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-16/<slug>/page.mdx`, 2,000–4,000 prose words counted **outside fences and tables**, English only.
- [X] T066 [P] Write the `TRAP` box. The candidate is the one the premise check found: **`stored_delta` is not stored bytes**, and a planner reading the column list would have concluded this chapter was half built.
- [X] T067 [P] Write the figures in `figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [X] T068 Publish R5's distribution, and publish it as a distribution: **p50 1 kB, mean 537 kB, max 25 MB**. The mean alone would say a lost event costs half a megabyte, which is true of no object in particular.
- [X] T069 Publish the delta-versus-sample trade (FR-012) and why DR-17 already made it: a materialised view fires on insert and a sampler needs a scheduler this platform does not have (ADR-28).
- [X] T070 Publish what the inventory measurement found — that the listing already worked, that pagination did not, and that the keys carry the tenant because 4.15 kept the platform's layout.
- [X] T071 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6) — an excerpt must be untitled, and 4.14 paid three fences for forgetting it.
- [X] T072 Generate hunks from the checker's own replay: `pnpm check:fences --dump <dir>`. A bare `--dump` writes the END state, which is what an appendix hunk wants. **Verify every pre-image matches the dumped state exactly once** before pasting, widening past `-U6` only when it does not.
- [X] T073 Put hunks in the appendix for any file the appendix already amends (4.8), and read T007a's counted table to work the bill biggest-first.
- [X] T074 Run `check:fences` to 0 and `pnpm build` green (SC-010, SC-011). **Run `check:fences` after any source edit** — the chain is a claim about `relay-platform`'s HEAD, so a platform edit made to turn CI green invalidates the hunks that publish it (4.14).
- [X] T075 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [X] T076 Write `specs/062-chapter-4-16/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [X] T077 [P] Write `gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: 050-8 (the ingester is not a deployment — this chapter depends on it more than any before), 055-3 and 061-4 (`check:errors` has no CI job; `check:refs` does not exist), 059-20, 043.
- [X] T078 [P] Write `traceability.md` by **reading**. 4.11's mechanical map raised fourteen false alarms out of fourteen.
- [X] T079 Run the quickstart end to end and correct it in place, recording each wrong version. **061's was right first time** because the corrections were applied before it ran; that is the bar, not luck.
- [X] T080 Stop the composed services **by name** — `api gateway dispatcher media-worker`, and **not `ingester`**, which has no Dockerfile and makes the whole command fail. Then run the full lane set once more.
- [X] T081 Commit each phase. Under five lines, no trailer.
- [X] T082 **Push submodules first, then the superproject.** `ci.yml` is the outer repository's and the other two are gitlinks, so the reverse order checks out commits no remote has.
- [X] T083 Compare the CI error set **per error** (SC-010) against T007's baseline, in both directions. One comparison supports *"this run introduced nothing new"*, not *"the set is stable"*.
- [X] T084 If CI is red, fix the platform, **re-dump, re-hunk, and push both** — repairing a platform file invalidates the appendix hunks that publish it.
- [X] T085 Tag `part4-ch16` on a commit that **checks out a working chapter**, annotated. 4.14's tag had to be moved off one that fails `pnpm typecheck`.
- [X] T086 Compress 061's `CLAUDE.md` entry to its headline, measurement block and still-cited findings, and add this one. **The file has a 150,000-character budget**; it stood at 133,308 after 061.

---

## Dependencies

```
Phase 1  →  Phase 2 (the record, the arm, the schema)
Phase 2  →  Phase 3 (US1)  →  Phase 4 (US2)  →  Phase 5 (US3)
Phases 3-5  →  Phase 6  →  Phase 7  →  Phase 8  →  Phase 9
```

**T010 blocks T012, and that order is the phase's whole point.** The probe has to be red against
the consumer as it stands, or shipping the arm proves nothing about what it fixed.

**US2 depends on US1** for a metered level to compare against. **US3 depends on US1's record**
for a `kind` to count, though its view change can be written against planted rows.

### Parallel opportunities

- **Phase 1**: T003–T006, T007a and T008 are independent reads.
- **Phase 2**: T011, T013, T014 and T017 touch different files; T012 follows T010, T016 follows T013–T015.
- **Phase 3**: T024–T027 are separate files; T021 and T022 touch one file and do not.
- **Phase 4**: T035, T038 and T039 are independent once T033 lands.
- **Phase 6**: T047–T049, T052 and T054 are independent measurements.
- **Phase 7**: T059–T062 touch different documents.

### Suggested MVP

**Phase 1 + Phase 2 + Phase 3 (US1).** A tenant's stored bytes have a daily history, recorded
when it becomes true and readable without scanning raw events — which is FR-MED-12's headline
and DR-17's stated technique. It is also the only part reachable without a scheduler.

### What this chapter does not build

FR-MED-10's reaper, so the `deleted` delta has no caller. DR-17's weekly cadence, because
ADR-28. The dashboard, because there is not one. Each is recorded in the SRS rather than left
to look built (FR-011).
