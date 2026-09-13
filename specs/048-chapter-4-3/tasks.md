# Tasks — chapter 4.3, the consumer that was promised

**Feature**: `specs/048-chapter-4-3/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**This chapter joins two things that already exist.** The `ANALYTICS` stream has been
filling since chapter 3.20 and the store landed in 4.2. Nothing between them.

**Verification methods, decided rather than defaulted.** The drain is **D**. The store-down
behaviour is **D** for the queue depth and **A** for the claim that messaging is unaffected.
The Postgres-isolation claim is **I**.

**The redelivery is D AND T, and that pair is a decision.** Constitution VI singles out
**idempotency** — with ordering and tenant isolation — for 100% branch coverage, and the
redelivery IS this chapter's idempotency. A demonstration proves the system behaves once; a
test proves the branch that makes it behave is exercised. **They are not substitutes**, and
choosing D alone here would have been choosing it without noticing which clause it touches.

**AND THIS ONE DOES JOIN A TEST LANE, UNLIKE THE LAST TWO.**
`vitest.coverage.config.mts` collects `packages/*/src/**` and `services/*/src/**`, so an
ingester under `services/` is collected like every other service — where 046's
`scripts/scale/` and 047's `analytics/` were collected by nothing. That is a reason to put
it there and a reason the phase gates mean more than they did.

---

## Phase 1: Premises, and the numbers this feature inherited

**Everything blocks on this.** Every figure in `research.md` came from a probe run during
planning. Re-run each at this chapter's tag, because a premise carried from a planning
document and never re-run is what this project finds most often — and because the last
feature found, at pass 9 of 9, that eight passes of correct measurement had been about the
wrong database.

- [ ] T001 Re-run R3's premise and record it in `specs/048-chapter-4-3/baseline.txt`: `curl -s 'localhost:8222/jsz?streams=1&consumers=1'` reporting the `ANALYTICS` stream's message count and **`consumers: 0`**. **If a consumer now exists, the chapter's opening is wrong** — that is the finding, not an inconvenience. Record `EVENTS` and `DELIVERIES` beside it and **name which services were running**, because a zero consumer count on a stream whose consumer simply is not started proves nothing (the planning probe made that mistake first).
- [ ] T002 Record in `specs/048-chapter-4-3/baseline.txt` that nothing in the repository consumes the stream: every `ANALYTICS_STREAM` reference outside `packages/protocol` is in `services/api/src/outbox/jetstream.publisher.ts`, creating or updating it, and `services/api/src/consumer/runtime.ts` filters on `ALL_EVENTS_SUBJECT`. **This is the claim the runtime check cannot make**, and it is the one the chapter rests on.
- [ ] T003 Quote the stream's own comment into `specs/048-chapter-4-3/baseline.txt` — *"no acknowledgement anywhere: nothing consumes this stream in this chapter"* — with its seven-day `max_age`, 1 GiB `max_bytes` and `discard: old`. Quote it from `jetstream.publisher.ts`, not from `research.md`.
- [ ] T004 Re-run R1 and record the exact call chain in `specs/048-chapter-4-3/baseline.txt`: `runtime.ts:195` calls `claimEvent(db, durable, parsed!.id, effect)`, and `repository.ts` implements it as a `db.transaction` inserting into `consumedEvents` with `onConflictDoNothing`. **Read the function, do not cite the line number** — this project has been wrong about a cited line before.
- [ ] T005 [P] Re-run R4 and record both numbers in `specs/048-chapter-4-3/baseline.txt`: a 1,000-row batch inserted twice into a `ReplacingMergeTree` with **identical sorting keys** gives `SELECT count()` 2,000 and `FINAL` 1,000. **Use identical keys.** The planning probe used `generateUUIDv4()` in the key column, so its two batches were not duplicates and it measured nothing while reporting a number.
- [ ] T006 [P] Re-run R5 and record all three lines in `specs/048-chapter-4-3/baseline.txt`: the token with no window (no dedup, **no error**), the token with the window (block refused), and a different token (inserts). **The first line is the finding**; the other two are the mechanism.
- [ ] T007 [P] Run `pnpm check:fences` in `relay-tutorial` and record the opening in `specs/048-chapter-4-3/baseline.txt` **broken down by kind and locale**. 047 opened and closed at 110 — APPLY 74 (30 en, 30 vi, 14 elsewhere), HEAD 36 en. **Thirty live in the Vietnamese chain, which is not this chapter's work**, so a bare total moves for reasons 4.3 did not cause.
- [ ] T008 [P] Pin the environment in `specs/048-chapter-4-3/baseline.txt`: node, pnpm, the NATS and ClickHouse image tags from `compose.yaml`, `SELECT version()`, cpus, RAM, and the `DOCKER_HOST` this machine needs.
- [ ] T009 [P] Record the lane's row counts and the `relay_analytics` state fresh in `specs/048-chapter-4-3/baseline.txt`. 047 closed at 31,685 environments · 46,143 channels · 303,885 messages · 487,481 outbox, **and none had drifted since 046**. They are part of the instrument.
- [ ] T010 Commit phase 1 — `specs/048-chapter-4-3/baseline.txt` only. No platform change yet.

---

## Phase 2: Foundational — a table, through the ledger that was built for it

**Blocking for all three stories.** Nothing can be written to a table that does not exist,
and this is the first statement file added since the chapter that built the runner.

- [ ] T011 Create `relay-platform/analytics/0003_webhook_attempts.sql` from [data-model.md](./data-model.md): ten columns, **`ReplacingMergeTree`**, `PARTITION BY toYYYYMM(ts)`, **`ORDER BY (environment_id, ts, delivery_id, attempt)`** — the sorting key is also the dedup key, and it is safe because `ts` is `attempted_at`, a field of the record rather than the time it was consumed — `TTL toDateTime(ts) + INTERVAL 90 DAY`. **Name `relay_analytics` in the statement** — `CLICKHOUSE_DB` creates a database without making it the session's, so an unqualified `CREATE TABLE` lands in `default` with no error, and `apply.mjs` refuses a statement that does not name it (047 R14).
- [ ] T011a In `relay-platform/analytics/0003_webhook_attempts.sql`, add **`CONSTRAINT ts_is_real CHECK ts > toDateTime64('2020-01-01 00:00:00', 3, 'UTC')`** (FR-007a). **It is the only thing between a field-name typo and an empty table.** The publisher's field is `attempted_at`, this column is `ts`, and a `JSONEachRow` insert with unmatched keys leaves the column at its default — the epoch — which is older than the ninety-day TTL, so **the row is deleted at insert and every instrument reports success.** Measured: a 1970 row gives 0 rows before and after a merge; with the constraint, `Code: 469 … Constraint 'ts_is_real' … violated`.
- [ ] T012 In `relay-platform/analytics/0003_webhook_attempts.sql`, make **`status` and `error` `Nullable`** and comment why. The publisher spreads them in only when present, because *"an explicit `undefined` is not the same as an absent key, and the difference is the whole meaning of 'nothing answered'"*. A non-nullable `status` writes **0** and claims an endpoint answered with status zero — 4.2's argument arriving in a new table before anyone can get it wrong again.
- [ ] T013 Record in `specs/048-chapter-4-3/baseline.txt` **why there is no `insert_deduplication_token` and no `non_replicated_deduplication_window`** — the mechanism built for at-least-once consumers, rejected after measuring it. It needs a token stable across a redelivery and **JetStream batch boundaries are not** (T034a), and it keys on itself rather than on the content, so a colliding token is **silent data loss** rather than a duplicate (T034b). The road not taken is worth a paragraph in the chapter because it is the answer a reader will find first.
- [ ] T014 Apply it with `node analytics/apply.mjs` and record the output in `specs/048-chapter-4-3/baseline.txt`: **`applied 1: 0003_webhook_attempts.sql`** and three skipped. Run it again and record **`applied nothing`**. This is the ledger's first use by somebody not trying to make it fire.
- [ ] T015 Amend `docs/05-sad.md` §6.2 to publish `webhook_attempts` (FR-008), and sync it: **`pnpm sync:docs` in `relay-tutorial`, or `check:docs` fails** with `content/docs/05-sad.md differs from docs/05-sad.md`. 047 hit that gate and it caught the omission.
- [ ] T016 Commit phase 2 — `relay-platform/analytics/`, `docs/05-sad.md`, `relay-tutorial/content/docs/`. Gates first: `pnpm lint && pnpm typecheck && pnpm test` in `relay-platform`.

---

## Phase 3: User Story 1 — the stream drains into the store (Priority: P1) 🎯 MVP

**Goal**: the records that have been accumulating become rows, and new ones follow.

**Independent test**: publish a known number of attempt records, run the ingester, and
compare the store's row count against the stream's delivered count.

- [ ] T017 [US1] Decide where the ingester lives and **record the decision, its reason, and its price** in `specs/048-chapter-4-3/baseline.txt` (FR-014). `services/*/src/**` is collected by the coverage lane; `analytics/**` is collected by nothing. A fourth service directory is the SAD's shape. **And a service is six files**: `Dockerfile`, `package.json`, `src/`, `tsconfig.json`, `tsconfig.build.json`, `vitest.integration.config.mts` — plus tests, plus a pin in the **fenced** `vitest.coverage.config.mts` (T038b).
- [ ] T017a [US1] Record the precedent in `specs/048-chapter-4-3/baseline.txt` **before writing any prose**: chapter 3.19 introduced `services/dispatcher` at **5,889 prose words and 47 titled fences**, against SC-008's 2,000–4,000 bound and 4.2's 2,580 and 2. The ingester is a smaller job — fetch, shape, insert, acknowledge, against HTTP delivery with signing, retries and expansion — so **47 is a ceiling, not an estimate.** State the expected fence count here — **counting `vitest.coverage.config.mts` as a second hunked amendment beside `compose.yaml`** — and treat **a split as likely rather than merely permitted.**
- [ ] T017b [US1] Decide the **scaffolding fence policy** and record it (T051 depends on it). Chapter 3.19 fenced `services/dispatcher/package.json` and the sources and **skipped the `Dockerfile`, both tsconfigs and the vitest config** — four files a reader needs to build the service. **Follow that precedent knowingly or differ from it deliberately**; deciding at T051 means deciding it while writing prose, which is the worst moment for it.
- [ ] T017c [US1] Record the two edits a fourth service does **not** need, checked because each would otherwise be a hunked amendment to a fenced file: `pnpm-workspace.yaml` globs `services/*`, and `turbo.json` names **no service at all** (0 occurrences of `dispatcher` or `gateway`). **Two anchoring risks that are not there** — worth a line, because an absent cost is invisible unless somebody looks for it.
- [ ] T018 [US1] Create the ingester with a durable pull consumer on `analytics.>`, **with `max_deliver: -1`** (FR-006a). Both existing consumers set a limit — `MAX_DELIVER = 5` on the api's runtime, 10 on the dispatcher, both at a 30-second `ack_wait` — and it is sound for a webhook endpoint that is probably gone. **A store that is restarting is not an endpoint that is gone**, and five attempts at thirty seconds is two and a half minutes before an outage becomes a silent strand (T027a). The queue's seven-day retention is the only bound. **State whether `createConsumerRuntime` is reused, parameterised or replaced, and why** — its claim is a Postgres transaction and constitution III forbids that here (T004). **The template written to stop a future consumer double-counting is the one this consumer may not reuse**, and that is the chapter's argument, not an inconvenience to route around.
- [ ] T019 [US1] Bound the batch by **both** a row count and an elapsed interval (DR-11 publishes 2 s or 10,000 rows). A count alone never flushes for a quiet tenant; an interval alone has no bound under load. **Publish what each bound costs at a stated publish rate** (SC-004) rather than quoting DR-11. **The time bound is why deduplication may not depend on grouping**: with it, batch boundaries follow arrival timing, so the same records are cut differently on a retry even at a fixed batch size (T034a).
- [ ] T020 [US1] Shape records with an **allow-list**, mirroring the publisher's own — *"An allow-list fails closed when somebody adds a field; a spread fails open."* **And it RENAMES: `attempted_at` becomes `ts`.** Build the row explicitly; never forward the publisher's JSON, because key-matching is what makes the mismatch silent.
- [ ] T020a [US1] Set **`input_format_skip_unknown_fields = 0`** and **`date_time_input_format = best_effort`** on every insert, and record in `specs/048-chapter-4-3/baseline.txt` what each one catches. The first turns a renamed field into `Code: 117` — its default is **1**, which is why T011a's failure was silent. The second is what parses the ISO-8601 string at all: the default `basic` refuses it with `Code: 27. Cannot parse input: expected '"' before: 'Z"…'`. **One of these two failures is loud and the other is silent, and that is the pair worth publishing.**
- [ ] T021 [US1] Insert one batch as one statement, and **acknowledge only after the insert returns** (FR-003). A record that was not written is not acknowledged.
- [ ] T022 [US1] Handle a malformed record: count it, **terminate it at the parse**, and do not let it stall the stream behind it (FR-010, FR-006b). **This is load-bearing now, not tidy**: with `max_deliver: -1` a payload that will never parse retries forever. The existing runtime already draws the line — *"A payload that will never parse must not consume five delivery attempts before being dropped anyway. The same bytes fail the same way every time."* **Retry forever on transport or store failure, terminate at parse. One rule, two arms.**
- [ ] T023 [US1] Run the drain and record in `specs/048-chapter-4-3/baseline.txt` **four numbers side by side**: the count published to the stream, then `count()`, `count() FINAL`, and `uniqExact((environment_id, ts, delivery_id, attempt))`. **The published count is what makes this a check rather than a tautology** — the other three agree at 0, 0, 0 over an empty table, which is exactly what T011a's failure produces. After a redelivery the bare `count()` exceeds the rest, and that is the engine working rather than a defect. Reading this table means `FINAL`.
- [ ] T024 [US1] Record the consumer's pending count after the drain, from the broker rather than from the ingester's own log. **A process reporting that it finished is not evidence that the queue is empty.**
- [ ] T025 [US1] Verify no request waits on an analytical write (FR-ANL-02) and record how it was verified. `publishAttempt` already *"never throws"* and is called after the outcome transaction commits; this task confirms the consumer added nothing to that path.
- [ ] T025a [US1] Write unit tests for the **shaping function** — the allow-list and the rename (T020). It is pure, it is decision-bearing, and it is where `attempted_at` becomes `ts`; a rename that silently stops happening is pass 3's failure returning by another route. The dispatcher's precedent is one `.test.ts` beside one `.itest.ts`.
- [ ] T026 [US1] Commit phase 3 — the ingester and `specs/048-chapter-4-3/baseline.txt`. Gates first.

---

## Phase 4: User Story 2 — the analytical store can be gone (Priority: P2)

**Goal**: NFR-REL-05 measured rather than asserted.

**Independent test**: stop the store, exercise the platform, confirm messaging is unaffected
and the queue grows; restart and confirm the backlog drains with no gap.

- [ ] T027 [US2] Stop ClickHouse and exercise the send and delivery paths. Record in `specs/048-chapter-4-3/baseline.txt` that neither reports an error attributable to the store, **with the requests counted** — "no errors" from a run that sent nothing is the zero that proves nothing.
- [ ] T028 [US2] Record **the stream's depth AND the consumer's `num_pending` together**, before, during and after the outage. The rise in depth is the claim NFR-REL-05 makes; **the pair is the only thing that can detect a strand.** A consumer that has exhausted its redeliveries reports `num_pending 0` while the stream still holds every record — measured — so stream depth alone looks like accumulation and consumer lag alone looks healthy. **Neither number is the signal; the disagreement between them is.**
- [ ] T029 [US2] Confirm the ingester **does not acknowledge** what it could not write (FR-003), and record how that was confirmed rather than asserting it. Record `num_redelivered` climbing as the evidence that the record is being re-offered rather than quietly abandoned.
- [ ] T027a [US2] **Re-run the measurement that found this** and record it in `specs/048-chapter-4-3/baseline.txt`: a consumer at `max_deliver: 3` delivered on rounds 1, 2 and 3, **delivered nothing on round 4 and after**, and then reported `num_pending 0 · ack_pending 0` **while the stream still held all three messages.** That is the failure FR-006a exists to prevent, and it is invisible to the instrument anyone would reach for.
- [ ] T030 [US2] Restart the store, drain, and reconcile: every record published during the outage is in the table, counted against what was published. **Record both numbers.**
- [ ] T031 [US2] Record what `discard: old` at 1 GiB means for records dropped while an ingester is down (FR-011), and **whether the ingester can tell**. The broker drops the oldest without telling anyone; if the honest answer is "it cannot know", that belongs in the prose rather than in a silence. **This is the same bound as T018's, from the other end**: with `max_deliver: -1` the retention is the only limit on how long a record may wait, so **retention exhaustion is now the single path to actual loss** — and the two bounds have to be reasoned about together or neither is a bound on anything.
- [ ] T032 [US2] Record whether seven days is still the right retention now that something consumes the stream (FR-011). It was chosen while nothing did. **Do not presume the answer**; the chapter states it either way.
- [ ] T033 [US2] Commit phase 4 — `specs/048-chapter-4-3/baseline.txt`. Gates first.

---

## Phase 5: User Story 3 — a redelivery does not become a second row (Priority: P3)

**Goal**: the defect that stays invisible until a customer disputes a bill.

**Independent test**: force a redelivery of a written batch, then compare counts.

- [ ] T034 [US3] Confirm the deduplication is on the **record**, not the batch: the `ReplacingMergeTree` key `(environment_id, ts, delivery_id, attempt)`. Record why the publisher's `{deliveryId}:{attempt}` id does not cover this — that is **broker-side publish dedup**, and at-least-once is about the consumer being handed the same record twice. **Two mechanisms, two failure modes**, agreeing about what a distinct record is.
- [ ] T034a [US3] **Re-run the measurement that killed the first design** and record it in `specs/048-chapter-4-3/baseline.txt`: a pull consumer's retry with a different `max_messages` returns a different set, out of order and interleaved with newer messages — `4,5,1,2,3,6,7,8,9,10` where the original batch was `1,2,3,4,5`. Record the case that DOES work too (same `max_messages` replays the batch exactly), because **that is the one configuration the first design was tested in.**
- [ ] T034b [US3] Record in `specs/048-chapter-4-3/baseline.txt` that `insert_deduplication_token` keys on **itself, not the content**: the same token with 500 completely different rows drops all 500 and reports success. **A token that is not provably unique per batch is silent data loss**, which is why it is not used even as a cheap first line.
- [ ] T035 [US3] Force a redelivery — stop the ingester after an insert and before the acknowledgement — and record `count()` and `count() FINAL` before and after. **`FINAL` must not move; the bare count may, and the chapter says why that is the engine rather than a defect.**
- [ ] T036 [US3] **Force the REGROUPING, because replaying the same batch shape proves only the easy half** — and the first design passed that half. Restart the ingester with a different batch size so the redelivered records are cut differently from the originals, then confirm `count() FINAL` is unchanged. Verified in analysis over three differently-cut batches of the same 500 records: physical count 500 → 800 → 1,200, `FINAL` **500** every time. **Clean up the probe before anything is counted.**
- [ ] T037 [US3] **Measure what `FINAL` costs** on this table at the corpus's size and record it (SC-003's shape). It is the price of deduplication that does not depend on batch boundaries, and it is 4.2's rollup lesson one engine over — there the read contract became `sum()` with `GROUP BY`, here it is `FINAL`. **A query whose correctness depends on somebody having run `OPTIMIZE` is right in a demo and wrong in production.**
- [ ] T038 [US3] Verify the ingester wrote nothing to PostgreSQL and issued no query against it on the ingestion path (FR-009, SC-005): `schema_migrations` unchanged, `consumed_events` unchanged, and the lane's row counts matching T009's. **Constitution III is the reason this chapter cannot reuse the obvious runtime**, so it is the claim most worth checking.
- [ ] T038a [US3] Write the integration test for the **redelivery** (FR-012a, SC-005a): a batch written, redelivered under a different grouping, and `count() FINAL` unchanged. This is the chapter's idempotency and the clause constitution VI names. **Force the regrouping, as T036 does** — a test that replays the same batch shape proves the half the first design already passed.
- [ ] T038b [US3] Pin the ingester's decision-bearing files in `relay-platform/vitest.coverage.config.mts` **at the measured figure, and record the gap against constitution VI's 100% branch clause** in `specs/048-chapter-4-3/baseline.txt`. The precedent is explicit and is not compliance: `repository.ts` holds ordering, idempotency and tenant isolation, measures **89.51%**, and is pinned there because *"a threshold nothing can pass makes CI permanently red and teaches everyone to ignore it."* **Measure, pin, name the shortfall.**
- [ ] T039 [US3] Record in [contracts/ingester.md](./contracts/ingester.md) anything the contract gained after the code ran, **and which task forced it**. A contract written by one caller is a contract written by one caller's opinion.
- [ ] T040 [US3] Commit phase 5 — the ingester, `specs/048-chapter-4-3/`. Gates first.

---

## Phase 6: The chapter, the amendments, and closing out

- [ ] T041 Choose the slug and create `relay-tutorial/app/(en)/part-4/chapter-03/<slug>/page.mdx`.
- [ ] T042 Write the opening: something has been publishing into a stream since chapter 3.20 and nothing has ever read it. **Open with the broker's own answer**, not with a description of it.
- [ ] T043 Write the section on why the reusable runtime cannot be reused — `claimEvent` is a Postgres transaction and constitution III keeps the paths apart. **Name the subject, not the ordinal** (045 FR-008).
- [ ] T044 Write the batching section with the measured cost of each bound, not DR-11's numbers restated.
- [ ] T044a Write the section on what the insert refuses and why, with both failure modes side by side: a **renamed** field is silent by default and becomes `Code: 117` with one setting; an **absent** one is silent even then and needs the constraint; a **badly parsed timestamp** is loud from the start. **The interesting part is that the quietest failure is the most destructive** — an epoch timestamp is older than the retention, so the row is deleted at insert and the whole chain reports success.
- [ ] T045 Write the redelivery section: why the obvious mechanism cannot be used here (a retry returns `4,5,1,2,3,6,7,8,9,10`, and a colliding token silently drops 500 rows), and why the key that works is the record's own. **Publish the `FINAL` cost.**
- [ ] T046 Write the store-down section with the queue depths and the reconciliation, what `discard: old` costs, and **why this consumer sets no redelivery limit where the other two do**. The measured strand — nothing delivered from round 4, `num_pending 0`, stream still full — is the argument, and it is a better one than the clause.
- [ ] T047 Write the `<ForwardRef>`: no reconciliation job, no query surface, no latency percentiles, and `message_events.delivery_latency_ms` still with no producer. **Say plainly that `webhook_attempts.latency_ms` is not that column** — one is how long an endpoint took to answer, the other how long a message took to reach a client.
- [ ] T048 Write the section amending SAD §6.2 to publish `webhook_attempts`, quoting what the publisher sends as the reason for each column.
- [ ] T049 [P] Write `relay-tutorial/app/(en)/part-4/chapter-03/<slug>/figures.ts` — at least two figures: the stream with a publisher and no consumer, and the two dedup mechanisms against the two failure modes.
- [ ] T050 [P] Add at least one `TRAP` box. The strongest candidate is the deduplication token that is accepted and ignored without the window — a mechanism that looks configured, does nothing, and reports success.
- [ ] T051 Publish the fences in **two kinds, because they are two mechanisms with two failure modes.** **New files take WHOLE-BODY fences** — `analytics/0003_webhook_attempts.sql` and every new service source — and carry no anchoring risk. **`compose.yaml` takes a HUNKED ```diff fence** if the ingester runs there; it is fenced in six chapters and 4.2's own amendment went through the same mechanism. **So does `vitest.coverage.config.mts`** once T038b pins the ingester's files — it is fenced in **eleven** chapters, most recently 3.23, and it is the amendment pass 4 missed while counting the two that are not needed. Name the file rather than saying "any amended fenced file": 4.2's hunk was verified before pasting precisely because its task named it. **And generate the hunk from the checker's own replay**: copy `check-fence-chain.mjs`, truncate it at the HEAD comparison, dump its end state, diff that against the working tree, delete the copy. **Normalise the trailing newline** — `fileLines` strips it on both sides, and not doing so produced a spurious second hunk in 4.2. **Verify the hunk applies clean before pasting, not after.**
- [ ] T052 Register the chapter in `relay-tutorial/lib/tutorial.ts` with a Vietnamese title.
- [ ] T053 Create `relay-tutorial/app/(vi)/vi/part-4/chapter-03/<slug>/` with `specs/046-chapter-4-1/vi-placeholder.py`, mirroring every fence. **Invent no Vietnamese** beyond the standing notice and the registry's own title.
- [ ] T054 Run `node scripts/prose-words.mjs` against the page and record the count. The bound is 2,000–4,000 outside fences (SC-008).
- [ ] T055 Run `pnpm check:fences` and **report the delta per line of T007's breakdown**, not only the total (SC-007). A total that moved in `(vi)` is somebody else's translation.
- [ ] T056 [P] Run the remaining gates and record each: `lint`, `typecheck`, `test`, **`build`** in `relay-platform` **first**, then `check:docs`, `check:srs`, `check:figures`, `check:errors` in `relay-tutorial`. `check:errors` reads `packages/protocol/dist`.
- [ ] T057 Write `specs/048-chapter-4-3/traceability.md`: FR-001…FR-014 and SC-001…SC-008 against the tasks that verify them, **with the method actually used** and a section recording every task premise that turned out to be wrong.
- [ ] T058 Write `specs/048-chapter-4-3/gaps.md`, carrying 047-1 (DR-10 against FR-ANL-06, both reasons), 047-2 (`delivery_latency_ms` still unproduced), 047-3 (the rollup is unbounded), 047-6 (no gate checks that a chapter's tag matches its chapter), and whatever this chapter opens.
- [ ] T059 Tag the chapter `part4-ch3` on `relay-platform`, **annotated**, following the convention 046 settled and 047 confirmed.
- [ ] T060 Confirm the close-out state: no stray `relay_corpus*` database, the lane's counts matching T009's, `services/api/migrations/` unchanged, and the stack down. Then commit phase 6 across all three repositories and update `CLAUDE.md`'s `<!-- SPECKIT -->` block with the close-out figures.

---

## Dependencies & Execution Order

```
Phase 1  premises        ──> everything. T001 and T002 can falsify the chapter's opening.
Phase 2  the table       ──> US1, US2, US3 all need somewhere to write
Phase 3  US1 (P1) 🎯     ──> US2 and US3 both need a working drain
Phase 4  US2 (P2)        ──> independent of US3
Phase 5  US3 (P3)        ──> independent of US2; both need Phase 3
Phase 6  the chapter     ──> needs all three stories' numbers
```

### User story dependencies

- **US1** depends on Phase 2 only. It is the MVP: the stream drains, which is the chapter's
  reason to exist.
- **US2** depends on US1 — you cannot measure a backlog draining without something that
  drains.
- **US3** depends on US1 for the same reason, and is independent of US2.

### Parallel opportunities

- Phase 1: T005–T009 are five independent recordings — `[P]`.
- Phase 6: T049, T050 and T056 touch different files from the prose tasks — `[P]`.
- **Phases 2 to 5 have none that matter.** Measurements are serial: nothing else runs on the
  machine during one.

## Implementation strategy

**MVP is Phases 1 + 2 + 3.** That yields a stream that drains into a store, which is the
chapter's title. US2 is what makes the second store affordable and US3 is what makes its
numbers trustworthy; neither is optional for the chapter, both are separable for the work.

**Stop points that are real:**

- **T001 and T002 can falsify the chapter's opening.** If something now consumes the stream,
  the chapter is about something else.
- **T013 and T036 are a pair.** If the dedup window turns out not to behave as R5 measured,
  US3's design changes and `ReplacingMergeTree` with `FINAL` is the fallback — at a read cost
  the chapter would then have to publish.
- **T031 may have no satisfying answer.** If the ingester cannot tell what `discard: old`
  dropped, say so.

## Notes

**ANALYSIS PASS 5 FOUND NO TESTS, IN A CHAPTER WHOSE SUBJECT THE CONSTITUTION NAMES.**
Twelve `test` matches in this file and every one an "Independent test:" header — manual
demonstrations. Constitution VI singles out **idempotency** and **tenant isolation** for 100%
branch coverage, and US3 is idempotency. **047's reason for shipping no tests does not
carry**: it said *"Nothing here joins a test lane"* and was right, because `analytics/`
matches no include glob. This chapter's preamble says the opposite and calls it a benefit —
**collected means measured**, and the benefit arrives with an obligation.

**THE STANDARD IS NOT 100%, AND THAT IS WRITTEN DOWN ALREADY.**
`vitest.coverage.config.mts` records `repository.ts` — which holds all three named
behaviours — at **89.51%**, pinned there deliberately because *"a threshold nothing can pass
makes CI permanently red and teaches everyone to ignore it."* **Measure, pin, name the
shortfall.** T038b does that.

**AND PASS 4 COUNTED THE COSTS IN ONE DIRECTION ONLY.** It found `pnpm-workspace.yaml` and
`turbo.json` need no amendment and recorded them as absent costs. It missed
`vitest.coverage.config.mts`, fenced in **eleven** chapters, which the pin amends. **Asking
what something costs is two searches, not one.**

**ANALYSIS PASS 4 CHANGED SHAPE: THREE ESTIMATES NOBODY WROTE DOWN.** The first three
passes found runtime behaviours that fail silently — a batch boundary, a redelivery limit, a
field name. This one found what the chapter costs. **Chapter 3.19 introduced
`services/dispatcher` at 5,889 prose words and 47 titled fences**, against SC-008's
2,000–4,000 and 4.2's 2,580 and 2, and no artifact had said so. The ingester is a smaller
job, so 47 is a ceiling — but **a split is likely rather than permitted**, and the plan
carries that now instead of Phase 6 discovering it.

**AND 3.19 ALREADY DECIDED THE SCAFFOLDING QUESTION.** It fenced the service's
`package.json` and its sources and skipped the `Dockerfile`, both tsconfigs and the vitest
config — four files a reader needs. That is the precedent, and T017b follows it knowingly
rather than meeting the question at T051 with prose half-written.

**TWO COSTS THAT ARE NOT THERE, CHECKED BECAUSE AN ABSENT COST IS INVISIBLE.**
`pnpm-workspace.yaml` globs `services/*` and `turbo.json` names no service at all, so a
fourth service amends neither — two hunked amendments to fenced files that do not have to
happen.

**ANALYSIS PASS 3 FOUND THE QUIETEST FAILURE OF THE THREE.** The publisher's field is
`attempted_at` and the column is `ts`. `JSONEachRow` leaves an unmatched column **at its
default** and reports success — and the default for `DateTime64` is the epoch, which is
older than the ninety-day TTL, so **the row is deleted at insert.** The insert returns OK,
the consumer acknowledges, the stream drains to zero, and the table is empty. Three settings
now stand between that and an empty table, each catching a different half: a renamed field
(`Code: 117`), an absent one (`Code: 469`, the constraint), and the ISO parse (`Code: 27`,
which was always loud).

**AND T023 PASSED ON IT.** Its three numbers agree at 0, 0, 0 over an empty table. **A
three-way equality with no floor is satisfied by nothing at all**, which is why the published
count is the fourth number now.

**THE PROBE ITSELF CONFLATED TWO CAUSES AND HAD TO BE SPLIT.** One run showed `ts = 1970`
with no error, another showed nothing inserted; they were a key mismatch and a parse failure
respectively, behaving in opposite directions. **The separation was the finding** — one
refuses, one lies.

**ANALYSIS PASS 2 FOUND A DEFAULT NOBODY CHOSE, WHICH IS WHERE PASS 1's DEFECT LIVED TOO.**
No artifact mentioned `max_deliver`, and with a finite one FR-006 is simply false. Measured
at `max_deliver: 3`: delivered on rounds 1–3, **nothing on round 4 or ever again**, and the
consumer then reported `num_pending 0 · ack_pending 0` **while the stream still held every
message.** At the existing runtimes' `MAX_DELIVER = 5` and 30-second `ack_wait`, two and a
half minutes of the store being down strands everything in flight.

**AND THE LOSS IS INVISIBLE TO THE INSTRUMENT YOU WOULD REACH FOR.** Stream depth stays high,
consumer lag goes to zero, and each number on its own reads as healthy. **The disagreement
between them is the signal**, which is why T028 records both.

**A LIMIT THAT IS RIGHT FOR ONE CONSUMER IS NOT A DEFAULT.** The dispatcher gives up after
ten attempts because an endpoint that has failed ten times is probably gone — sound, and it
does not transfer to a store that is merely restarting. Two passes, two defects, both in a
value inherited rather than decided.

**ANALYSIS PASS 1 KILLED THE PLAN'S CENTRAL MECHANISM.** The design derived a deduplication
token from a batch's stream sequence range, and **JetStream batch boundaries are not stable
across a redelivery**: a retry returned `4,5,1,2,3,6,7,8,9,10` where the original batch was
`1,2,3,4,5`, out of order and interleaved with newer messages. The token would differ, the
duplicate would be inserted — and since the token keys on itself rather than on the content,
a colliding range would have **silently dropped a different batch entirely.** Replaced by a
`ReplacingMergeTree` on the record's natural key, verified against three differently-cut
batches rather than against a replay of the same one.

**THE FAILURE IS NOT THAT THE PROBE WAS WRONG. IT IS THAT IT WAS RIGHT ABOUT ONE
CONFIGURATION.** R5 proved the token works when the server is handed the same batch twice.
It never asked whether the broker will hand you the same batch twice. **A design tested in
one configuration is a design tested nowhere**, and the plan had even flagged this as a stop
point at T013/T036 — it just arrived four phases earlier than expected, which is the
cheapest place it could have.

**RESEARCH RAN SIX PROBES AND TWO OF THEM WERE WRONG FIRST.** The dedup probe built both
batches with `generateUUIDv4()` in the sorting key, so its two inserts were not duplicates
and it reported 2,000 rows after `OPTIMIZE FINAL` as though that were a fact about
ClickHouse. And the stream probe read `consumers 0` on all three streams as evidence before
noticing that the services do not run as compose services — the code search is what settles
it, which is why T002 exists beside T001.

**THE CHAPTER'S BEST FINDING WAS WRITTEN DOWN BY SOMEBODY ELSE, THREE CHAPTERS AGO.**
`runtime.ts` says it exists because *"a future consumer forgets to dedupe → double webhooks
/ double metering"*, mitigated by *"a consumer template with dedup built in"*. This is that
consumer, and the dedup built in is a Postgres transaction it may not use. The comment was
right about the risk and could not have known which principle would bar the remedy.

**THREE NUMBERS ARE INHERITED AND T005, T006 AND T007 REPLACE THEM.** R4's 2,000/1,000,
R5's three lines, and the fence chain's 110. The first two are re-measured because a probe
that was wrong once is not evidence; the third because thirty of its problems belong to a
translation that is not this chapter's work.
