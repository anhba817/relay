# Tasks — chapter 4.3, the consumer that was promised

**Feature**: `specs/048-chapter-4-3/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**This chapter joins two things that already exist.** The `ANALYTICS` stream has been
filling since chapter 3.20 and the store landed in 4.2. Nothing between them.

**Verification methods, stated.** The drain and the redelivery are **D**. The store-down
behaviour is **D** for the queue depth and **A** for the claim that messaging is unaffected.
The Postgres-isolation claim is **I**.

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

- [ ] T011 Create `relay-platform/analytics/0003_webhook_attempts.sql` from [data-model.md](./data-model.md): ten columns, `MergeTree`, `PARTITION BY toYYYYMM(ts)`, `ORDER BY (environment_id, ts)`, `TTL toDateTime(ts) + INTERVAL 90 DAY`. **Name `relay_analytics` in the statement** — `CLICKHOUSE_DB` creates a database without making it the session's, so an unqualified `CREATE TABLE` lands in `default` with no error, and `apply.mjs` refuses a statement that does not name it (047 R14).
- [ ] T012 In `relay-platform/analytics/0003_webhook_attempts.sql`, make **`status` and `error` `Nullable`** and comment why. The publisher spreads them in only when present, because *"an explicit `undefined` is not the same as an absent key, and the difference is the whole meaning of 'nothing answered'"*. A non-nullable `status` writes **0** and claims an endpoint answered with status zero — 4.2's argument arriving in a new table before anyone can get it wrong again.
- [ ] T013 In `relay-platform/analytics/0003_webhook_attempts.sql`, add `SETTINGS non_replicated_deduplication_window = <n>` and **choose `<n>` deliberately**. It bounds how far back a redelivery can be recognised. Without this line the `insert_deduplication_token` in Phase 5 is accepted and ignored: the insert succeeds, the duplicate lands, nothing reports anything.
- [ ] T014 Apply it with `node analytics/apply.mjs` and record the output in `specs/048-chapter-4-3/baseline.txt`: **`applied 1: 0003_webhook_attempts.sql`** and three skipped. Run it again and record **`applied nothing`**. This is the ledger's first use by somebody not trying to make it fire.
- [ ] T015 Amend `docs/05-sad.md` §6.2 to publish `webhook_attempts` (FR-008), and sync it: **`pnpm sync:docs` in `relay-tutorial`, or `check:docs` fails** with `content/docs/05-sad.md differs from docs/05-sad.md`. 047 hit that gate and it caught the omission.
- [ ] T016 Commit phase 2 — `relay-platform/analytics/`, `docs/05-sad.md`, `relay-tutorial/content/docs/`. Gates first: `pnpm lint && pnpm typecheck && pnpm test` in `relay-platform`.

---

## Phase 3: User Story 1 — the stream drains into the store (Priority: P1) 🎯 MVP

**Goal**: the records that have been accumulating become rows, and new ones follow.

**Independent test**: publish a known number of attempt records, run the ingester, and
compare the store's row count against the stream's delivered count.

- [ ] T017 [US1] Decide where the ingester lives and **record the decision and its reason** in `specs/048-chapter-4-3/baseline.txt` (FR-014). `services/*/src/**` is collected by the coverage lane; `analytics/**` is collected by nothing. A fourth service directory is the SAD's shape.
- [ ] T018 [US1] Create the ingester with a durable pull consumer on `analytics.>`. **State whether `createConsumerRuntime` is reused, parameterised or replaced, and why** — its claim is a Postgres transaction and constitution III forbids that here (T004). **The template written to stop a future consumer double-counting is the one this consumer may not reuse**, and that is the chapter's argument, not an inconvenience to route around.
- [ ] T019 [US1] Bound the batch by **both** a row count and an elapsed interval (DR-11 publishes 2 s or 10,000 rows). A count alone never flushes for a quiet tenant; an interval alone has no bound under load. **Publish what each bound costs at a stated publish rate** (SC-004) rather than quoting DR-11.
- [ ] T020 [US1] Shape records with an **allow-list**, mirroring the publisher's own — *"An allow-list fails closed when somebody adds a field; a spread fails open."*
- [ ] T021 [US1] Insert one batch as one statement, and **acknowledge only after the insert returns** (FR-003). A record that was not written is not acknowledged.
- [ ] T022 [US1] Handle a malformed record: count it, set it aside, and **do not let it stall the stream behind it** (FR-010). The existing runtime's comment names this case — *"A payload that will never parse must not consume five delivery attempts"* — so there is a precedent to follow or to differ from deliberately.
- [ ] T023 [US1] Run the drain and record in `specs/048-chapter-4-3/baseline.txt` **two counts side by side**: rows in `relay_analytics.webhook_attempts` and `uniqExact((delivery_id, attempt))`. **They must be equal.** A count alone cannot tell you whether something was written twice.
- [ ] T024 [US1] Record the consumer's pending count after the drain, from the broker rather than from the ingester's own log. **A process reporting that it finished is not evidence that the queue is empty.**
- [ ] T025 [US1] Verify no request waits on an analytical write (FR-ANL-02) and record how it was verified. `publishAttempt` already *"never throws"* and is called after the outcome transaction commits; this task confirms the consumer added nothing to that path.
- [ ] T026 [US1] Commit phase 3 — the ingester and `specs/048-chapter-4-3/baseline.txt`. Gates first.

---

## Phase 4: User Story 2 — the analytical store can be gone (Priority: P2)

**Goal**: NFR-REL-05 measured rather than asserted.

**Independent test**: stop the store, exercise the platform, confirm messaging is unaffected
and the queue grows; restart and confirm the backlog drains with no gap.

- [ ] T027 [US2] Stop ClickHouse and exercise the send and delivery paths. Record in `specs/048-chapter-4-3/baseline.txt` that neither reports an error attributable to the store, **with the requests counted** — "no errors" from a run that sent nothing is the zero that proves nothing.
- [ ] T028 [US2] Record the stream's depth before, during and after the outage. The rise is the claim NFR-REL-05 makes.
- [ ] T029 [US2] Confirm the ingester **does not acknowledge** what it could not write (FR-003), and record how that was confirmed rather than asserting it.
- [ ] T030 [US2] Restart the store, drain, and reconcile: every record published during the outage is in the table, counted against what was published. **Record both numbers.**
- [ ] T031 [US2] Record what `discard: old` at 1 GiB means for records dropped while an ingester is down (FR-011), and **whether the ingester can tell**. The broker drops the oldest without telling anyone; if the honest answer is "it cannot know", that belongs in the prose rather than in a silence.
- [ ] T032 [US2] Record whether seven days is still the right retention now that something consumes the stream (FR-011). It was chosen while nothing did. **Do not presume the answer**; the chapter states it either way.
- [ ] T033 [US2] Commit phase 4 — `specs/048-chapter-4-3/baseline.txt`. Gates first.

---

## Phase 5: User Story 3 — a redelivery does not become a second row (Priority: P3)

**Goal**: the defect that stays invisible until a customer disputes a bill.

**Independent test**: force a redelivery of a written batch, then compare counts.

- [ ] T034 [US3] Derive the `insert_deduplication_token` from the batch's **stream sequence range**, so a redelivery of the same range reproduces it exactly. Record why the publisher's `{deliveryId}:{attempt}` id does not cover this: that is **broker-side publish dedup**, and at-least-once is about the consumer being handed the same record twice. **Two mechanisms, two failure modes.**
- [ ] T035 [US3] Force a redelivery — stop the ingester after an insert and before the acknowledgement — and record the row count before and after. **It must not move.**
- [ ] T036 [US3] **Test the mechanism red, and for its own reason.** Remove `non_replicated_deduplication_window` from the table, repeat the redelivery, and record that the count **doubles with no error reported**. Restore, repeat, confirm it holds again. A mechanism that fails silently when half-configured has to be shown failing, or a reader assumes the token alone was doing the work. **Clean up the probe before anything is counted.**
- [ ] T037 [US3] Record what falls **outside** the dedup window: a redelivery older than `<n>` blocks slips through. State the number and what it bounds.
- [ ] T038 [US3] Verify the ingester wrote nothing to PostgreSQL and issued no query against it on the ingestion path (FR-009, SC-005): `schema_migrations` unchanged, `consumed_events` unchanged, and the lane's row counts matching T009's. **Constitution III is the reason this chapter cannot reuse the obvious runtime**, so it is the claim most worth checking.
- [ ] T039 [US3] Record in [contracts/ingester.md](./contracts/ingester.md) anything the contract gained after the code ran, **and which task forced it**. A contract written by one caller is a contract written by one caller's opinion.
- [ ] T040 [US3] Commit phase 5 — the ingester, `specs/048-chapter-4-3/`. Gates first.

---

## Phase 6: The chapter, the amendments, and closing out

- [ ] T041 Choose the slug and create `relay-tutorial/app/(en)/part-4/chapter-03/<slug>/page.mdx`.
- [ ] T042 Write the opening: something has been publishing into a stream since chapter 3.20 and nothing has ever read it. **Open with the broker's own answer**, not with a description of it.
- [ ] T043 Write the section on why the reusable runtime cannot be reused — `claimEvent` is a Postgres transaction and constitution III keeps the paths apart. **Name the subject, not the ordinal** (045 FR-008).
- [ ] T044 Write the batching section with the measured cost of each bound, not DR-11's numbers restated.
- [ ] T045 Write the redelivery section: `ReplacingMergeTree` at 2,000 against 1,000, the token-plus-window that refuses at insert, and **the half-configured case that reports success**.
- [ ] T046 Write the store-down section with the queue depths and the reconciliation, and what `discard: old` costs.
- [ ] T047 Write the `<ForwardRef>`: no reconciliation job, no query surface, no latency percentiles, and `message_events.delivery_latency_ms` still with no producer. **Say plainly that `webhook_attempts.latency_ms` is not that column** — one is how long an endpoint took to answer, the other how long a message took to reach a client.
- [ ] T048 Write the section amending SAD §6.2 to publish `webhook_attempts`, quoting what the publisher sends as the reason for each column.
- [ ] T049 [P] Write `relay-tutorial/app/(en)/part-4/chapter-03/<slug>/figures.ts` — at least two figures: the stream with a publisher and no consumer, and the two dedup mechanisms against the two failure modes.
- [ ] T050 [P] Add at least one `TRAP` box. The strongest candidate is the deduplication token that is accepted and ignored without the window — a mechanism that looks configured, does nothing, and reports success.
- [ ] T051 Publish any amended fenced file as a **hunked ```diff fence**, and **generate the hunk from the checker's own replay**: copy `check-fence-chain.mjs`, truncate it at the HEAD comparison, dump its end state, diff that against the working tree, delete the copy. **Normalise the trailing newline** — `fileLines` strips it on both sides, and not doing so produced a spurious second hunk in 4.2. **Verify the hunk applies clean before pasting, not after.**
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
